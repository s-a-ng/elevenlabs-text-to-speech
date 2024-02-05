from pygame import mixer 
from termcolor import colored

import requests
import os
import io
import time
import re 
import json 

all_voices = { }


elevenapikey = "" # add your api key here 

def remove_emojis(text):
    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"  
                               u"\U0001F300-\U0001F5FF"  
                               u"\U0001F680-\U0001F6FF"  
                               u"\U0001F1E0-\U0001F1FF"  
                               u"\U00002500-\U00002BEF"  
                               u"\U00002702-\U000027B0"
                               u"\U00002702-\U000027B0"
                               u"\U000024C2-\U0001F251"
                               u"\U0001f926-\U0001f937"
                               u"\U00010000-\U0010ffff"
                               u"\u2640-\u2642"
                               u"\u2600-\u2B55"
                               u"\u200d"
                               u"\u23cf"
                               u"\u23e9"
                               u"\u231a"
                               u"\ufe0f"  
                               u"\u3030"
                               "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', text)

def get_voices(elevenapikey):
    headers = {
        "xi-api-key": elevenapikey
    }

    parsed_voices = { }
    voices = requests.get("https://api.elevenlabs.io/v1/voices", headers=headers).json()

    details = voices.get("detail")

    if details and details.get("status"):
        print(colored(details.get("message"), "red"))
        exit()
    
    voices = voices['voices']
    
    print(colored("Available voices: ", "blue"))

    for voice in voices:
        category = voice["category"]
        name = remove_emojis(voice["name"]).strip()
        all_voices[name] = voice["voice_id"]
        print(colored(f"    - {name} ({category})", "light_blue"))

    return parsed_voices


get_voices(elevenapikey)

while True: 
    voice_input = input(colored("Select your voice: ", "light_green"))
    voice_id = all_voices.get(voice_input)
    if voice_id:
        break
    else:
        print(colored("Couldn't find that voice", "red"))

mixer.init() 
mixer.quit() 
mixer.init(devicename='CABLE Input (VB-Audio Virtual Cable)') 


def tts_endpoint(Text):
    VoiceData = requests.post(f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}", headers = {
        "xi-api-key" : elevenapikey
    }, json = {
        "text" : Text 
    })
    return VoiceData.content

def elevenlabs_tts(Text):
    audio_blob = tts_endpoint(Text)

    if len(audio_blob) <= 200: 
        try:
            load = json.loads(audio_blob)
            details = load["detail"]
            error_type = details["status"]
            message = details["message"]

            print(f'''
{colored("ElevenLabs returned an error", "light_red")}:
    {colored(f'- Error type: "{error_type}"', "red")}
    {colored(f'- More details: "{message}"', "red")}
                ''')

            return None
        except Exception:
            return None

    return io.BytesIO(audio_blob) 

def play_audio(audio_file):
    file_path = "temp_audio.mp3"

    with open(file_path, 'wb') as f:
        f.write(audio_file.getvalue())


    mixer.music.load(file_path)
    mixer.music.set_volume(1.0)
    mixer.music.play()

    while mixer.music.get_busy():
        time.sleep(0.1)

    mixer.music.stop()
    mixer.music.unload()
    os.remove(file_path)


while True:
    text = input("Type what you'd like to say: ")
    voice_audio = elevenlabs_tts(text)

    if not voice_audio:
        print(colored("Failed to process audio", "red"))
        continue
    play_audio(voice_audio)
