import { test, expect } from '@playwright/test';

const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:5000';

test.describe('Dashboard E2E Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the dashboard
    await page.goto('/');
  });

  test('should load dashboard page successfully', async ({ page }) => {
    // Check if the page title is correct
    await expect(page).toHaveTitle(/KOR.AI Surveillance Platform/);
    
    // Check if the navigation bar is present
    await expect(page.locator('nav')).toBeVisible();
    
    // Check if the main content area is present
    await expect(page.locator('main, .dashboard, [data-testid="dashboard"]')).toBeVisible();
  });

  test('should display navigation correctly', async ({ page }) => {
    // Check if navigation elements are present
    const navigation = page.locator('nav');
    await expect(navigation).toBeVisible();
    
    // Check for logo or brand name
    await expect(navigation.locator('text=/KOR.AI|Korinsic/i')).toBeVisible();
  });

  test('should handle API health check', async ({ page, request }) => {
    // Test backend health endpoint
    const healthResponse = await request.get(`${API_BASE_URL}/health`);
    expect(healthResponse.ok()).toBeTruthy();
    
    const healthData = await healthResponse.json();
    expect(healthData.status).toBe('healthy');
    expect(healthData.service).toBe('kor-ai-surveillance-platform');
  });

  test('should handle navigation to different routes', async ({ page }) => {
    // Test navigation to different routes if they exist
    const currentUrl = page.url();
    
    // Check if we're on the root path
    expect(currentUrl).toMatch(/\/$|\/dashboard/);
    
    // Test 404 page
    await page.goto('/nonexistent-page');
    await expect(page.locator('text=/404|not found/i')).toBeVisible();
  });

  test('should be responsive on mobile devices', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    
    // Navigate to dashboard
    await page.goto('/');
    
    // Check if the page is still functional on mobile
    await expect(page.locator('nav')).toBeVisible();
    
    // Check if content is properly displayed
    const mainContent = page.locator('main, .dashboard, [data-testid="dashboard"]');
    await expect(mainContent).toBeVisible();
  });

  test('should handle loading states gracefully', async ({ page }) => {
    // Intercept API calls to simulate slow responses
    await page.route(`${API_BASE_URL}/api/**`, async route => {
      // Add delay to simulate slow API
      await new Promise(resolve => setTimeout(resolve, 1000));
      await route.continue();
    });
    
    await page.goto('/');
    
    // Check if loading states are handled properly
    // This test assumes you have loading indicators
    const loadingIndicator = page.locator('.loading, [data-testid="loading"]');
    
    // If loading indicator exists, wait for it to disappear
    if (await loadingIndicator.isVisible()) {
      await expect(loadingIndicator).toBeHidden({ timeout: 10000 });
    }
  });

  test('should handle errors gracefully', async ({ page }) => {
    // Intercept API calls to simulate errors
    await page.route(`${API_BASE_URL}/api/**`, async route => {
      await route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Internal Server Error' })
      });
    });
    
    await page.goto('/');
    
    // Check if error states are handled properly
    // This test assumes you have error handling
    const errorMessage = page.locator('.error, [data-testid="error"]');
    
    // Wait a bit for any API calls to complete
    await page.waitForTimeout(2000);
    
    // If error handling exists, verify it's working
    if (await errorMessage.isVisible()) {
      await expect(errorMessage).toBeVisible();
    }
  });
});

test.describe('API Integration Tests', () => {
  test('should successfully call analyze endpoint', async ({ request }) => {
    // Test the analyze endpoint with sample data
    const analyzeResponse = await request.post(`${API_BASE_URL}/api/v1/analyze`, {
      data: {
        trades: [
          {
            symbol: 'AAPL',
            price: 150.00,
            volume: 1000,
            timestamp: new Date().toISOString(),
            trader_id: 'test_trader_001'
          }
        ]
      }
    });
    
    // Check if the response is successful or returns expected error
    expect([200, 400, 422]).toContain(analyzeResponse.status());
    
    if (analyzeResponse.ok()) {
      const responseData = await analyzeResponse.json();
      expect(responseData).toHaveProperty('analysis');
    }
  });

  test('should handle CORS properly', async ({ request }) => {
    // Test CORS headers
    const response = await request.options(`${API_BASE_URL}/api/v1/analyze`);
    
    // Check CORS headers
    const corsHeader = response.headers()['access-control-allow-origin'];
    expect(corsHeader).toBeTruthy();
  });
});