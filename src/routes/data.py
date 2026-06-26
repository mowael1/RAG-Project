from fastapi import APIRouter, Depends, UploadFile, status
from fastapi.responses import JSONResponse
from helpers import get_settings, Settings
from controllers import DataController , ProjectController
from models.enums import ResponseSignal
import aiofiles
import logging

logger = logging.getLogger("uvicorn")

data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["api_v1", "data"]
)

@data_router.post("/upload/{project_id}")
async def upload_file(project_id: str, file:UploadFile, 
                    app_settings:Settings = Depends(get_settings)):
    
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
        
    return JSONResponse(
            content={
                "signal": ResponseSignal.FILE_UPLOAD_SUCCESS.value
            }
    )