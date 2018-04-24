import math

from kivy import Vector


class Ellipse():

    def __init__(self):
        self.startPoint = Vector(0, 0)
        self.endPoint = Vector(50, 0)
        self.height = 10
        self.t = 0
        self.pointList = []

    def getPointList(self):
        distCoords = Vector(self.endPoint - self.startPoint)
        distToTravel = max(distCoords[0] + distCoords[1])
        (x, y) = self.startPoint
        dx = distCoords[0] / distToTravel
        dy = distCoords[1] / distToTravel
        inflection = self.startPoint + (distCoords / 2)


        while self.t < distToTravel/2:
            self.pointList.append((x, y))
            x += dx + w
            y += dy + h
            self.t+=1


    def getCenter(self,start,end):
        Vector(end)
        Vector (start)

        # Find the center of the circle and the radius then tick through 180* worth of radians and store points along the way
    def circle(self, center, r, a):
        ''' a in radians, center is the center point of circle, r is radius'''
        destAngle = math.radians(180)

        #this will find the x,y per point
        x = cx + r * cos(a)
        y = cy + r * sin(a)
