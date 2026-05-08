import logging
import os
import requests
import ask_sdk_core.utils as ask_utils
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler, AbstractExceptionHandler

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

SERP_API_KEY = os.environ.get("SERP_API_KEY")

CITY_TO_IATA = {
    "delhi": "DEL", "new delhi": "DEL",
    "mumbai": "BOM", "bombay": "BOM",
    "kolkata": "CCU", "calcutta": "CCU",
    "bangalore": "BLR", "bengaluru": "BLR",
    "chennai": "MAA", "hyderabad": "HYD",
    "ahmedabad": "AMD", "pune": "PNQ",
    "goa": "GOI", "kochi": "COK",
    "jaipur": "JAI", "lucknow": "LKO",
    "patna": "PAT", "varanasi": "VNS",
    "nagpur": "NAG", "srinagar": "SXR",
    "amritsar": "ATQ", "chandigarh": "IXC",
    "visakhapatnam": "VTZ", "vizag": "VTZ",
    "trivandrum": "TRV", "guwahati": "GAU",
    "dubai": "DXB", "abu dhabi": "AUH",
    "doha": "DOH", "riyadh": "RUH",
    "muscat": "MCT", "kuwait": "KWI",
    "london": "LHR", "paris": "CDG",
    "frankfurt": "FRA", "amsterdam": "AMS",
    "rome": "FCO", "madrid": "MAD",
    "zurich": "ZRH", "vienna": "VIE",
    "istanbul": "IST", "milan": "MXP",
    "munich": "MUC", "barcelona": "BCN",
    "singapore": "SIN", "bangkok": "BKK",
    "hong kong": "HKG", "tokyo": "NRT",
    "osaka": "KIX", "seoul": "ICN",
    "beijing": "PEK", "shanghai": "PVG",
    "kuala lumpur": "KUL", "jakarta": "CGK",
    "manila": "MNL", "colombo": "CMB",
    "kathmandu": "KTM", "dhaka": "DAC",
    "sydney": "SYD", "melbourne": "MEL",
    "new york": "JFK", "los angeles": "LAX",
    "chicago": "ORD", "toronto": "YYZ",
    "san francisco": "SFO", "miami": "MIA",
    "nairobi": "NBO", "johannesburg": "JNB",
    "cairo": "CAI", "lagos": "LOS",
}

def get_iata(city_name):
    return CITY_TO_IATA.get(city_name.lower().strip(), city_name.upper())

def get_flight(origin, destination, date):
    try:
        origin_code = get_iata(origin)
        dest_code = get_iata(destination)
        logger.info(f"Searching: {origin_code} to {dest_code} on {date}")
        params = {
            "engine": "google_flights",
            "departure_id": origin_code,
            "arrival_id": dest_code,
            "outbound_date": date,
            "type": "2",
            "currency": "INR",
            "hl": "en",
            "api_key": SERP_API_KEY
        }
        response = requests.get("https://serpapi.com/search", params=params, timeout=15)
        data = response.json()
        logger.info(f"SerpAPI keys: {list(data.keys())}")
        flights = data.get("best_flights", data.get("other_flights", []))
        if not flights:
            return None
        flight = flights[0]
        price = flight.get("price", 0)
        airline = flight["flights"][0].get("airline", "an airline")
        duration = flight.get("total_duration", 0)
        hours = duration // 60
        minutes = duration % 60
        duration_str = f"{hours} hours {minutes} minutes" if hours else f"{minutes} minutes"
        return {"price": price, "airline": airline, "duration": duration_str}
    except Exception as e:
        logger.error(f"SerpAPI error: {e}")
        return None

class LaunchRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_request_type("LaunchRequest")(handler_input)
    def handle(self, handler_input):
        msg = "Welcome to Flight Search! Say: find me a flight from Kolkata to London on June twentieth."
        return handler_input.response_builder.speak(msg).ask(msg).response

class SearchFlightIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("SearchFlightIntent")(handler_input)
    def handle(self, handler_input):
        slots = handler_input.request_envelope.request.intent.slots
        origin      = slots["origin"].value      if slots.get("origin")      else None
        destination = slots["destination"].value if slots.get("destination") else None
        date        = slots["date"].value        if slots.get("date")        else None
        if not origin or not destination:
            msg = "I need both an origin and a destination. Try: find me a flight from Delhi to Dubai."
            return handler_input.response_builder.speak(msg).ask(msg).response
        if not date:
            date = "2026-06-20"
        result = get_flight(origin, destination, date)
        if result:
            msg = (
                f"I found a {result['airline']} flight from {origin.title()} to {destination.title()} "
                f"on {date}, taking {result['duration']}, "
                f"for {result['price']:,} Indian Rupees. "
                f"Would you like to search for another flight?"
            )
        else:
            msg = (
                f"Sorry, I couldn't find live flights from {origin.title()} to {destination.title()} "
                f"on {date}. Would you like to try a different route?"
            )
        return handler_input.response_builder.speak(msg).ask("Would you like to search for another flight?").response

class YesIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("AMAZON.YesIntent")(handler_input)
    def handle(self, handler_input):
        msg = "Great! Say: find me a flight from Mumbai to Singapore."
        return handler_input.response_builder.speak(msg).ask(msg).response

class NoIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("AMAZON.NoIntent")(handler_input)
    def handle(self, handler_input):
        msg = "Okay! To search again say: find me a flight from Mumbai to Singapore."
        return handler_input.response_builder.speak(msg).ask(msg).response

class HelpIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)
    def handle(self, handler_input):
        msg = "Say: find me a flight from Mumbai to Singapore on June twentieth. I will tell you the live fare and duration."
        return handler_input.response_builder.speak(msg).ask(msg).response

class CancelOrStopIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return (
            ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
            ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input)
        )
    def handle(self, handler_input):
        return handler_input.response_builder.speak("Goodbye! Happy travels!").set_should_end_session(True).response

class SessionEndedRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)
    def handle(self, handler_input):
        return handler_input.response_builder.response

class CatchAllExceptionHandler(AbstractExceptionHandler):
    def can_handle(self, handler_input, exception):
        return True
    def handle(self, handler_input, exception):
        logger.error(exception, exc_info=True)
        msg = "Sorry, I couldn't understand that. Try: find me a flight from Mumbai to Singapore."
        return handler_input.response_builder.speak(msg).ask(msg).response

sb = SkillBuilder()
sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(SearchFlightIntentHandler())
sb.add_request_handler(YesIntentHandler())
sb.add_request_handler(NoIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()
