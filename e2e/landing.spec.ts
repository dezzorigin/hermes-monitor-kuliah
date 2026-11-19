import { test, expect } from "@playwright/test";

// E2E landing hermes-monitor-kuliah — HANYA di CI.
// Memeriksa judul, strip hari-ini (jam WIB live), 6 blok hari, 13 baris
// pelajaran, papan status monitor, dan tidak ada overflow horizontal
// di mobile 390px (Pixel 7).
test("landing memuat judul + jadwal lengkap", async ({ page }) => {
  await page.goto("/");
  await expect(page).toHaveTitle(/Hermes Monitor Kuliah/);
  await expect(page.locator("h1")).toContainText("Hermes Monitor Kuliah");

  // strip hari ini terisi oleh app.js (jam WIB live)
  await expect(page.locator("#today-date")).not.toHaveText("—");
  await expect(page.locator("#wib-clock")).not.toHaveText("—");
  await expect(page.locator("#now-class")).not.toHaveText(/Memuat status/);

  // jadwal: 6 hari, 13 pelajaran, bentrok Sabtu terdokumentasi
  await expect(page.locator("article.day")).toHaveCount(6);
  await expect(page.locator("li.lesson")).toHaveCount(13);
  await expect(page.locator("article.day[data-hari='Sabtu'] li.lesson")).toHaveCount(2);
  await expect(page.locator("article.day[data-hari='Rabu']")).toContainText("Komputasi Numerik");
  await expect(page.locator("article.day[data-hari='Kamis']")).toContainText("Sistem Operasi");

  // papan status monitor + stempel khas
  await expect(page.locator(".monitor")).toContainText("Gerbang absen");
  await expect(page.locator(".stamp-idle")).toContainText("Di luar jendela");
  await expect(page.locator(".stamp-ok")).toContainText("Hadir");
  await expect(page.locator(".monitor")).toContainText("contoh");
});

test("mobile: tanpa overflow horizontal", async ({ page }) => {
  await page.goto("/");
  const overflow = await page.evaluate(
    () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
  );
  expect(overflow).toBeLessThanOrEqual(0);
  // target sentuh: baris pelajaran cukup tinggi
  const box = await page.locator("li.lesson").first().boundingBox();
  expect(box?.height).toBeGreaterThanOrEqual(44);
});
