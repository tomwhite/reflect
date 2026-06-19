import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { Board, formatDate } from './reflect.js';

const puzzleText = readFileSync('./puzzles/puzzle-2023-03-31.txt', 'utf8');

// formatDate

test('formatDate formats a basic date as YYYY-MM-DD', () => {
  assert.equal(formatDate(new Date(2025, 0, 13)), '2025-01-13');
});

test('formatDate zero-pads single-digit day', () => {
  assert.equal(formatDate(new Date(2025, 0, 5)), '2025-01-05');
});

test('formatDate zero-pads single-digit month', () => {
  assert.equal(formatDate(new Date(2025, 8, 1)), '2025-09-01');
});

test('formatDate handles year-end date', () => {
  assert.equal(formatDate(new Date(2024, 11, 31)), '2024-12-31');
});

test('formatDate handles leap day', () => {
  assert.equal(formatDate(new Date(2024, 1, 29)), '2024-02-29');
});

// Board construction

test('board.n is 4 for a 4x4 puzzle', () => {
  const board = new Board(puzzleText);
  assert.equal(board.n, 4);
});

test('board.hiddenBlocks is an n×n array', () => {
  const board = new Board(puzzleText);
  assert.equal(board.hiddenBlocks.length, 4);
  assert.equal(board.hiddenBlocks[0].length, 4);
});

// Board.pieces

test('board.pieces returns sorted non-empty interior pieces', () => {
  const board = new Board(puzzleText);
  assert.deepEqual(board.pieces, ['/', '/', '\\', '\\', 'o']);
});

// Board.beamNames

test('board.beamNames returns sorted unique beam labels from edges', () => {
  const board = new Board(puzzleText);
  assert.deepEqual(board.beamNames, ['A', 'B', 'C', 'D', 'G', 'J']);
});

// Board.edgeLocations()

test('edgeLocations yields 4*n locations for an n×n board', () => {
  const board = new Board(puzzleText);
  assert.equal([...board.edgeLocations()].length, 4 * board.n);
});

// Board.getPath() — mirror physics
// Uses a minimal n=2 board (4×4 fullBoard) with a single piece in the interior.

function makeBoard(interiorChar) {
  // n=2: fullBoard rows 0..3, cols 0..3
  // interior is rows 1..2, cols 1..2
  // Place interiorChar at (1,1) — row 1, col 1
  return new Board(
    `....\n.${interiorChar}..\n....\n....\n`
  );
}

test('getPath: beam travels straight through empty board', () => {
  const board = makeBoard('.');
  const path = board.getPath(1, 0); // enter from top at col 1
  assert.deepEqual(path, [[1, 0], [1, 1], [1, 2], [1, 3]]);
});

test('getPath: / mirror deflects beam left', () => {
  const board = makeBoard('/');
  const path = board.getPath(1, 0);
  assert.deepEqual(path, [[1, 0], [1, 1], [0, 1]]);
});

test('getPath: \\ mirror deflects beam right', () => {
  const board = makeBoard('\\');
  const path = board.getPath(1, 0);
  assert.deepEqual(path, [[1, 0], [1, 1], [2, 1], [3, 1]]);
});

test('getPath: o mirror ball reflects beam back', () => {
  const board = makeBoard('o');
  const path = board.getPath(1, 0);
  assert.deepEqual(path, [[1, 0], [1, 1], [1, 0]]);
});

// Board.beamPaths — integration

test('beamPaths has one path per beam name', () => {
  const board = new Board(puzzleText);
  assert.equal(board.beamPaths.length, board.beamNames.length);
});

test('each beam path starts and ends at an edge location', () => {
  const board = new Board(puzzleText);
  const n1 = board.n + 1;
  for (const path of board.beamPaths) {
    const [sx, sy] = path[0];
    const [ex, ey] = path[path.length - 1];
    assert.ok(
      sx === 0 || sx === n1 || sy === 0 || sy === n1,
      `start (${sx},${sy}) not on edge`
    );
    assert.ok(
      ex === 0 || ex === n1 || ey === 0 || ey === n1,
      `end (${ex},${ey}) not on edge`
    );
  }
});
