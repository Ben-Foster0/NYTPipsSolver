from pips import Pips
import json
import time
import copy


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
    solutions = []
    # if len(puzzle.tiles - puzzle.placed_tiles) == 0 and puzzle.is_solved():
    #     return [puzzle.copy()]

    is_base = False
    if placement is None:
        is_base = True
        placement = tile_placements(Grid(puzzle.shape))

    pos = placement.item
    for i, tile in enumerate(sorted(puzzle.tiles - puzzle.placed_tiles, key=lambda t: abs(t[0]-t[1])), 1):
        for dir in [(0, 1), (1, 0)]:
            if pos is not None:
                puzzle.place(tile, (pos[dir[0]], pos[dir[1]]))
            if puzzle.is_solved():
                # return copy.copy(puzzle)
                solutions += [copy.copy(puzzle)]

            if puzzle.is_valid():
                for child in placement.children:
                    if sol := solve_puzzle(puzzle, placement=child):
                        # return sol
                        solutions += sol

            if pos is not None:
                puzzle.remove((pos[dir[0]], pos[dir[1]]))

            if tile[0] == tile[1]:
                break

        if is_base:
            print(f'{i:>3} / {len(puzzle.tiles):>3}')

    # return False
    return list(set(solutions))


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


def load_puzzle_old(date, difficulty):
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


def load_puzzle(date, difficulty):
    with open('games.json', 'r') as f:
        d = json.load(f)[date][difficulty]

        return Pips(
            shape=d['shape'],
            tiles=[tuple(t) for t in d['tiles']],
            regions=[(r['type'], r['value']) for r in d['regions']]
        )


def main():
    puzzle = load_puzzle('2026-03-17', 'hard')

    start = time.time()
    sols = solve_puzzle(puzzle)
    end = time.time()
    print(f'Found {len(sols)} solutions in {1000*(end-start):.0f} ms.')
    for sol in sols:
        print(sol)
        print(sol.shape)
        print()


if __name__ == '__main__':
    main()
