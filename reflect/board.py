import numpy as np


class Board:
    """A board for Reflect.

        A board has an outer and an inner part.

        The outer part is one square wide and runs around the edges.
        It is where beams start and end, and doesn't contain blocks.
        The corners are not used.

        The inner part contains blocks.

        Here is an example board, containing two blocks (`/` and `\\`)
        on the inner board, and with some beams shown on the
        outer edges (indicated by A, B, and C).

        The board is of size n=4, since the inner board is a 4x4 square.

    ```
        ....A.
        ......
        ......
        .../\\A
        B....B
        ...CC.
    ```
    """

    def __init__(self, n, hidden_blocks, values, num_beams):
        self.n = n
        self.hidden_blocks = hidden_blocks
        self.values = values
        self.num_beams = num_beams

    @classmethod
    def create(cls, *, hidden_blocks=None, full_board=None):
        # construct with either hidden_blocks, where no beams have been set
        # or full board, which has beams set

        if hidden_blocks is None and full_board is None:
            raise ValueError("Must specify one of hidden_blocks or full_board")

        if hidden_blocks is not None and full_board is not None:
            raise ValueError("Cannot specify both of hidden_blocks and full_board")

        # parse into arrays
        if hidden_blocks is not None:
            hidden_blocks = cls._parse(hidden_blocks)
        if full_board is not None:
            full_board = cls._parse(full_board)

        if hidden_blocks is not None:
            n = len(hidden_blocks)
            hidden_blocks = hidden_blocks
            values = np.full((n + 2, n + 2), ".")
            num_beams = 0
            return cls(n, hidden_blocks, values, num_beams)
        else:
            # get hidden blocks from full board
            n = len(full_board) - 2
            hidden_blocks = full_board[1 : n + 1, 1 : n + 1].copy()
            values = full_board
            values[1 : n + 1, 1 : n + 1] = "."  # hide on board
            # find num_beams from values
            num_beams = np.unique(values).size - 1  # don't count "."
            return cls(n, hidden_blocks, values, num_beams)

    @classmethod
    def create_from_arrays(cls, hidden_blocks, beams):
        n = len(hidden_blocks)
        values = np.full((n + 2, n + 2), ".")
        num_beams = len(beams)
        for i in range(num_beams):
            label = chr(ord("A") + i)
            x = beams[i, 0] + 1
            y = beams[i, 1] + 1
            values[y, x] = label
            x = beams[i, 2] + 1
            y = beams[i, 3] + 1
            values[y, x] = label
        return cls(n, hidden_blocks, values, num_beams)

    @staticmethod
    def _parse(rep):
        # split into lines (ignore empty lines)
        lines = [line for line in rep.splitlines() if len(line) > 0]
        x = np.array(lines, dtype=bytes)
        return x.view("S1").reshape((x.size, -1)).astype(str)

    def _format(self):
        return "\n".join("".join(row) for row in self.values)

    def __str__(self):
        return self._format()

    def _format_blocks(self):
        return "\n".join("".join(row) for row in self.hidden_blocks)

    def copy(self):
        return Board(
            self.n, self.hidden_blocks.copy(), self.values.copy(), self.num_beams
        )

    def puzzle_string(self):
        """Return a string showing the puzzle"""
        return f"{self}\n\nBlocks: {''.join(self.pieces)}"

    def on_edge(self, x, y):
        """Return True if x, y is on an outer edge (not the corners)"""
        return (x in (0, self.n + 1)) != (y in (0, self.n + 1))

    def on_inner_board(self, x, y):
        """Return True if x, y is on the inner board (not outer edge or corners)"""
        return 0 < x <= self.n and 0 < y <= self.n

    @property
    def pieces(self):
        """The pieces on the board, in sorted order"""
        p = self.hidden_blocks[self.hidden_blocks != "."]
        p = p.flatten()
        p = np.sort(p)
        return p

    @property
    def pieces_ints(self):
        return block_str_to_int_array(self.pieces)

    @property
    def hidden_blocks_ints(self):
        return block_str_to_int_array(self.hidden_blocks)

    @property
    def beams(self):
        x = list(range(self.n + 2))
        y = list(range(self.n + 2))
        xv, yv = np.meshgrid(x, y, indexing="xy")
        # adjust indexing so top of inner board is at 0, 0
        xv = xv - 1
        yv = yv - 1

        b = np.empty((self.num_beams, 4), dtype=np.int8)
        for i in range(self.num_beams):
            cond = self.values == chr(ord("A") + i)
            xvc = xv[cond]
            yvc = yv[cond]
            xvc = np.broadcast_to(xvc, (2,))
            yvc = np.broadcast_to(yvc, (2,))
            b[i, 0] = xvc[0]
            b[i, 1] = yvc[0]
            b[i, 2] = xvc[1]
            b[i, 3] = yvc[1]
        return b

    def set_value(self, x, y, value):
        """Change block at position (x, y) to `value`"""
        if not self.on_inner_board(x, y):
            raise ValueError(f"Cannot set value at ({x}, {y})")
        self.values[y][x] = value

    def beam(self, x, y):
        """Send a beam from edge (x, y)"""
        if not self.on_edge(x, y):
            raise ValueError(f"Cannot beam from ({x}, {y})")
        n1 = self.n + 1
        label = chr(ord("A") + self.num_beams)
        self.values[y][x] = label

        path = []
        path.append((x, y))
        if x == 0:
            dx, dy = 1, 0
        elif x == n1:
            dx, dy = -1, 0
        elif y == 0:
            dx, dy = 0, 1
        elif y == n1:
            dx, dy = 0, -1
        x, y = x + dx, y + dy
        path.append((x, y))
        while True:
            if x in (0, n1) or y in (0, n1):
                break
            val = self.hidden_blocks[y - 1, x - 1]  # hidden_blocks is stored as y,x
            if val == "/":
                dx, dy = -dy, -dx
            elif val == "\\":
                dx, dy = dy, dx
            elif val == "o":
                dx, dy = -dx, -dy
            # otherwise if val == "." then don't change dx, dy
            x, y = x + dx, y + dy
            path.append((x, y))
        self.num_beams += 1
        self.values[y][x] = label
        return path

    def score(self):
        """Return a score for the values on the board, 1 if they match the hidden blocks, 0 otherwise."""
        eq = np.array_equal(
            self.values[1 : self.n + 1, 1 : self.n + 1], self.hidden_blocks
        )
        return 1 if eq else 0

    def rot90(self):
        """Rotate the board through 90 degrees"""

        # rotate values themselves
        def rot90_val(val):
            if val == "/":
                return "\\"
            elif val == "\\":
                return "/"
            else:
                return val

        n = self.n  # size doesn't change
        hidden_blocks = np.rot90(self.hidden_blocks)
        hidden_blocks = np.vectorize(rot90_val)(hidden_blocks)
        values = np.rot90(self.values)
        values = np.vectorize(rot90_val)(values)
        num_beams = self.num_beams  # number of beams doesn't change
        return Board(n, hidden_blocks, values, num_beams)

    def transpose(self):
        """Reflect the board in y=x"""

        # transpose values themselves
        def transpose_val(val):
            if val == "/":
                return "\\"
            elif val == "\\":
                return "/"
            else:
                return val

        n = self.n  # size doesn't change
        hidden_blocks = self.hidden_blocks.copy().T
        hidden_blocks = np.vectorize(transpose_val)(hidden_blocks)
        values = self.values.copy().T
        values = np.vectorize(transpose_val)(values)
        num_beams = self.num_beams  # number of beams doesn't change
        return Board(n, hidden_blocks, values, num_beams)

    def transforms(self):
        """Return all the transforms of this board."""
        board = self
        yield board
        board = board.rot90()
        yield board
        board = board.rot90()
        yield board
        board = board.rot90()
        yield board
        board = self.transpose()
        yield board
        board = board.rot90()
        yield board
        board = board.rot90()
        yield board
        board = board.rot90()
        yield board


def block_str_to_int_array(blocks):
    condlist = [blocks == x for x in [".", "/", "\\", "o"]]
    choicelist = [0, 1, 2, 3]
    return np.select(condlist, choicelist, 0).astype(np.int8)


def block_int_to_str_array(blocks):
    condlist = [blocks == x for x in [0, 1, 2, 3]]
    choicelist = [".", "/", "\\", "o"]
    return np.select(condlist, choicelist, 0)


def boards_are_unique(boards, include_transforms=True):
    """Test if all boards in a collection are unique.

    This function is useful for checking if a puzzle has been set before.
    Uniqueness is based only on the hidden blocks, not on the beams, which are ignored.
    It might be useful to include beams in the test for uniqueness, but that would
    require that they are canonicalized somehow.
    """
    if include_transforms:
        all_boards = []
        for board in boards:
            all_boards.extend(board.transforms())
    else:
        all_boards = boards

    arr = np.stack([board.hidden_blocks.flatten() for board in all_boards])
    arr_unique = np.unique(arr, axis=0)

    return arr.shape[0] == arr_unique.shape[0]
