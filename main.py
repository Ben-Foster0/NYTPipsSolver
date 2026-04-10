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
    # find next available cell
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
    srt += list(tiles)
    return srt


def solve_puzzle(puzzle, max_time=None, placement=None):
    if max_time is not None and time.time() > max_time:
        raise Exception('Time limit exceeded')

    solutions = []

    if placement is None:
        placement = tile_placements(to_grid(puzzle.shape))

    pos = placement.item
    for i, tile in enumerate(sort_pieces(puzzle.tiles - puzzle.placed_tiles)):
        for dir in [(0, 1), (1, 0)]:
            if pos is not None:
                puzzle.place(tile, (pos[dir[0]], pos[dir[1]]))

            if puzzle.is_solved():
                solutions += [copy.copy(puzzle)]

            if puzzle.is_valid():
                for child in placement.children:
                    if sol := solve_puzzle(puzzle, max_time=max_time, placement=child):
                        solutions += sol

            if pos is not None:
                puzzle.remove((pos[dir[0]], pos[dir[1]]))

            if tile[0] == tile[1]:
                break

    return list(set(solutions))


def load_puzzles(strong_check=True):
    puzzles = {}
    with open('games.json', 'r') as f:
        d = json.load(f)
        for date, vs in d.items():
            for diff, v in vs.items():
                p = Pips(
                    shape=v['shape'],
                    tiles=[tuple(t) for t in v['tiles']],
                    regions=[(r['type'], r['value']) for r in v['regions']],
                    strong_check=strong_check
                )
                puzzles[f'{date}-{diff}'] = p
    return puzzles


def time_all_puzzles(time_limit, difficulties):
    """
    Function to check the solving time for each puzzle
    Used to create statistics for CS4795 presentation & report

    :param time_limit: maximum time elapsed solving a puzzle before skipping
    :param difficulties: the difficulties to be included in the output
    :return: list of puzzle runtimes in ms
    """
    puzzles = load_puzzles()

    times = []
    full_start = time.time()
    for i, (name, puzzle) in enumerate(puzzles.items()):
        if not difficulties[name.split('-')[-1]]:
            continue

        try:
            start = time.perf_counter()
            sols = solve_puzzle(puzzle, time.time()+time_limit)
            end = time.perf_counter()
        except Exception as e:
            print(f'Time limit exceeded.')
            times.append(-1)
            continue

        times.append(1000*(end-start))

        progress = (i+1) / len(puzzles)
        elapsed = time.time() - full_start
        print(f'{i:>3}/{len(puzzles):>3} - {elapsed / progress - elapsed:>.2f} seconds remaining.')
    return times


def main():
    # print(time_all_puzzles(60*2.5, {'easy': True, 'medium': False, 'hard': False}))

    puzzle = load_puzzles(strong_check=True)['2026-04-10-hard']

    start = time.perf_counter()
    sols = solve_puzzle(puzzle)
    end = time.perf_counter()

    for i, sol in enumerate(sols, 1):
        print(sol, end='\n\n')
    print(f'Found {len(sols)} solutions in {1000*(end-start):.0f} ms.')


if __name__ == '__main__':
    main()
