from abc import ABC

from src.Figure import Figure


class Rectangle(Figure, ABC):
    def __init (self, side_a, side_b):
        if side_a <=0 or side_b <= 0:
            raise ValueError("Стороны прямоугольника не могут быть меньше 0. "
                             "Введите положительное значение")
        self.side_a = side_a
        self.side_b = side_b

    def area(self):
        return self.side_a * self.side_b

    def perimeter(self):
        return self.side_a + self.side_b
