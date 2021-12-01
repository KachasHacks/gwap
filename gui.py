import eel, os, random
import os
import pprint
from modzy import ApiClient
from modzy._util import file_to_bytes
from dotenv import load_dotenv
from pydub import AudioSegment as am

load_dotenv()


client = ApiClient(base_url="https://app.modzy.com/api", api_key=os.environ["MODZY_API_KEY"])

AUDIO_FILE_TYPES = ['mp3']

def process_words(words):
    with open("words.txt", "w") as f:
        for word in words:
            f.write(f"{word}\n")

def process_audio(file):
    sound = am.from_file(file)
    sound = sound.set_frame_rate(16000)
    sound.export(f'{file}-temp.wav', format='wav')
    return f'{file}-temp.wav'

def process_multiple_audio_files(file_path ):
    for root, directory, files in os.walk(file_path):
        if ".git" in root:
            continue
        for file in files:
            print(file)
            try:
                ext = file.split('.')[1]
            except IndexError:
                continue
            if ext in AUDIO_FILE_TYPES:
                process_audio(os.path.join(root, file))

def get_all_sources():
    sources = {}
    for root, directory, files in os.walk('.'):
        if ".git" in root:
            continue
        for file in files:
            if "-temp" in file:
                sources[f"{file}-input"] = {
                        "word.txt": file_to_bytes('words.txt'),
                        "input.wav": file_to_bytes(os.path.join(root, file))
                        }

    return sources

eel.init('web')

@eel.expose
def pick_file(folder):
    if os.path.isdir(folder):
        process_multiple_audio_files(folder)
        sources = get_all_sources()
        job = client.jobs.submit_file("s25ge4ufw4", "0.0.1", sources)
        results = client.results.block_until_complete(job, timeout=None)
        if results["failed"] == 0:
            lines = ''
            for job in sources.keys():
                for result in results["results"][job]["results.json"]:
                    lines += f'{job}: {result["word"]}, start time: {result["start_time "]}, duration: {result["duration"]}s <br />'
            pprint.pprint(results["results"])
            return lines 
        return "Something failed"
    else:
        return 'Not valid folder'

eel.start('index.html', size=(600, 400))
