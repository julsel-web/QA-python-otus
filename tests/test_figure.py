import pytest
from src.Figure import Figure
from src.Square import Square

@pytest.fixture
def first_square():
    return Square(4)

@pytest.fixture
def second_square():
    return Square(10)

def test_add_area(first_square, second_square):
    assert first_square.add_area(second_square) == 116


def test_negative_area(first_square):
    with pytest.raises(ValueError, match="Была передана не геометрическая фигура"):
         first_square.add_area("Другая фигура")
