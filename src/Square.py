from abc import ABC

from src.Rectangle import Rectangle


class Square(Rectangle, ABC):
    def __init__(self, side_a):
        if side_a <= 0:
            raise ValueError("Стороны прямоугольника не могут быть меньше 0. "
                             "Введите положительное значение")
        super().__init__(side_a, side_a)
