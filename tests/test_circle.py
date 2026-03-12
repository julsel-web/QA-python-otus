from src.Circle import Circle
import pytest
import math

@pytest.mark.parametrize(
    'radius, area, perimeter',
    [
        pytest.param(5, 78.5 , 31.4)
    ]
)
def test_positive_circle(radius, area, perimeter):

    S = Circle(radius)
    assert round(S.area, 1) == area, f'Площадь круга с радиусом {radius} равна заданной'
    assert round(S.perimeter,1) == perimeter, f'Периметр круга с радиусом {radius} равен заданному'


@pytest.mark.parametrize(
    'radius',
    [
        -10,
        -1,
        -0.1
    ]
)
def test_negative_circle(radius):
    with pytest.raises(ValueError, match="Радиус не может быть отрицательным"):
        Circle(radius)