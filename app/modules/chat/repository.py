class ChatRepository:
    def __init__(self,db):
        self.collection = db.conversations