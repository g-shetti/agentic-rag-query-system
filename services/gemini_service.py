from google import genai
import os
from dotenv import load_dotenv

from prompts.answer_prompt import build_answer_prompt
from prompts.cypher_prompt import build_cypher_prompt

load_dotenv()

class GeminiService:
    def __init__(self):
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    def generate_cypher(self, question):
        prompt = build_cypher_prompt(question)

        response = self.client.models.generate_content(
            model="gemini-flash-latest",
            contents=prompt
        )

        return response.text.strip()

    def generate_answer(self, question, data):
        prompt = build_answer_prompt(question, data)
        
        response = self.client.models.generate_content(
            model="gemini-flash-latest",
            contents=prompt
        )
        return response.text

    def generate_text(self, prompt: str) -> str:
        try:
            response = self.client.models.generate_content(
                model="gemini-flash-latest",
                contents=prompt
            )

            if not response or not response.text:
                raise Exception("Empty response from Gemini")

            return response.text.strip()

        except Exception as e:
            raise Exception(f"Gemini text generation failed: {str(e)}")
