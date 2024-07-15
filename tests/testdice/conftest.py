import pytest
from dice.dice import expression

@pytest.fixture(scope="module")
def expr():
    return expression 

@pytest.fixture
def normal_single_number():
    return "6"

@pytest.fixture
def normal_single_calc():
    return "4+2*3"

@pytest.fixture
def normal_single_dice():
    return "3d6"

@pytest.fixture
def normal_braket_dice():
    return "3d(1d6)"

@pytest.fixture
def normal_combine_dice():
    return "3n2d6"

@pytest.fixture
def normal_minmum_dice():
    return "1d(10, 20)"

@pytest.fixture
def normal_max_kn_dice():
    return "3d6k2"

@pytest.fixture
def normal_min_kn_dice():
    return "3d6l2"

@pytest.fixture
def normal_gt_dice():
    return "1d6 > 0"

@pytest.fixture
def normal_lt_dice():
    return "1d6 < 0"

@pytest.fixture
def normal_ge_dice():
    return "1d6 >= 1"

@pytest.fixture
def normal_le_dice():
    return "1d6 <= 1"

@pytest.fixture
def normal_eq_dice():
    return "1d(6, 6) == 6"

@pytest.fixture
def normal_ne_dice():
    return "1d6 != 0"

@pytest.fixture
def normal_complex_dice():
    return "(5d6)n(2n((((2*3)d6 > 3)l3)d6))"
