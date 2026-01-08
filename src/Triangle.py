
import math


class Triangle():
    def __init__(self, side_a, side_b, side_c):
        if side_c+side_a < side_b or side_c+side_b < side_a or side_a+side_b < side_c:
            raise ValueError ("Составить треугольник из таких сторон невозможно")
        self.side_a = side_a
        self.side_b = side_b
        self.side_c = side_c

    def perimeter(self):
        return self.side_a+self.side_b+self.side_c

    def area(self):
        s = self.perimeter()/2
        return math.sqrt(s*(s-self.side_a)*(s-self.side_b)*(s-self.side_c))

r = Triangle(2, 3, 4)
