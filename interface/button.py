

from engine import Engine
from enums import color
from tcod.console import Console
from tcod import libtcodpy
from enums import color as color
class Button:
    
    
    def __init__(self,x,y,title :str,width=7,height=3,disabled=False,fg =color.button_color,text_color = color.button_text,bg = color.black,hover=color.button_hover, disabled_color = color.button_grey, decoration="╔═╗║ ║╚═╝", on_click = None,framed=True,underscore = False) -> None:
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.fg = fg
        self.text_color = text_color
        self.bg = bg
        self.hover = hover
        self.title = title
        self.decoration = decoration
        self.on_click = on_click
        self.disabled = disabled
        self.disabled_color = disabled_color
        self.framed = framed
        self.underscore = underscore
    def render(self, console: Console, engine : Engine):
        
        
        # self.fg = self.text_color
        if self.disabled:
            self.fg = self.disabled_color
            
        if self.framed:
            console.draw_frame(self.x,self.y,self.width,self.height,fg=self.fg,bg= self.bg,decoration=self.decoration)

        console.print(x= self.x+ self.width//2, y= self.y + self.height//2,string=self.title,fg=self.fg, alignment=libtcodpy.CENTER)
        if self.underscore:
            console.print(x= self.x+ self.width//2, y= self.y + self.height//2+1,string='─────',fg=color.interface_lowlight, alignment=libtcodpy.CENTER)
       
        
    def hovering(self,engine: Engine)-> bool:
        x,y = engine.map_to_camera_coordinates(*engine.mouse_location)
        
        if (x > self.x + self.width or
            x < self.x or 
            y > self.y + self.height or 
            y < self.y) :
            return False

        return True