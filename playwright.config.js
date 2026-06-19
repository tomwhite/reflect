const { defineConfig } = require('@playwright/test');

module.exports = defineConfig({
  testDir: './tests',
  use: {
    // Match game canvas dimensions exactly so game coords === browser coords
    viewport: { width: 480, height: 800 },
    baseURL: 'http://localhost:8080',
    // launchOptions: {
    //   slowMo: 1000,  // ms delay after each action
    // },
  },
  webServer: {
    command: 'python3 -m http.server 8080',
    url: 'http://localhost:8080',
    reuseExistingServer: !process.env.CI,
  },
});
