import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()

GOOGLE_AI_KEY = os.getenv("GOOGLE_AI_KEY")
system_prompt = str(os.getenv("SYSTEM_PROMPT"))
image_prompt = system_prompt

genai.configure(api_key=GOOGLE_AI_KEY)

text_generation_config = {
    "temperature": 1,
    "top_p": 1,
    "top_k": 32,
    "max_output_tokens": 512,
}

image_generation_config = {
    "temperature": .6,
    "top_p": 1,
    "top_k": 32,
    "max_output_tokens": 512,
}

safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
]

text_model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=text_generation_config,
    safety_settings=safety_settings,
    system_instruction=system_prompt
)

image_model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=image_generation_config,
    safety_settings=safety_settings,
    system_instruction=image_prompt
)

async def generate_response_with_text(message_text):
    prompt_parts = [message_text]
    response = text_model.generate_content(prompt_parts)
    if response._error:
        return "❌" + str(response._error)
    return response.text

async def generate_response_with_image_and_text(image_data, text):
    image_parts = [{"mime_type": "image/jpeg", "data": image_data}]
    prompt_parts = [image_parts[0], f"\n{text if text else 'The user has sent an image.'}"]
    response = image_model.generate_content(prompt_parts)
    if response._error:
        return "❌" + str(response._error)
    return response.text
