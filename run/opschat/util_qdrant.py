import os
from qdrant_client.models import VectorParams, Distance, PointStruct
from qdrant_client import QdrantClient, models
import uuid
from openai import OpenAI

from util_embeddings import EmbeddingsUtil

class QdrantUtil:
    embedding_model = os.getenv("EMBEDDING_MODEL")

    def __init__(self):
        # Setup Qdrant
        qdrant_url = os.getenv('QDRANT_URL')
        self.client = QdrantClient(url=qdrant_url)

        # Setup embeddings
        self.embeddings_util = EmbeddingsUtil(self.embedding_model)


    def open_collection(self, collection_name, create_if_not_exists=False):
        self.collection_name = collection_name
        if create_if_not_exists:
            if self.client.collection_exists(collection_name) is None:
                self.create_collection(collection_name)


    def create_collection(self, collection_name):
        self.collection_name = collection_name
        self.client.recreate_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                #size=1536,
                size=384,
                distance=Distance.COSINE,
            )
        )

    
    def delete_collection(self, collection_name):
        self.client.delete_collection(collection_name)


    def list_collections(self):
        return self.client.get_collections()


    def upsert_data(self, data: list[dict], field_name_for_embeddings: str):
        # Get the embeddings
        messages = []
        for item in data:
            message = item.get(field_name_for_embeddings)
            messages.append(message)
        embeddings = self.embeddings_util.get(messages)

        # Build the points array and push it
        points = []
        i = 0
        for item in data:
            text_vector = embeddings[i]
            i = i + 1
            item.pop(field_name_for_embeddings)
            text_id = str(uuid.uuid4())
            point = PointStruct(id=text_id, vector=text_vector, payload=item)
            points.append(point)
            if len(points) % 100 == 0:
                self.put_data(points)
                points.clear()

        if len(points) > 0:
            self.put_data(points)


    def put_data(self, points):
        print("writing " + str(len(points)) + " records")
        operation_info = self.client.upsert(
            collection_name=self.collection_name,
            wait=False,
            points=points)
    

    def query_data(self, collection_name, prompt, intent, begin_date=None, end_date=None):
        limit = 100
        embeddings = self.embeddings_util.get(prompt.lower())
        query_filter = self.__get_query_filter(intent, begin_date, end_date)

        if query_filter is not None:
            results = self.client.search(
                collection_name,
                limit=limit,
                query_vector=embeddings[0],
                with_payload=True,
                query_filter=query_filter
            )
        else:
            results = self.client.search(
                collection_name,
                limit=limit,
                query_vector=embeddings[0],
                with_payload=True
            )

        data = [' '.join(str(val) for val in result.payload.values()) for result in results]
        return data
        

    def __get_query_filter(self, intent, begin_date, end_date):
        query_filter = None
        key, value = self.__getKeyValue(intent)

        if begin_date is not None:
            if key is not None:
                query_filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key=key,
                            match=models.MatchValue(value=value),
                        ),
                        models.FieldCondition(
                            key="timestamp",
                            range=models.DatetimeRange(
                                gt=begin_date,
                                gte=None,
                                lt=None,
                                lte=end_date
                            )
                        )
                    ]
                )
            else:
                query_filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="timestamp",
                            range=models.DatetimeRange(
                                gte=begin_date,
                                lte=end_date
                            )
                        )
                    ]
                )
        elif key is not None:
            query_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key=key,
                        match=models.MatchValue(value=value),
                    )
                ]
            )

        return query_filter
    

    def __getKeyValue(self, intent):
        if intent is not None:
            items = intent.items()
            for key, value in items:
                return str(key), str(value)
        else:
            return None, None


    def __get_begin_end_timestamps(self, timestamp):
        begin_date = timestamp.get("begin_date")
        if begin_date is not None:
            begin = begin_date
        else:
            begin = None

        end_date = timestamp.get("end_date")
        if end_date is not None:
            end = end_date
        else:
            end = None

        return begin, end

    