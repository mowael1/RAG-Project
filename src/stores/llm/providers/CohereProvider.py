from ..LLMInterface import LLMInterface
from ..LLMEnums import CoHereEnums ,DocumentTypeEnum
import cohere
import logging

from ....helpers.config import get_settings

class CoHereProvider(LLMInterface):
    
    def __init__(self, api_key: str,
                default_input_max_char: int= 1000,
                default_generation_max_output_tokens: int= 1000,
                default_generation_temperature: float = .1):
        
        self.api_key = api_key
        self.settings = get_settings()
        
        self.default_input_max_char = default_input_max_char
        self.default_generation_max_output_tokens = default_generation_max_output_tokens or self.settings.max_output_tokens
        self.default_generation_temperature = default_generation_temperature or self.settings.temperature
        
        self.generation_model_id = None
        self.embedding_model_id = None
        self.embedding_size = None
        
        self.client = cohere.ClientV2(api_key=self.api_key)
        self.enums = CoHereEnums
        self.logger = logging.getLogger(__name__)
        
    def set_generation_model(self, model_id: str):
        self.generation_model_id = model_id
        
    def set_embedding_model(self, model_id: str, embedding_size: int):
        self.embedding_model_id = model_id
        self.embedding_size = embedding_size
            
    def construct_prompt(self, prompt: str, role: str):
        return {"role": role, "content": prompt}
    
    def generate_text(self, prompt: str,chat_history: list = [], max_output_tokens: int = None, temperature: float= None):
        
        if not self.client:
            self.logger.error("CoHere client was not set")
            return None
        
        if not self.generation_model_id:
            self.logger.error("Generation model for CoHere was not set")
            return None
        
        max_output_tokens = max_output_tokens or self.default_generation_max_output_tokens
        temperature = temperature or self.default_generation_temperature
        
        chat_history.append(self.construct_prompt(prompt=prompt, role=CoHereEnums.USER.value))
        
        response = self.client.chat(
            model=self.generation_model_id,
            messages=chat_history,
            temperature=temperature,
            max_tokens=max_output_tokens
        )
        
        if not response or not response.message or not response.message.content or len(response.message.content) == 0:
            self.logger.error("Error while generating text with Cohere")
            return None

        return response.message.content[0].text
    

    def embed_text(self, text: str, document_type: str= None):

        if not self.client:
            self.logger.error("Cohere client was not set")
            return None
        
        if not self.embedding_model_id:
            self.logger.error("Embedding model for Cohere was not set")
            return None
        
        input_type = None
        if document_type == DocumentTypeEnum.DOCUMENT.value:
            input_type = CoHereEnums.DOCUMENT.value
        elif document_type == DocumentTypeEnum.QUERY.value:
            input_type = CoHereEnums.QUERY.value

        response = self.client.embed(
            model=self.embedding_model_id,
            texts=[text],
            input_type=input_type,
            embedding_types=["float"]
        )
        
        if not response or not response.embeddings or not response.embeddings.float or len(response.embeddings.float) == 0:
            self.logger.error("Error while embedding text with Cohere")
            return None
        
        return response.embeddings.float[0]

    # def embed_text(self, text, document_type = None):
    #     raise NotImplementedError

    def embed_many(self, texts: list[str], document_type: str = None):
        
        if not self.client:
            self.logger.error("Cohere client was not set")
            return None
        
        if not self.embedding_model_id:
            self.logger.error("Embedding model for Cohere was not set")
            return None

        input_type = None
        if document_type == DocumentTypeEnum.DOCUMENT.value:
            input_type = CoHereEnums.DOCUMENT.value
        elif document_type == DocumentTypeEnum.QUERY.value:
            input_type = CoHereEnums.QUERY.value

        response = self.client.embed(
            model=self.embedding_model_id,
            texts=[text for text in texts],  # ← كل الـ texts دفعة واحدة
            input_type=input_type,
            embedding_types=["float"]
        )

        if not response or not response.embeddings or not response.embeddings.float or len(response.embeddings.float) == 0:
            self.logger.error("Error while embedding texts with Cohere")
            return None

        return response.embeddings.float  # ← بترجع list مش واحدة بس