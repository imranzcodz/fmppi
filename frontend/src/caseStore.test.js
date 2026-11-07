const { createCase, canAddEvidence, canViewAdmin, verifyMatch } = require("../src/caseStore");

test("createCase returns a case with open status", () => {
  const c = createCase("CASE-1", "Missing person");
  expect(c.caseNumber).toBe("CASE-1");
  expect(c.title).toBe("Missing person");
  expect(c.status).toBe("open");
  expect(typeof c.id).toBe("number");
});

test("createCase throws when missing fields", () => {
  expect(() => createCase("", "x")).toThrow();
  expect(() => createCase("CASE-1", "")).toThrow();
});

test("canAddEvidence allows admin and investigator", () => {
  expect(canAddEvidence("admin")).toBe(true);
  expect(canAddEvidence("investigator")).toBe(true);
  expect(canAddEvidence("reporter")).toBe(false);
  expect(canAddEvidence("reviewer")).toBe(false);
});

test("canViewAdmin only allows admin", () => {
  expect(canViewAdmin("admin")).toBe(true);
  expect(canViewAdmin("reporter")).toBe(false);
});

test("verifyMatch returns true for identical images", () => {
  expect(verifyMatch("a.jpg", "a.jpg")).toBe(true);
  expect(verifyMatch("a.jpg", "b.jpg")).toBe(false);
});
