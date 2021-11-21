import click
import os
import pprint
from modzy import ApiClient
from modzy._util import file_to_bytes
from dotenv import load_dotenv
from pydub import AudioSegment as am

load_dotenv()


client = ApiClient(base_url="https://app.modzy.com/api", api_key=os.environ["MODZY_API_KEY"])


def process_words(words):
    with open("words.txt", "w") as f:
        for word in words:
            f.write(f"{word}\n")

def process_audio(file):
    sound = am.from_file(file)
    sound = sound.set_frame_rate(16000)
    sound.export('temp.wav', format='wav')

@click.command()
@click.argument('words', nargs=-1)
@click.argument('file', nargs=1)
def au_grep(words, file):
    process_words(words)
    process_audio(file)
    sources = {}
    sources["my-input"] = {
        "word.txt": file_to_bytes('words.txt'),
        "input.wav": file_to_bytes('temp.wav'),
    }
    job = client.jobs.submit_file("s25ge4ufw4", "0.0.1", sources)
    results = client.results.block_until_complete(job, timeout=None)
    if results["failed"] == 0:
        for result in results["results"]["my-input"]["results.json"]:
            # Note that the audio keyword spotting has a weird key for start_time: "start_time " with a space
            click.echo(f'{result["word"]}, Start time: {result["start_time "]}, Duration: {result["duration"]}s')

if __name__ == "__main__":
    au_grep()
