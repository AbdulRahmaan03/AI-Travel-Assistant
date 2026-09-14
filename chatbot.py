import os

from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


print("Travel AI Assistant")
print("Type 'exit' to quit.\n")

while True:

    user_message = input("You: ")

    if user_message.lower() == "exit":
        break

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=user_message
    )

    print(f"Agent: {response.text}\n")