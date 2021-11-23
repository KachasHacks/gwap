import click
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
    for root, directory, files in os.walk('.'):
        if ".git" in root:
            continue
        for file in files:
            if file.split(".")[1] in AUDIO_FILE_TYPES:
                click.echo(os.path.join(root, file))
                process_audio(os.path.join(root, file))

def get_all_sources():
    sources = {}
    for root, directory, files in os.walk('.'):
        if ".git" in root:
            continue
        for file in files:
            if "-temp" in file:
                click.echo(os.path.join(root, file))
                sources[f"{file}-input"] = {
                        "word.txt": file_to_bytes('words.txt'),
                        "input.wav": file_to_bytes(os.path.join(root, file))
                        }

    return sources



@click.command()
@click.argument('words', nargs=-1)
@click.argument('file', nargs=1, type=click.Path(exists=True))
@click.option('-r', is_flag=True)
def au_grep(words, file, r):
    process_words(words)
    # process_audio(file)
    sources = {}
    if r:
        process_multiple_audio_files(file)
        sources = get_all_sources()
        job = client.jobs.submit_file("s25ge4ufw4", "0.0.1", sources)
        results = client.results.block_until_complete(job, timeout=None)
        if results["failed"] == 0:
            for job in sources.keys():
                for result in results["results"][job]["results.json"]:
                    # note that the audio keyword spotting has a weird key for start_time: "start_time " with a space
                    click.echo(f'{job}: {result["word"]}, start time: {result["start_time "]}, duration: {result["duration"]}s')
    else:
        name = process_audio(file)

        sources["my-input"] = {
            "word.txt": file_to_bytes('words.txt'),
            "input.wav": file_to_bytes(f'{name}'),
        }
        job = client.jobs.submit_file("s25ge4ufw4", "0.0.1", sources)
        results = client.results.block_until_complete(job, timeout=None)
        if results["failed"] == 0:
            for result in results["results"]["my-input"]["results.json"]:
                # note that the audio keyword spotting has a weird key for start_time: "start_time " with a space
                click.echo(f'{result["word"]}, start time: {result["start_time "]}, duration: {result["duration"]}s')

if __name__ == "__main__":
    au_grep()
