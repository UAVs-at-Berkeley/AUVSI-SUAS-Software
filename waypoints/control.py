from interface import *
from pathfinding import *

def findPaths():
    '''
    Gives a list of coordinates to path to given the waypoints
    '''
    cookie = getCookie()
    waypoints = getWayPoints(cookie)
    temp = [getHomePos(cookie)]
    for i in range(1, len(waypoints)):
        if waypoints[i] != waypoints[i-1]:
            temp.append(waypoints[i])
    waypoints = temp

    grid, convert = createGrid()
    for i in range(len(grid[0]) - 1, 0, -10):
        for j in range(0, len(grid), 10):
            print('*' if grid[j][i] > 0 else '-', end=' ')
        print(" ")
    print(" ")
   
    print("Waypoints: ", waypoints) 
    print("Paths:")
    for i in range(len(waypoints) - 1):
        a = WayPointsProblem(grid, convert(waypoints[i], 'scaled'), convert(waypoints[i+1], 'scaled'), scaleObstacles(convert))
        k = smooth(aStarSearch(a)[0], a)
        print([convert(i) for i in k])

findPaths()
