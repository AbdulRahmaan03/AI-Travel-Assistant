import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

from tools import search_flights

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


search_flights_declation = types.FunctionDeclaration(
    name='search_flights',
    description='Search for flights between two airports on a specific date.',
    parameters=types.Schema(
        type = "object",
        properties = {
            "origin": types.Schema(
                type="string",
                description='Departure airport code, for example DXB.'
            ),
            "destination": types.Schema(
                type="string",
                description="Arrival airport code, for example LHR."
            ),
            "date": types.Schema(
                type="string",
                description="Travel date in YYYY-MM-DD format."
            )
        },
        required=["origin", "destination", "date"]
    )
)


flight_tool = types.Tool(
    function_declarations=[search_flights_declation]
)


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
        types.Content(
            role= "user",
            parts= [
                types.Part.from_text(text=user_message)
            ]
        )
    )

    # Get Gemini response
    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=conversation_history,
        config=types.GenerateContentConfig(
            tools=[flight_tool]
        )
    )

    for part in response.candidates[0].content.parts:

        if part.function_call:

            function_call = part.function_call

            print("Tool requested:")
            print(function_call.name)
            print(function_call.args)

    # # Store Gemini response
    # conversation_history.append(
    #         types.Content(
    #             role="model",
    #             parts=types.Part.from_text(text=response.text)
    #         )
    #     )

    # print(f"Agent: {response.text}\n")