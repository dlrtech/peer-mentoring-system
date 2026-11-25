import { test, expect } from '@playwright/test';

const BACKEND_URL = 'http://localhost:8000';

test.describe('Akran Mentörlük Sistemi - Smoke (Duman) Testleri', () => {
  test('Uygulama ana sayfası hatasız açılmalı', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('body')).toBeVisible();
  });

  test('Backend sağlık kontrolü (GET /health) 200 OK dönmeli', async ({ request }) => {
    const response = await request.get(`${BACKEND_URL}/health`);
    expect(response.status()).toBe(200);

    const body = await response.json();
    expect(body).toEqual({ status: 'ok' });
  });

  test('Backend ana uç noktası (GET /) erişilebilir olmalı', async ({ request }) => {
    const response = await request.get(`${BACKEND_URL}/`);
    expect(response.ok()).toBeTruthy();
  });
});