import os
from openai import OpenAI

from .llm_client import LLMClient
from ..data import DataModel
from ..session import Session

MODEL_NAME = "gpt-4o-mini"
#MODEL_NAME = "o1-mini"
#MODEL_NAME = "o1-preview"

class LLMClientOpenAI(LLMClient):
    def __init__(self, data_model: DataModel=None, session: Session=None):
        super().__init__(data_model, session)
        self.client =  self.client=OpenAI(
            api_key=os.environ.get("OPENAI_API_KEY"),
        )

    @LLMClient.log_completion
    def get_chat_completion(self, input_message: str, model_name: str = None) -> str:
        chat_completion = self.client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": input_message
                }
            ],
            model=model_name or MODEL_NAME,
        )
        return chat_completion.choices[0].message.content
