/**
 * Client-side resume parser.
 * Extracts structured fields from raw resume text using regex heuristics.
 */

const SKILL_KEYWORDS = [
  'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'go', 'rust', 'ruby', 'php',
  'swift', 'kotlin', 'scala', 'r', 'matlab', 'perl', 'sql', 'nosql', 'html', 'css',
  'react', 'angular', 'vue', 'svelte', 'next.js', 'node.js', 'express', 'django', 'flask',
  'fastapi', 'spring', 'spring boot', '.net', 'laravel', 'rails',
  'tensorflow', 'pytorch', 'keras', 'scikit-learn', 'pandas', 'numpy', 'opencv',
  'machine learning', 'deep learning', 'nlp', 'computer vision', 'ai',
  'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform', 'ansible',
  'jenkins', 'github actions', 'gitlab ci', 'ci/cd', 'devops',
  'git', 'linux', 'bash', 'powershell', 'rest api', 'graphql', 'grpc',
  'mongodb', 'postgresql', 'mysql', 'redis', 'elasticsearch', 'dynamodb', 'sqlite',
  'kafka', 'rabbitmq', 'nginx', 'apache',
  'figma', 'sketch', 'adobe xd', 'photoshop', 'illustrator',
  'agile', 'scrum', 'jira', 'confluence', 'trello',
  'data analysis', 'data engineering', 'data science', 'etl', 'power bi', 'tableau',
  'blockchain', 'solidity', 'web3',
  'cybersecurity', 'penetration testing', 'networking',
  'android', 'ios', 'flutter', 'react native', 'xamarin',
  'selenium', 'cypress', 'jest', 'pytest', 'junit', 'mocha',
  'streamlit', 'gradio', 'hugging face', 'transformers', 'langchain',
  'microservices', 'system design', 'design patterns', 'oop',
  'communication', 'leadership', 'teamwork', 'problem solving', 'critical thinking'
];

function extractName(text) {
  const lines = text.split('\n').map(l => l.trim()).filter(l => l.length > 0);
  // First non-empty line is usually the name
  for (const line of lines.slice(0, 5)) {
    // Skip lines that look like headers or contain email/phone
    if (line.match(/@/) || line.match(/\d{10}/) || line.length > 60) continue;
    if (line.match(/resume|curriculum|vitae|cv|objective|summary/i)) continue;
    // A name is typically 2-4 words, all starting with uppercase
    const words = line.split(/\s+/);
    if (words.length >= 2 && words.length <= 5) {
      const looksLikeName = words.every(w => w.match(/^[A-Z]/));
      if (looksLikeName) return line;
    }
  }
  // Fallback: first short line
  for (const line of lines.slice(0, 3)) {
    if (line.length > 3 && line.length < 50 && !line.match(/@|\d{5,}/)) return line;
  }
  return 'Unknown';
}

function extractEmail(text) {
  const match = text.match(/[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}/);
  return match ? match[0] : '';
}

function extractPhone(text) {
  const patterns = [
    /(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}/,
    /(?:\+?\d{1,3}[-.\s]?)?\d{10}/,
    /(?:\+?\d{1,3}[-.\s]?)?\d{5}[-.\s]?\d{5}/
  ];
  for (const p of patterns) {
    const match = text.match(p);
    if (match) return match[0];
  }
  return '';
}

function extractSkills(text) {
  const lower = text.toLowerCase();
  const found = [];
  for (const skill of SKILL_KEYWORDS) {
    // Match whole-word (with some flexibility for special chars)
    const escaped = skill.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const regex = new RegExp(`\\b${escaped}\\b`, 'i');
    if (regex.test(lower)) {
      found.push(skill.charAt(0).toUpperCase() + skill.slice(1));
    }
  }
  return [...new Set(found)];
}

function extractEducation(text) {
  const education = [];
  const degreePatterns = [
    /(?:B\.?(?:Tech|Sc|A|E|Com|Eng)|M\.?(?:Tech|Sc|A|BA|Com|Eng)|Ph\.?D|MBA|BCA|MCA|B\.?S|M\.?S|Bachelor|Master|Diploma|Associate)/gi
  ];
  const lines = text.split('\n');
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    for (const pattern of degreePatterns) {
      pattern.lastIndex = 0;
      const match = pattern.exec(line);
      if (match) {
        // Try to find college name nearby
        const context = lines.slice(Math.max(0, i - 1), i + 3).join(' ');
        const collegePat = /(?:university|institute|college|school|iit|nit|iiit|bits|vit|srm|anna|amity|manipal|jntu|osmania|delhi|mumbai|bangalore|chennai|pune|hyderabad)\b[^,.\n]*/i;
        const collegeMatch = context.match(collegePat);
        education.push({
          degree: match[0],
          college: collegeMatch ? collegeMatch[0].trim() : ''
        });
        break;
      }
    }
  }
  return education;
}

function extractExperience(text) {
  const experience = [];
  const lines = text.split('\n');
  // Look for patterns like "Company Name | Role | Duration" or similar
  const expPattern = /(?:(\d+(?:\.\d+)?)\s*(?:\+?\s*)?(?:years?|yrs?))/gi;
  const roleKeywords = /(?:engineer|developer|architect|analyst|manager|lead|intern|designer|consultant|specialist|administrator|director|coordinator|associate|scientist|researcher)/i;

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    if (roleKeywords.test(line)) {
      const yearsMatch = lines.slice(i, i + 3).join(' ').match(expPattern);
      const years = yearsMatch ? parseFloat(yearsMatch[0]) : 0;
      // Try to extract company from the line or surrounding lines
      const parts = line.split(/[|•·–—,]/);
      experience.push({
        role: parts[0]?.trim() || line.substring(0, 50),
        company: parts[1]?.trim() || '',
        years: years
      });
    }
  }
  return experience.slice(0, 10); // Cap at 10
}

function extractProjects(text) {
  const projects = [];
  const lines = text.split('\n');
  let inProjectSection = false;

  for (const line of lines) {
    const trimmed = line.trim();
    if (trimmed.match(/^projects?\b/i)) {
      inProjectSection = true;
      continue;
    }
    if (inProjectSection) {
      if (trimmed.match(/^(education|experience|skills|certif|achiev|award|hobby|interest|referenc)/i)) {
        break;
      }
      if (trimmed.length > 5 && trimmed.length < 120) {
        const cleaned = trimmed.replace(/^[•\-▸▪○●◦‣]\s*/, '');
        if (cleaned.length > 3) projects.push(cleaned);
      }
    }
  }
  return projects.slice(0, 8);
}

function parseResume(text) {
  return {
    name: extractName(text),
    email: extractEmail(text),
    phone: extractPhone(text),
    skills: extractSkills(text),
    education: extractEducation(text),
    experience: extractExperience(text),
    projects: extractProjects(text),
    resumeText: text
  };
}

// Export
window.ResumeParser = { parseResume };
