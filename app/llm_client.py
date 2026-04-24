import os
import json
import time
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MODEL = "gemini-3-flash-preview"


def call_llm(system_prompt: str, user_message: str, max_retries: int = 5) -> dict:
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=user_message,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=0.1,
                    max_output_tokens=3000,
                ),
            )
            raw_text = response.text.strip()
            if "```" in raw_text:
                raw_text = raw_text.split("```")[1]
                if raw_text.startswith("json"):
                    raw_text = raw_text[4:]
                raw_text = raw_text.strip()
            try:
                return json.loads(raw_text)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON: {raw_text} | Error: {e}")
        except Exception as e:
            err = str(e)
            if "429" in err or "503" in err or "quota" in err.lower() or "unavailable" in err.lower():
                wait = 60 if "429" in err else 30
                print(f"API error attempt {attempt + 1}. Waiting {wait}s...")
                time.sleep(wait)
            else:
                raise
    raise ValueError("LLM call failed after max retries.")