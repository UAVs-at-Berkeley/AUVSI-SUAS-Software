import requests 
import math
from pathfinding import *
IP = "http://localhost:8000"
readFromFile = False

def getCookie():
    r = requests.post(IP+"/api/login", json={"username": "testuser", "password": "testpass"}, headers={'content-type': 'application/json'})
    return r.headers["Set-Cookie"].split()[0][:-1]

def getMissionData(cookie, readFromFile = False):
    if readFromFile:
        f = open("WaypointsData.txt", "r")
        data = eval(f.readline())
        f.close()
        return data
    return requests.get(IP+"/api/missions", headers={'cookie': cookie}).json()[0]

def getObstacles(cookie, readFromFile = False):
    '''
    returns a list of dictionaries
        latitude
        longitude
        cylinder_radius
        cylinder_height
    '''
    if readFromFile:
        f = open("WaypointsData.txt", "r")
        f.readline()
        data = eval(f.readline())
        f.close()
        return data
        
    r = requests.get(IP+"/api/obstacles", headers={'cookie': cookie}) 
    data = r.json()['stationary_obstacles']
    obstacles = []
    for i in data:
        obstacles.append((i['latitude'], i['longitude'], i['cylinder_radius'], i['cylinder_height']))
    return obstacles
   
def getWayPoints(cookie, readFromFile = False):
    '''
    returns a list of waypoints (latitude, longitude, altitude) for a mission
    '''
    data = getMissionData(cookie, readFromFile)['mission_waypoints']
    waypoints = []
    for i in data:
        waypoints.append((i['latitude'], i['longitude'], i['altitude_msl']))
    return waypoints    

def getHomePos(cookie, readFromFile = False):
    '''
    gets the home position for a mission
    '''
    pos = getMissionData(cookie, readFromFile)['home_pos']
    return (pos['latitude'], pos['longitude'], 0)

def fillGrid(grid, boundary, obstacles=None):
    '''
    fill the grid with true and false
    '''
    for i in range(len(boundary)):
        startx, starty = boundary[i]
        endx, endy = boundary[(i + 1) % len(boundary)]
        diff = (endx - startx) // abs(endx - startx)
        for j in range(startx, endx + diff, diff):
            grid[j][starty + (endy - starty) * (j - startx) // (endx - startx)] += 1;

   
    for i in range(len(boundary)):
        xF = boundary[(i+1) % len(boundary)][0]
        xP = boundary[len(boundary) - 1 if i == 0 else i-1][0]
        if (xF - boundary[i][0]) / abs(xF - boundary[i][0]) == (boundary[i][0] - xP) / abs(boundary[i][0] - xP):
            grid[boundary[i][0]][boundary[i][1]] -= 1
    

    for x in range(len(grid)):
        counter = 0

        for y in range(len(grid[x])):
            if grid[x][y] > 1:
                counter += grid[x][y] - 1
                grid[x][y] = False
            elif counter%2 == 1:
                grid[x][y] = False    
      

    if(obstacles is None):
        return grid

    for i in obstacles:
        for x in range(int(i[0] - i[2]), int(i[0] + i[2] + 1)):
            if (x - i[0]) * (x - i[0]) / i[2] / i[2] <= 1:
                k1 = -int(math.sqrt(i[3] * i[3] * (1 - (x - i[0]) * (x - i[0]) / i[2] / i[2]))) + i[1] - 1
                k2 = int(math.sqrt(i[3] * i[3] * (1 - (x - i[0]) * (x - i[0]) / i[2] / i[2]))) + i[1] + 1
                for y in range(k1, k2 + 1):
                    if(x >= 0 and x < len(grid) and y >= 0 and y < len(grid[0])):
                        grid[x][y] = i[4];
    return grid
            

def scaleBoundary(readFromFile = False):
    '''
    Returns a list of scaled boundary coordinates and a function convert(coordinates, type_to_convert_to)
    to convert to and from the scaled boundary coordinates
    '''
    r = getMissionData(getCookie(), readFromFile)['fly_zones']
    boundaryPoints = [r[x]['boundary_pts'] for x in range(len(r))]
    scaledCoordinates, coordinates, xcoords, ycoords = [], [], [], []
    for zone in boundaryPoints:
        for i in zone:
            coordinates.append((i['longitude'] * (1e5), i['latitude'] * (1e5)))
            xcoords.append(i['longitude'] * (1e5))
            ycoords.append(i['latitude'] * (1e5))
    xmin, ymin = min(xcoords), min(ycoords)
    for i in coordinates:
        scaledCoordinates.append((int(i[0] - xmin), int(i[1] - ymin)))
    
    def convert(coordinates, type_to_convert_to=None):
        if type_to_convert_to == 'scaled':
            #converts (latitude, longitude) to scaled coordinates
            first = int(coordinates[1] * (1e5) - xmin)
            second = int(coordinates[0] * (1e5) - ymin) 
        else:
            #converts scaled coordinates = (latitude, longitude)
            first = (coordinates[1] + ymin) / (1e5)
            second = (coordinates[0] + xmin) / (1e5)
        if len(coordinates) == 2:
            return (first, second)
        else:
            return (first, second, coordinates[2])
    return scaledCoordinates, convert


def scaleObstacles(convert, readFromFile = False):
    '''
    Converts obstacles in (latitude, longitude, altitude) to (x, y, major axis, minor axis, altitude (feet))
    '''
    scaledObstacles = []
    obstacles = getObstacles(getCookie(), readFromFile)
    for i in obstacles:
        a = convert((i[0], i[1]), 'scaled')
        scaledObstacles.append((a[0], a[1], i[2]/2.87615, i[2]/3.64170, i[3]))
    scaledObstacles.sort(key = lambda o: o[4])
    return scaledObstacles
    

def createGrid(readFromFile = False):
    '''
    creates a grid[x][y] with true if there is a boundary or an obstacle and false otherwise
    returns the grid with a conversion function to convert latitude/longitude to scaled coordinates and vice versa
    '''
    boundaryPoints, convert = scaleBoundary(readFromFile)
    xsize = max([i[0] for i in boundaryPoints]) + 100  #adding the extra constant value at the end acts as a buffer 
    ysize = max([i[1] for i in boundaryPoints]) + 100
    grid = [[True for i in range(ysize)] for j in range(xsize)]
    obstacles = scaleObstacles(convert, readFromFile)
    return boundaryPoints, fillGrid(grid, boundaryPoints, obstacles), convert

'''
boundaryPoints, grid, convert = createGrid()
for i in range(len(grid[0]) - 1, 0, -10):
    for j in range(0, len(grid), 10):
        print('*' if grid[j][i] > 0 else '-', end=' ')
    print(" ")
print(" ")
a = WayPointsProblem(grid, (800, 10, 0), convert((38.142544, -76.434088, 200), 'scaled') , scaleObstacles(convert), boundaryPoints)
k = smooth(aStarSearch(a)[0], a)
print([convert(i) for i in k])
'''

'''
grid = [[True for i in range(50)] for j in range(50)]
grid = fillGrid(grid, [(2, 2), (15, 25), (2, 48), (25, 33), (48, 48), (33, 25), (48, 2), (25, 15)], [(25, 25, 4, 4, 200)])
for i in range(len(grid[0]) - 1, 0, -1):
    for j in range(len(grid)):
        print('*' if grid[j][i] > 0 else '-', end=' ')
    print(" ")
print(" ")
a = WayPointsProblem(grid, (10, 14, 100), (40, 14, 100), [(25, 25, 4, 4, 200)],  [(2, 2), (15, 25), (2, 48), (25, 33), (48, 48), (33, 25), (48, 2), (25, 15)])
print(smooth(aStarSearch(a)[0], a))
'''

