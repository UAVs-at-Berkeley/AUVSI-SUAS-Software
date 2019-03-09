from queue import PriorityQueue
import math

class WayPointsProblem:
    def __init__(self, inputGrid, startPos, goalPos):
        self.grid = inputGrid
        self.start = startPos
        self.goal = goalPos
        
    def getStartState(self):
        '''state is (x, y, cost, (x_direction, y_direction))'''
        if not self.valid(self.start[0], self.start[1]) or not self.valid(self.goal[0], self.goal[1]): 
            print("ERROR: Start or end state is not valid!")
        elif self.obstacle(self.start[0], self.start[1]) or self.obstacle(self.goal[0], self.goal[1]):
            print("ERROR: Start of end state is an obstacle or out of bounds!")
         
        return [(self.start[0], self.start[1], 0, (1, 1)), (self.start[0], self.start[1], 0, (1, -1)), (self.start[0], self.start[1], 0, (-1, 1)), (self.start[0], self.start[1], 0, (-1, -1))]

    def valid(self, x, y):
        return x >= 0 and x < len(self.grid) and y >= 0 and y < len(self.grid[0])  

    def getSuccessors(self, state):
        x, y, cost, direction = state
        next_diagonal = []
        if self.valid(x, y) and not self.obstacle(x + direction[0], y + direction[1]):
            next_diagonal = [(x + direction[0], y + direction[1], cost + math.sqrt(2), direction)]
            if self.obstacle(x, y + direction[1]) and not self.obstacle(x, y + 2 * direction[1]):
                next_diagonal.append((x + direction[0], y + direction[1], cost + math.sqrt(2), (-direction[0], direction[1])))
            if self.obstacle(x + direction[0], y) and not self.obstacle(x + 2 * direction[0], y):
                next_diagonal.append((x + direction[0], y + direction[1], cost + math.sqrt(2), (direction[0], -direction[1]))) 
                 
        return self.search_horizontal(state, direction[0]) + self.search_vertical(state, direction[1]) + next_diagonal
          
    def obstacle(self, x, y):
        if not self.valid(x, y):
            return True;
        return self.grid[x][y]

    def search_horizontal(self, state, hdir): 
        x, y, cost, direction = state
        nodes = [];
        a = []
         
        while self.valid(x + hdir, y):
            if self.obstacle(x + hdir, y):
                return nodes

            if (x + hdir, y) == self.goal: 
                return [(x + hdir, y, cost + 1, "END")]
            
            if self.obstacle(x + hdir, y - 1) and not self.obstacle(x + hdir * 2, y - 1):
                nodes.append((x + hdir, y, cost + 1, (hdir, -1)))
      
            if self.obstacle(x + hdir, y + 1) and not self.obstacle(x + hdir * 2, y + 1):
                nodes.append((x + hdir, y, cost + 1, (hdir, 1)))
            
            cost = cost + 1
            x = x + hdir
            a = nodes[:]
        return nodes

    def search_vertical(self, state, vdir): 
        x, y, cost, direction = state
        nodes = [];

        while self.valid(x, y + vdir):
            if self.obstacle(x, y + vdir): 
                return nodes 
    
            if (x, y + vdir) == self.goal: 
                return [(x, y + vdir, cost + 1, "END")] 
    
            if self.obstacle(x - 1, y + vdir) and not self.obstacle(x - 1, y + vdir * 2):
                nodes.append((x, y + vdir, cost + 1,  (-1, vdir)))
      
            if self.obstacle(x + 1, y + vdir) and not self.obstacle(x + 1, y + vdir * 2):
                nodes.append((x, y + vdir, cost + 1, (1, vdir)))
 
            cost = cost + 1
            y = y + vdir
        return nodes

    def isGoalState(self, state):
        x, y, cost, direction = state
        return x == self.goal[0] and y == self.goal[1] 
 
    def heuristic(self, state):
        x, y, cost, direction = state
        return math.sqrt((self.goal[0] - x) * (self.goal[0] - x) + (self.goal[1] - y) * (self.goal[1] - y))

def aStarSearch(problem):
    q = PriorityQueue();
    visited = set()

    for i in problem.getStartState():
        if problem.valid(i[0], i[1]) and not problem.obstacle(i[0], i[1]):
            q.put((0, (i, [])))

    while(not q.empty()):
        priority, item = q.get()
        expand, directions = item
        if problem.isGoalState(expand):
            expand = (expand[0], expand[1], expand[2], expand[3])
            return directions + [(expand[0], expand[1])], expand[2]
        if (expand[0], expand[1], expand[3]) in visited:
            continue;
        visited.add((expand[0], expand[1], expand[3]))
        for successor in problem.getSuccessors(expand):
            q.put((successor[2] + problem.heuristic(successor), (successor, directions+[(expand[0], expand[1])])))
    print("Path Not Found!")
    return ([], -1)

def smooth(path, problem):
    waypoints = [(path[0][0], path[0][1])]
    for i in range(len(path) - 1):
        x0, y0, x1, y1 = path[i][0], path[i][1], path[i + 1][0], path[i + 1][1]
        if x1 - x0 == 0:
            xdiff = 0
        else:
            xdiff = int((x1 - x0) / abs(x1 - x0))
        if y1 - y0 == 0:
            ydiff = 0 
        else:
            ydiff = int((y1 - y0) / abs(y1 - y0))
        dirx = [1, -1, 0, 0]
        diry = [0, 0, 1, -1]
        while(x0 != x1):
            for j in range(4):
                if problem.obstacle(x0 + dirx[j], y0 + diry[j]) and problem.valid(x0 + dirx[j], y0 + diry[j]):
                    if ((x0, y0) != waypoints[len(waypoints) - 1]):
                        waypoints.append((x0, y0))
            x0 += xdiff
            y0 += ydiff
    waypoints.append((path[len(path) - 1][0], path[len(path) - 1][1]))
    
    smoothedPoints = waypoints[:]
    for i in range(len(waypoints) - 2):
        x0, y0, x1, y1 = waypoints[i][0], waypoints[i][1], waypoints[i + 1][0], waypoints[i + 1][1]
        x2, y2 = waypoints[i + 2][0], waypoints[i + 2][1]
        if (y1 - y0) * (x2 - x1) == (x1 - x0) * (y2 - y1):
            smoothedPoints[i + 1] = None
    
    waypoints = []
    for i in smoothedPoints:
        if i is not None:
            waypoints.append(i)
        
    return waypoints

