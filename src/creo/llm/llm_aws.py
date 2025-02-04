import json
import os
import boto3
from typing import List

from dotenv import load_dotenv
load_dotenv()

from .llm_client import LLMClient
from ..data import DataModel
from ..session import Session


MODEL_NAME_DEFAULT = 'anthropic.claude-3-5-sonnet-20240620-v1:0'

class LLMClientBedrock(LLMClient):
    def __init__(self, data_model: DataModel=None, session: Session=None):
        super().__init__(data_model, session)
        aws_session = boto3.Session(
            #aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            #aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            #aws_session_token=os.getenv('AWS_SESSION_TOKEN'),
            region_name=os.getenv('AWS_REGION')
        )
        self.client = aws_session.client('bedrock-runtime')

    def get_request(self, messages):
        def format_message(message):
            if type(message) is dict:
                return {"role": message.get("role", "user"), "content": [{"type": "text", "text": message.get("content")}]}
            else:
                return {"role": "user", "content":  [{"type": "text", "text": message}]}

        message_list = []
        if type(messages) is list:
            message_list = [format_message(m) for m in messages]
        else:
            message_list = [format_message(messages)]

        return {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 5000,
            "temperature": 0.1,
            "messages": message_list
        }

    @LLMClient.log_completion
    def get_chat_completion(self, input_messages: str, model_name: str = None) -> str:
        request = json.dumps(self.get_request(input_messages))
        response = self.client.invoke_model(modelId=model_name or MODEL_NAME_DEFAULT, body=request)
        model_response = json.loads(response["body"].read())
        content = model_response["content"]
        if len(content)>0:
            return content[0]["text"]
        else:
            return "[no-output]"
