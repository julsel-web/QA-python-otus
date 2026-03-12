import pytest
from src.Rectangle import Rectangle
from src.Square import Square

@pytest.mark.parametrize(
    'side_a, area, perimeter',
    [
        pytest.param(5,25,10, id= 'Для квадрата'),
    ]
)
def test_square(side_a, area, perimeter):
    r = Square(side_a)
    assert r.perimeter == perimeter, f'Периметр равен заданному'
    assert r.area == area, f'Площадь равена заданной'



@pytest.mark.parametrize(
    'side_a, side_b, area, perimeter',
    [
        pytest.param(5,3,15,8, id= 'Для прямоугольника')
    ]
)
def test_rectangle(side_a,side_b, area, perimeter):
    r = Rectangle(side_a, side_b)
    assert r.perimeter == perimeter, f'Периметр равен заданному'
    assert r.area == area, f'Площадь равена заданной'



@pytest.mark.parametrize('figure, params',
                        [
                            pytest.param(Square, (-5,), id= 'Для квадрата'),
                            pytest.param(Rectangle, (5, -3), id= 'Для прямоугольника'),
                        ]
                         )

def test_negative_square_rectangle(figure, params):
    with pytest.raises(ValueError, match="Стороны прямоугольника не могут быть меньше 0. "
                             "Введите положительное значение"):
        figure(*params)


