from kivy.animation import Animation
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.graphics import *

class MyButton(Button):
    pass

class Example(Widget):
    def animate(self, instance):
        self.rotate(instance)
        animation = Animation(pos=(instance.x+100,instance.y+100), t='linear')
        animation.start(instance)

    def rotate(self, instance):
        instance.angle += 90

class rotationApp(App):
    def build(self):
        e = Example()
        return e


if __name__ == '__main__':
    rotationApp().run()