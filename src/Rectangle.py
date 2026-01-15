from src.Figure import Figure


class Rectangle(Figure):
    def __init__ (self, side_a, side_b):
        if side_a <=0 or side_b <= 0:
            raise ValueError("Стороны прямоугольника не могут быть меньше 0. "
                             "Введите положительное значение")
        self.side_a = side_a
        self.side_b = side_b

    @property
    def area(self):
        return self.side_a * self.side_b
    @property
    def perimeter(self):
        return self.side_a + self.side_b
