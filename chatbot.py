import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

from tools import search_flights

from datetime import date



load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


today = date.today().isoformat()

system_instruction = f"""
You are a helpful travel booking assistant.

Today's date is {today}.

Rules:
- If the user gives a travel date without a year, assume the next upcoming occurrence.
- Never invent flight information.
- Use the flight search tool when flight information is required.
- Only state information that is present in the tool result.
"""


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
            tools=[flight_tool],
            system_instruction=system_instruction
        )
    )

    # Store Gemini response
    conversation_history.append(
        types.Content(
            role="model",
            parts=response.candidates[0].content.parts
        )
    )


    # Check whether Gemini requested a tool
    tool_called = False

    # Check whether Gemini requested a tool 
    for part in response.candidates[0].content.parts:

        if part.function_call:

            tool_called = True

            function_call = part.function_call


            # Execute the requested Python function
            if function_call.name == "search_flights":

                result = search_flights(
                    origin=function_call.args["origin"],
                    destination=function_call.args["destination"],
                    date=function_call.args["date"]
                )

                # print("Tool requested:")
                # print(function_call.name)

                # print("Tool result:")            
                # print(result)


                # Give the tool result back to Gemini
                tool_response = types.Part.from_function_response(
                    name=function_call.name,
                    response={
                        "result": result
                    }
                )

                # Store tool response
                conversation_history.append(
                        types.Content(
                            role="user",
                            parts=[tool_response]
                        )
                    )

                # Ask Gemini to formulate the final answer
                final_response = client.models.generate_content(
                    model = "gemini-3.5-flash-lite",
                    contents=conversation_history,
                    config = types.GenerateContentConfig(
                        tools=[flight_tool],
                        system_instruction=system_instruction
                    )
                )

                # print(f"Final_response\n {final_response} \n\n")
                
                # Store Gemini's Tool result based response
                conversation_history.append(
                    types.Content(
                        role="model",
                        parts=final_response.candidates[0].content.parts
                    )
                )

                print(f"Agent: {final_response.text}\n")


    # If no tool was needed, Gemini already has the answer
    if not tool_called:
        print(f"\nAgent: {response.text}\n")