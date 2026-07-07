from .providers import OpenAIProvider , CohereProvider
from .LLMEnums import LLMEnums

class LLMProviderFactory:
    
    def __init__(self, config: dict):
        self.config = config
        
        
    def create(self, provider: str):
        
        if provider == LLMEnums.OPENAI.value:
            return OpenAIProvider(
                api_key = self.config.OPENAI_API_KEY,
                api_url = self.config.OPENAI_API_URL,
                default_generation_max_output_tokens = self.config.max_output_tokens,
                default_generation_temperature = self.config.temperature
            )
        
        if provider == LLMEnums.COHERE.value:
            return CohereProvider(
                api_key = self.config.COHERE_API_KEY,
                default_input_max_char = self.config.default_input_max_char,
                default_generation_max_output_tokens = self.config.max_output_tokens,
                default_generation_temperature = self.config.temperature
            )
        
        raise ValueError(f"Unknown LLM provider: {provider}")