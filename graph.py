class Graph:
    def __init__(self):
        self.nodes = {}

    def from_grid(self, game):
        grid = [[hash(c) for c in row] for row in game.board]
        width, height = len(grid[0]), len(grid)

        for j, row in enumerate(grid):
            for i, c in enumerate(row):
                if c is None:
                    continue
                self.add_node(c)

        for j in range(height):
            for i in range(width):
                for (xp, yp) in [(0, -1), (1, 0), (0, 1), (-1, 0)]:
                    x, y = xp+i, yp+j
                    if x < 0 or x >= width:
                        continue
                    if y < 0 or y >= height:
                        continue

                    a = grid[j][i]
                    b = grid[y][x]

                    if a is None or b is None:
                        continue

                    if a != b:
                        self.add_edge(a, b)

    def add_node(self, node):
        if node not in self.nodes:
            self.nodes[node] = set()

    def add_edge(self, n1, n2):
        self.nodes[n1].add(n2)
        self.nodes[n2].add(n1)

    def next_node(self, possible, filled):
        min_count = 99999
        min_node = None
        for node in self.nodes:
            if filled[node]:
                continue
            if len(possible[node]) < min_count:
                min_count = len(possible[node])
                min_node = node
        return min_node

    def color_graph(self):
        possible = {}
        filled = {}
        history = []

        for node in self.nodes:
            possible[node] = {0, 1, 2, 3}
            filled[node] = False

        while len(history) < len(self.nodes):
            node = self.next_node(possible, filled)
            if len(possible[node]) == 0:
                break

            # possible[node] = {random.choice(list(possible[node]))}
            possible[node] = {list(possible[node])[0]}
            # possible[node] = {list(possible[node])[node % len(possible[node])]}
            for other in self.nodes[node]:
                possible[other] -= possible[node]

            filled[node] = True
            history.append(node)

        return {k: list(v)[0] for k, v in possible.items()}