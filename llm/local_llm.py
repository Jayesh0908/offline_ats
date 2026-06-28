"""
Local LLM interface for parsing resumes into structured JSON.
Supports both Ollama API and direct llama.cpp GGUF inference.
"""
import json
import re
import requests
import subprocess
import tempfile
import os
from typing import Dict, Any, Optional, List
import config


def build_parse_prompt(resume_text: str) -> str:
    """
    Build a prompt for the LLM to extract structured information from a resume.
    
    Args:
        resume_text: Raw text extracted from the resume
        
    Returns:
        Formatted prompt string
    """
    prompt = f"""<|system|>
You are a resume parsing assistant. Extract the following fields from the resume and return ONLY valid JSON without any additional text, markdown, or code blocks.

Fields to extract:
- name (string)
- email (string)
- phone (string)
- skills (array of strings)
- education (array of objects with degree, college fields)
- experience (array of objects with company, role, years fields)
- projects (array of strings)

If a field is not found, use empty string or empty array as appropriate.
<|end|>
<|user|>
Resume:
{resume_text[:3000]}
<|end|>
<|assistant|>"""

    return prompt


def parse_llm_response(response_text: str) -> Dict[str, Any]:
    """
    Parse the LLM response to extract valid JSON.
    
    Args:
        response_text: Raw response from the LLM
        
    Returns:
        Parsed JSON dictionary
    """
    # Remove any markdown code block markers
    cleaned = re.sub(r'```json\s*', '', response_text, flags=re.IGNORECASE)
    cleaned = re.sub(r'```\s*', '', cleaned)
    
    # Try to find JSON object in the response
    json_match = re.search(r'\{.*\}', cleaned, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass
    
    # Fallback: try parsing the entire cleaned text
    try:
        return json.loads(cleaned.strip())
    except json.JSONDecodeError:
        print(f"[LLM] Failed to parse response as JSON. Raw: {response_text[:200]}")
        return {
            "name": "",
            "email": "",
            "phone": "",
            "skills": [],
            "education": [],
            "experience": [],
            "projects": []
        }


def parse_with_ollama(resume_text: str) -> Dict[str, Any]:
    """
    Parse a resume using Ollama's API.
    
    Args:
        resume_text: Raw text from the resume
        
    Returns:
        Structured JSON with candidate information
    """
    prompt = build_parse_prompt(resume_text)
    
    try:
        response = requests.post(
            f"{config.OLLAMA_BASE_URL}/api/generate",
            json={
                "model": config.OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "temperature": config.LLM_TEMPERATURE,
                "num_predict": config.LLM_MAX_TOKENS
            },
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()
            raw_response = result.get("response", "")
            return parse_llm_response(raw_response)
        else:
            print(f"[LLM] Ollama API error: {response.status_code} - {response.text}")
            return {}
            
    except requests.exceptions.ConnectionError:
        print("[LLM] Ollama connection failed. Is Ollama running?")
        return {}
    except Exception as e:
        print(f"[LLM] Ollama error: {e}")
        return {}


def parse_with_llamacpp(resume_text: str) -> Dict[str, Any]:
    """
    Parse a resume using direct llama.cpp GGUF inference.
    
    Args:
        resume_text: Raw text from the resume
        
    Returns:
        Structured JSON with candidate information
    """
    prompt = build_parse_prompt(resume_text)
    
    # Determine which model to use
    model_path = config.PHI3_GGUF_PATH
    if config.LLM_MODEL == "qwen2.5":
        model_path = config.QWEN_GGUF_PATH
    
    if not model_path.exists():
        print(f"[LLM] Model not found at {model_path}")
        return {}
    
    # Write prompt to a temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(prompt)
        prompt_file = f.name
    
    try:
        result = subprocess.run(
            [
                "llama-cli",
                "-m", str(model_path),
                "-f", prompt_file,
                "--temp", str(config.LLM_TEMPERATURE),
                "-n", str(config.LLM_MAX_TOKENS),
                "--ctx-size", str(config.LLM_CONTEXT_SIZE),
                "--no-display-prompt"
            ],
            capture_output=True,
            text=True,
            timeout=180
        )
        
        if result.returncode == 0:
            return parse_llm_response(result.stdout)
        else:
            print(f"[LLM] llama.cpp error: {result.stderr}")
            return {}
            
    except FileNotFoundError:
        print("[LLM] llama-cli not found. Install llama.cpp or use Ollama.")
        return {}
    except subprocess.TimeoutExpired:
        print("[LLM] llama.cpp inference timed out")
        return {}
    except Exception as e:
        print(f"[LLM] llama.cpp error: {e}")
        return {}
    finally:
        os.unlink(prompt_file)


def parse_resume(resume_text: str) -> Dict[str, Any]:
    """
    Parse a resume using the configured local LLM method.
    Falls back to rule-based extraction if LLM is unavailable.
    
    Args:
        resume_text: Raw text extracted from the resume
        
    Returns:
        Structured JSON with candidate information
    """
    if not resume_text.strip():
        print("[LLM] Empty resume text, cannot parse")
        return {}
    
    # Try LLM-based parsing
    if config.LLM_MODEL in ("phi3", "qwen2.5"):
        result = parse_with_ollama(resume_text)
        if result and result.get("name"):
            return result
        result = parse_with_llamacpp(resume_text)
        if result and result.get("name"):
            return result
    
    # Fallback: basic rule-based extraction
    print("[LLM] LLM parsing failed or unavailable, using rule-based fallback")
    return rule_based_parse(resume_text)


def rule_based_parse(text: str) -> Dict[str, Any]:
    """
    Basic rule-based resume parsing as fallback when LLM is unavailable.
    Extracts email, phone, and basic fields using regex patterns.
    
    Args:
        text: Raw resume text
        
    Returns:
        Partially parsed JSON
    """
    result = {
        "name": "",
        "email": "",
        "phone": "",
        "skills": [],
        "education": [],
        "experience": [],
        "projects": []
    }
    
    lines = text.split('\n')
    
    # First non-empty line is likely the name
    for line in lines:
        line = line.strip()
        if line and len(line) < 100:
            result["name"] = line
            break
    
    # Extract email
    email_match = re.search(r'[\w.+-]+@[\w-]+\.[\w.-]+', text)
    if email_match:
        result["email"] = email_match.group()
    
    # Extract phone
    phone_match = re.search(
        r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
        text
    )
    if phone_match:
        result["phone"] = phone_match.group()
    
    # Simple skill extraction from common tech keywords
    common_skills = [
        "Python", "Java", "JavaScript", "TypeScript", "C++", "C#", "Ruby", "Go", "Rust",
        "React", "Angular", "Vue", "Node.js", "Django", "Flask", "Spring", "Express",
        "SQL", "MongoDB", "PostgreSQL", "MySQL", "Redis", "Docker", "Kubernetes",
        "AWS", "Azure", "GCP", "Git", "Linux", "REST", "GraphQL", "HTML", "CSS",
        "TensorFlow", "PyTorch", "Machine Learning", "Deep Learning", "NLP",
        "Data Science", "Data Analysis", "Tableau", "Power BI",
        "Agile", "Scrum", "JIRA", "CI/CD", "Jenkins", "Terraform"
    ]
    
    found_skills = []
    text_lower = text.lower()
    for skill in common_skills:
        if skill.lower() in text_lower:
            found_skills.append(skill)
    
    # Also check for comma-separated skills section
    skills_section = re.search(
        r'(?:skills|technical skills|technologies)[:\s]*(.+?)(?:\n\n|\Z)',
        text, re.IGNORECASE | re.DOTALL
    )
    if skills_section:
        raw_skills = skills_section.group(1)
        # Extract individual skills
        for s in re.split(r'[,;•\n]', raw_skills):
            s = s.strip().strip('•-')
            if s and len(s) < 50:
                found_skills.append(s)
    
    result["skills"] = list(set(found_skills))
    
    return result