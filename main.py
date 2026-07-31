import queue
import time

import pyttsx3
import speech_recognition as sr
from googletrans import Translator

if __name__ == "__main__":
    translator = Translator()
    text_historic = []

    engine = pyttsx3.init()
    ###adding a queue for translations for more otimization
    translation_queue = queue.Queue()

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

        try:
            """Instead of saying it here, we put the text in the queue."""
            translation = translator.translate(text_en, dest="pt").text
            print(f"🇧🇷 Tradução: {translation}\n" + "-" * 40)

            translation_queue.put(translation)
        except Exception as e:  # noqa: BLE001
            print(e)
            return

    r = sr.Recognizer()
    mic = sr.Microphone()

    with mic as source:
        print("adjusting ambient noise...")
        r.adjust_for_ambient_noise(source, duration=1)
        print("READ!")

    stop_listening = r.listen_in_background(mic, callback_audio)

    try:
        while True:
            if not translation_queue.empty():
                """Check if there is anything in the queue blocking recognition."""
                text_to_speak = translation_queue.get()
                engine.say(text_to_speak)
                engine.runAndWait()

            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nEnding...")
        stop_listening(wait_for_stop=False)
