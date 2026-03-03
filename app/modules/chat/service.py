import aiofiles
from fastapi.responses import FileResponse, StreamingResponse
import os
import uuid

class ChatService:
    def __init__(self,repo):
        self.repo =repo

    ALLOWED_SIGNATURES = {
    b"\x89PNG": "image/png",
    b"\xff\xd8\xff": "image/jpeg",
    b"%PDF": "pdf",                
    b"PK\x03\x04": "docx",
}
    
    async def create_conversation(self,data,current_user):
        if current_user not in data.user_ids:
            data.user_ids.append(current_user)

        return await self.repo.create_conversation(data)
    
    async def get_conversation(self,current_user):
        return await self.repo.get_conversation(current_user)
    
    async def conversation_by_id(self,current_user,conversation_id):
        return await self.repo.conversation_by_id(current_user,conversation_id)
    
    async def add_participants(self,conversation_id,user_id):
        return await self.repo.add_participants(conversation_id,user_id)
    
    async def remove_participants(self,conversation_id,user_id):
        return await self.repo.remove_participants(conversation_id,user_id)
    
    async def delete_conversation(self,conversation_id,user_id):
        return await self.repo.delete_conversation(conversation_id,user_id)
    
    async def upload_file(self,conversation_id,current_user,files):
            results=[]
            file_urls=[]
            for file in files:
                ext = os.path.splitext(file.filename)[1]        # get extension e.g. .png
                unique_name = f"{uuid.uuid4()}{ext}"            # random unique filename
                file_path = f"uploads/{unique_name}"
                async with aiofiles.open(file_path,"wb") as out_file:
                    while chunk:=await file.read(1024*1024):
                        await out_file.write(chunk)
                        results.append(file.filename)
                        file_urls.append(f"/uploads/{unique_name}")
            return await self.repo.upload_file(conversation_id,current_user,results,file_urls)
    
    async def download_file(self,filename):
        async def file_generator():
            async with aiofiles.open(f"/uploads/{filename}","rb") as out_file:
                while chunk:=await out_file.read(1024*1024):
                 yield chunk

        return StreamingResponse(
          file_generator(),
          media_type="application/octet-stream",
          headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    async def get_messages(self,conversation_id,page,limit):
        return self.repo.get_messages(conversation_id,page,limit)

        


    