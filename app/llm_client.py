import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

# Initialize the OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def llm_generate(prompt: str, model="gpt-4", temperature=0):
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant that converts natural language queries into SQL or Pandas queries."},
            {"role": "user", "content": prompt}
        ],
        temperature=temperature,
        max_tokens=500
    )
    return response.choices[0].message.content.strip()