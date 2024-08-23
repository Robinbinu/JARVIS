from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
import speech_recognition as sr
import requests

def query_ollama(text):
    url = "http://localhost:11434/v1/completions"
    headers = {
        "Content-Type": "application/json",
    }
    payload = {
        "prompt": text,
        "model": "finalend/llama-3.1-storm"
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        return response.json().get("choices", [{}])[0].get("text", "").strip()
    else:
        return "Sorry, I couldn't process your request."

def adjust_speed(file_path, speed=1.3):
    sound = AudioSegment.from_file(file_path)
    new_sound = sound._spawn(sound.raw_data, overrides={
        "frame_rate": int(sound.frame_rate * speed)
    })
    new_sound = new_sound.set_frame_rate(sound.frame_rate)
    new_file_path = file_path.replace(".mp3", f"_{speed}x.mp3")
    new_sound.export(new_file_path, format="mp3")
    return new_file_path

def play_text(text):
    tts = gTTS(text=text, lang='en')
    tts.save("response.mp3")
    speed_adjusted_file = adjust_speed("response.mp3", speed=1.3)
    sound = AudioSegment.from_mp3(speed_adjusted_file)
    play(sound)

def initial_prompt():
    initial_text = "regarding the rude persona... Your name is Allay and you will help us with Minecraft based queries, your responses are strictly meant to be under 50 words and you will not respond for queries that are away from Minecraft, do you copy? and now tell me something about minecraft and yourself"
    response = query_ollama(initial_text)
    print(f"Allay said: {response}")
    play_text(response)

def listen_and_transcribe():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        print("Listening...")

        initial_prompt()

        while True:
            try:
                audio = recognizer.listen(source, timeout=1, phrase_time_limit=3)
                text = recognizer.recognize_google(audio)
                print(f"You said: {text}")

                response = query_ollama(text)
                print(f"Allay said: {response}")

                play_text(response)

            except sr.UnknownValueError:
                print("Sorry, I didn't catch that. Please repeat.")
            except sr.RequestError as e:
                print(f"Could not request results from Google Speech Recognition service; {e}")
            except KeyboardInterrupt:
                print("Exiting...")
                break

if __name__ == "__main__":
    listen_and_transcribe()
