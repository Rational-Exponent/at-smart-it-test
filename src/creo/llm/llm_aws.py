import json
import os
import boto3
from dotenv import load_dotenv
load_dotenv()

from .llm_client import LLMClient
from ..data import DataModel
from ..session import Session


class LLMClientBedrock(LLMClient):
    def __init__(self, data_model: DataModel=None, session: Session=None):
        super().__init__(data_model, session)
        aws_session = boto3.Session(
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            aws_session_token=os.getenv('AWS_SESSION_TOKEN'),
            region_name=os.getenv('AWS_REGION')
        )
        self.client = aws_session.client('bedrock-runtime')

    def get_request(self, message):
        return {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 5000,
            "temperature": 0.1,
            "messages": [{"role":"user", "content": [{"type": "text", "text": message}]}]
        }

    @LLMClient.log_completion
    def get_chat_completion(self, input_message: str, model_name: str = None) -> str:
        request = json.dumps(self.get_request(input_message))
        response = self.client.invoke_model(modelId='anthropic.claude-v2:1', body=request)
        model_response = json.loads(response["body"].read())
        return model_response["content"][0]["text"]
