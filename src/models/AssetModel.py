from .db_schemes import asset_scheme
from .BaseDataModel import BaseDataModel
from .enums import DataBaseEnum
from bson import ObjectId
class AssetModel(BaseDataModel):
    
    def __init__(self, db_client):
        super().__init__(db_client= db_client)
        self.collection = self.db_client[DataBaseEnum.COLLECTION_ASSET_NAME.value]
        
    #==========================================================#
    # indexing هنا بقي هنبدا اننا نضيف ال 

    # indexes الي هتضيف لينا ال function فاول حاجه احنا عملنا ال 
    # ده collection وهنبقي عاوزين اننا نستدعيها اول ما ننشا ال 
    async def init_collection(self):
        indexes = asset_scheme.get_indexes()
        for index in indexes:
            await self.collection.create_index(
                index["key"],
                name=index["name"],
                unique=index["unique"]
            )
            
    # ده collection دي بقي الي انت هتستعملها عشان تعمل ال 
    # فعملنا دي كحاجه وسيطه __init__ مينفعش اننا نضيفها جوه ال async function ودي عملناها لان ال 
    @classmethod
    async def create_instance(cls, db_client: object):
        instance = cls(db_client)
        await instance.init_collection()
        
        return instance
    #==========================================================#
    async def create_asset(self, asset: asset_scheme):
        
        result = await self.collection.insert_one(asset.model_dump(by_alias=True, exclude_unset=True))
        asset.id = result.inserted_id
        
        return asset
    
    # الي هندهوله project_idبتاعت ال assets تانيه تجيب كل ال function و 
    async def get_all_project_assets(self,asset_project_id: str, asset_type: str):
        
        records =  await self.collection.find({
            # ObjectId بس ده عشان يدور بيه لازم يكون 
            "asset_project_id": ObjectId(asset_project_id) if isinstance(asset_project_id,str) else asset_project_id,
            "asset_type": asset_type
        }).to_list(length = None)
        
        return [
            asset_scheme(**record)
            for record in records
        ]
        
    async def get_asset_record(self, asset_project_id: str, asset_name: str):
        
        record = await self.collection.find_one({
            "asset_project_id": ObjectId(asset_project_id) if isinstance(asset_project_id,str) else asset_project_id,
            "asset_name": asset_name
        })
        
        if record: 
            return asset_scheme(**record)
        
        return None