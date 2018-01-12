import pygame
import itertools
import os
from localdefs import imgLoad
import time

class Animate():

    def __init__(self, folder = None,spritesheet = None, startframe = 0, endframe = 1, row = 0, defaultrotation = 0):
        self.frames = list()
        self.folder = folder
        self.spritesheet = spritesheet
        #frame (picture) counting should start at zero.
        self.startframe = startframe
        self.endframe = endframe
        self.row = row
        self.defaultrotation = int(defaultrotation)
        self.frame_dict = self.make_dict()
        self.animate_timer = 0
        self.animate_fps = 12
        self.old_direction = "right"
        self.redraw = True
        self.moveframes = None
        self.adjust_images("right")


    def make_dict(self):
        '''Make a dict of frames to be used for animation'''
        if self.spritesheet == None:
            for dirpath, dirnames, files in os.walk(self.folder, topdown=True):
                i=0
                j=0
                for img in files:
                    filepath = os.path.join(dirpath,img)
                    image = imgLoad(filepath)
                    self.frames.append(image)
                    j += 1
                #print self.frame_dict
                if i== 0:
                    break
        else:
            ##assumes row 0 contains walking sprites. Frame counting should start at 0
            self.frames = self.spritesheet[self.row][self.startframe:self.endframe+1]
            if self.defaultrotation != 0:
                self.frames = [pygame.transform.rotate(frame, self.defaultrotation) for frame in self.frames]

        flips = [pygame.transform.flip(frame, True, False) for frame in self.frames]
        up = [pygame.transform.rotate(frame,90) for frame in self.frames]
        down = [pygame.transform.rotate(frame,-90) for frame in self.frames]
        move_cycles = {"right": itertools.cycle(self.frames[0:3]),
                       "left": itertools.cycle(flips[0:3]),
                       "up": itertools.cycle(up[0:3]),
                       "down": itertools.cycle(down[0:3])}
        return move_cycles


    def adjust_images(self,direction):
        '''
        Update the sprite's walkframes as the sprite's direction changes.
        '''
        if direction == "right" and self.old_direction != "right":
            self.moveframes = self.frame_dict["right"]
            self.redraw = True
        elif direction == "left" and self.old_direction != "left":
            self.moveframes = self.frame_dict["left"]
            self.redraw = True
        elif direction == "up" and self.old_direction != "up":
            self.moveframes = self.frame_dict["up"]
            self.redraw = True
        elif direction == "down" and self.old_direction != "down":
            self.moveframes = self.frame_dict["down"]
            self.redraw = True
        elif self.moveframes == None:
            self.moveframes = self.frame_dict["right"]
        self.old_direction = direction
        return self.make_image()


    def make_image(self):
        '''
        Update the sprite's animation as needed.
        '''
        elapsed = time.time() - self.animate_timer > 1.0 / self.animate_fps
        if self.redraw or elapsed:
            #print(self.redraw, elapsed)
            self.image = next(self.moveframes)
            self.animate_timer = time.time()
        self.redraw = False

        return self.image