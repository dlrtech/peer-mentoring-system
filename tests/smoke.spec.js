import { test, expect } from '@playwright/test';

test('Uygulama ana sayfası hatasız açılmalı', async ({ page }) => {
  await page.goto('/');
  await expect(page.locator('body')).toBeVisible();
});
