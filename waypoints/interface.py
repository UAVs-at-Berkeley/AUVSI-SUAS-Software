import requests 
import math
from pathfinding import *
IP = "http://localhost:8000"

def getCookie():
    r = requests.post(IP+"/api/login", json={"username": "testadmin", "password": "testpass"}, headers={'content-type': 'application/json'})
    return r.headers["Set-Cookie"].split()[0][:-1]

def getMissionData(cookie):
    return requests.get(IP+"/api/missions", headers={'cookie': cookie}).json()

def getObstacles(cookie):
    '''returns a list of dictionaries
        latitude
        longitude
        cylinder_radius
        cylinder_height'''
    r = requests.get(IP+"/api/obstacles", headers={'cookie': cookie}) 
    data = r.json()['stationary_obstacles']
    obstacles = []
    for i in data:
        obstacles.append((i['latitude'], i['longitude'], i['cylinder_radius'], i['cylinder_height']))
    return obstacles
    

def fillGrid(grid, boundary, obstacles=None):
    '''
    fill the grid with true and false
    '''
    for i in range(len(boundary)):
        startx, starty = boundary[i]
        endx, endy = boundary[(i + 1) % len(boundary)]
        diff = (endx - startx) // abs(endx - startx)
        for j in range(startx, endx + diff, diff):
            grid[j][starty + int((endy - starty) / (endx - startx) * (j - startx))] = False;
    
    for x in range(len(grid)):
        fillstart, fillend = -1, -1;
        for y in range(len(grid[x])):
            if not grid[x][y]:
                if fillstart == -1:
                    fillstart = y
                else:
                    fillend = y
        if fillend == -1:
            fillend = fillstart
        for y in range(fillstart, fillend):
            grid[x][y] = False

    if(obstacles is None):
        return grid

    for i in obstacles:
        for x in range(i[0] - i[2], i[0] + i[2] + 1):
            k1 = -int(math.sqrt(i[3] * i[3] * (1 - (x - i[0]) * (x - i[0]) / i[2] / i[2]))) + i[1] - 1
            k2 = int(math.sqrt(i[3] * i[3] * (1 - (x - i[0]) * (x - i[0]) / i[2] / i[2]))) + i[1] + 1
            for y in range(k1, k2 + 1):
                grid[x][y] = True;
    return grid
            

def scaleBoundary():
    '''
    Returns a list of scaled boundary coordinates and a function convert(coordinates, type_to_convert_to)
    to convert to and from the scaled boundary coordinates
    '''
    boundaryPoints = getMissionData(getCookie())[0]['fly_zones'][0]['boundary_pts']
    scaledCoordinates, coordinates, xcoords, ycoords = [], [], [], []
    for i in boundaryPoints:
        coordinates.append((i['longitude'] * (1e5), i['latitude'] * (1e5)))
        xcoords.append(i['longitude'] * (1e5))
        ycoords.append(i['latitude'] * (1e5))
    xmin, ymin = min(xcoords), min(ycoords)
    for i in coordinates:
        scaledCoordinates.append((int(i[0] - xmin), int(i[1] - ymin)))
    
    def convert(coordinates, type_to_convert_to):
        if type_to_convert_to == 'scaled':
            #converts (latitude, longitude) to scaled coordinates
            return (int(coordinates[1] * (1e5) - xmin), int(coordinates[0] * (1e5) - ymin))
        else:
            #converts scaled coordinates = (latitude, longitude)
            return (coordinates[1] / (1e5) + ymin, coordinates[0] / (1e5) + xmin)
    return scaledCoordinates, convert

def scaleObstacles(convert):
    obstacles = getObstacles()
    scaledObstacles = []
    for i in obstacles:
        a = convert((i[0], i[1]), 'scaled')
        scaledObstacles.append((a[0], a[1], i[2]/2.882, i[2]/3.64, i[3]))
    return scaledObstacles
    

def createGrid():
    '''
    creates a grid[x][y] with true if there is a boundary or an obstacle and false otherwise
    returns the grid with a conversion function to convert latitude/longitude to scaled coordinates and vice versa
    '''
    boundaryPoints, convert = scaleBoundary()
    xsize = max([i[0] for i in boundaryPoints]) + 100  #adding the extra constant value at the end acts as a buffer 
    ysize = max([i[1] for i in boundaryPoints]) + 100
    grid = [[False for i in range(ysize)] for j in range(xsize)]
    return fillGrid(grid, boundaryPoints), convert

'''grid, convert = createGrid()
for i in range(len(grid)):
    for j in range(len(grid[0])):
        print('*' if grid[i][j] else '-', end=' ')
    print(" ")
'''
grid = [[True for i in range(50)] for j in range(50)]
grid = fillGrid(grid, [(1, 2), (25, 40), (48, 2)], [(20, 20, 6, 6, 5), (30, 8, 3, 3, 300)])
for i in range(len(grid[0]) - 1, 0, -1):
    for j in range(len(grid)):
        print('*' if grid[j][i] else '-', end=' ')
    print(" ")
print(" ")
a = WayPointsProblem(grid, (10, 10), (25, 40))
print(smooth(aStarSearch(a)[0], a))
