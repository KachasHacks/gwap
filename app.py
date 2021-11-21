import click
import os
import pprint
from modzy import ApiClient
from modzy._util import file_to_bytes
from dotenv import load_dotenv
from pydub import AudioSegment as am

load_dotenv()


client = ApiClient(base_url="https://app.modzy.com/api", api_key=os.environ["MODZY_API_KEY"])

sources = {}
sound = am.from_mp3('mc8.mp3')
sound = sound.set_frame_rate(16000)
sound.export('test.wav', format='wav')
#Add any number of inputs
sources["my-input"] = {
    "word.txt": file_to_bytes('word.txt'),
    "input.wav": file_to_bytes('test.wav'),
}
#Once you are ready, submit the job

@click.command()
def hello():
    click.echo("Hello world")
    job = client.jobs.submit_file("s25ge4ufw4", "0.0.1", sources)
    click.echo(f"job: {job}")
    results = client.results.block_until_complete(job, timeout=None)
    click.echo(results)
    pprint.pprint(results)

if __name__ == "__main__":
    hello()
