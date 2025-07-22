from openai import AsyncOpenAI
from ..core.interfaces import AbstractLLMClient, AbstractEmbeddingClient

class OpenAIAdapter(AbstractLLMClient, AbstractEmbeddingClient):
    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)

    async def generate_response(self, prompt: str, context: str | None = None) -> str:
        from openai.types.chat import ChatCompletionMessageParam
        messages: list[ChatCompletionMessageParam] = [
            {"role": "user", "content": f"Context: {context}\n\nQuestion: {prompt}"} if context else {"role": "user", "content": prompt}
        ]
        response = await self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=500
        )
        content = response.choices[0].message.content
        return content if content is not None else ""

    async def create_embedding(self, text: str) -> list[float]:
        response = await self.client.embeddings.create(
            model="text-embedding-ada-002",
            input=[text]
        )
        embedding = response.data[0].embedding
        return embedding if embedding is not None else []