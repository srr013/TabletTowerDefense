from kivy.uix.image import Image
from kivy.uix.widget import Widget

import os
import math
import Map

def imgLoad(source, pos=(0,0)):
    '''Load an image via a kivy Image layout. By default does not size the widget containing the image.
    img = filepath to image
    Returns: Image instance which includes size (w/h) data via .size'''
    file = os.path.join(source)
    image = Image(source=file, pos=pos)
    return image

def createRect(*args, instance=None):
    '''
    :param args: x,y,w,h or a tuple or list (or kivy object) (x,y) and (w,h)
    :param instance: usually "self", or the instance being used in the function
    :return: tuple (x,y,w,h). If a class instance is passed in then it is updated with this data
    '''
    if 'tuple' in str(type(args[0])) or 'List' in str(type(args[0])):
        x = int(args[0][0])
        y = int(args[0][1])
    else:
        x=int(args[0])
        y=int(args[1])

    if 'tuple' in str(type(args[1])) or 'List' in str(type(args[1])):
        w = int(args[1][0])
        h = int(args[1][1])
    else:
        w = int(args[2])
        h = int(args[3])

    if instance:
        instance.rect_x = x
        instance.rect_y = y
        instance.rect_h = h
        instance.rect_w = w
        instance.rect_centerx = int(instance.rect_x+(instance.rect_w/2))
        instance.rect_centery = int(instance.rect_y+(instance.rect_h/2))

    #print ("creating rect:", x,y,w,h)
    return (x,y,w,h)

class container(Widget):
    def __init__(self,**kwargs):
        super(container, self).__init__(**kwargs)
        self.pos = (0,0)
        self.size = (0,0)

def roundPoint(point):
    '''Takes the location of a mouse event (click) and rounds it to match the game grid
    Point = mouse position point (x,y)'''
    x = Map.squsize*int(point[0]/Map.squsize)
    y = Map.squsize*int(point[1]/Map.squsize)
    return (x,y)

def roundRect(rect):
    '''Creates a rect based on grid location instead of mouse x,y location
    Rect = rect created based on mouse pos location'''
    roundpos = roundPoint(rect.pos)
    new = createRect(roundpos, rect.size)
    return new

def getPos(point):
    '''Returns the kivy pos (bottom left) of the square with a touchdown'''
    x = point[0]
    y = point[1]

    pos = [x - x%Map.squsize, y - y%Map.squsize]
    return pos

def get_rotation(obj, enemy):
    '''Rotates an image to face the enemy
    obj is an object to be rotated
    '''
    #distance between the image and the enemy. this is "A" and "B" in the arctan equation
    x = obj.image.pos[0] - enemy.rect_centerx
    y = obj.image.pos[1] - enemy.rect_centery
    #calculates the rotation of the image.
    rotation = math.degrees(math.atan2(y, x))
    return rotation

##Use this if the sprite comes in a single PNG
def split_sheet(sheet, size, columns, rows):
    '''Divide a loaded sprite sheet into subsurfaces.
    Sheet = the sheet to load
    Size = (w,h) of each frame
    Columns and rows are the number of cells horizontally and vertically.'''
    subsurfaces = []
    for y in range(rows):
        row = []
        for x in range(columns):
            rect = createRect((x * size[0], y * size[1]), size)
            row.append(sheet.subsurface(rect))
        subsurfaces.append(row)
    return subsurfaces