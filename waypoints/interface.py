import requests 
import math
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
    obstacles = requests.get(IP+"/api/obstacles", headers={'cookie': cookie}) 
    return obstacles.json()['stationary_obstacles']

def fillGrid(grid, boundary, obstacles):
    '''
    fill the grid with true and false
    '''
    for i in range(len(boundary)):
        startx, starty = boundary[i]
        endx, endy = boundary[(i + 1) % len(boundary)]
        diff = (endx - startx) // abs(endx - startx)
        for j in range(startx, endx + diff, diff):
            grid[j][starty + int((endy - starty) / (endx - startx) * (j - startx))] = True;
    
    for x in range(len(grid)):
        fillstart, fillend = -1, -1;
        for y in range(len(grid[x])):
            if grid[x][y]:
                if fillstart == -1:
                    fillstart = y
                else:
                    fillend = y
        if fillend == -1:
            fillend = fillstart
        for y in range(fillstart, fillend):
            grid[x][y] = True
    return grid
            

def scaleBoundary():
    '''
    Returns a list of scaled boundary coordinates and a function convert(coordinates, type_to_convert_to)
    to convert to and from the scaled boundary coordinates
    '''
    boundaryPoints = getMissionData(getCookie())[0]['fly_zones'][0]['boundary_pts']
    scaledCoordinates, coordinates, xcoords, ycoords = [], [], [], []
    for i in boundaryPoints:
        coordinates.append((i['longitude'] * (1e6), i['latitude'] * (1e6)))
        xcoords.append(i['longitude'] * (1e6))
        ycoords.append(i['latitude'] * (1e6))
    xmin, ymin = min(xcoords), min(ycoords)
    for i in coordinates:
        scaledCoordinates.append((int(i[0] - xmin), int(i[1] - ymin)))
    
    def convert(coordinates, type_to_convert_to):
        if type_to_convert_to == 'scaled':
            #converts (latitude, longitude) to scaled coordinates
            return (int(coordinates[1] * (1e6) - xmin), int(coordinates[0] * (1e6) - ymin))
        else:
            #converts scaled coordinates = (latitude, longitude)
            return (coordinates[1] / (1e6) + ymin, coordinates[0] / (1e6) + xmin)
    return scaledCoordinates, convert

def createGrid():
    '''
    creates a grid[x][y] with true if there is a boundary or an obstacle and false otherwise
    returns the grid with a conversion function to convert latitude/longitude to scaled coordinates and vice versa
    '''
    boundaryPoints, convert = scaleBoundary()
    xsize = max([i[0] for i in boundaryPoints]) + 100
    ysize = max([i[1] for i in boundaryPoints]) + 100
    grid = [[False for i in range(ysize)] for j in range(xsize)]
    return fillGrid(grid, boundaryPoints), convert

'''grid, convert = createGrid()
for i in range(len(grid)):
    for j in range(len(grid[0])):
        print('*' if grid[i][j] else '-', end=' ')
    print(" ")
'''
grid = [[False for i in range(10)] for j in range(10)]
grid = fillGrid(grid, [(1, 2), (4, 7), (8, 2)])
for i in range(len(grid[0]) - 1, 0, -1):
    for j in range(len(grid)):
        print('*' if grid[j][i] else '-', end=' ')
    print(" ")
