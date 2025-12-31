import os, sys
import pyaudio
import wave
import threading
import time
import whisper
import numpy
import ollama
#import piper

FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
CHUNK = 1024
WAVE_OUTPUT_FILENAME = "file.wav"

#llm_name = 'ministral-3:3b'
#llm_name = 'gemma3:270m'
llm_name = 'gemma3:1b'

#whisper_model = 'base.en'
whisper_model = 'small'

class Assistant:
    def __init__(self, do_audio=True, audio_filename=None):
        self.do_audio = do_audio
        self.audio_filename = audio_filename
        self.started = False
        self.t = None
        self.frames = []

        print('Initializing audio...')
        if do_audio:
            self.audio = pyaudio.PyAudio()

        print("Loading the audio model...\n")
        self.audio_model = whisper.load_model(whisper_model)
        print("Model loaded.\n")

    def help(self):
        print('')
        print('Press "q" + [Enter] to quit')
        print('Press [Enter] to start talking.')
        print('Press [Enter] again once finished.')

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
        if self.do_audio:
            self.audio.terminate()
            self.audio = None

        if exc_val:
            raise

    def stop(self):
        print('Stop')
        if self.t is not None:
            self.started = False
            self.t.join()
            self.t = None
        if self.do_audio:
            self.stream = None

    def record(self):
        self.started = True
        self.frames = []
        self.t = threading.Thread(target=assistant._record, args=())
        self.t.start()

    def _record(self):
        num = 0

        # start Recording
        if self.do_audio:
            self.stream = self.audio.open(format=FORMAT, channels=CHANNELS,
                            rate=RATE, input=True,
                            frames_per_buffer=CHUNK)
            print ("recording start ...")

        while self.started:
            if self.do_audio:
                data = self.stream.read(CHUNK)
                num += 1
                self.frames.append(data)
            else:
                print('Just sleeping', 'started', self.started)
                time.sleep(1)

        # stop recording
        if self.do_audio:
            print('recording done!')
            self.stream.stop_stream()
            self.stream.close()

            waveFile = wave.open(self.audio_filename, 'wb')
            waveFile.setnchannels(CHANNELS)
            waveFile.setsampwidth(self.audio.get_sample_size(FORMAT))
            waveFile.setframerate(RATE)
            waveFile.writeframes(b''.join(self.frames))
            waveFile.close()
            waveFile = None

    def transcribe(self):
        result = self.audio_model.transcribe(self.audio_filename)
        print(type(result), result)
        text = result['text'].strip()
        print('Transcription', text)
        return text

#    def ask_llm(self, text):

if __name__ == '__main__':
    do_audio = '--do_audio' in sys.argv
    do_speak = '--do_speak' in sys.argv
    do_llm = '--do_llm' in sys.argv
    with Assistant(do_audio=do_audio, audio_filename=WAVE_OUTPUT_FILENAME) as assistant:
        while True:
            assistant.help()
            res = input('')
            if res == 'q':
                break

            print ("start recording")
            assistant.record()
            res =  input('')
            print ("stop recording")

            assistant.stop()
            if res == 'q':
                break

            text = assistant.transcribe()

            if not do_llm:
                continue

            print('Asking to llm', llm_name)
            stream = ollama.chat(
                    model = llm_name, 
                    messages = [{'role': 'user', 'content': text}],
                    stream = True,
            )
            if do_speak:
                es = PiperVoice.load("en_US-lessac-medium.onnx")
            for chunk in stream:
                if do_speak:
                    es.say(chunk['message']['content'], sync=True)
                print(chunk['message']['content'], end='', flush=True)
            stream = None
            es = None
