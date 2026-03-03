class UserService:
    def __init__(self,repo):
        self.repo = repo

    async def get_user(self,user_id):
      return await self.repo.get_user(user_id)