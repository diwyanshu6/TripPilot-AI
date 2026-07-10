import os
import json
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def get_llm():
    if not GROQ_API_KEY:
        print("Warning: GROQ_API_KEY is missing. Agent will operate in simulated mode.")
        return None
    try:
        llm = ChatGroq(
            groq_api_key=GROQ_API_KEY,
            model_name="llama-3.3-70b-versatile",
            temperature=0.2,
            max_tokens=4096
        )
        return llm
    except Exception as e:
        print(f"Failed to initialize ChatGroq: {e}. Operating in simulated mode.")
        return None

def call_llm_json(prompt: str, system_prompt: str = None) -> dict:
    """
    Utility helper that calls LLM and expects a JSON response.
    Includes fallback heuristics if JSON parsing fails or LLM is missing.
    """
    llm = get_llm()
    if not llm:
        return {}
    
    messages = []
    if system_prompt:
        messages.append(("system", system_prompt + "\nResponse MUST be valid JSON only. Do not wrap in markdown code blocks like ```json ... ```."))
    messages.append(("user", prompt))
    
    try:
        response = llm.invoke(messages)
        content = response.content.strip()
        
        # Clean up possible markdown code blocks if the LLM outputted them anyway
        if content.startswith("```"):
            lines = content.splitlines()
            if lines[0].startswith("```json") or lines[0].startswith("```"):
                content = "\n".join(lines[1:-1]).strip()
        
        # Parse JSON
        return json.loads(content)
    except Exception as e:
        print(f"Error calling LLM or parsing JSON: {e}")
        # Try a regex-based search for JSON brackets if parsing raw string failed
        try:
            import re
            match = re.search(r"\{.*\}", content, re.DOTALL)
            if match:
                return json.loads(match.group(0))
        except Exception:
            pass
        return {}
