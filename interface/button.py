
from components.interactable_component import Interactable
from engine import Engine
from enums import color
from tcod.console import Console
from tcod import libtcodpy

class Button:
    
    def __init__(self,x,y,title :str,width=7,height=3,fg =color.button_color,bg = color.black,hover=color.button_hover, decoration="╔═╗║ ║╚═╝", on_click = None) -> None:
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.fg = fg
        self.bg = bg
        self.hover = hover
        self.title = title
        self.decoration = decoration
        self.on_click = on_click
        
    def render(self, console: Console, engine : Engine):
        
        fg = self.fg
        if self.hovering(engine):
            fg = self.hover
        console.draw_frame(self.x,self.y,self.width,self.height,fg=fg,bg= self.bg,decoration=self.decoration)

        console.print(x= self.x+ self.width//2, y= self.y + self.height//2,string=self.title,fg=fg, alignment=libtcodpy.CENTER)
        
        
    def hovering(self,engine: Engine)-> bool:
        x,y = engine.map_to_camera_coordinates(*engine.mouse_location)
        
        if (x > self.x + self.width or
            x < self.x or 
            y > self.y + self.height or 
            y < self.y) :
            return False

        return True