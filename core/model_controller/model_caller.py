import os
from litellm import completion
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("API_KEY")
model = os.getenv("MODEL")

def get_model_response(message, api_key=api_key, model=model):
    resp = completion(
        model=model,
        messages=message,
        api_key=api_key,
    )

    msg = resp.choices[0].message
    answer = msg.content or ""

    thinking_text = getattr(msg, "reasoning_content", "") or ""

    if not thinking_text and hasattr(msg, "thinking_blocks"):
        for block in (msg.thinking_blocks or []):
            if block.get("type") == "thinking":
                thinking_text += block.get("thinking", "")

    if thinking_text:
        answer = f"<think>{thinking_text}</think>\n\n{answer}"

    return answer