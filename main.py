import time

import pyttsx3
import speech_recognition as sr
from googletrans import Translator

if __name__ == "__main__":
    translator = Translator()
    text_historic = []
    engine = pyttsx3.init()

    def callback_audio(recognizer, audio):
        try:
            text_en = recognizer.recognize_google(audio, language="en-US")
            print(f"🇺🇸, Listening: {text_en}")
        except sr.UnknownValueError:
            return
        except sr.RequestError as e:
            print(e)
            return

        text_historic.append(text_en)
        if len(text_historic) > 3:
            text_historic.pop(0)

        complete_context = " ".join(text_historic)
        try:
            translation = translator.translate(complete_context, dest="pt").text
            print(f"🇧🇷 Tradução: {translation}\n" + "-" * 40)
        except Exception as e:  # noqa: BLE001
            print(e)
            return
        engine.say(translation)
        engine.runAndWait()

    r = sr.Recognizer()
    mic = sr.Microphone()

    with mic as source:
        r.adjust_for_ambient_noise(source, duration=1)

    stop_listening = r.listen_in_background(mic, callback_audio)
    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        stop_listening(wait_for_stop=False)
