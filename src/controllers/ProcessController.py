from .BaseController import BaseController
from .ProjectController import ProjectController
from langchain_community.document_loaders import TextLoader, PyMuPDFLoader
from models.enums import ProcessEnum
from langchain_text_splitters import RecursiveCharacterTextSplitter

import os
class ProcessController(BaseController):
    
    def __init__(self, project_id):
        super().__init__()
        
        self.project_id = project_id
        self.project_path = ProjectController().get_project_path(project_id=project_id)

        
    def get_file_extension(self,file_id):
        return  os.path.splitext(file_id)[-1]
    
    
    # convert pdf into loader to deal with it
    def get_file_loader(self, file_id: str):
        extension = self.get_file_extension(file_id=file_id)
        
        file_path = os.path.join(
            self.project_path,
            file_id
        )
        
        if not os.path.exists(file_path):
            return "None"
        
        if extension == ProcessEnum.TXT.value:
            return TextLoader(file_path=file_path)
        
        if extension == ProcessEnum.PDF.value:
            return PyMuPDFLoader(file_path=file_path)
        
        return None
    
    # get file content from the loader
    # we will get list that contain Document object and this object has (page_content, metadata) for every page in the file
    def get_file_content(self, file_id: str):
        
        loader = self.get_file_loader(file_id=file_id)
        
        if loader:
            return loader.load()
        else:
            return None
        
    def process_file_content(self, file_id: str,chunk_size: int = 100, overlap_size: int= 20):
        
        text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap_size)
        pages = self.get_file_content(file_id=file_id)

        chunks = text_splitter.split_documents(pages)
        
        return chunks