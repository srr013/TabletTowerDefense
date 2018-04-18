import Queue


class MyPriorityQueue(Queue.PriorityQueue):
    def __init__(self):
        Queue.PriorityQueue.__init__(self)

    def put(self, item, priority):
        Queue.PriorityQueue.put(self, (priority, item))

    def get(self, *args, **kwargs):
        _, item = Queue.PriorityQueue.get(self, *args, **kwargs)
        return item

def heuristic(a, b):
    '''Returns the absolute value difference between 2 points a and b'''
    (x1, y1) = a
    (x2, y2) = b
    return abs(x1 - x2) + abs(y1 - y2)

def a_star_search(graph, start, goal):
    '''Implements the A* search algorithm
    Returns: came_from dict, cost_so_far
    Graph: the available space to move. Usually from GridWithWeights
    Start: the starting point of the unit (x,y)
    Goal: Unit's end point (x,y)'''
    frontier = MyPriorityQueue()
    frontier.put(start, 0)
    came_from = {}
    cost_so_far = {}
    came_from[start] = None
    cost_so_far[start] = 0

    while not frontier.empty():
        current = frontier.get()
        if current == goal:
            break
        neighbors = graph.nodeDict[current]

        for next in neighbors: # neighbors is a dict w/ a list of lists for each node: [(8, 3), True, 0.0]. 1 list for each dir
            if next ==[]:
                pass
            else:
                node = next[0]
                passable = next[1]
                cost = next[2]
                if passable and (node not in cost_so_far or cost < cost_so_far[node]):
                    cost_so_far[node] = cost
                    priority = cost + heuristic(goal, node)
                    frontier.put(node, priority)
                    came_from[node] = [current]

        if not neighbors or frontier.qsize()==0:
            came_from = 'Path Blocked'
            cost_so_far = current
    return came_from, cost_so_far



def get_path(map, start, goal):
    '''This is the main function call in Pathfinding.py. See a_star_search for info.'''
    came_from, cost_so_far = a_star_search(map, start, goal)
    # draw_grid(map, width=1, point_to=came_from, start=start, goal=goal)
    # draw_grid(map, width=1, number=cost_so_far, start=start, goal=goal)
    # print came_from
    return came_from, cost_so_far


def reconstruct_path(came_from, start, goal):
    '''Takes the variables output by a_star_search and produces a movelist. See a_star_search for variable info'''
    current = goal
    path = []
    while current != start:
        path.append(current)
        try:
            current = came_from[current][0]
        except KeyError:
            return "Path Blocked", current
    path.append(start)
    path.reverse()

    x = 0
    direction = []
    while x < len(path) - 1:
        if path[x][1] == path[x + 1][1]:
            if path[x][0] < path[x + 1][0]:
                direction.append('r')
            else:
                direction.append('l')
        if path[x][0] == path[x + 1][0]:
            if path[x][1] < path[x + 1][1]:
                direction.append('u')
            else:
                direction.append('d')
        x += 1
    direction.append('r')  # last square will always be right

    y = 0
    move = []
    movedir = []
    move.append(path[y])
    movedir.append(direction[y])
    y += 1
    while y < len(direction):
        if y == len(direction) - 1:
            move.append(path[y])
            movedir.append(direction[y])
            break
        if direction[y - 1] == direction[y]:
            pass
        else:
            move.append(path[y])
            movedir.append(direction[y])
        y += 1
    return path, direction, move, movedir


class MapGrid():
    def __init__(self, width, height, border):
        '''Creates a basic grid for use in pathfinding algorithms.
        Width: the width of the available space to move
        Height: the height of the available spave to move
        border: a list of points that are impassable'''
        self.width = width - (border * 2)
        self.height = height - (border * 2)
        self.border = border
        self.walls = []

    def in_bounds(self, id):
        '''Used to ensure a unit doesn't move outside the boundaries'''
        (x, y) = id
        return 0 <= x < self.width and 0 <= y < self.height

    def passable(self, id):
        '''Used to ensure a unit doesn't move through a wall'''

        return id not in self.walls

    # def neighbors(self, id):
    #     '''Find neighboring spaces that the unit can move to'''
    #     (x, y) = id
    #     results = []
    #     if x < Map.mapvar.squwid - Map.mapvar.squborder:
    #         results.append((x+1,y))
    #     if x > Map.mapvar.squborder:
    #         results.append((x-1,y))
    #     if y < Map.mapvar.squhei - Map.mapvar.squborder:
    #         results.append((x,y+1))
    #     if y > Map.mapvar.squborder:
    #         results.append((x,y-1))
    #
    #     #if (x + y) % 2 == 0: results.reverse()  # aesthetics
    #     # results = filter(self.in_bounds, results)
    #     results = filter(self.passable, results)
    #
    #     return results

    def neighbors(self, id):
        '''Find neighboring spaces that the unit can move to'''
        (x, y) = id
        results = []
        results.append((int(x+1),int(y)))
        results.append((int(x-1),int(y)))
        results.append((int(x),int(y+1)))
        results.append((int(x),int(y-1)))

        #if (x + y) % 2 == 0: results.reverse()  # aesthetics
        # results = filter(self.in_bounds, results)
        #results = filter(self.passable, results)

        return results

class neighborGridwithWeights(MapGrid):
    def __init__(self, width, height, border, goal):
        MapGrid.__init__(self, width, height, border)
        self.width = width
        self.height = height
        self.goal = goal
        self.weights = self.genWeights()
        self.nodeDict = {}

    def genNodeDict(self):
        x = 0
        while x < self.width:
            y = 0
            while y < self.height:
                self.nodeDict[(x, y)] = []
                self.updateDict((x,y))
                y += 1
            x += 1

    def updateWalls(self, wall):
        neighbors = self.neighbors(wall)
        for neighbor in neighbors:
            self.updateDict(neighbor)

    def updateDict(self, id):
        self.nodeDict[id] = []
        for neighbor in self.neighbors(id):
            if neighbor[0] < 0 or neighbor[0] > self.width or neighbor[1] < 0 or neighbor[1] > self.height:
                self.nodeDict[id].append([])
            else:
                self.nodeDict[id].append(
                    [neighbor, self.passable(neighbor), self.weights.get(neighbor, 1)])

    def genWeights(self):
        weights = {}
        y_weight = 0
        x_weight = 0
        # weighting prefers movement closer to the base X coord over Y coord.
        for x in range(0, int(self.width)):
            if x + 1 % self.goal[0] == 0:
                x_weight = 0
            else:
                x_weight = abs(self.goal[0] - x) * 1

            for y in range(0, int(self.height)):
                if y + 1 % self.goal[1] == 0:
                    y_weight = 0
                else:
                    y_weight = abs(self.goal[1] - y) * 10
                weights[x, y] = round(x_weight, 1) + round(y_weight, 1)
        # print weights
        return weights

    def cost(self, from_node, to_node):
        '''Determines the best route based on grid weighting'''
        return self.weights.get(to_node, 1)


# class GridWithWeights(MapGrid):
#     '''Creates a MapGrid then adds weight to each square to indicate the best route'''
#
#     def __init__(self, width, height, border, goal):
#         MapGrid.__init__(self, width, height, border)
#         self.goal = goal
#         self.weights = self.genWeights()
#
#     def genWeights(self):
#         weights = {}
#         y_weight = 0
#         x_weight = 0
#         # weighting prefers movement closer to the base X coord over Y coord.
#         for x in range(0, int(self.width)):
#             if x + 1 % self.goal[0] == 0:
#                 x_weight = 0
#             else:
#                 x_weight = abs(self.goal[0] - x) * .01
#
#             for y in range(0, int(self.height)):
#                 if y + 1 % self.goal[1] == 0:
#                     y_weight = 0
#                 else:
#                     y_weight = abs(self.goal[1] - y) * .1
#                 weights[x, y] = round(x_weight, 1) + round(y_weight, 1)
#         # print weights
#         return weights
#
#     def cost(self, from_node, to_node):
#         '''Determines the best route based on grid weighting'''
#         return self.weights.get(to_node, 1)


# utility functions for dealing with square grids
def from_id_width(id, width):
    return (id % width, id // width)


def draw_tile(graph, id, style, width):
    r = "."
    if 'number' in style and id in style['number']: r = "%d" % style['number'][id]
    if 'point_to' in style and style['point_to'].get(id, None) is not None:
        (x1, y1) = id
        (x2, y2) = style['point_to'][id]
        if x2 == x1 + 1: r = ">"
        if x2 == x1 - 1: r = "<"
        if y2 == y1 + 1: r = "v"
        if y2 == y1 - 1: r = "^"
    if 'start' in style and id == style['start']: r = "A"
    if 'goal' in style and id == style['goal']: r = "Z"
    if 'path' in style and id in style['path']: r = "@"
    if id in graph.walls: r = "#" * width
    return r


def draw_grid(graph, width=1, **style):
    for y in range(int(graph.height)):
        xlist = list()
        for x in range(int(graph.width)):
            xlist.append("%%-%ds" % width % draw_tile(graph, (x, y), style, width))
        print (xlist)
