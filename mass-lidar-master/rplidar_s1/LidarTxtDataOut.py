import math
from shapely.geometry import Point, Polygon
import matplotlib.pyplot as plt


def CalculatePoints(radius):
    x = radius * math.cos(angleOfMeasurement)
    y = radius * math.sin(angleOfMeasurement)
    return Point(x, y)


name = "out.txt"
with open(name, "r") as textFile:
    fileString = textFile.read()

fileString = fileString.replace("[", "")
fileString = fileString.replace("]", "")
radiusString = fileString.split(',')
angleOfMeasurement = -3.1415927410125732
increseOfMeasurementAngle = 0.004893446806818247
pointList = []
listCount = 0
lastRadius = 0

plt.xlim(-40, 40)
plt.ylim(-40, 40)

for radius in radiusString:
    if (radius.__contains__("inf")):
        radius = 40
    p1 = CalculatePoints(float(radius))
    if (listCount > 0):
        distanceBetweenPoints = math.fabs(float(radius) - float(lastRadius))
    else:
        distanceBetweenPoints = 0

    if (distanceBetweenPoints < 3 and float(radius) < 40):
        if (listCount == 0):
            pointList.append(CalculatePoints(float(radius) + 2))
        listCount += 1
        pointList.append(p1)
    else:
        pointList.append(CalculatePoints(float(lastRadius) + 2))
        if (listCount > 5):
            fig = Polygon([[p.x, p.y] for p in pointList])
            xPoly, yPoly = fig.exterior.coords.xy
            plt.plot(xPoly, yPoly)
        listCount = 0
        pointList.clear()
    lastRadius = radius
    angleOfMeasurement += increseOfMeasurementAngle
plt.show()
textFile.close()
