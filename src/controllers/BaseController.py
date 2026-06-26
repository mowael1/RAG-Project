from helpers import Settings, get_settings
import os

class BaseController:
    
    def __init__(self):
        self.app_settings = get_settings()
        
        # "/home/mw865/RAG-Project/src"
        self.base_dir = os.path.dirname(os.path.dirname(__file__))
        
        self.files_dir = os.path.join(
            self.base_dir,
            "assets/files"
        )