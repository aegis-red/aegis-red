import pytest

from aegis_red.runtime import set_sut_override


@pytest.fixture(autouse=True)
def reset_sut_override():
    set_sut_override({})
    yield
    set_sut_override({})
