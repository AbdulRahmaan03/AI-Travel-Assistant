def search_flights(origin, destination, date):
    flights = [
        {
            "airline": "Emirates",
            "flight_number": "EK001",
            "departure": "10:00",
            "arrival": "15:00",
            "price": 1250,
            "currency": "AED",
            "stops": 0
        },
        {
            "airline": "British Airways",
            "flight_number": "BA108",
            "departure": "14:00",
            "arrival": "19:00",
            "price": 980,
            "currency": "AED",
            "stops": 0
        },
        {
            "airline": "Turkish Airlines",
            "flight_number": "TK761",
            "departure": "02:00",
            "arrival": "13:30",
            "price": 850,
            "currency": "AED",
            "stops": 1
        }
    ]
    return flights


def search_hotels(city, check_in, check_out):
    hotels = [
        {
            "name": "Hilton London Kensington",
            "city": "London",
            "price_per_night": 650,
            "currency": "AED",
            "rating": 4.2
        },
        {
            "name": "Premier Inn London City",
            "city": "London",
            "price_per_night": 420,
            "currency": "AED",
            "rating": 4.0
        },
        {
            "name": "The Savoy",
            "city": "London",
            "price_per_night": 1450,
            "currency": "AED",
            "rating": 4.8
        }
    ]

    return hotels