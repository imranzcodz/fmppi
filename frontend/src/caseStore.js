function createCase(caseNumber, title) {
  if (!caseNumber || !title) {
    throw new Error("caseNumber and title required");
  }
  return { caseNumber, title, status: "open", id: Date.now() };
}

function canAddEvidence(role) {
  return role === "admin" || role === "investigator";
}

function canViewAdmin(role) {
  return role === "admin";
}

function verifyMatch(probe, gallery) {
  return probe === gallery;
}

module.exports = { createCase, canAddEvidence, canViewAdmin, verifyMatch };
