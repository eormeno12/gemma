import os
import speech_recognition as sr
import pyttsx3
import pywhatkit
import datetime
import wikipedia
import pyjokes
from googletrans import Translator
from dotenv import load_dotenv
import openai

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

completion = openai.Completion
main_chat_log = None
sec_chat_log = None
start_chat_log = '''Human: Hola, ¿cómo estás?
AI: Estoy muy bien. ¿Cómo puedo ayudarte?'''

translator = Translator()


listener = sr.Recognizer()
engine = pyttsx3.init()


def setup_ceo():
    voices = engine.getProperty("voices")

    engine.setProperty("voice", voices[31].id)
    engine.say("Hola! Soy Gema, tu asistente virtual.")
    engine.runAndWait()


def talk(text):
    engine.say(text)
    engine.runAndWait()


def askGPT3(statement, chat_log):
    global main_chat_log
    if chat_log is None:
        chat_log = start_chat_log

    prompt = f"{chat_log}\nHuman: {statement}\nAI:"
    prompt = translator.translate(prompt, src="es", dest="en").text

    response = completion.create(prompt=prompt,
                                 engine="davinci",
                                 stop=['\nHuman:'],
                                 temperature=0.9,
                                 top_p=1, frequency_penalty=0,
                                 presence_penalty=0.6,
                                 best_of=2,
                                 max_tokens=150)
    answer = response.choices[0].text.strip()
    main_chat_log = f"{prompt} {answer}"

    answer = translator.translate(answer, src="en", dest="es").text
    return answer


def listen(name="gema"):
    try:
        with sr.Microphone() as source:
            print("Listening...")
            voice = listener.listen(source)
            command = listener.recognize_google(voice, language="es-MX")
            command = command.lower()

            if name in command:
                print(command)
    except:
        pass

    return command


def talk_with(name, statement, chat_log):
    global sec_chat_log
    if chat_log is None:
        chat_log = start_chat_log.replace("AI: Estoy muy bien. ¿Cómo puedo ayudarte?", f'{name}: Hola soy {name}.')

    prompt = f"{chat_log}\nHuman: {statement}\n{name}:"
    prompt = translator.translate(prompt, src="es", dest="en").text

    response = completion.create(prompt=prompt,
                                 engine="davinci",
                                 stop=['\nHuman:'],
                                 temperature=0.75,
                                 top_p=1, frequency_penalty=0,
                                 presence_penalty=0.6,
                                 best_of=2,
                                 max_tokens=150)
    answer = response.choices[0].text.strip()

    sec_chat_log = f"{prompt} {answer}"

    answer = translator.translate(answer, src="en", dest="es").text
    return answer


def run_ceo():
    command = listen()
    command = command.replace("gema", "")

    if "reproduce" in command:
        song = command.replace("reproduce", "")

        command = command.replace("reproduce", "Reproduciendo")
        talk(command + ". ¡Hecho!")
        print(command)

        pywhatkit.playonyt(song)
    elif "hora" in command:
        time = datetime.datetime.now().strftime("%I:%M %p")
        print(time)
        talk("La hora es: " + time)
    elif "quién es" in command:
        element = command.replace("quién es", "")
        wikipedia.set_lang("es")
        info = wikipedia.summary(element.replace(" ", "-"), 2)
        print(info)
        talk(info)
    elif "chiste" in command:
        joke = pyjokes.get_joke(language="es")
        print(joke)
        talk(joke)
    elif "quiero hablar con" in command:
        name = command.replace("quiero hablar con", "")
        talk(f"¡Perfecto! Me retiro por un momento, te dejo con {name}")

        while True:
            command = listen(name)
            if "terminar conversación" not in command:
                answer = talk_with(name, command, sec_chat_log)
                print(answer)
                talk(answer)
            else:
                break
    else:
        answer = askGPT3(command, main_chat_log)
        answer.replace("AI:", "")
        answer.replace("HUMAN:", "")
        print(answer)
        talk(answer)


if __name__ == '__main__':
    setup_ceo()

    while True:
        try:
            run_ceo()
        except UnboundLocalError:
            pass
