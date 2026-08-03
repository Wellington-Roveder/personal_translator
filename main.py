import queue
import time

import pyttsx3
import speech_recognition as sr
from deep_translator import GoogleTranslator

if __name__ == "__main__":
    translator = GoogleTranslator(source="en", target="pt")
    text_historic = []

    engine = pyttsx3.init()
    engine.setProperty("rate", 175)  # addin natural speek
    engine.setProperty("volume", 0.9)

    voices = engine.getProperty("voices")
    """founding a portuguese voice"""
    for voice in voices:
        if "portuguese" in voice.name.lower() or "brazil" in voice.name.lower():
            engine.setProperty("voice", voice.id)
            break

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
            translation = translator.translate(text_en)
            print(f"🇧🇷 Tradução: {translation}\n" + "-" * 40)

            translation_queue.put(translation)
        except Exception as e:  # noqa: BLE001
            print(f"[Erro na tradução] {e}")
            return

    r = sr.Recognizer()
    mic = sr.Microphone()

    with mic as source:
        print("adjusting ambient noise...")
        r.adjust_for_ambient_noise(source, duration=1)
        print("READ!")

    stop_listening = r.listen_in_background(mic, callback_audio)
    last_status = time.time()

    try:
        while True:
            if not translation_queue.empty():
                """Check if there is anything in the queue blocking recognition."""
                text_to_speak = translation_queue.get()
                engine.say(text_to_speak)
                engine.runAndWait()

                # """using the text_historic for simultaneous translation"""
                # if len(text_historic) >= 2:
                # full_text = " ".join(text_historic)
                # translation = translator.translate(full_text)

            if time.time() - last_status > 5:
                print(
                    f"Fila: {translation_queue.qsize()} | Histórico: {len(text_historic)}"
                )
                last_status = time.time()

            time.sleep(0.05)
    except KeyboardInterrupt:
        print("\nEnding...")
        stop_listening(wait_for_stop=False)
