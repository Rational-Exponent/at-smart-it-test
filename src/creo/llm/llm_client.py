from abc import ABC, abstractmethod
import functools
import json

from ..data import DataModel
from ..data.types import (
    InputType,
    OutputType
)
from ..session import Session

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LLMClient(ABC):
    def __init__(self, data_model: DataModel=None, session: Session=None):
        self.data = data_model
        self.session = session
        

    def log_completion(func):
        @functools.wraps(func)
        def wrapper(self: LLMClient, input_message: str, model_name: str = None) -> str:
            logger.info(f">>>> Requesting completion for model: {model_name}")
            try:
                if self.data is not None:
                    # Log Input
                    if type(input_message) is not str:
                        input_str = json.dumps(input_message)
                    else:
                        input_str = input_message

                    self.data.input.add_input(InputType(
                        self.session.session_id,
                        self.session.thread_id,
                        input_str
                    ))

                response = func(self, input_message, model_name)

                if self.data is not None:
                    # Log Output
                    self.data.output.add_output(OutputType(
                        self.session.session_id,
                        self.session.thread_id,
                        response
                    ))
                
                logger.info(f">>>> Completion successful for model: {model_name}")
                return response
            except Exception as e:
                logger.error(f">>>> Error getting completion: {str(e)}")
                raise
        return wrapper
    
    @abstractmethod
    def get_chat_completion(self, input_message: str, model_name: str=None) -> str:
        pass
        