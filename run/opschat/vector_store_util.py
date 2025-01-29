import os
import requests

class VectorStoreUtil:
    def __init__(self):
        self.host = os.getenv('VS_SERVICE_HOST') or 'localhost:6333'
        self.vector_store = os.getenv('VS_NAME') or 'qdrant'
        self.collection_name = os.getenv('VS_COLLECTION') or 'opschat_data'


    def query_data(self, prompt, intent):
        data = {
            'prompt': f'{prompt}',
            'intent': intent,
        }
        response = requests.post(
            url=self.host+'/collection/query/' + self.vector_store + '/' + self.collection_name, 
            json=data
        )
        response.raise_for_status()
        response_data = response.json()
        return response_data