import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

from tools import search_flights, search_hotels, search_activities

from datetime import date



load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


today = date.today().isoformat()

system_instruction = f"""
You are a helpful travel booking assistant.

Today's date is {today}.

Rules:
- If the user gives a travel date without a year, assume the next upcoming occurrence.
- Use the available travel tools when flight, hotel, or activity information is required.
- Never invent travel information.
- Only state information that is present in the tool results.
- Use search_flights for flight searches.
- Use search_hotels for hotel searches.
- Use search_activities for activities and things to do.
"""


search_flights_declaration = types.FunctionDeclaration(
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


search_hotels_declaration = types.FunctionDeclaration(
    name="search_hotels",
    description="Search for hotels in a city for specific check-in and check-out dates.",
    parameters=types.Schema(
        type="OBJECT",
        properties={
            "city": types.Schema(
                type="STRING",
                description="City where the hotel is located, for example London."
            ),
            "check_in": types.Schema(
                type="STRING",
                description="Hotel check-in date in YYYY-MM-DD format."
            ),
            "check_out": types.Schema(
                type="STRING",
                description="Hotel check-out date in YYYY-MM-DD format."
            )
        },
        required=["city", "check_in", "check_out"]
    )
)


search_activities_declaration = types.FunctionDeclaration(
    name="search_activities",
    description="Search for activities and things to do in a city on a specific date.",
    parameters=types.Schema(
        type="OBJECT",
        properties={
            "city": types.Schema(
                type="STRING",
                description="City where the activity takes place, for example London."
            ),
            "date": types.Schema(
                type="STRING",
                description="Date of the activity in YYYY-MM-DD format."
            ),
        },
        required=["city", "date"],
    ),
)



travel_tools = types.Tool(
    function_declarations=[search_flights_declaration,
                           search_hotels_declaration,
                           search_activities_declaration]
)


available_tools = {
    "search_flights": search_flights,
    "search_hotels": search_hotels,
    "search_activities": search_activities
}



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
            tools=[travel_tools],
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


            # # Execute the requested Python function
            # if function_call.name == "search_flights":

            #     result = search_flights(
            #         origin=function_call.args["origin"],
            #         destination=function_call.args["destination"],
            #         date=function_call.args["date"]
            #     )

                # print("Tool requested:")
                # print(function_call.name)

                # print("Tool result:")            
                # print(result)


            tool_name = function_call.name

            tool = available_tools.get(tool_name)

            if tool is None:
                print(f"Unknown tool requested: {tool_name}")
                continue

            result = tool(**function_call.args)

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
                    tools=[travel_tools],
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