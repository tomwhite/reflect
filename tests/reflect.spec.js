const { test, expect } = require('@playwright/test');

// Use a fixed date so tests are independent of the current day's puzzle
const TEST_DATE = '2023-03-31';
const URL = `/?date=${TEST_DATE}`;

// Wait for Phaser to finish loading the puzzle
async function waitForGame(page) {
  await page.waitForFunction(() => {
    const scene = window.game?.scene?.getScene('PlayScene');
    // isActive() is true after create() but interactive objects sit in
    // _pendingInsertion until the InputPlugin flushes them on the next step.
    // Wait for _list to be populated so clicks land on the right objects.
    return window.game?.scene?.isActive('PlayScene') &&
      (scene?.input?._list?.length ?? 0) > 0;
  });
}

async function drag(page, fromX, fromY, toX, toY) {
  await page.mouse.move(fromX, fromY);
  await page.mouse.down();
  // Move in steps so Phaser's drag tracking fires
  await page.mouse.move(toX, toY, { steps: 10 });
  await page.mouse.up();
}

// --- Basic load tests ---

test('page loads without console errors', async ({ page }) => {
  const errors = [];
  page.on('console', msg => { if (msg.type() === 'error') errors.push(msg.text()); });
  page.on('pageerror', err => errors.push(err.message));
  await page.goto(URL);
  await waitForGame(page);
  expect(errors).toHaveLength(0);
});

test('canvas is rendered', async ({ page }) => {
  await page.goto(URL);
  await waitForGame(page);
  await expect(page.locator('canvas')).toBeVisible();
});

// --- Interaction tests ---

test('help button opens menu and close returns to game', async ({ page }) => {
  await page.goto(URL);
  await waitForGame(page);

  // Help button: blockIndexToCoord(5, 0) = (440, 120)
  await page.mouse.click(440, 120);
  await page.waitForFunction(() => window.game?.scene?.isActive('MenuScene'));

  // Close button in MenuScene is also at blockIndexToCoord(5, 0) = (440, 120)
  await page.mouse.click(440, 120);
  await page.waitForFunction(() => window.game?.scene?.isActive('PlayScene'));
});

// --- Solve test ---

// Puzzle 2023-03-31 solution (pieces sorted: ['/', '/', '\', '\', 'o']):
//   BLOCK_SIZE = 80, board_y_offset = 80
//   Board cell (i,j) centre: x=(i+1)*80+40, y=(j+2)*80+40
//   Tray piece index k centre: x=(k%4+1)*80+40, y=floor(k/4)*80+40+560
//
//   hiddenBlocks:
//     (i=1,j=0): '\'  tray[2]='\' at (280,600) → board (200,200)
//     (i=0,j=1): '/'  tray[0]='/' at (120,600) → board (120,280)
//     (i=2,j=1): '/'  tray[1]='/' at (200,600) → board (280,280)
//     (i=3,j=2): 'o'  tray[4]='o' at (120,680) → board (360,360)
//     (i=0,j=3): '\'  tray[3]='\' at (360,600) → board (120,440)

test('solving the puzzle records a solve in localStorage', async ({ page }) => {
  await page.goto(URL);
  await waitForGame(page);

  await drag(page, 280, 600, 200, 200); // '\' → (i=1,j=0)
  await drag(page, 120, 600, 120, 280); // '/' → (i=0,j=1)
  await drag(page, 200, 600, 280, 280); // '/' → (i=2,j=1)
  await drag(page, 120, 680, 360, 360); // 'o' → (i=3,j=2)
  await drag(page, 360, 600, 120, 440); // '\' → (i=0,j=3)

  const solved = await page.evaluate(() =>
    JSON.parse(localStorage.getItem('solvedHistory') ?? '[]')
  );
  expect(solved).toContain(TEST_DATE);
});
