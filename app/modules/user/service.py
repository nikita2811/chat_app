class UserService:
    def __init__(self,repo):
        self.repo = repo

    
    
    async def recommendations(self,current_user):
       return await self.repo.recommendations(current_user)