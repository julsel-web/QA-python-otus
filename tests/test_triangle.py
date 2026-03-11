from src.Triangle import Triangle
import pytest


@pytest.mark.parametrize(
        'side_a, side_b, side_c, area, perimeter',
        [
            pytest.param(5, 6, 10, 11.4, 21, id='Для треугольника')
        ]
    )
def test_triangle(side_a, side_b, side_c, area, perimeter):
    r = Triangle(side_a, side_b, side_c)
    assert r.perimeter == perimeter, f'Периметр равен заданному'
    assert round(r.area, 1) == area, f'Площадь равена заданной'

@pytest.mark.parametrize(
        'side_a, side_b, side_c',
        [
            pytest.param(5,-1,2),
            pytest.param(5,-6,1),
            pytest.param(-5,7,2),
        ]
    )
def test_minus_circle(side_a, side_b, side_c):
        with pytest.raises(ValueError, match="Стороны треугольника не могут быть меньше 0. "
                             "Введите положительное значение"):
            Triangle(side_a, side_b, side_c)


@pytest.mark.parametrize(
        'side_a, side_b, side_c',
        [
            pytest.param(5,1,2),
            pytest.param(5,3,1)
        ]
    )
def test_impossible_circle(side_a, side_b, side_c):
        with pytest.raises(ValueError, match="Составить треугольник из таких сторон невозможно"):
            Triangle(side_a, side_b, side_c)



