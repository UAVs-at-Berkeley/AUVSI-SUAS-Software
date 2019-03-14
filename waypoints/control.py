from interface import *
from pathfinding import *

def getData():
    cookie = getCookie()
    f = open("WaypointsData.txt", "w+")
    f.write(str(getMissionData(cookie)) + '\n') 
    f.write(str(getObstacles(cookie)))    
    f.close()
        

def findPaths(readFromFile):
    '''
    Gives a list of coordinates to path to given the waypoints
    readFromFile is True if the methods should read and false if the methods should read from the interop server
    ''' 
    cookie = getCookie()
    waypoints = getWayPoints(cookie, readFromFile)
    temp = [getHomePos(cookie, readFromFile)]
    for i in range(1, len(waypoints)):
        if waypoints[i] != waypoints[i-1]:
            temp.append(waypoints[i])
    waypoints = temp

    boundary, grid, convert = createGrid(readFromFile)
    for i in range(len(grid[0]) - 1, 0, -10):
        for j in range(0, len(grid), 10):
            print('*' if grid[j][i] > 0 else '-', end=' ')
        print(" ")
    print(" ")
   
    print("Waypoints: ", waypoints) 
    print("Paths:")
    for i in range(len(waypoints) - 1):
        a = WayPointsProblem(grid, convert(waypoints[i], 'scaled'), convert(waypoints[i+1], 'scaled'), scaleObstacles(convert, readFromFile), boundary)
        k = smooth(aStarSearch(a)[0], a)
        print([convert(i) for i in k])

#getData()
findPaths(True)
