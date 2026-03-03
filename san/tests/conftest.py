from unittest.mock import MagicMock, patch

import pytest

from san.api_config import ApiConfig
from san.tests.utils import TestResponse


@pytest.fixture(autouse=True)
def _disable_retries():
    """Disable retries in all tests to avoid delays and simplify mocking."""
    original = ApiConfig.max_retries
    ApiConfig.max_retries = 0
    yield
    ApiConfig.max_retries = original


@pytest.fixture
def test_response():
    def _create_test_response(**kwargs):
        response = TestResponse()
        response.setup(**kwargs)
        return response

    return _create_test_response


@pytest.fixture
def mock_gql_post():
    """Provide a mock for the sync HTTP client's .post() method."""
    with patch("san.graphql._get_sync_client") as mock_fn:
        mock_client = MagicMock()
        mock_fn.return_value = mock_client
        yield mock_client.post
