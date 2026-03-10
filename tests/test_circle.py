from src.Circle import Circle
import pytest
import math

@pytest.fixture
def get_circle_data():
    radius, area, perimeter = 5, 78.5 , 31.4

    radius -=4.5
    area = 0.8
    perimeter = 3.1

    yield radius, area, perimeter

    radius = 5
    area = 78.5
    perimeter = 31.4



def test_circle(get_circle_data):
    radius, area, perimeter = get_circle_data

    S = Circle(radius)
    assert round(S.area, 1) == area, f'Площадь круга с радиусом {radius} равна заданной'
    assert round(S.perimeter,1) == perimeter, f'Периметр круга с радиусом {radius} равен заданному'
