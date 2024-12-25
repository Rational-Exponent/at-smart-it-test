import uuid

class Session():
    session_id: str
    thread_id: str

    def __init__(self, session_id: str, thread_id: str):
        self.session_id = session_id
        self.thread_id = thread_id

    @staticmethod
    def new_session():
        return Session(str(uuid.uuid4()), str(uuid.uuid4()))
    
    def new_thread(self):
        return Session(self.session_id, str(uuid.uuid4()))
    
    def to_dict(self):
        return {
            "session_id": self.session_id,
            "thread_id": self.thread_id
        }