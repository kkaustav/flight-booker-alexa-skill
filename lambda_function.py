import logging
import random
import ask_sdk_core.utils as ask_utils
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler, AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Mock flight data
FLIGHTS = [
    {"origin": "Delhi", "destination": "Dubai", "price": 17630},
    {"origin": "Delhi", "destination": "London", "price": 32400},
    {"origin": "Kolkata", "destination": "London", "price": 35200},
    {"origin": "Kolkata", "destination": "Dubai", "price": 19800},
    {"origin": "Mumbai", "destination": "Singapore", "price": 14500},
    {"origin": "Mumbai", "destination": "Dubai", "price": 12300},
    {"origin": "Bangalore", "destination": "Singapore", "price": 13700},
    {"origin": "Chennai", "destination": "Dubai", "price": 11900},
]


# ── Launch ─────────────────────────────────────────────────────────────────────

class LaunchRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        speak_output = "Welcome to Flight Booker! Say: find me a flight from Kolkata to London."
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


# ── Search Flight ──────────────────────────────────────────────────────────────

class SearchFlightIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("SearchFlightIntent")(handler_input)

    def handle(self, handler_input):
        slots = handler_input.request_envelope.request.intent.slots
        origin = slots["origin"].value if slots.get("origin") else None
        destination = slots["destination"].value if slots.get("destination") else None
        date = slots["date"].value if slots.get("date") else None

        if not origin or not destination:
            speak_output = "I need both an origin and a destination. Try: find me a flight from Delhi to Dubai."
            return handler_input.response_builder.speak(speak_output).ask(speak_output).response

        # Find a matching flight (case-insensitive)
        flight = next(
            (f for f in FLIGHTS
             if f["origin"].lower() == origin.lower()
             and f["destination"].lower() == destination.lower()),
            None
        )

        if not flight:
            # Fallback: generate a random price for any route
            price = random.randint(10000, 50000)
        else:
            price = flight["price"]

        date_display = date if date else "the selected date"

        # Save to session for Yes/No handlers
        session_attrs = handler_input.attributes_manager.session_attributes
        session_attrs["origin"] = origin
        session_attrs["destination"] = destination
        session_attrs["date"] = date_display
        session_attrs["price"] = price

        speak_output = (
            f"I found a flight from {origin} to {destination} "
            f"on {date_display} for {price} Indian Rupees. Shall I book it?"
        )
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask("Shall I go ahead and book this flight?")
                .response
        )


# ── Yes Intent ─────────────────────────────────────────────────────────────────

class YesIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("AMAZON.YesIntent")(handler_input)

    def handle(self, handler_input):
        session_attrs = handler_input.attributes_manager.session_attributes
        origin = session_attrs.get("origin", "your origin")
        destination = session_attrs.get("destination", "your destination")
        date = session_attrs.get("date", "the selected date")
        price = session_attrs.get("price", "the quoted price")

        speak_output = (
            f"Great! Your flight from {origin} to {destination} "
            f"on {date} for {price} Indian Rupees has been booked. "
            f"Have a wonderful trip!"
        )
        return (
            handler_input.response_builder
                .speak(speak_output)
                .set_should_end_session(True)
                .response
        )


# ── No Intent ──────────────────────────────────────────────────────────────────

class NoIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("AMAZON.NoIntent")(handler_input)

    def handle(self, handler_input):
        speak_output = "Okay, booking cancelled. You can search for another flight anytime!"
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask("Would you like to search for another flight?")
                .response
        )


# ── Cancel / Stop ──────────────────────────────────────────────────────────────

class CancelOrStopIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return (
            ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
            ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input)
        )

    def handle(self, handler_input):
        speak_output = "Goodbye! Have a great trip!"
        return (
            handler_input.response_builder
                .speak(speak_output)
                .set_should_end_session(True)
                .response
        )


# ── Session Ended ──────────────────────────────────────────────────────────────

class SessionEndedRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        return handler_input.response_builder.response


# ── Error Handler ──────────────────────────────────────────────────────────────

class CatchAllExceptionHandler(AbstractExceptionHandler):
    def can_handle(self, handler_input, exception):
        return True

    def handle(self, handler_input, exception):
        logger.error(exception, exc_info=True)
        speak_output = "Sorry, I had trouble doing that. Try: find me a flight from Mumbai to Singapore."
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


# ── Skill Builder ──────────────────────────────────────────────────────────────

sb = SkillBuilder()
sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(SearchFlightIntentHandler())
sb.add_request_handler(YesIntentHandler())
sb.add_request_handler(NoIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()
