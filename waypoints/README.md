Pathing for AUVSI Drone using Jump Point Search 

How to run:
1. Instantiate WayPointsProblem(grid, starting position, ending position)
    grid should be a 2d grid of booleans with false if there is no obstacle and true if there is
`   starting and ending position should be a coordinate (x, y) 
2. directions, cost = aStarSearch(WayPointsProblem)
    calling aStarSearch on the WayPointsProblem instance returns a tuple (directions, cost) for the shortest path from the start node to the goal node
    directions is a list of coordinates/waypoints to move to
    cost is the cost of the path (given that we can only move horizontally/vertically at a 45 degree angle)

Smoothing:
There are two problems with the list of coordinates returned by jump point search: 
1. Because of the nature of the jump point search algorithm, the drone will try to deviate from a straight path earlier to avoid obstacles, which can cause room for error.
2. The waypoints returned by jump point search only cause the move at a 45 degree angle or in a straight line 

To fix this, call:
smooth(directions, WayPointsProblems)
where directions is the set of coordinates returned by jump point search and WayPointsProblem is the problem instance

Smoothing creates a list of waypoints along the path that are next to obstacles. This allows the drone to move at different angles than 45 degrees and causes the drone to more gradually deviate from a straight path in order to avoid an obstacle. Note that there are a lot more waypoints returned near obstacles than far away from them.

Example:
grid = []
for i in range(8):
    grid.append([False for j in range(8)])
grid[4][4] = True
grid[3][3] = True
grid[3][4] = True
grid[5][3] = True
grid[4][2] = True
grid[4][0] = True
grid[4][1] = True
problem = WayPointsProblem(grid, (0, 3), (7, 3))
directions, cost = aStarSearch(problem)
print("Directions: ", directions)
print("Smoothed Directions: ", smooth(directions, problem))
print("Cost: ", cost)

