from pips import Pips
import json
import time


class Tree:
    def __init__(self, item, children=None, is_leaf=False):
        self.item = item
        if children is None:
            self.children = []
        else:
            self.children = children
        self.is_leaf = is_leaf

    def __iter__(self):
        yield self.item
        for child in self.children:
            yield from child


class Grid:
    def __init__(self, shape):
        self.elements = [[0 if c >= 0 else -1 for c in row]for row in shape]

    def __getitem__(self, item):
        if isinstance(item, tuple):
            i, j = item
            return self.elements[j][i]
        elif isinstance(item, int):
            return self.elements[item]

    def __setitem__(self, key, value):
        i, j = key
        self.elements[j][i] = value

    def __len__(self):
        return len(self.elements)

    def __iter__(self):
        return iter(self.elements)


def tile_placements(grid, n=1):
    x, y = 0, 0
    w, h = len(grid[0]), len(grid)
    while grid[x, y] != 0:
        x += 1
        if x >= w:
            x = 0
            y += 1
            if y >= h:
                return Tree(None, is_leaf=True)

    placements = Tree(None)
    # right facing
    if x < w-1 and grid[x+1, y] == 0:
        grid[x, y] = n
        grid[x+1, y] = n
        solved = tile_placements(grid, n=n+1)
        grid[x, y] = 0
        grid[x+1, y] = 0
        if solved.children or solved.is_leaf:
            solved.item = [(x, y), (x+1, y)]
            placements.children.append(solved)

    # down facing
    if y < h-1 and grid[y+1][x] == 0:
        grid[x, y] = n
        grid[x, y+1] = n
        solved = tile_placements(grid, n=n+1)
        grid[x, y] = 0
        grid[x, y+1] = 0
        if solved.children or solved.is_leaf:
            solved.item = [(x, y), (x, y+1)]
            placements.children.append(solved)

    return placements


def solve_puzzle(puzzle, placement=None):
    if len(puzzle.tiles - puzzle.placed_tiles) == 0 and puzzle.is_solved():
        return puzzle

    if placement is None:
        placement = tile_placements(Grid(puzzle.shape))

    pos = placement.item
    for tile in puzzle.tiles - puzzle.placed_tiles:
        for dir in [(0, 1), (1, 0)]:
            if pos is not None:
                puzzle.place(tile, (pos[dir[0]], pos[dir[1]]))
            if puzzle.is_solved():
                return puzzle

            if puzzle.is_valid():
                for child in placement.children:
                    if sol := solve_puzzle(puzzle, placement=child):
                        return sol

            if pos is not None:
                puzzle.remove((pos[dir[0]], pos[dir[1]]))

    return False


def desmos_region_helper(width, height, code):
    regions = {}
    for j in range(height):
        for i in range(width):
            idx = width*(height-j-1) + i
            r = code[idx]
            if r <= 0:
                continue
            if r not in regions:
                regions[r] = []
            regions[r].append((i, j))
    return [regions[k] for k in sorted(regions.keys())]


def load_puzzle(date, difficulty):
    r_types = ['???', 'equal_to', 'equal', 'not_equal', 'greater_than', 'less_than']

    with open('games.json', 'r') as f:
        d = json.load(f)
        puzzle = [int(n) for n in d[date][difficulty].split(',')]

        width, height = puzzle[0], puzzle[1]
        layout = puzzle[2:2+width*height]
        regions = desmos_region_helper(width, height, layout)
        shape = [''.join(['_' if layout[width * (height-j-1) + i] == -1 else 'X' for i in range(width)]) for j in range(height)]

        idx = 2+width*height
        region_count = len(regions)
        region_types = puzzle[idx:idx+region_count]

        idx = idx+region_count
        region_targets = puzzle[idx:idx+region_count]
        rules = [(r_types[rt], rg) for rt, rg in zip(region_types, region_targets)]

        idx = idx+region_count
        tiles = []
        for i in range(idx, len(puzzle), 2):
            tiles.append((puzzle[i], puzzle[i+1]))

        return Pips(shape=shape, tiles=tiles, regions=regions, rules=rules)


def main():
    n = -1
    """# 2026-03-19_medium
    puzzle = Pips(
        shape=[
            [n, n, 1, 1, n, n],
            [2, 0, 3, 4, n, n],
            [0, 3, 3, 4, 4, 0],
            [5, n, n, 6, n, n],
        ],
        tiles=[
            (2, 4),
            (5, 1),
            (4, 3),
            (5, 6),
            (5, 5),
            (3, 3),
            (2, 0),
        ],
        regions=[
            ('greater_than', 9),
            ('greater_than', 2),
            ('equal', 0),
            ('equal', 0),
            ('less_than', 2),
            ('less_than', 2),
        ]
    )"""
    # 2025-11-07_hard
    puzzle = Pips(
        shape=[
            [n, n, n, n, 0, n],
            [1, 1, 1, 2, 2, n],
            [n, 3, 2, 2, 4, 0],
            [n, 0, 2, 5, 5, n],
            [n, 6, 6, n, 5, n],
            [n, 6, 7, 7, 5, n],
        ],
        tiles=[
            (4, 2),
            (4, 4),
            (4, 0),
            (5, 6),
            (4, 3),
            (3, 0),
            (0, 0),
            (3, 3),
            (6, 3),
            (1, 4),
            (1, 0),
        ],
        regions=[
            ('equal_to', 12),
            ('equal', 0),
            ('equal_to', 2),
            ('equal_to', 1),
            ('equal_to', 12),
            ('equal_to', 12),
            ('equal_to', 12),
        ]
    )
    """puzzle = Pips(
        shape=[
            [0, n, n, n, n],
            [1, 1, 1, n, n],
            [n, 0, n, 2, 2],
            [n, 3, 3, 2, n],
        ],
        tiles=[
            (3, 1),
            (1, 6),
            (5, 3),
            (6, 6),
            (2, 2),
        ],
        regions=[
            ('equal', 0),
            ('equal_to', 5),
            ('equal', 0),
        ]
    )"""
    """puzzle = Pips(
        shape=[
            [0, 1],
            [0, 1],
        ],
        tiles=[
            (1, 6),
            (3, 6),
        ],
        regions=[
            ('equal', 0)
        ]
    )"""

    start = time.time()
    sols = solve_puzzle(puzzle)
    end = time.time()
    print(f'Found {0} solutions in {1000*(end-start):.0f} ms.')
    print(sols)


if __name__ == '__main__':
    main()
