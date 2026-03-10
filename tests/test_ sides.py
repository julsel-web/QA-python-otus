import pytest
from src.Rectangle import Rectangle
from src.Triangle import Triangle
from src.Square import Square

@pytest.mark.parametrize(
    'side_a, side_b, side_c, area, perimeter',
    [
        pytest.param(5,5,0,25,10, id= 'Для квадрата'),
        pytest.param(5,3,0,15,8, id= 'Для прямоугольника'),
        pytest.param(5,6,10,11.4,21, id= 'Для треугольника'),


    ]
)
def test_triangle_square_rectangle(side_a, side_b, side_c, area, perimeter):
    if side_c == 0:
        if side_b == side_a:
            r = Square(side_a)
            assert r.perimeter == perimeter, f'Периметр равен заданному'
            assert r.area == area, f'Площадь равена заданной'
        else:
            r = Rectangle(side_a, side_b)
            assert r.perimeter == perimeter, f'Периметр равен заданному'
            assert r.area == area, f'Площадь равена заданной'
    else:
        r = Triangle(side_a, side_b, side_c)
        assert r.perimeter == perimeter, f'Периметр равен заданному'
        assert round(r.area, 1) == area, f'Площадь равена заданной'