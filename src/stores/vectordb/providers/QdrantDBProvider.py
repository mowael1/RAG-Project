from qdrant_client import models, QdrantClient
from ..VectorDBInterface import VectorDBInterface
from ..VectorDBEnums import DistanceMethodEnums
from ....models.db_schemes import RetrieveDocument
from ....helpers.config import get_settings
import logging

class QdrantDBProvider(VectorDBInterface):
    
    # اصلا عندي file والي هتكون db_path هو هيكون محتاج ال 
    # vectors الي هيستعملها عشان يشوف العلاقه ما بين ال distance method وكمان ال 
    def __init__(self, db_path: str, distance_method: str):
        
        self.db_path = db_path
        self.distance_method = None
        
        # databaseوببعت من عليه الاوامر ل connect هو الي من خلاله بعمل client بيكون ليها Database اي 
        # connect بتاعت ال method بس دي مش هنعرفها هنا هي هتكون معرفه جوه ال 
        self.client = None
        
        if distance_method == DistanceMethodEnums.COSINE.value :
            self.distance_method = models.Distance.COSINE
            
        elif distance_method == DistanceMethodEnums.DOT.value :
            self.distance_method = models.Distance.DOT
            
        
        self.settings = get_settings()
        self.limit_documents = self.settings.limit_documents
        
        self.logger = logging.getLogger(__name__)
        
    
    def connect(self):
        self.client = QdrantClient(path=self.db_path)
        
    def disconnect(self):
        self.client = None
        
    def is_collection_existed(self, collection_name: str) -> bool:
        return self.client.collection_exists(collection_name=collection_name)
    
    def list_all_collection(self) -> list[str]:
        return self.client.get_collections()
    
    def get_collection_info(self, collection_name: str) -> dict:
        return self.client.get_collection(collection_name=collection_name)
    
    def delete_collection(self, collection_name: str) -> dict:
        
        if not self.is_collection_existed(collection_name=collection_name):
            self.logger.warning(f"Collection {collection_name} does not exist")
            return False
        
        result = self.client.delete_collection(collection_name=collection_name)
        print(f"Delete result: {result}") 
        
        # تأكد إنها اتمسحت فعلاً
        print(f"Collection still exists after delete: {self.is_collection_existed(collection_name=collection_name)}")
    
    def create_collection(self, collection_name: str,
                    embedding_size: int, do_reset: bool = False):
        
        if do_reset:
            _ =  self.delete_collection(collection_name=collection_name)

        if not self.is_collection_existed(collection_name=collection_name):
            _ = self.client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(size=embedding_size, distance=self.distance_method),
            )
            return True
        
        return False
    
    def insert_one(self, collection_name: str, text: str, vector: list,
                metadata: dict = None,
                record_id: str = None):
        
        if not self.is_collection_existed(collection_name=collection_name):
            self.logger.warning(f"Can not insert new record to non-existed collection: {collection_name}")
            return False
        
        
        self.client.upsert(
            collection_name=collection_name,
            points= [
                models.PointStruct(
                    id=[record_id],
                    vector = vector,
                    payload= {
                        "text": text,
                        **metadata
                    }
                )
            ]
        )
        return True
    
    def insert_many(self, collection_name: str, texts: list, vectors: list,
                metadata: list = None,
                record_ids: list = None, batch_size: int = 50):
    
        if not self.is_collection_existed(collection_name=collection_name):
            self.logger.warning(f"Can not insert new record to non-existed collection: {collection_name}")
            
            return False
        
        metadata = metadata or [{} for _ in range(len(texts))]
        record_ids = record_ids or [None] * len(texts)
        
        points = []
        
        for text, vector, meta,record_id in zip(texts,vectors,metadata,record_ids):
            points.append(
                models.PointStruct(
                    id=record_id,
                    vector=vector,
                    payload={
                        "text": text,
                        **meta
                    }
                )
            )            
        try:
            for i in range(0, len(points), batch_size):
                batch = points[i:i + batch_size]

                self.client.upsert(
                    collection_name=collection_name,
                    points=batch
                )
                
        except Exception as e:
            self.logger.error(f"Error while iserting batch: {e}")
            return False
        return True
        
        
    def search_by_vector(self, collection_name: str,
                        vector: list[float], limit: int = None):

        if not self.is_collection_existed(collection_name):
            self.logger.warning(f"Collection {collection_name} does not exist")
            return []


        limit = limit or self.limit_documents
        
        results = self.client.query_points(
            collection_name=collection_name,
            query=vector,
            limit=limit,
            with_payload=True   # عشان يرجع الـ metadata مع النتائج
        )

        all_results =  results.points
        
        if not all_results or len(all_results) == 0:
            return None
        
        
        return [
            RetrieveDocument(text=result.payload["text"], score=result.score)
            for result in all_results
        ]
    