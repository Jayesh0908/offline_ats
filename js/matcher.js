/**
 * Client-side candidate matcher.
 * Scores candidates against a job description using TF-IDF-like keyword matching.
 */

function tokenize(text) {
  return text.toLowerCase()
    .replace(/[^a-z0-9+#.\s]/g, ' ')
    .split(/\s+/)
    .filter(t => t.length > 1);
}

function computeTF(tokens) {
  const tf = {};
  for (const t of tokens) {
    tf[t] = (tf[t] || 0) + 1;
  }
  const total = tokens.length || 1;
  for (const t in tf) tf[t] /= total;
  return tf;
}

function cosineSimilarity(vecA, vecB) {
  const allKeys = new Set([...Object.keys(vecA), ...Object.keys(vecB)]);
  let dot = 0, magA = 0, magB = 0;
  for (const k of allKeys) {
    const a = vecA[k] || 0;
    const b = vecB[k] || 0;
    dot += a * b;
    magA += a * a;
    magB += b * b;
  }
  const denom = Math.sqrt(magA) * Math.sqrt(magB);
  return denom === 0 ? 0 : dot / denom;
}

function skillMatchScore(jdSkills, candidateSkills) {
  if (jdSkills.length === 0) return 0;
  const jdSet = new Set(jdSkills.map(s => s.toLowerCase()));
  const candSet = new Set(candidateSkills.map(s => s.toLowerCase()));
  let matches = 0;
  for (const s of jdSet) {
    if (candSet.has(s)) matches++;
  }
  return matches / jdSet.size;
}

function rankCandidates(jdText, candidates) {
  const jdTokens = tokenize(jdText);
  const jdTF = computeTF(jdTokens);

  // Extract skills from JD for skill matching
  const jdSkills = window.ResumeParser
    ? window.ResumeParser.parseResume(jdText).skills
    : [];

  const results = candidates.map(candidate => {
    // Text similarity (TF cosine)
    const candText = [
      candidate.name || '',
      ...(candidate.skills || []),
      ...(candidate.experience || []).map(e => `${e.role} ${e.company}`),
      ...(candidate.projects || []),
      candidate.resumeText || ''
    ].join(' ');

    const candTokens = tokenize(candText);
    const candTF = computeTF(candTokens);
    const textScore = cosineSimilarity(jdTF, candTF);

    // Skill match
    const skillScore = skillMatchScore(jdSkills, candidate.skills || []);

    // Combined: 60% text similarity + 40% skill match
    const finalScore = 0.6 * textScore + 0.4 * skillScore;

    return {
      ...candidate,
      textScore: Math.round(textScore * 100) / 100,
      skillScore: Math.round(skillScore * 100) / 100,
      finalScore: Math.round(finalScore * 100) / 100,
      finalScorePct: Math.round(finalScore * 100)
    };
  });

  results.sort((a, b) => b.finalScore - a.finalScore);
  return results;
}

// Export
window.Matcher = { rankCandidates };
