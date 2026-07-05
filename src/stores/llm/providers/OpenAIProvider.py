from ..LLMInterface import LLMInterface
from ..LLMEnums import OpenAIEnums
from openai import OpenAI
import logging

from ....helpers.config import get_settings

class OpenAIProvider(LLMInterface):
    
# Every Provider will have their own __init__() function
    def __init__(self, api_key: str, api_url: str= None,
                default_input_max_char: int= 1000,
                default_generation_max_output_tokens: int= None,
                default_generation_temperature: float = None):
        
        self.api_key = api_key
        self.api_url = api_url
        
        self.settings = get_settings()
        
        self.default_input_max_char = default_input_max_char
        self.default_generation_max_output_tokens = default_generation_max_output_tokens or self.settings.max_output_tokens
        self.default_generation_temperature = default_generation_temperature or self.settings.temperature
        
        # embedding , generationدلوقتي والي هما ال two tasks في openai هستعمل ال 
        # vector databaseلاننا هنبقي محتاجينه في ال embedding size لازم اخد كمان ال embedding ومع ال 
        self.generation_model_id = None
        self.embedding_model_id = None
        self.embedding_size = None
        
        # client لازم انك تعرف openai عشان تبدا تتعامل مع 
        self.client = OpenAI(
            api_key= self.api_key,
            base_url= self.api_url,
        )
                
        # الي هو موجود فيه file كده هو هاخد اسم ال 
        self.logger = logging.getLogger(__name__)
        
        self.enums = OpenAIEnums
        
    # بتاعها logic ونحط ال interface الي موجوده في ال functions هنبدا بقي دلوقتي نجيب ال 
    # instructor تحطه في model_id ودي كل الي هتعملوا دلوقتي انها هتاخد ال 
    # شغال فعلا علي السيرفر client في اي وقت اثناء من ال model وحطيناه هنا لاننا ممكن نغير ال 
    # يبقي كنا هنثبت عليه ومش هنقدر اننا نغيره بعد كده__init__ فلو كنا حطيناه في ال 
    def set_generation_model(self, model_id: str):
        self.generation_model_id = model_id
        
    def set_embedding_model(self, model_id: str, embedding_size: int):
        self.embedding_model_id = model_id
        self.embedding_size = embedding_size
        
    # بيتعامل بيه API عشان ده الي ال chat completions يتبعت تحوله للشكل بتاع ال prompt دي المسؤله ان اي 
    
    def construct_prompt(self, prompt: str, role: str):
        return {"role": role, "content": prompt}
    
    def generate_text(self, prompt: str,chat_history: list = [], max_output_tokens: int = None, temperature: float= None):
        
        chat_history = chat_history.copy() if chat_history else []  # ✅ copy عشان منعدلش الأصلي

        if not self.client:
            self.logger.error("OpenAI was not set")
            return None
        
        if not self.generation_model_id:
            self.logger.error("Generation model for OpenAI was not set")
            return None
        
        max_output_tokens = max_output_tokens or self.default_generation_max_output_tokens
        temperature = temperature or self.default_generation_temperature
        
        # LLM بتاع ال API دي كلها بعد كده ونبعتها ل list الي هناخد ال user هتكون هي الرساله بتاعت ال chat_history وان اخر رساله في ال 
        chat_history.append(self.construct_prompt(prompt=prompt, role=OpenAIEnums.USER.value))
        
        response = self.client.chat.completions.create(
            model=self.generation_model_id,
            messages=chat_history,
            max_tokens=self.max_output_tokens,
            temperature=temperature)
        
        # الي راجع ده هل هو مضبوط ولا فيه مشاكلresponse بعد كده لازم اشيك علي ال 
        if not response or not response.choices or len(response.choices) == 0 or not response.choices[0].message:
            
            self.logger.error("Error while generating text with OpenAI")
            return None
        
        return response.choices[0].message.content
        
        
    def embed_text(self, text: str, document_type: str= None):

        # موجود ولا لاclient لازم الاول تشيك هل ال 
        if not self.client:
            self.logger.error("OpenAI was not set")
            return None
        
        # اصلا embedding عشان لو مش موجود مش هعرف اعمل embedding_model_id وبردو اشيك علي ال 
        if not self.embedding_model_id:
            self.logger.error("Embedding model for OpenAI was not set")
            return None
        
        # data ل embedding لو خلاص الاتنين الي فوق تمام يبقي هروح اعمل 
        response = self.client.embeddings.create(
            model=self.embedding_model_id,
            input = text
        )
        
        # الي داخل input بتاع ال embedding الي هو ال response عاوز بقي انا اشيك علي ال 
        if not response or not response.data or len(response.data) == 0 or not response.data[0].embedding:
            
            self.logger.error("Error while embedding text with OpenAI")
            return None
        
        # embedding وخلاص لو عدي بقي يبقي يرجع ال 
        return response.data[0].embedding