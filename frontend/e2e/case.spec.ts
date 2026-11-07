import { test, expect } from "@playwright/test";

test("homepage renders the FMPPI case dashboard title", async ({ page }) => {
  await page.goto("/");
  await expect(page.locator("h1")).toContainText("FMPPI Case Dashboard");
});

test("case count element is present on load", async ({ page }) => {
  await page.goto("/");
  await expect(page.locator("#case-count")).toBeVisible();
});
