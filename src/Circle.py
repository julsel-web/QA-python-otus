import math

from src.Figure import Figure


class Circle(Figure):
    def __init__(self, radius):
        if radius < 0:
            raise ValueError("Радиус не может быть отрицательным")
        self.radius = radius
        self.center = (0, 0)

    @property
    def area(self):
        return math.pi * (self.radius ** 2)
    @property
    def perimeter(self):
        return 2 * math.pi * self.radius
