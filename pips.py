from graph import Graph


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


class Region:
    def __init__(self, type, target=None):
        self.type = type
        self.target = target
        self.cells = []

    def is_valid(self, puzzle):
        values = []
        for cell in self.cells:
            if not puzzle[cell].occupied:
                return True
            values.append(puzzle[cell].value)

        # not using early-exit math yet
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


class Pips:
    def __init__(self, shape, tiles, regions):
        self.shape = shape
        self.tiles = set(tiles)
        self.placed_tiles = set()
        self.regions = [Region('true')] + [Region(type, target) for (type, target) in regions]

        self.board = [[Cell(placeable=(c >= 0)) for c in row] for row in shape]
        for j, row in enumerate(self.shape):
            for i, n in enumerate(row):
                if n >= 0:
                    self.regions[n].cells.append((i, j))

    def __getitem__(self, item):
        i, j = item
        return self.board[j][i]

    def can_place(self, pos):
        (i, j), (x, y) = pos

        if j < 0 or j >= len(self.board):
            return False
        if i < 0 or i >= len(self.board[j]):
            return False
        if y < 0 or y >= len(self.board):
            return False
        if x < 0 or x >= len(self.board[y]):
            return False
        return self.board[j][i].placeable and self.board[y][x].placeable

    def place(self, tile, pos):
        (i, j), (x, y) = pos

        self[i, j].place(tile, 0)
        self[x, y].place(tile, 1)

        self.placed_tiles.add(tile)

    def remove(self, pos):
        (i, j), (x, y) = pos

        self.placed_tiles.remove(self[i, j].piece)

        self[i, j].remove()
        self[x, y].remove()

    def is_valid(self):
        for i, region in enumerate(self.regions, 0):
            if not region.is_valid(self):
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
        g.from_grid(self)
        color_ids = g.color_graph()
        colors = [9, 10, 12, 11]

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
