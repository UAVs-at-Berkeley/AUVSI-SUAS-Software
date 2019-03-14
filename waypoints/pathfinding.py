from queue import PriorityQueue
import math

class WayPointsProblem:
    def __init__(self, inputGrid, startPos, goalPos, cylinders, boundaryPoints):
        self.grid = inputGrid
        self.start = (startPos[0], startPos[1])
        self.startAlt = startPos[2]
        self.goal = (goalPos[0], goalPos[1])
        self.goalAlt = goalPos[2]
        self.obstacles = [i for i in cylinders if i[4] >= min(self.startAlt, self.goalAlt)]
        self.boundary = boundaryPoints
        #print(inputGrid[25][13])
        
    def getStartState(self):
        '''
        Gets the starting state for the search
        state is (x, y, cost, (x_direction, y_direction))
        '''
        if not self.valid(self.start[0], self.start[1]):
            print("ERROR: Start state is not valid!")
        if not self.valid(self.goal[0], self.goal[1]): 
            print("ERROR: End state is not valid!")
        if self.obstacle(self.start[0], self.start[1]): 
            print("ERROR: Start state is an obstacle or out of bounds!") 
        if self.obstacle(self.goal[0], self.goal[1]):
            print("ERROR: End state is an obstacle or out of bounds!")
         
        return [(self.start[0], self.start[1], 0, (1, 1)), (self.start[0], self.start[1], 0, (1, -1)), (self.start[0], self.start[1], 0, (-1, 1)), (self.start[0], self.start[1], 0, (-1, -1))]

    def valid(self, x, y):
        return x >= 0 and x < len(self.grid) and y >= 0 and y < len(self.grid[0])  

    def getSuccessors(self, state):
        '''
        Gets the successors of the search problem with constraints added by jump point search
        '''
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
        '''
        Determines if there is an obstacle at a specific point
        '''
        if not self.valid(x, y):
            return True;
        return self.grid[x][y] > 0 and (self.grid[x][y] == 1 or self.grid[x][y] > self.startAlt)

    def search_horizontal(self, state, hdir): 
        '''
        jump point search horizontal search
        '''
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
        '''
        jump point search vertical search
        '''
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
        '''
        checks if we found out goal
        '''
        x, y, cost, direction = state
        return x == self.goal[0] and y == self.goal[1] 
 
    def heuristic(self, state):
        '''
        heuristic for A-star
        '''
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
    '''
    takes a path found by jump point search and smooths it  
    '''

    if len(path) < 2:
        print('ERROR: Path must have at least 2 points for smoothing to work!')
        return None
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
    prev, totalDistance = None, 0
    for i in smoothedPoints:
        if i is not None:
            if prev is not None:
                totalDistance += dist(prev, i)
            prev = i
            waypoints.append(i)
    
    altitudePoints = [(waypoints[0][0], waypoints[0][1], problem.startAlt)] 
    
    partialDistance = problem.startAlt
    for i in range(1, len(waypoints)):
        partialDistance += (problem.goalAlt - problem.startAlt) * dist(waypoints[i-1], waypoints[i]) / totalDistance
        altitudePoints.append((waypoints[i][0], waypoints[i][1], partialDistance))

    print(altitudePoints)
    return altitudeSmooth(altitudePoints, problem)

def dist(p1, p2):
    return math.sqrt((p1[0] - p2[0]) * (p1[0] - p2[0]) + (p1[1] - p2[1]) * (p1[1] - p2[1]))

def intersect(ellipse, point1, point2):
    '''
    checks if a line between two points intersects an ellipse 
    assumes we are uniformly increasing the altitude
    '''
    h, k, a, b, altitude = ellipse
    x0, y0, altitude0 = point1
    x1, y1, altitude1 = point2
    m = (y1 - y0) / (x1 - x0)
    c = y0 - m * x0
    epsilon = c - k
    delta = c + m * h
    discriminant = a*a + m*m + b*b - delta * delta - k * k + 2 * delta * k
    if discriminant < 0:
        return False
    xans0 = (h*b*b - m*a*a*epsilon + a*b*math.sqrt(discriminant)) / (a*a*m*m + b*b)
    xans1 = (h*b*b - m*a*a*epsilon - a*b*math.sqrt(discriminant)) / (a*a*m*m + b*b)
    yans0 = (xans0 - x0) * m + y0
    yans1 = (xans1 - x0) * m + y0
    ansCoords = []
    if xans0 >= min(x0, x1) and xans0 <= max(x0, x1):
        ansCoords.append((xans0, yans0))
    if xans1 >= min(x0, x1) and xans1 <= max(x0, x1):
        ansCoords.append((xans1, yans1))
    if ansCoords == []:
        return False
    if altitude0 < altitude1:
        point = min(ansCoords, key = lambda p: dist(p, (x0, y0)))
    else:
        point = min(ansCoords, key = lambda p: dist(p, (x1, y1))) 
    if (altitude1 - altitude0) / dist((x0, y0), (x1, y1)) * dist((x0, y0), point) + altitude0 <= altitude:
        return True
    return False

def intersectLine(linePoint1, linePoint2, point1, point2):
    '''
    determines if two line segements intersect
    '''
    point1 = (point1[0], point1[1])
    point2 = (point2[0], point2[1])
    if linePoint1 == point1 or linePoint2 == point1 or linePoint1 == point2 or linePoint2 == point2:
        return False
    return ccw(linePoint1, point1, point2) != ccw(linePoint2, point1, point2) and ccw(linePoint1, linePoint2, point1) != ccw(linePoint1, linePoint2, point2)
    
def ccw(point1, point2, point3):
    '''
    determines if points are counter-clockwise
    '''
    return (point3[1] - point1[1]) * (point2[0] - point1[0]) > (point2[1] - point1[1]) * (point3[0] - point1[0])

def altitudeSmooth(altitudePoints, problem):
    '''
    shortens the path by not considering some obstacles that are not present at a specific altitude
    '''
    smoothPoints = [altitudePoints[0]]
    i = 0
    while (i < len(altitudePoints) - 1):
        ioriginal = i
        for j in range(len(altitudePoints) - 1, i, -1):
            #there is guaranteed to be a valid j that is greater than i, namely i + 1
            valid = True
            for k in problem.obstacles:
                if intersect(k, altitudePoints[i], altitudePoints[j]):
                    valid = False
            for k in range(len(problem.boundary)):
                if intersectLine(problem.boundary[k], problem.boundary[(k + 1) % len(problem.boundary)], altitudePoints[i], altitudePoints[j]):
                    valid = False
            if valid:
                smoothPoints.append(altitudePoints[j])
                i = j
                break;
        if i == ioriginal:
            print("Altitude Smoothing Failed!")
            j = i + 1
            print(altitudePoints[i], altitudePoints[j])
            for k in range(len(problem.boundary)):
                if intersectLine(problem.boundary[k], problem.boundary[(k + 1) % len(problem.boundary)], altitudePoints[i], altitudePoints[j]):
                    print(problem.boundary[k], problem.boundary[(k + 1) % len(problem.boundary)])

            return altitudePoints
    return smoothPoints
