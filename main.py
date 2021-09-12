from speech_to_text import takeCommand
from neuralintents import GenericAssistant
from googletrans import Translator
import core
from playsound import playsound
import os
from dotenv import load_dotenv

load_dotenv()


translator = Translator()


mappings = {
    "greeting": core.hello,
    "ask_time": core.time_,
    "ask_day": core.date_,
    "question": core.wiki,
    "ask_news": core.get_news,
    "calculate": core.calculate,
    "ask_weather": core.weatherForecast,
    "ask_covid": core.getInfoCovid,
    "ask_crypto": core.getPriceCrypto,
    "open_song": core.get_song,
    "ask_schedule": core.get_schedule,
    "goodbye": core.bye,
    "ask_food": core.getInfoFood
    }

assistant = GenericAssistant("intents\intents.json", intent_methods=mappings)
assistant.train_model()
#assistant.save_model()
wake_word = os.getenv("WAKE_WORD")

def main():
    core.hello()
    while True:
        # Get input from user 
        command = takeCommand(default=False).lower()
        if wake_word.lower() in command:
            playsound("sounds\zalo.mp3")
            query = takeCommand()
            if query != "None":
                result = translator.translate(query, src='vi', dest='en')
                ints = assistant. _predict_class(result.text)
                if ints[0]['intent'] in mappings.keys():
                    if ints[0]['intent'] in ["calculate", "ask_weather", "open_song", "ask_schedule", "ask_news", "ask_food"]:
                        mappings[ints[0]['intent']](query.lower())
                    elif ints[0]['intent'] == "question":
                        core.wiki(query)
                    else:
                        mappings[ints[0]['intent']]()

if __name__=='__main__':
    main()


        






