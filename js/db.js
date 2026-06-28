/**
 * IndexedDB wrapper for Offline ATS.
 * Stores candidate data entirely in the browser.
 */
const DB_NAME = 'OfflineATS';
const DB_VERSION = 1;
const STORE_NAME = 'candidates';

let _db = null;

function openDB() {
  return new Promise((resolve, reject) => {
    if (_db) return resolve(_db);
    const req = indexedDB.open(DB_NAME, DB_VERSION);
    req.onupgradeneeded = e => {
      const db = e.target.result;
      if (!db.objectStoreNames.contains(STORE_NAME)) {
        const store = db.createObjectStore(STORE_NAME, { keyPath: 'id', autoIncrement: true });
        store.createIndex('name', 'name', { unique: false });
        store.createIndex('email', 'email', { unique: false });
        store.createIndex('skills', 'skills', { unique: false, multiEntry: true });
      }
    };
    req.onsuccess = e => { _db = e.target.result; resolve(_db); };
    req.onerror = e => reject(e.target.error);
  });
}

async function addCandidate(candidate) {
  const db = await openDB();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE_NAME, 'readwrite');
    const store = tx.objectStore(STORE_NAME);
    candidate.createdAt = new Date().toISOString();
    const req = store.add(candidate);
    req.onsuccess = () => resolve(req.result);
    req.onerror = e => reject(e.target.error);
  });
}

async function getAllCandidates() {
  const db = await openDB();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE_NAME, 'readonly');
    const store = tx.objectStore(STORE_NAME);
    const req = store.getAll();
    req.onsuccess = () => resolve(req.result);
    req.onerror = e => reject(e.target.error);
  });
}

async function getCandidate(id) {
  const db = await openDB();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE_NAME, 'readonly');
    const store = tx.objectStore(STORE_NAME);
    const req = store.get(id);
    req.onsuccess = () => resolve(req.result);
    req.onerror = e => reject(e.target.error);
  });
}

async function deleteCandidate(id) {
  const db = await openDB();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE_NAME, 'readwrite');
    const store = tx.objectStore(STORE_NAME);
    const req = store.delete(id);
    req.onsuccess = () => resolve();
    req.onerror = e => reject(e.target.error);
  });
}

async function deleteAllCandidates() {
  const db = await openDB();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE_NAME, 'readwrite');
    const store = tx.objectStore(STORE_NAME);
    const req = store.clear();
    req.onsuccess = () => resolve();
    req.onerror = e => reject(e.target.error);
  });
}

async function getCandidateCount() {
  const db = await openDB();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE_NAME, 'readonly');
    const store = tx.objectStore(STORE_NAME);
    const req = store.count();
    req.onsuccess = () => resolve(req.result);
    req.onerror = e => reject(e.target.error);
  });
}

async function searchCandidates(query) {
  const all = await getAllCandidates();
  const q = query.toLowerCase();
  return all.filter(c => {
    const haystack = [
      c.name, c.email, c.phone,
      ...(c.skills || []),
      ...(c.education || []).map(e => `${e.degree} ${e.college}`),
      ...(c.experience || []).map(e => `${e.company} ${e.role}`),
      ...(c.projects || [])
    ].join(' ').toLowerCase();
    return haystack.includes(q);
  });
}

// Export
window.DB = {
  openDB, addCandidate, getAllCandidates, getCandidate,
  deleteCandidate, deleteAllCandidates, getCandidateCount, searchCandidates
};
