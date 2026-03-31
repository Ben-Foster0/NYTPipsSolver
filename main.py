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


def to_grid(shape):
    return [[0 if c >= 0 else -1 for c in row]for row in shape]


def tile_placements(grid, n=1):
    x, y = 0, 0
    w, h = len(grid[0]), len(grid)
    while grid[y][x] != 0:
        x += 1
        if x >= w:
            x = 0
            y += 1
            if y >= h:
                return Tree(None, is_leaf=True)

    placements = Tree(None)
    # right facing
    if x < w-1 and grid[y][x+1] == 0:
        grid[y][x] = n
        grid[y][x+1] = n
        solved = tile_placements(grid, n=n+1)
        grid[y][x] = 0
        grid[y][x+1] = 0
        if solved.children or solved.is_leaf:
            solved.item = [(x, y), (x+1, y)]
            placements.children.append(solved)

    # down facing
    if y < h-1 and grid[y+1][x] == 0:
        grid[y][x] = n
        grid[y+1][x] = n
        solved = tile_placements(grid, n=n+1)
        grid[y][x] = 0
        grid[y+1][x] = 0
        if solved.children or solved.is_leaf:
            solved.item = [(x, y), (x, y+1)]
            placements.children.append(solved)

    return placements


def sort_pieces(tiles):
    srt = []
    for t in tiles:
        if t[0] == t[1]:
            srt.append(t)

    tiles = set(tiles) - set(srt)
    srt += sorted(tiles, key=lambda e: max(e))
    return srt


def solve_puzzle(puzzle, placement=None):
    solutions = []

    if placement is None:
        placement = tile_placements(to_grid(puzzle.shape))

    pos = placement.item
    # for i, tile in enumerate(sorted(puzzle.tiles - puzzle.placed_tiles, key=lambda t: abs(t[0]-t[1])), 1):
    for i, tile in enumerate(sort_pieces(puzzle.tiles - puzzle.placed_tiles)):
        for dir in [(0, 1), (1, 0)]:
            if pos is not None:
                puzzle.place(tile, (pos[dir[0]], pos[dir[1]]))

            if puzzle.is_solved():
                solutions += [copy.copy(puzzle)]

            if puzzle.is_valid():
                for child in placement.children:
                    if sol := solve_puzzle(puzzle, placement=child):
                        solutions += sol

            if pos is not None:
                puzzle.remove((pos[dir[0]], pos[dir[1]]))

            if tile[0] == tile[1]:
                break

    return list(set(solutions))


def load_puzzles():
    puzzles = {}
    with open('games.json', 'r') as f:
        d = json.load(f)
        for date, vs in d.items():
            for diff, v in vs.items():
                p = Pips(
                    shape=v['shape'],
                    tiles=[tuple(t) for t in v['tiles']],
                    regions=[(r['type'], r['value']) for r in v['regions']],
                    strong_check=True
                )
                puzzles[f'{date}-{diff}'] = p
    return puzzles


def main():
    puzzle = load_puzzles()['2026-03-17-medium']

    start = time.time()
    sols = solve_puzzle(puzzle)
    end = time.time()

    for sol in sols:
        print(sol)
        print(sol.shape)
        print()
    print(f'Found {len(sols)} solutions in {1000*(end-start):.0f} ms.')


if __name__ == '__main__':
    main()
