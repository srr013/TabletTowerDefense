import random
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.scatterlayout import ScatterLayout

class MyButton(Button):
    pass

class Example(ScatterLayout):
    def __init__(self):
        super(Example, self).__init__()
        self.pos = (0,0)
        self.size = (200,200)


    def runProgram(self):
        image1 = MyImage()
        self.add_widget(image1)
        image1.flip()
        image2 = MyImage()
        self.add_widget(image2)
        print image1.texture, image2.texture


class MyImage(Image):
    def __init__(self):
        super(MyImage, self).__init__()
        self.source = 'data/icons/next.png'
        self.pos = (random.randint(0,200), random.randint(0, 200))

    def flip(self):
        self.texture.flip_horizontal()

class horizontal_flipApp(App):
    def build(self):
        e = Example()
        return e


if __name__ == '__main__':
    horizontal_flipApp().run()