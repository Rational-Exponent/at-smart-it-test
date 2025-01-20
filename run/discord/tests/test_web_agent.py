import asyncio
import pytest
from unittest.mock import patch
import sys, os
import uuid
import json

# Add the src directory to the system path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from discord_app import DiscordBotApp

def pack_message(content):
    return {
        "from_session": 
            {
                "session_id": uuid.uuid4(), 
                "thread_id": uuid.uuid4()
            }, 
        "from_queue": "MOCK_FROM_QUEUE", 
        "to_queue": "MOCK_TO_QUEUE", 
        "content": content
    }

def unpack_message(packed_messag_obj):
    message = packed_messag_obj.get("message")
    try:
        return json.loads(message)
    except:
        return message

@pytest.fixture
def test_query_data():
    return pack_message("Current weather conditions in New York City")

@pytest.fixture
def test_search_data():
    return pack_message("Current weather conditions in New York City")

@pytest.fixture
def test_request_data():
    return pack_message("Go to weather.com and give me the top news item")

g_process_main_output = None
async def mock_process_main_output(response):
    global g_process_main_output
    g_process_main_output = response

g_publish_message = None
async def mock_publish_message(message, queue_name):
    global g_publish_message
    g_publish_message = {
        "queue_name": queue_name,
        "message": message
    }

@pytest.mark.asyncio
async def test_web_agent_query(test_query_data):
    app = DiscordBotApp()
    app.web_agent.process_main_output = mock_process_main_output
    await app.web_agent.handle_main(queue_name="mock-data", message=test_query_data)
    response = g_process_main_output
    assert response
    assert type(response) == str
    assert "<search>" in response


@pytest.mark.asyncio
async def test_web_agent_url_request(test_request_data):
    app = DiscordBotApp()
    app.web_agent.process_main_output = mock_process_main_output
    await app.web_agent.handle_main(queue_name="mock-data", message=test_request_data)
    response = g_process_main_output
    assert "<request>" in response


@pytest.mark.asyncio
async def test_web_agent_search(test_search_data):
    app = DiscordBotApp()
    app.web_agent.publish_message = mock_publish_message
    await app.web_agent.handle_web_search(queue_name="mock-data", message=test_search_data)
    response = g_publish_message
    assert response
    assert response.get("queue_name") == app.web_agent.reply_queue
    message = json.loads(response.get("message"))
    assert message
    assert "query" in message
    assert "results" in message
    results = message.get("results")
    assert results
    assert type(results) == list

