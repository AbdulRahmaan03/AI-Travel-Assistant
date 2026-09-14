import os

from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


print("Travel AI Assistant")
print("Type 'exit' to quit.\n")

# Create list to store conversation to give as memory to LLM
conversation_history = []

while True:

    user_message = input("You: ")

    if user_message.lower() == "exit":
        break

    # Store user_message to conversation_history
    conversation_history.append(
        {
            "role": "user",
            "parts": [
                {"text": user_message}
            ]
        }
    )

    # Get Gemini response
    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=conversation_history
    )

    # Store Gemini response
    conversation_history.append(
            {
                "role": "model",
                "parts": [
                    {"text": response.text}
                ]
            }
        )

    print(f"Agent: {response.text}\n")