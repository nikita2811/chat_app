
class UserRepository:
    def __init__(self,db):
        self.collection = db.users
    

    
    
    async def recommendations(self,current_user):
        user_id = current_user.id

