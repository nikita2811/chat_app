from bson import ObjectId
class UserRepository:
    def __init__(self,db):
        self.collection = db.users
    

    async def get_user(self,user_id):
        user = await self.collection.find_one({"_id":ObjectId(user_id)})
        print(user)
        user["_id"] = str(user["_id"])
        return user