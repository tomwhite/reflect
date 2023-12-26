// Scale sprites so we can have a high resolution for other graphics (text, lines)
const SCALE = 2;

const SCREEN_WIDTH = 240 * SCALE;
const SCREEN_HEIGHT = 400 * SCALE;

const BLOCK_SIZE = 40 * SCALE;
const CELL_SIZE = 38 * SCALE;

const BEAM_WIDTH = 5 * SCALE;
const GRID_WIDTH = 1 * SCALE;

const SPRITE_NAMES = {
  "/": "oblique_mirror",
  "\\": "reverse_oblique_mirror",
  o: "mirror_ball",
};

// https://sashamaps.net/docs/resources/20-colors/
const COLOURS = [
  "#e6194B",
  "#3cb44b",
  "#ffe119",
  "#4363d8",
  "#f58231",
  "#42d4f4",
  "#f032e6",
  "#fabed4",
  "#469990",
  "#dcbeff",
  "#9A6324",
  "#fffac8",
  "#800000",
  "#aaffc3",
  "#000075",
  "#a9a9a9",
].map((hex) => Phaser.Display.Color.HexStringToColor(hex).color);

const TEXT_STYLE_10_PT = {
  fontFamily: "Arial",
  fontSize: 10 * SCALE,
  color: "black",
  padding: {
    bottom: 2,
  },
};

const BUTTON_STYLE = {
  fontFamily: "Arial",
  fontSize: 16 * SCALE,
  color: "black",
  backgroundColor: "#f0f8ff",
  textDecoration: "none",
  padding: {
    y: 12 * SCALE,
  },
  align: "center",
  fixedWidth: 170 * SCALE,
};

const TEXT_STYLE_18_PT = {
  fontFamily: "Arial",
  fontSize: 18 * SCALE,
  color: "black",
  padding: {
    bottom: 2,
  },
};

const TEXT_STYLE_24_PT = {
  fontFamily: "Arial",
  fontSize: 24 * SCALE,
  color: "black",
  padding: {
    bottom: 2,
  },
};

function blockIndexToCoord(i, j, y_offset = BLOCK_SIZE) {
  const x = i * BLOCK_SIZE + BLOCK_SIZE / 2;
  const y = j * BLOCK_SIZE + BLOCK_SIZE / 2;
  return [x, y + y_offset];
}

class Board {
  constructor(text) {
    this.fullBoard = text
      .split("\n")
      .filter((line) => line.trim().length > 0 && !line.startsWith("#"))
      .map((line) => line.split(""));
    this.n = this.fullBoard.length - 2;
    this.hiddenBlocks = this.fullBoard
      .slice(1, this.n + 1)
      .map((arr) => arr.slice(1, this.n + 1));
  }

  get pieces() {
    return this.hiddenBlocks
      .flat()
      .filter((piece) => piece != ".")
      .sort();
  }

  // Return all the edge locations in a predictable order.
  *edgeLocations() {
    for (let x = 1; x <= this.n; x++) {
      yield [x, 0];
    }
    for (let y = 1; y <= this.n; y++) {
      yield [0, y];
    }
    for (let x = 1; x <= this.n; x++) {
      yield [x, this.n + 1];
    }
    for (let y = 1; y <= this.n; y++) {
      yield [this.n + 1, y];
    }
  }

  // Return all the beam names ("A", "B", etc) in sorted order
  get beamNames() {
    return [...this.edgeLocations()]
      .map((loc) => this.fullBoard[loc[1]][loc[0]])
      .filter((piece) => piece != ".")
      .sort()
      .filter((value, index, array) => array.indexOf(value) === index); // unique
  }

  getPath(x, y) {
    const n1 = this.n + 1;
    const path = [];
    path.push([x, y]);
    let dx = 0;
    let dy = 0;
    if (x == 0) {
      dx = 1;
      dy = 0;
    } else if (x == n1) {
      dx = -1;
      dy = 0;
    } else if (y == 0) {
      dx = 0;
      dy = 1;
    } else if (y == n1) {
      dx = 0;
      dy = -1;
    }
    x += dx;
    y += dy;
    path.push([x, y]);
    while (true) {
      if ([0, n1].includes(x) || [0, n1].includes(y)) {
        // TODO: check end point has same path label
        break;
      }
      const val = this.fullBoard[y][x];
      if (val == "/") {
        [dx, dy] = [-dy, -dx];
      } else if (val == "\\") {
        [dx, dy] = [dy, dx];
      } else if (val == "o") {
        [dx, dy] = [-dx, -dy];
      }
      x += dx;
      y += dy;
      path.push([x, y]);
    }
    return path;
  }
  get beamPaths() {
    const paths = [];
    for (let beamName of this.beamNames) {
      let startLoc = null;
      for (let loc of this.edgeLocations()) {
        if (this.fullBoard[loc[1]][loc[0]] == beamName) {
          startLoc = loc;
          const path = this.getPath(loc[0], loc[1]);
          paths.push(path);
          break;
        }
      }
    }
    return paths;
  }
}

// Format a date in ISO format (YYYY-MM-DD) according to local time
// From https://stackoverflow.com/a/50130338
function formatDate(date) {
  return new Date(date.getTime() - date.getTimezoneOffset() * 60000)
    .toISOString()
    .split("T")[0];
}

// From https://stackoverflow.com/a/2117523
// prettier-ignore
function uuidv4() {
    return ([1e7]+-1e3+-4e3+-8e3+-1e11).replace(/[018]/g, c =>
        (c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> c / 4).toString(16)
    );
    }

function getDeviceId() {
  let deviceId = localStorage.getItem("deviceId");
  if (deviceId == null) {
    deviceId = uuidv4();
    localStorage.setItem("deviceId", deviceId);
  }
  return deviceId;
}

function isLocalhost() {
  return location.hostname === "localhost" || location.hostname === "127.0.0.1";
}

// Return "today" in YYYY-MM-DD
// Allow overriding with url param ?date=YYYY-MM-DD
function getEffectiveDate() {
  const urlParams = new URLSearchParams(window.location.search);
  const dateParam = urlParams.get("date");
  return dateParam ? dateParam : formatDate(new Date());
}

const firebaseConfig = {
  apiKey: "AIzaSyBgI928NCooaWIQNtNU1beD25Nzg7B6W50",
  authDomain: "reflect-826a3.firebaseapp.com",
  projectId: "reflect-826a3",
  storageBucket: "reflect-826a3.appspot.com",
  messagingSenderId: "694197574513",
  appId: "1:694197574513:web:908d805861beec1db1b4d0",
};

firebase.initializeApp(firebaseConfig);

const db = firebase.firestore();

const today = getEffectiveDate();
const deviceId = getDeviceId();

function saveEvent(name) {
  const eventHistoryJson = localStorage.getItem("eventHistory");
  const eventHistory =
    eventHistoryJson == null ? [] : JSON.parse(eventHistoryJson);
  const event = {
    puzzle: today,
    name: name,
    timestamp: Date.now(),
  };
  eventHistory.push(event);
  localStorage.setItem("eventHistory", JSON.stringify(eventHistory));

  event.device = deviceId;
  if (isLocalhost()) {
    console.log("Ignoring event on localhost");
  } else {
    db.collection("puzzles")
      .doc(today)
      .collection("events")
      .add(event)
      .then((docRef) => {
        console.log("Event written to firestore with ID: ", docRef.id);
      })
      .catch((error) => {
        console.error("Error adding event to firestore: ", error);
      });
  }
}

function savePlayed() {
  const solvedHistoryJson = localStorage.getItem("solvedHistory");
  const solvedHistory =
    solvedHistoryJson == null
      ? []
      : Array.from(new Set(JSON.parse(solvedHistoryJson))).sort();
  const playedHistoryJson = localStorage.getItem("playedHistory");
  const playedHistory =
    playedHistoryJson == null
      ? solvedHistory // init from solved history
      : Array.from(new Set(JSON.parse(playedHistoryJson))).sort();
  if (!playedHistory.includes(today)) {
    playedHistory.push(today);
    localStorage.setItem("playedHistory", JSON.stringify(playedHistory));
  }
}

function saveSolved() {
  const solvedHistoryJson = localStorage.getItem("solvedHistory");
  const solvedHistory =
    solvedHistoryJson == null
      ? []
      : Array.from(new Set(JSON.parse(solvedHistoryJson))).sort();
  if (!solvedHistory.includes(today)) {
    solvedHistory.push(today);
    localStorage.setItem("solvedHistory", JSON.stringify(solvedHistory));
  }
}

function getStats() {
  const playedHistoryJson = localStorage.getItem("playedHistory");
  const playedHistory =
    playedHistoryJson == null
      ? []
      : Array.from(new Set(JSON.parse(playedHistoryJson))).sort();
  const played = Array.from(new Set(playedHistory)).length;
  console.log(`Played: ${played}`);

  const solvedHistoryJson = localStorage.getItem("solvedHistory");
  const solvedHistory =
    solvedHistoryJson == null
      ? []
      : Array.from(new Set(JSON.parse(solvedHistoryJson))).sort();
  const solved = Array.from(new Set(solvedHistory)).length;
  console.log(`Solved: ${solved}`);

  let currentStreak = 0;
  Array.from(new Set(solvedHistory))
    .sort()
    .reverse()
    .map((d) => new Date(d))
    .forEach((d, i) => {
      if (new Date(today) - d === i * 60 * 60 * 24 * 1000) {
        currentStreak++;
      }
    });
  console.log(`Streak: ${currentStreak}`);
  return { played: played, solved: solved, currentStreak: currentStreak };
}

function drawBeams(n, beamGraphics, beamPaths, board_y_offset) {
  for (var bi = 0; bi < beamPaths.length; bi++) {
    const beamPath = beamPaths[bi];
    const start = beamPath[0];
    const end = beamPath[beamPath.length - 1];
    for (let [i, j] of [start, end]) {
      beamGraphics.lineStyle(BEAM_WIDTH, COLOURS[bi]);
      const [x, y] = blockIndexToCoord(i, j, board_y_offset);
      if (i == 0) {
        beamGraphics.lineBetween(BEAM_WIDTH, y, BLOCK_SIZE, y);
      } else if (i == n + 1) {
        beamGraphics.lineBetween(
          BLOCK_SIZE * (n + 1),
          y,
          BLOCK_SIZE * (n + 2) - BEAM_WIDTH,
          y
        );
      } else if (j == 0) {
        beamGraphics.lineBetween(
          x,
          BEAM_WIDTH + board_y_offset,
          x,
          BLOCK_SIZE + board_y_offset
        );
      } else if (j == n + 1) {
        beamGraphics.lineBetween(
          x,
          BLOCK_SIZE * (n + 1) + board_y_offset,
          x,
          BLOCK_SIZE * (n + 2) - BEAM_WIDTH + board_y_offset
        );
      }
    }
  }
}

function drawBeamPaths(n, beamPathGraphics, beamPaths, board_y_offset) {
  for (var bi = 0; bi < beamPaths.length; bi++) {
    const beamPath = beamPaths[bi];
    for (var bj = 0; bj < beamPath.length - 1; bj++) {
      const start = beamPath[bj];
      const end = beamPath[bj + 1];
      const [x0, y0] = blockIndexToCoord(start[0], start[1], board_y_offset);
      const [x1, y1] = blockIndexToCoord(end[0], end[1], board_y_offset);

      beamPathGraphics.lineStyle(BEAM_WIDTH, COLOURS[bi]);
      beamPathGraphics.lineBetween(x0, y0, x1, y1);
    }
  }
}

function drawBoardLines(n, boardGraphics, board_y_offset) {
  boardGraphics.lineStyle(GRID_WIDTH, "black");
  for (var x = BLOCK_SIZE; x < BLOCK_SIZE * (n + 2); x += BLOCK_SIZE) {
    boardGraphics.lineBetween(
      x,
      BLOCK_SIZE + board_y_offset,
      x,
      BLOCK_SIZE * (n + 1) + board_y_offset
    );
  }
  for (var y = BLOCK_SIZE; y < BLOCK_SIZE * (n + 2); y += BLOCK_SIZE) {
    boardGraphics.lineBetween(
      BLOCK_SIZE,
      y + board_y_offset,
      BLOCK_SIZE * (n + 1),
      y + board_y_offset
    );
  }
}

class PlayScene extends Phaser.Scene {
  constructor() {
    super({ key: "PlayScene" });
  }

  preload() {
    this.load.image("logo", "sprites/reflect.png");
    for (const name of Object.values(SPRITE_NAMES)) {
      this.load.image(name, `sprites/${name}_tr.png`);
    }
    this.load.image("help", "sprites/help.png");
    this.load.image("close", "sprites/close-circle-line.png");
    this.load.text("puzzle", `puzzles/puzzle-${today}.txt`);
    savePlayed(); // assume played if loaded today's puzzle
    plausible("preload");
    saveEvent("preload");
  }

  create() {
    const puzzle = this.cache.text.get("puzzle");
    const board = new Board(puzzle);
    const n = board.n;
    const hiddenBlocks = board.hiddenBlocks;
    const beamPaths = board.beamPaths;
    const pieces = board.pieces;
    const board_y_offset = BLOCK_SIZE;

    let gameOver = false;
    let seenFirstMove = false;

    // Logo
    const logo = this.add.image(SCREEN_WIDTH / 2, BLOCK_SIZE / 2, "logo");
    logo.setScale(SCALE);

    // Beams
    const beamGraphics = this.add.graphics();
    drawBeams(n, beamGraphics, beamPaths, board_y_offset);

    // Board lines
    const boardGraphics = this.add.graphics();
    drawBoardLines(n, boardGraphics, board_y_offset);

    // Beam paths
    const beamPathGraphics = this.add.graphics();
    beamPathGraphics.visible = false;
    drawBeamPaths(n, beamPathGraphics, beamPaths, board_y_offset);

    // Cells (board)
    const cellGraphics = this.add.graphics();
    cellGraphics.fillStyle(0xf0f8ff);

    for (var i = 0; i < n; i++) {
      for (var j = 0; j < n; j++) {
        const [x, y] = blockIndexToCoord(i + 1, j + 1);
        const zone = this.add
          .zone(x, y, CELL_SIZE, CELL_SIZE)
          .setRectangleDropZone(CELL_SIZE, CELL_SIZE)
          .setData("loc", [i, j]);

        cellGraphics.fillRect(
          zone.x - zone.input.hitArea.width / 2,
          zone.y - zone.input.hitArea.height / 2,
          zone.input.hitArea.width,
          zone.input.hitArea.height
        );
      }
    }

    // Cells (below board)
    const zones = [];
    for (var i = 0; i < pieces.length; i++) {
      let [x, y] = blockIndexToCoord(
        (i % 4) + 1,
        Math.floor(i / 4),
        BLOCK_SIZE * (n + 2) + board_y_offset
      );

      const zone = this.add
        .zone(x, y, CELL_SIZE, CELL_SIZE)
        .setRectangleDropZone(CELL_SIZE, CELL_SIZE);
      zones.push(zone);

      cellGraphics.fillRect(
        zone.x - zone.input.hitArea.width / 2,
        zone.y - zone.input.hitArea.height / 2,
        zone.input.hitArea.width,
        zone.input.hitArea.height
      );
    }

    // Blocks (these are last so they are on top of everything else)
    this.blockImages = [];
    for (var i = 0; i < pieces.length; i++) {
      let [x, y] = blockIndexToCoord(
        (i % 4) + 1,
        Math.floor(i / 4),
        BLOCK_SIZE * (n + 2) + board_y_offset
      );

      const image = this.add
        .image(x, y, SPRITE_NAMES[pieces[i]])
        .setInteractive();
      image.setScale(SCALE);
      image.setData("piece", pieces[i]);
      this.input.setDraggable(image);
      this.blockImages.push(image);

      // Cell zone has a reference to block image and vice versa.
      // This invariant is maintained during drag and drop, and this
      // state is used to construct board values.
      const zone = zones[i];
      zone.setData("image", image);
      image.setData("zone", zone);
    }

    let [x, y] = blockIndexToCoord(5, 0);
    const help = this.add.image(x, y, "help").setInteractive();
    help.setScale(SCALE);
    help.on("pointerup", (e) => {
      this.scene.setVisible(false, "PlayScene");
      this.scene.launch("MenuScene");
      this.scene.pause();
    });

    this.input.on("drag", function (pointer, gameObject, dragX, dragY) {
      // update image coordinates as it is dragged
      gameObject.x = dragX;
      gameObject.y = dragY;
    });

    this.input.on(
      "drop",
      function (pointer, gameObject, dropZone) {
        if (dropZone.data && dropZone.data.get("image") !== undefined) {
          // drop zone already occupied - reset position
          gameObject.x = gameObject.input.dragStartX;
          gameObject.y = gameObject.input.dragStartY;
          return;
        }

        gameObject.x = dropZone.x;
        gameObject.y = dropZone.y;
        dropZone.setData("image", gameObject);

        // remove image from previous drop zone
        gameObject.data.get("zone").data.remove("image");
        // set image to new drop zone
        gameObject.setData("zone", dropZone);

        if (dropZone.data.get("loc") !== undefined) {
          // drop zone is on board

          // test if game over
          const boardValues = Array.from(Array(n), () => Array(n).fill("."));
          for (let block of this.blockImages) {
            const loc = block.data.get("zone").data.get("loc");
            if (loc === undefined) {
              continue;
            }
            const [i, j] = loc;
            boardValues[j][i] = block.data.get("piece");
          }
          if (JSON.stringify(boardValues) == JSON.stringify(hiddenBlocks)) {
            cellGraphics.visible = false;
            beamPathGraphics.visible = true;
            gameOver = true;
            // disable dragging
            let images = this.children.list.filter(
              (x) => x instanceof Phaser.GameObjects.Image
            );
            images.forEach((image) =>
              image.input ? this.input.setDraggable(image, false) : null
            );
            // save to local storage
            saveSolved();
            const stats = getStats();
            this.add
              .text(
                BLOCK_SIZE * 1.5,
                BLOCK_SIZE * (n + 2) + BLOCK_SIZE / 2 + board_y_offset,
                stats.played,
                TEXT_STYLE_24_PT
              )
              .setOrigin(0.5);
            this.add
              .text(
                BLOCK_SIZE * 1.5,
                BLOCK_SIZE * (n + 2) + BLOCK_SIZE + board_y_offset,
                "Played",
                TEXT_STYLE_10_PT
              )
              .setOrigin(0.5, 0);
            this.add
              .text(
                BLOCK_SIZE * 3,
                BLOCK_SIZE * (n + 2) + BLOCK_SIZE / 2 + board_y_offset,
                stats.solved,
                TEXT_STYLE_24_PT
              )
              .setOrigin(0.5);
            this.add
              .text(
                BLOCK_SIZE * 3,
                BLOCK_SIZE * (n + 2) + BLOCK_SIZE + board_y_offset,
                "Solved",
                TEXT_STYLE_10_PT
              )
              .setOrigin(0.5, 0);
            this.add
              .text(
                BLOCK_SIZE * 4.5,
                BLOCK_SIZE * (n + 2) + BLOCK_SIZE / 2 + board_y_offset,
                stats.currentStreak,
                TEXT_STYLE_24_PT
              )
              .setOrigin(0.5);
            this.add
              .text(
                BLOCK_SIZE * 4.5,
                BLOCK_SIZE * (n + 2) + BLOCK_SIZE + board_y_offset,
                "Current",
                TEXT_STYLE_10_PT
              )
              .setOrigin(0.5, 0);
            this.add
              .text(
                BLOCK_SIZE * 4.5,
                BLOCK_SIZE * (n + 2) + BLOCK_SIZE * 1.3 + board_y_offset,
                "Streak",
                TEXT_STYLE_10_PT
              )
              .setOrigin(0.5, 0);
            plausible("solved");
            saveEvent("solved");
          }
        }
      },
      this
    );

    this.input.on("dragend", function (pointer, gameObject, dropped) {
      if (!dropped) {
        // not dropped on drop zone - reset position
        gameObject.x = gameObject.input.dragStartX;
        gameObject.y = gameObject.input.dragStartY;
      }
      if (!seenFirstMove) {
        saveEvent("firstMove");
        seenFirstMove = true;
      }
    });
  }
}

class MenuScene extends Phaser.Scene {
  constructor() {
    super({ key: "MenuScene" });
  }

  preload() {}

  create() {
    // Logo
    const logo = this.add.image(SCREEN_WIDTH / 2, BLOCK_SIZE / 2, "logo");
    logo.setScale(SCALE);

    let [x, y] = blockIndexToCoord(5, 0);
    const close = this.add.image(x, y, "close").setInteractive();
    close.setScale(SCALE);
    close.on("pointerup", (e) => {
      this.scene.resume("PlayScene");
      this.scene.stop();
      this.scene.setVisible(true, "PlayScene");
    });

    let y_offset = BLOCK_SIZE * 2;
    this.add
      .text(SCREEN_WIDTH / 2, y_offset, "How to play", BUTTON_STYLE)
      .setOrigin(0.5)
      .setInteractive()
      .on("pointerup", (e) => {
        this.scene.launch("HelpScene");
        this.scene.stop();
      });
    y_offset += BLOCK_SIZE * 1.5;
    this.add
      .text(SCREEN_WIDTH / 2, y_offset, "Yesterday's solution", BUTTON_STYLE)
      .setOrigin(0.5)
      .setInteractive()
      .on("pointerup", (e) => {
        this.scene.launch("SolutionScene");
        this.scene.stop();
      });
  }
}

class HelpScene extends Phaser.Scene {
  constructor() {
    super({ key: "HelpScene" });
  }

  preload() {
    this.load.text("helpPuzzle", "puzzles/puzzle-help.txt");
  }

  create() {
    const puzzle = this.cache.text.get("helpPuzzle");
    const board = new Board(puzzle);
    const n = board.n;
    const hiddenBlocks = board.hiddenBlocks;
    const beamPaths = board.beamPaths;
    const pieces = board.pieces;
    const board_y_offset = BLOCK_SIZE * 2;

    // Logo
    const logo = this.add.image(SCREEN_WIDTH / 2, BLOCK_SIZE / 2, "logo");
    logo.setScale(SCALE);

    // Beams
    const beamGraphics = this.add.graphics();
    drawBeams(n, beamGraphics, beamPaths, board_y_offset);

    // Board lines
    const boardGraphics = this.add.graphics();
    drawBoardLines(n, boardGraphics, board_y_offset);

    // Beam paths
    const beamPathGraphics = this.add.graphics();
    drawBeamPaths(n, beamPathGraphics, beamPaths, board_y_offset);

    // Blocks
    for (let i = 0; i < n; i++) {
      for (let j = 0; j < n; j++) {
        const ch = board.hiddenBlocks[i][j];
        if (ch != ".") {
          const [x0, y0] = blockIndexToCoord(j + 1, i + 1, board_y_offset);
          this.add.image(x0, y0, SPRITE_NAMES[ch]).setScale(SCALE);
        }
      }
    }

    let [x, y] = blockIndexToCoord(5, 0);
    const close = this.add.image(x, y, "close").setInteractive();
    close.setScale(SCALE);
    close.on("pointerup", (e) => {
      this.scene.resume("PlayScene");
      this.scene.stop();
      this.scene.setVisible(true, "PlayScene");
    });

    // Help text
    this.add.text(
      0,
      BLOCK_SIZE * 1.25,
      "Drag all of the mirrors onto the grid, so each",
      TEXT_STYLE_10_PT
    );
    this.add.text(
      0,
      BLOCK_SIZE * 1.625,
      "beam of light connects to the same colour",
      TEXT_STYLE_10_PT
    );
    this.add.text(0, BLOCK_SIZE * 2.375, "For example:", TEXT_STYLE_10_PT);
    let y_offset = BLOCK_SIZE * (n + 2) + board_y_offset;
    this.add.text(
      0,
      y_offset,
      "A new puzzle is released every day",
      TEXT_STYLE_10_PT
    );
    y_offset += BLOCK_SIZE * 0.375;
    y_offset += BLOCK_SIZE * 0.375;
    this.add.text(
      0,
      y_offset,
      "© 2023 Tom White (tom.e.white@gmail.com)",
      TEXT_STYLE_10_PT
    );
  }
}

class SolutionScene extends Phaser.Scene {
  constructor() {
    super({ key: "SolutionScene" });
  }

  preload() {
    const yesterdayDate = new Date();
    yesterdayDate.setDate(yesterdayDate.getDate() - 1);
    const yesterday = formatDate(yesterdayDate);
    this.load.text("yesterdayPuzzle", `puzzles/puzzle-${yesterday}.txt`);
  }

  create() {
    const puzzle = this.cache.text.get("yesterdayPuzzle");
    const board = new Board(puzzle);
    const n = board.n;
    const hiddenBlocks = board.hiddenBlocks;
    const beamPaths = board.beamPaths;
    const pieces = board.pieces;
    const board_y_offset = BLOCK_SIZE * 2;

    // Logo
    const logo = this.add.image(SCREEN_WIDTH / 2, BLOCK_SIZE / 2, "logo");
    logo.setScale(SCALE);

    // Beams
    const beamGraphics = this.add.graphics();
    drawBeams(n, beamGraphics, beamPaths, board_y_offset);

    // Board lines
    const boardGraphics = this.add.graphics();
    drawBoardLines(n, boardGraphics, board_y_offset);

    // Beam paths
    const beamPathGraphics = this.add.graphics();
    drawBeamPaths(n, beamPathGraphics, beamPaths, board_y_offset);

    // Blocks
    for (let i = 0; i < n; i++) {
      for (let j = 0; j < n; j++) {
        const ch = board.hiddenBlocks[i][j];
        if (ch != ".") {
          const [x0, y0] = blockIndexToCoord(j + 1, i + 1, board_y_offset);
          this.add.image(x0, y0, SPRITE_NAMES[ch]).setScale(SCALE);
        }
      }
    }

    this.add
      .text(
        SCREEN_WIDTH / 2,
        BLOCK_SIZE * 1.5,
        "Yesterday's solution",
        TEXT_STYLE_18_PT
      )
      .setOrigin(0.5);

    let [x, y] = blockIndexToCoord(5, 0);
    const close = this.add.image(x, y, "close").setInteractive();
    close.setScale(SCALE);
    close.on("pointerup", (e) => {
      this.scene.resume("PlayScene");
      this.scene.stop();
      this.scene.setVisible(true, "PlayScene");
    });
  }
}

const config = {
  type: Phaser.AUTO,
  width: SCREEN_WIDTH,
  height: SCREEN_HEIGHT,
  scale: {
    mode: Phaser.Scale.FIT,
    autoCenter: Phaser.Scale.CENTER_BOTH,
  },
  backgroundColor: "#FFFFFF",
  scene: [PlayScene, MenuScene, HelpScene, SolutionScene],
};

const game = new Phaser.Game(config);
