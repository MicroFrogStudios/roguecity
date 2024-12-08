import random
from typing import Iterator, Tuple
import tcod




class RectangularRoom:
    def __init__(self, x: int, y: int, width: int, height: int):
        self.x1 = x
        self.y1 = y
        self.x2 = x + width
        self.y2 = y + height
        
    @property
    def center(self) -> Tuple[int, int]:
        center_x = int((self.x1 + self.x2) / 2)
        center_y = int((self.y1 + self.y2) / 2)

        return center_x, center_y

    @property
    def height(self) -> int:
        return self.y2 - self.y1
    
    @property
    def width(self) -> int:
        return self.x2 - self.x1
    @property
    def area(self) -> int:
        return self.height*self.width
    @property
    def inner(self) -> Tuple[slice, slice]:
        """Return the inner area of this room as a 2D array index."""
        return slice(self.x1 + 1, self.x2), slice(self.y1 + 1, self.y2)

    def intersects(self, other: 'RectangularRoom') -> bool:
        """Return True if this room overlaps with another RectangularRoom."""
        return (
            self.x1 < other.x2
            and self.x2 > other.x1
            and self.y1 < other.y2
            and self.y2 > other.y1
        ) 
    
    def touchMiddlePoint(self,other: 'RectangularRoom')-> Tuple[int, int]:
        inner_x1 = max(self.x1,other.x1)
        inner_x2 = min(self.x2,other.x2)
        inner_y1 = max(self.y1,other.y1)
        inner_y2 = min(self.y2,other.y2)

        if self.x1 == other.x2 and self.y1 < other.y2 and other.y1 < self.y2:
            return (self.x1,(inner_y1 + inner_y2)//2)
        if self.x2 == other.x1 and self.y1 < other.y2 and other.y1 < self.y2:
            return (self.x2,(inner_y1 + inner_y2)//2)
        if self.y1 == other.y2 and self.x1 < other.x2 and other.x1 < self.x2:
            return ((inner_x1 + inner_x2)//2,self.y1)
        if self.y2 == other.y1 and self.x1 < other.x2 and other.x1 < self.x2: 
            return ((inner_x1 + inner_x2)//2,self.y2)
        
        return None

    def touching(self,other: 'RectangularRoom') -> bool:
        return self.touchMiddlePoint(other) is not None
    
    def roomFromCenter(center:'Point',height,width):
        return RectangularRoom(center.x-width//2,center.y-height//2,width,height)

    def adjacentRoomFromCenter(self,center:'Point',min_dimension:int):
        
        if center.y < self.y1:
            if center.x < self.x2 and center.x > self.x1:
                width = min_dimension
            else:
                width = max(min_dimension,abs(self.center[0] - center.x)*2)
            return RectangularRoom.roomFromCenter(center,(self.y1-center.y)*2,width)
        elif center.y > self.y2:
            if center.x < self.x2 and center.x > self.x1:
                width = min_dimension
            else:
             width = max(min_dimension,abs(self.center[0] - center.x)*2)
            return RectangularRoom.roomFromCenter(center,(center.y - self.y2)*2,width)
        elif center.x > self.x2:
            if center.y < self.y2 and center.y > self.y1:
                height = min_dimension
            else:
                height = max(min_dimension,abs(self.center[1] - center.y)*2)
            return RectangularRoom.roomFromCenter(center,height,(center.x - self.x2)*2)
        elif center.x < self.x1:
            if center.y < self.y2 and center.y > self.y1:
                height = min_dimension
            else:
                height = max(min_dimension,abs(self.center[1] - center.y)*2)
            return RectangularRoom.roomFromCenter(center,height,(self.x1-center.x)*2)

    def connectRooms(self,other: 'RectangularRoom') -> 'RectangularRoom':
        
        return RectangularRoom

def tunnel_between(
    start: Tuple[int, int], end: Tuple[int, int]
) -> Iterator[Tuple[int, int]]:
    """Return an L-shaped tunnel between these two points."""
    x1, y1 = start
    x2, y2 = end
    if random.random() < 0.5:  # 50% chance.
        # Move horizontally, then vertically.
        corner_x, corner_y = x2, y1
    else:
        # Move vertically, then horizontally.
        corner_x, corner_y = x1, y2

    # Generate the coordinates for this tunnel.
    for x, y in tcod.los.bresenham((x1, y1), (corner_x, corner_y)).tolist():
        yield x, y
    for x, y in tcod.los.bresenham((corner_x, corner_y), (x2, y2)).tolist():
        yield x, y


class Point:

    def __init__(self,x,y):
        self.x = x
        self.y = y

    def sqDistanceTo(self,p:'Point') -> float:
        return (p.x - self.x)**2 + (p.y - self.y)**2
    
    def nearestToSelf(self,points:list['Point']):
        i_nearest = 0
        p_nearest = points[0]
        for i,p in enumerate(points):
            if p.sqDistanceTo(self) < p_nearest.sqDistanceTo(self):
                i_nearest = i
                p_nearest = p
        
        return i_nearest
    
    def inside(self,room:RectangularRoom) -> bool:
        return self.x >= room.x1 and self.x <= room.x2 and self.y >= room.y1 and self.y <= room.y2