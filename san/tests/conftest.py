import pytest
from san.tests.utils import TestResponse


@pytest.fixture
def test_response():
    def _create_test_response(**kwargs):
        response = TestResponse()
        response.setup(**kwargs)
        return response

    return _create_test_response
