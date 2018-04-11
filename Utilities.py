import math
import os
from kivy.uix.image import Image
from kivy.uix.widget import Widget

import Map
import Wall


def imgLoad(source, pos=(0, 0)):
    '''Load an image via a kivy Image layout. By default does not size the widget containing the image.
    img = filepath to image
    Returns: Image instance which includes size (w/h) data via .size'''
    file = os.path.join(source)
    image = Image(source=file, pos=pos)
    return image


def createRect(*args, **kwargs):
    '''
    :param args: x,y,w,h or a tuple or list (or kivy object) (x,y) and (w,h)
    :param instance: usually "self", or the instance being used in the function
    :return: tuple (x,y,w,h). If a class instance is passed in then it is updated with this data
    '''
    instance = None
    if kwargs:
        instance = kwargs['instance']

    if 'tuple' in str(type(args[0])) or 'List' in str(type(args[0])):
        x = int(args[0][0])
        y = int(args[0][1])
    else:
        x = int(args[0])
        y = int(args[1])

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
        instance.rect_centerx = int(instance.rect_x + (instance.rect_w / 2))
        instance.rect_centery = int(instance.rect_y + (instance.rect_h / 2))

    # print ("creating rect:", x,y,w,h)
    return (x, y, w, h)


class container(Widget):
    """Containers hold widgets of a specific type for ease of access later"""
    def __init__(self, **kwargs):
        super(container, self).__init__(**kwargs)
        self.pos = (0, 0)
        self.size = (0, 0)


def roundPoint(point):
    '''Takes the location of a touch/mouse event and rounds it to match the game grid (bottom left corner)
    Point = mouse position point (x,y)'''
    x = Map.mapvar.squsize * int(point[0] / Map.mapvar.squsize)
    y = Map.mapvar.squsize * int(point[1] / Map.mapvar.squsize)
    return (x, y)


def roundRect(rect):
    '''Creates a rect based on grid location instead of mouse x,y location
    Rect = rect created based on mouse pos location'''
    roundpos = roundPoint(rect.pos)
    new = createRect(roundpos, rect.size)
    return new


def genWalls(pos, squarewidth, squareheight):
    '''Generating the Walls for the tower used in collision and path generation'''
    walls = []
    h = squareheight
    k = 0
    while h > 0:
        j = 0
        w = squarewidth
        while w > 0:
            wall = Wall.Wall(squpos=((pos[0] / Map.mapvar.squsize) + j, (pos[1] / Map.mapvar.squsize) + k))
            walls.append(wall)
            w -= 1
            j += 1
        k += 1
        h -= 1
    Map.myGrid.walls = Map.path.get_wall_list()
    for wall in walls:
        Map.myGrid.updateWalls(wall.squpos)
    return walls


def getPos(point):
    '''Returns the kivy pos (bottom left) of the square with a touchdown'''
    x = point[0]
    y = point[1]

    pos = [x - x % Map.mapvar.squsize, y - y % Map.mapvar.squsize]
    return pos


def get_rotation(obj, enemy):
    '''Rotates an image to face the enemy
    obj is an object to be rotated
    '''
    # distance between the image and the enemy. this is "A" and "B" in the arctan equation
    x = obj.image.center[0] - enemy.rect_centerx
    y = obj.image.center[1] - enemy.rect_centery
    # calculates the rotation of the image.
    rotation = math.degrees(math.atan2(y, x))
    return rotation


def in_range(tower, enemy):
    """Determines if an enemy is within the tower's defined range"""
    return (enemy.right > tower.center[0] - tower.range and enemy.pos[0] < tower.center[0] + tower.range) and \
           (enemy.top > tower.center[1] - tower.range and enemy.pos[1] < tower.center[1] + tower.range)

def get_all_in_range(tower, list, flyingOnly = False):
    results = []
    for x in list:
        if flyingOnly:
            if x.isair:
                if (x.right > tower.center[0] - tower.range and x.pos[0] < tower.center[0] + tower.range) and \
                        (x.top > tower.center[1] - tower.range and x.pos[1] < tower.center[1] + tower.range):
                    results.append(x)
        else:
            if (x.right > tower.center[0] - tower.range and x.pos[0] < tower.center[0] + tower.range) and \
            (x.top > tower.center[1] - tower.range and x.pos[1] < tower.center[1] + tower.range):
                results.append(x)
    return results


def get_pos(pos, h, w, num):

    if num == 0:
        return pos
    if num == 1:
        return (pos[0], pos[1] + 2 * h / 3)
    if num == 2:
        return (pos[0] + 2 * w / 3, pos[1] + 2 * h / 3)
    if num == 3:
        return (pos[0] + 2 * w / 3, pos[1])
    if num == 4:
        return (pos[0] + w / 3, pos[1] + h / 3)


def adjacentRoadPos(pos):
    """Creates a list of possible positions for a road around a tower. Used to change road color based on tower type"""
    list = []
    y = int(pos[1] + Map.mapvar.squsize * 2)
    x = int(pos[0] - Map.mapvar.squsize)
    list.append([x, y])

    while x <= pos[0] + Map.mapvar.squsize:
        x += Map.mapvar.squsize
        list.append([x, y])
    while y >= pos[1]:
        y -= Map.mapvar.squsize
        list.append([x, y])
    while x >= pos[0]:
        x -= Map.mapvar.squsize
        list.append([x, y])
    while y <= pos[1]:
        y += Map.mapvar.squsize
        list.append([x, y])
    return list

##Use this if the sprite comes in a single PNG
# def split_sheet(sheet, size, columns, rows):
#     '''Divide a loaded sprite sheet into subsurfaces.
#     Sheet = the sheet to load
#     Size = (w,h) of each frame
#     Columns and rows are the number of cells horizontally and vertically.'''
#     subsurfaces = []
#     for y in range(rows):
#         row = []
#         for x in range(columns):
#             rect = createRect((x * size[0], y * size[1]), size)
#             row.append(sheet.subsurface(rect))
#         subsurfaces.append(row)
#     return subsurfaces
