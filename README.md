# Flight Booker — Alexa Skill

A voice-based flight search skill built with Amazon Alexa + AWS Lambda.

## Features
- Search flights by origin, destination and date
- Supports 8 Indian routes with mock fares
- Built with Python 3.12 + ask-sdk-core

## Invocation
> "Alexa, open flight booker"
> "Find me a flight from Delhi to Dubai on June 20th"

## Intents
| Intent | Description |
|---|---|
| SearchFlightIntent | Search for a flight |
| AMAZON.YesIntent | Search another flight |
| AMAZON.NoIntent | Decline and get prompt |
| AMAZON.HelpIntent | Get usage instructions |
| AMAZON.StopIntent | Exit the skill |
