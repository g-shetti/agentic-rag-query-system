from langchain_google_genai import GoogleGenerativeAIEmbeddings
import os

class EmbeddingService:
    _model = None

    def __init__(self):
        if EmbeddingService._model is None:
            EmbeddingService._model = GoogleGenerativeAIEmbeddings(
                model="models/embedding-001",
                google_api_key=os.getenv("GEMINI_API_KEY")
            )
        self.model = EmbeddingService._model

    def embed(self, text: str):
        return self.model.embed_query(text)