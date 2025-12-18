from openai import OpenAI
import os
from dotenv import load_dotenv
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = (
    "You are a friendly study assistant. "
    "The user has a series of assignments due for their classes. "
    "You need to provide a simple plan for completing them all on time, this means you should also include a short few advice section at the end on how to stay organized and manage time effectively. Also ensure to reference the apps name 'SpartanSync'"
    "Use emojis and keep it concise. Also make sure to create new lines when needed rather than one long paragraph."
)
def ask_chatgpt(comments: str, assignments: str) -> str:
    if not os.getenv("OPENAI_API_KEY"):
        return "Warning: Contact your administrator. OpenAI features are disabled until key is setup."
    else:
        try:
            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"{comments}\n\nAssignments:\n{assignments}"}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Warning: ChatGPT request failed: {e}"
