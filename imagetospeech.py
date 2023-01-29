import io
import os
from google.cloud import vision
from google.cloud import texttospeech
from PIL import Image
import pyaudio
import wave

def image_to_speech(image_file):
    # Authenticate and construct the Vision client
    client = vision.ImageAnnotatorClient()

    # Open the image file
    with io.open(image_file, 'rb') as image:
        content = image.read()

    # Use the Vision client to detect text in the image
    response = client.text_detection(image=vision.types.Image(content=content))
    text = response.text_annotations[0].description

    # Authenticate and construct the Text-to-Speech client
    client = texttospeech.TextToSpeechClient()

    # Set the text and voice attributes
    synthesis_input = texttospeech.types.SynthesisInput(text=text)
    voice = texttospeech.types.VoiceSelectionParams(
        language_code='en-US',
        ssml_gender=texttospeech.enums.SsmlVoiceGender.NEUTRAL)
    audio_config = texttospeech.types.AudioConfig(
        audio_encoding=texttospeech.enums.AudioEncoding.MP3)

    # Perform the text-to-speech request on the text input with the selected voice parameters and audio settings
    response = client.synthesize_speech(synthesis_input, voice, audio_config)

    # The response's audio_content is binary.
    with open('output.mp3', 'wb') as out:
        out.write(response.audio_content)
        print('Audio content written to file "output.mp3"')
   
    CHUNK = 1024

    wf = wave.open("output.mp3", 'rb')

    p = pyaudio.PyAudio()

    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
                output=True)

    data = wf.readframes(CHUNK)

    while len(data) > 0:
        stream.write(data)
        data = wf.readframes(CHUNK)

    stream.stop_stream()
    stream.close()

    p.terminate()
