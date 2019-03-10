# Waypoints Software for AUVSI Drone  
Currently, the waypoints software for the drone consists of two files: interface.py and pathing.py (although this is subject to change). The interface.py file is responsible for communicating with the Interop server to get data on the boundary, waypoints, and obstacles. 

## Getting the data (interface.py)
### How to run:
1.  grid, convert = createGrid()
    the createGrid() method takes boundary and obstacle data from the Interop server and creates a two dimensional grid of booleans indicating where there is an obstacle or a position is invalid.   
    The latitude and longitude points of the boundary are scaled so to (x, y) coordinates (note that x corresponds to longitude and y corresponds to latitude).   
    convert(coordinates, type_to_convert_to) is a method that converts latitude and longitude to the scaled coordinates if type_to_convert_to = 'scaled' and converts scaled coordinates to latitude to longitude if type_to_convert_to = 'not scaled'  
2.  obstacles = scaledObstacles(convert)
    This method gives a sorted list of obstacles needed for the search problem
3.  After creating a grid and getting the obstacles, we can run a pathing algorithm to find the short    est path between the start and end points.

## Pathing using Jump Point Search (pathing.py)

### How to run:  
1. Instantiate WayPointsProblem(grid, starting position, ending position, obstacles)  
    grid should be a 2d grid of booleans with false if there is no obstacle and true if there is  
    starting and ending position should be a coordinate (x, y, altitude) 
    obstacles are a list of cylinders. Those which have height less than the minimum altitude of the     start and end positions are filtered out
2. directions, cost = aStarSearch(WayPointsProblem)  
    calling aStarSearch on the WayPointsProblem instance returns a tuple (directions, cost) for the shortest path from the start node to the goal node  
    directions is a list of coordinates/waypoints to move to  
    cost is the cost of the path (given that we can only move horizontally/vertically at a 45 degree angle)  

### Smoothing:  
There are two problems with the list of coordinates returned by jump point search:   
1. Because of the nature of the jump point search algorithm, the drone will try to deviate from a straight path earlier to avoid obstacles, which can cause room for error.  
2. The waypoints returned by jump point search only cause the drone to move at a 45 degree angle or in a straight line   

To fix this, call:  
smooth(directions, WayPointsProblems)  
where directions is the set of coordinates returned by jump point search and WayPointsProblem is the problem instance  

Smoothing creates a list of waypoints along the path that are next to obstacles. This allows the drone to move at different angles than 45 degrees and causes the drone to more gradually deviate from a straight path in order to avoid an obstacle. Note that there are a lot more waypoints returned near obstacles than far away from them.  

### Altitude:
The smoothing algorithm not only smooths the path, but potentially makes it shorter by introducing altitude into its calculations. Without altitude, the drone will try to avoid obstacles that are not high enough to collide with it. 

After being given a smoothed path, the method altitudeSmooth(altitudePoints, problem) is called. This method looks at each pair of points in the path and sees if a drone can cross through an "obstacle" that it thought was once there given it uniformly increases in altitude. This allows the path to be shorter than it was before.

## Example:
grid, convert = createGrid()  
a = WayPointsProblem(grid, (800, 10, 0), (1, 71, 0), scaleObstacles(convert))  
k = smooth(aStarSearch(a)[0], a)  
print([convert(i) for i in k])  

## Potential Errors
1. One degree of latitude and longitude differs given the coordinates of the drone. This causes conversion from feet for the radius of each cylinder into latitude and longitude to have some error. (Note that because one degree latitude is not the same as 1 degree longitude, the cylinder obstacles are now ellipses.
2. Given the margin of error of the GPS, we may need to add some buffer length to the radius of each obstacle to absolutely ensure that the drone will not collide with an obstacle. This needs to be done with testing.
