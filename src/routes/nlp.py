from fastapi import APIRouter, status, Request, FastAPI
from fastapi.responses import JSONResponse
from .scheme.nlp_scheme import SearchRequest, PushRequest
from models import ProjectModel,ChunkModel
from controllers import NLPController
from models.enums import ResponseSignal
import logging

logger = logging.getLogger("uvicorn.error")

nlp_router = APIRouter(
    prefix="/api/v1/nlp",
    tags=["api_v1","nlp"]
)

# qdrant ويضيفها ل embedding الي متخزنه تبعه ويعملها chunks ويروح يشوف ال project_id ده الي هيكون مسؤول انه ياخد ال 
@nlp_router.post("/index/push/{project_id}")
async def index_project(request: Request, project_id: str, push_request: PushRequest):
    
    project_model = await ProjectModel.create_instance(db_client=request.app.mongo_db_client)
    # الي اترفع project دي عشان اجيب ال 
    project = await project_model.get_project_or_create_one(project_id=project_id)
    
    if not project: 
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"signal": ResponseSignal.PROJECT_NOT_FOUND_ERROR.value}
        )
        
    nlp_controller = NLPController(
        vectordb_client=request.app.vectordb_client,
        generation_client=request.app.generation_client,
        embedding_client=request.app.embedding_client
    )
    
    if push_request.do_reset:
        nlp_controller.vectordb_client.delete_collection(
            collection_name=nlp_controller.create_collection_name(project_id=project.project_id)
        )
        
    chunk_model = await ChunkModel.create_instance(db_client=request.app.mongo_db_client)
    
    has_records = True
    page_no = 1
    inserted_items_count = 0
    idx = 0
    
    while has_records:
        
        # project.id الي ليها علياقه ب chunks هنا هجيب كل ال 
        page_chunks = await chunk_model.get_project_chunks(project_id=project.id, page_no=page_no)
        
        if not page_chunks or len(page_chunks) == 0:
            has_records = False
            break
        
        page_no += 1
        
        chunk_ids = list(range(idx, idx+len(page_chunks)))
        idx += len(page_chunks)
        
        is_inserted = nlp_controller.index_into_vector_db(
            project=project,
            chunks=page_chunks,
            chunk_ids = chunk_ids,
            do_reset=False  # ← loop مش محتاجها هنا خالص لانك شيكت عليها قبل ال
        )
        
        if not is_inserted:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"signal": ResponseSignal.INSERT_INTO_VECTORDB_ERROR.value}
            )
        
        inserted_items_count += len(page_chunks)
        
    return JSONResponse(
        content={
            "signal": ResponseSignal.INSERT_INTO_VECTORDB_SUCCESS.value,
            "inserted_items_count": inserted_items_count
        }
    )
    
@nlp_router.get("/index/info/{project_id}")
async def get_project_index_info(request: Request, project_id: str):
    
    project_model = await ProjectModel.create_instance(
        db_client=request.app.mongo_db_client
    )
    project = await project_model.get_project_or_create_one(project_id=project_id)
    
    if not project: 
        return JSONResponse(
            status_code= status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.PROJECT_NOT_FOUND_ERROR.value
            }
        )
        
    nlp_controller = NLPController(
        vectordb_client=request.app.vectordb_client,
        generation_client=request.app.generation_client,
        embedding_client= request.app.embedding_client
    )
    
    collection_info = nlp_controller.get_vector_db_collection_info(project=project)
    
    return JSONResponse(
        content={
            "signal": ResponseSignal.INSERT_INTO_VECTORDB_SUCCESS.value,
            "collection_info": collection_info.model_dump()
        }
    )