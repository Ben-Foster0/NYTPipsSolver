from graph import Graph
import copy


class Cell:
    def __init__(self, placeable):
        self.placeable = placeable
        self.occupied = False
        self.value = None
        self.piece = None

    def place(self, piece, idx):
        self.occupied = True
        self.value = piece[idx]
        self.piece = piece

    def remove(self):
        self.occupied = False
        self.value = None
        self.piece = None

    def __str__(self):
        return f'Cell({self.occupied}, {self.value}, {self.piece})'

    def __hash__(self):
        return hash(self.piece)

    def __copy__(self):
        cpy = Cell(self.placeable)
        cpy.occupied = self.occupied
        cpy.value = self.value
        cpy.piece = self.piece
        return cpy

    def __eq__(self, other):
        return hash(self) == hash(other)


class Region:
    def __init__(self, type, target=None):
        self.type = type
        self.target = target
        self.cells = []

    def is_valid(self, puzzle, counts, strong_check):
        if strong_check:
            return self.is_valid_strong(puzzle, counts)
        else:
            return self.is_valid_weak(puzzle, counts)

    def is_valid_weak(self, puzzle, counts):
        """
        Simple heuristic, regions with blank cells are always considered to be valid
        """
        values = []
        blanks = 0
        for cell in self.cells:
            if not puzzle[cell].occupied:
                blanks += 1
                continue
            values.append(puzzle[cell].value)

        # exit early if contains blank tiles
        if blanks > 0:
            return True

        # using loose early-exit checks
        if self.type == 'equal_to':
            return sum(values) == self.target
        elif self.type == 'equal':
            return len(set(values)) == 1
        elif self.type == 'not_equal':
            return len(set(values)) == len(values)
        elif self.type == 'greater_than':
            return sum(values) > self.target
        elif self.type == 'less_than':
            return sum(values) < self.target
        else:
            return True

    def is_valid_strong(self, puzzle, counts):
        """
        Improved heuristic, considers "best-case" for blank cells
        """
        values = []
        blanks = 0
        for cell in self.cells:
            if not puzzle[cell].occupied:
                blanks += 1
                continue
            values.append(puzzle[cell].value)

        # exit early if completely empty
        if blanks == len(self.cells):
            return True

        if self.type == 'equal_to':
            return self.target-6*blanks <= sum(values) <= self.target
        elif self.type == 'equal':
            return len(set(values)) == 1 and counts[values[0]] >= blanks
        elif self.type == 'not_equal':
            return len(set(values)) == len(values)
        elif self.type == 'greater_than':
            return sum(values)+6*blanks > self.target
        elif self.type == 'less_than':
            return sum(values) < self.target
        else:
            return True


class Pips:
    def __init__(self, shape, tiles, regions, strong_check=True):
        self.shape = shape
        self.tiles = set(tiles)
        self.placed_tiles = set()
        self.regions = [Region('true')] + [Region(type, target) for (type, target) in regions]

        self.counts = [0 for _ in range(0, 7)]
        for tile in self.tiles:
            for p in tile:
                self.counts[p] += 1

        self.strong_check = strong_check

        self.board = [[Cell(placeable=(c >= 0)) for c in row] for row in shape]
        if regions:
            for j, row in enumerate(self.shape):
                for i, n in enumerate(row):
                    if n >= 0:
                        self.regions[n].cells.append((i, j))

    def __copy__(self):
        cpy = Pips(shape=self.shape, tiles=self.tiles, regions=[])
        cpy.board = copy.deepcopy(self.board)
        return cpy

    def __getitem__(self, item):
        i, j = item
        return self.board[j][i]

    def place(self, tile, pos):
        (i, j), (x, y) = pos

        self[i, j].place(tile, 0)
        self[x, y].place(tile, 1)

        self.placed_tiles.add(tile)
        for p in tile:
            self.counts[p] -= 1

    def remove(self, pos):
        (i, j), (x, y) = pos
        for p in self[i, j].piece:
            self.counts[p] += 1

        self.placed_tiles.remove(self[i, j].piece)

        self[i, j].remove()
        self[x, y].remove()

    def is_valid(self):
        for i, region in enumerate(self.regions, 0):
            if not region.is_valid(self, counts=self.counts, strong_check=self.strong_check):
                return False
        return True

    def is_solved(self):
        for row in self.board:
            for cell in row:
                if cell.placeable and not cell.occupied:
                    return False

        return self.is_valid()

    def __str__(self):
        g = Graph()
        g.from_grid([[c.piece if c.occupied else None for c in row] for row in self.board])
        color_ids = g.color_graph()
        colors = [9, 10, 12, 11, 14]

        string = ''
        for j, row in enumerate(self.board):
            for i, c in enumerate(row):
                if c.placeable:
                    if c.occupied:
                        string += f'\033[48;5;{colors[color_ids[hash(c)]]}m\033[38;5;0m {c.value}\033[0m'
                    else:
                        string += ' _'
                else:
                    string += '  '
            string += '\n'
        return string[:-1]

    def __eq__(self, other):
        for j, row in enumerate(self.board):
            for i, _ in enumerate(row):
                if self[i, j] != other[i, j]:
                    return False
        return True

    def __hash__(self):
        return hash(tuple([tuple([c.value for c in row]) for row in self.board]))
