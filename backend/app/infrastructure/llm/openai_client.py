import openai
import time
from typing import Optional, Dict, Any
from ...application.interfaces.llm_interface import LLMInterface


class OpenAIClient(LLMInterface):
    """
    OpenAI LLM client implementation.
    """
    
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        """
        Initialize OpenAI client.
        
        Args:
            api_key: OpenAI API key
            model: Model name to use
        """
        self.api_key = api_key
        self.model = model
        self.client = openai.AsyncOpenAI(api_key=api_key)
    
    async def generate_response(self, prompt: str, context: Optional[str] = None, 
                              **kwargs) -> str:
        """Generate a response from OpenAI."""
        try:
            # Build the full prompt
            full_prompt = prompt
            if context:
                full_prompt = f"Context: {context}\n\nQuestion: {prompt}"
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that answers questions based on the provided context."},
                    {"role": "user", "content": full_prompt}
                ],
                **kwargs
            )
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error generating response from OpenAI: {e}")
            return f"Error: {str(e)}"
    
    async def generate_response_with_metadata(self, prompt: str, context: Optional[str] = None,
                                           **kwargs) -> Dict[str, Any]:
        """Generate a response with metadata from OpenAI."""
        start_time = time.time()
        
        try:
            # Build the full prompt
            full_prompt = prompt
            if context:
                full_prompt = f"Context: {context}\n\nQuestion: {prompt}"
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that answers questions based on the provided context."},
                    {"role": "user", "content": full_prompt}
                ],
                **kwargs
            )
            
            processing_time = time.time() - start_time
            
            return {
                "response": response.choices[0].message.content,
                "metadata": {
                    "provider": "openai",
                    "model": self.model,
                    "processing_time": processing_time,
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
        except Exception as e:
            processing_time = time.time() - start_time
            return {
                "response": f"Error: {str(e)}",
                "metadata": {
                    "provider": "openai",
                    "model": self.model,
                    "processing_time": processing_time,
                    "error": str(e)
                }
            }
    
    async def is_available(self) -> bool:
        """Check if OpenAI service is available."""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=1
            )
            return True
        except Exception:
            return False
    
    @property
    def provider_name(self) -> str:
        """Get the provider name."""
        return "openai"
    
    @property
    def model_name(self) -> str:
        """Get the model name."""
        return self.model 