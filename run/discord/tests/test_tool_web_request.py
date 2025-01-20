import asyncio
import pytest
import sys, os

# Add the src directory to the system path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from tool_web_request import make_web_request

@pytest.fixture
def test_data():
    return {
        "url": "http://example.com",
        "method": "GET",
        "body": "",
        "headers": {}
    }

@pytest.mark.asyncio
async def test_make_web_request(test_data):
    response = await make_web_request(
        test_data["url"],
        test_data["method"],
        test_data["body"],
        test_data["headers"]
    )

    # Verify the response structure
    assert "url" in response
    assert "method" in response
    assert "result" in response

    # Verify the response content
    assert response["url"] == test_data["url"]
    assert response["method"] == test_data["method"]
    assert isinstance(response["result"], list)


