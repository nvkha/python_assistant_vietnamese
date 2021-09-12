import speech_recognition as sr


def takeCommand(wait_time=None, default=True):
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print()
        print("Listening...")
        if not default:
            r.dynamic_energy_threshold = False
            r.energy_threshold = 300
        try:
            audio = r.listen(source, timeout=wait_time)
        except Exception as e:
            print(e)
            return "None"
    try:
        print("Recognizing...")
        query = r.recognize_google(audio, language="vi-VN")
        print(query)
    except Exception as e:
        print(e)
        print("Say that again please") 
        return "None"
    return query


