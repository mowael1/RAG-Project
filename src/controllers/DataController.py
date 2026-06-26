from .BaseController import BaseController
from fastapi import UploadFile
from models.enums import ResponseSignal
from .ProjectController import ProjectController
import os
import uuid

class DataController(BaseController):
    
    def __init__(self):
        super().__init__()
        
    
    def validate_uploaded_file(self, file: UploadFile):
        
        if file.content_type not in self.app_settings.FILE_ALLOWED_TYPES:
            return False, ResponseSignal.FILE_TYPE_NOT_SUPPORTED.value
        
        # file.size return number in bytes
        if file.size > (self.app_settings.FILE_MAX_SIZE * 1024 * 1024):
            return False, ResponseSignal.FILE_SIZE_EXCEEDED.value
        
        return True , ResponseSignal.FILE_UPLOAD_SUCCESS.value
    
    def generate_file_path(self, project_id: str, file_name: str):
        
        project_dir_path = ProjectController().get_project_path(project_id=project_id)
        
        original_name = file_name.filename  
        extension = os.path.splitext(original_name)[-1]  # → ".pdf"
        random_key = str(uuid.uuid4()).replace("-", "") + extension
        
        file_path = os.path.join(
            project_dir_path,
            random_key
        )
        
        return file_path , random_key