from fastapi import APIRouter, Depends, UploadFile, status, Request
from fastapi.responses import JSONResponse
from helpers import get_settings, Settings
from controllers import DataController , ProjectController, ProcessController
from models.enums import ResponseSignal
from .scheme import ProcessRequest

from models import ProjectModel, ChunkModel
from models.db_schemes import chunk_scheme

import aiofiles
import logging

logger = logging.getLogger("uvicorn")

data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["api_v1", "data"]
)

@data_router.post("/upload/{project_id}")
async def upload_file(request: Request, project_id: str, file:UploadFile, 
                    app_settings:Settings = Depends(get_settings)):
    
    mongo_db_client = request.app.mongo_db_client
    
    is_valid, result_signal = DataController().validate_uploaded_file(file=file)

    if not is_valid:
        return JSONResponse(
            status_code= status.HTTP_400_BAD_REQUEST,
            content={
                "signal": result_signal
            }
        )

    # Change file name and make file_path
    file_path , file_id = DataController().generate_file_path(project_id=project_id, file_name=file)
    
    try:
        # here we need file_path to write data in it
        async with aiofiles.open(file_path, "wb") as f:
            while True:
                chunk = await file.read(app_settings.FILE_DEFAULT_CHUNK_SIZE)
                if not chunk:
                    break
                await f.write(chunk)
    except Exception as e:
        
        logger.error(f"Error while uploading file: {e}")
        return JSONResponse(
            status_code= status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.FILE_UPLOAD_FAILED.value
            }
        )
        
    
    project_model = await ProjectModel.create_instance(db_client=mongo_db_client)
    
    project = await project_model.get_project_or_create_one(project_id=project_id)
    
    return JSONResponse(
            content={
                "signal": ResponseSignal.FILE_UPLOAD_SUCCESS.value,
                "file_id": file_id,
                "project_id": str(project.id)
            }
    )
    

@data_router.post("/process/{project_id}")
async def process_endpoint(request: Request, project_id: str, process_request_data: ProcessRequest):
    chunk_size = process_request_data.chunk_size
    overlap_size = process_request_data.overlap_size
    do_reset = process_request_data.do_reset
    file_id = process_request_data.file_id
    
    # process_controller = ProcessController(project_id=project_id)
    
    file_content = ProcessController(project_id=project_id).get_file_content(file_id = file_id)
    
    if file_content is None:
        logger.error(f"Error while processing file: {file_id}")
    
    
    file_chunks = ProcessController(project_id=project_id).process_file_content(
        file_id= file_id,
        chunk_size=chunk_size,
        overlap_size=overlap_size
    )

    if file_chunks is None or len(file_chunks) == 0:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "singal": ResponseSignal.PROCESSING_FAILED.value
            }
        )
        
    # We write this to get project id
    project_model = await ProjectModel.create_instance(db_client=request.app.mongo_db_client)
    
    project = await project_model.get_project_or_create_one(project_id=project_id)
    
    file_chunks_records = [
        chunk_scheme(
            chunk_text = chunk.page_content,
            chunk_metadata = chunk.metadata,
            chunk_order = i+1,
            chunk_project_id = project.id 
        )
        for i,chunk in enumerate(file_chunks)
    ]
    
    
    chunk_model = await ChunkModel.create_instance(request.app.mongo_db_client)
    
    
    if do_reset == 1: 
        await chunk_model.delete_chunks_by_project_id(project.id)
        
    no_records = await chunk_model.insert_many_chunks(file_chunks_records)
    
    return JSONResponse(
            content={
                "singal": ResponseSignal.PROCESSING_SUCCESS.value,
                "inserted_chunks": no_records
            }
        )