#!/usr/bin/env python

# Copyright (C) 2017 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import print_function

import sys

#Changes
import speech_recognition as sr
from gtts import gTTS
import os

import argparse
import json
import os.path
import pathlib2 as pathlib


import google.oauth2.credentials

from google.assistant.library import Assistant
from google.assistant.library.event import EventType
from google.assistant.library.file_helpers import existing_file
from google.assistant.library.device_helpers import register_device

from google.cloud import texttospeech

import alsaaudio
from playsound import playsound
import pygame
import time

try:
    FileNotFoundError
except NameError:
    FileNotFoundError = IOError

global INPUT, GA_RESPONSE, SPEED, SOUND_LEVEL, PITCH

INPUT = 'Pre-input'
SPEED = 'normal'
PITCH = 'medium'
SOUND_LEVEL = 'medium'
GA_RESPONSE = ''

MIXER = alsaaudio.Mixer()

WARNING_NOT_REGISTERED = """
    This device is not registered. This means you will not be able to use
    Device Actions or see your device in Assistant Settings. In order to
    register this device follow instructions at:

    https://developers.google.com/assistant/sdk/guides/library/python/embed/register-device
"""


def process_event(event):
    """Pretty prints events.

    Prints all events that occur with two spaces between each new
    conversation and a single space between turns of a conversation.

    Args:
        event(event.Event): The current event to process.
    """
    
    global INPUT, GA_RESPONSE
    MIXER.setvolume(0)

    text = ''
    if event.type == EventType.ON_CONVERSATION_TURN_STARTED:
        print('Convo has begun')

    print()
    print('The type is {0}'.format(event.type))
    #print('Printing out the event now...\n{0}'.format(event))
    
    if (event.type == EventType.ON_RENDER_RESPONSE):
        print("Rendering response")
        text = event.args['text'] #transcript given by GA
        #print('GA += {0}'.format(event.args['text']))
        GA_RESPONSE += (' ' + event.args['text'])
        print()

    #if (event.type == EventType.ON_CONVERSATION_TURN_FINISHED and
     #       event.args and not event.args['with_follow_on_turn']):
      #  print()
       # pickup = listener()
        #speak(pickup)
        
    if event.type == EventType.ON_RESPONDING_STARTED:
        print("I shall talk now")
        #time.sleep(2)
        #os.system("ffmpeg -f pulse -ac 2 -ar 44100 -i default -t 6 -y response.wav")
    
    if ( event.type == EventType.ON_RECOGNIZING_SPEECH_FINISHED ):
        INPUT = event.args['text'] #voice input from user
        print('INPUT IS NOW: ' + INPUT)
        update_settings()
        #print('You said: {0}'.format(event.args['text']))
     
       
    if (event.type == EventType.ON_CONVERSATION_TURN_FINISHED):
        print("ENDING CONVERSATION")
        MIXER.setvolume(100)
        os.system('mpg321 output.mp3')
        if (os.path.exists('output.mp3')):
            print("Removing file")
            os.remove('output.mp3')
        
     
    if ( event.type == EventType.ON_RESPONDING_STARTED ):
        GA_RESPONSE = ''

    if event.type == EventType.ON_DEVICE_ACTION:
        for command, params in event.actions:
            print('Do command', command, 'with params', str(params))
            
    return text

def update_settings():
    global SPEED, PITCH, SOUND_LEVEL
    #Fix if statements
    print(INPUT.split(' '))
    
    if 'fast' == INPUT.split(" ")[0]:
        SPEED = 'fast'
        print("Speed is now fast")
    elif 'faster' == INPUT.split(" ")[0]:
        SPEED = 'faster'
        print("Speed is now faster")
    elif 'fastest' == INPUT.split(" ")[0]:
        SPEED = 'fastest'
    elif ('slow' == INPUT.split(" ")[0]):
        print("Speed is now slow")
        SPEED = 'slow'
    elif ('normal' == INPUT.split(" ")[0]):
        print("Speed is normal")
        SPEED = 'normal'

    if 'high pitch' == INPUT.split(" ")[:2]:
        print("pitch is now high")
        PITCH = 'high'
    elif 'low pitch' == INPUT.split(" ")[:2]:
        print("pitch is now low")
        PITCH = 'low'
    elif ('normal pitch' == INPUT.split(" ")[:2]):
        print("pitch is medium")
        PITCH = 'medium'
        
    if ('loud' == INPUT.split(" ")[0]):
        print("Volume is loud")
        SOUND_LEVEL = 'loud'
    elif ('soft' == INPUT.split(" ")[0]):
        print("Volume is soft")
        SOUND_LEVEL = 'soft'
    elif ( 'normal' == INPUT.split(" ")[0]):
        print("Volume is medium")
        SOUND_LEVEL = 'medium'



def speak(string_to_repeat):
    string_to_repeat += "."
    tts = gTTS( text=(string_to_repeat), lang = "en", slow = False )
    #tts.save('output.mp3')
    os.system("omxplayer -o local output.mp3")
    
    
def listener():
    r = sr.Recognizer()
    with sr.AudioFile("response.wav") as source:
        print("Reading File...")
        audio = r.listen(source)
        
        data = ""
        
        try:
            print("processing")
            time.sleep(1)
            data = r.recognize_google(audio)
            print("~~~~~Loopback Response: " + data)
            
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand your audio")
        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition service: {0}".format(e))
        return data


def synthesize_ssml(ssml):
    """Synthesizes speech from the input string of ssml.
    Note: ssml must be well-formed according to:
        https://www.w3.org/TR/speech-synthesis/
    Example: <speak>Hello there.</speak>
    """
    global INPUT, SPEED, SOUND_LEVEL, PITCH
    
    client = texttospeech.TextToSpeechClient()

    #ssml = "<speak>Team BETA is literally the bset team ever made of all time ever, seriously</speak>"
    
    if SPEED == 'fast' or SPEED == 'faster' or SPEED == 'fastest':
        ssml = ssml.split(' ')

        for index, word in enumerate(ssml):
            if (index+1)%2 == 0:
                ssml[index] += "<break time = '0.1s'/>"
    
        ssml = ' '.join(ssml)        


    ssml_conv = "<speak><prosody"
    
    if SPEED == "fast":
        ssml_conv += " rate='160%'"
    elif SPEED == 'faster':
        ssml_conv += " rate='175%'"
    elif SPEED == 'fastest':
        ssml_conv += " rate='200%'"
    elif SPEED == "slow":
        ssml_conv += " rate='80%'"
    elif SPEED == "normal":
        ssml_conv += " rate='100%'"

    

    if PITCH == "high":
        ssml_conv += " pitch='high'"
    elif PITCH == "low":
        ssml_conv += " pitch='low'"
    elif PITCH == "medium":
        ssml_conv += " pitch='medium'"
    
    
    if SOUND_LEVEL == "loud":
        ssml_conv += " volume='+50.0dB'"
    elif SOUND_LEVEL == "soft":
        ssml_conv += " volume='soft'"
    elif SOUND_LEVEL == "medium":
        ssml_conv += " volume='medium'"
    
    ssml_conv += ">" + ssml
    ssml_conv += "</prosody></speak>"
    
    print()
    print('THIS IS YORUR INPUT: ' + INPUT)
    print(ssml_conv)

    input_text = texttospeech.types.SynthesisInput(ssml=ssml_conv)

    # Note: the voice can also be specified by name.
    # Names of voices can be retrieved with client.list_voices().
    voice = texttospeech.types.VoiceSelectionParams(
        language_code='en-US',
        ssml_gender=texttospeech.enums.SsmlVoiceGender.FEMALE)

    audio_config = texttospeech.types.AudioConfig(
        audio_encoding=texttospeech.enums.AudioEncoding.MP3)

    response = client.synthesize_speech(input_text, voice, audio_config)

    # The response's audio_content is binary.
    

    
    with open('output.mp3', 'wb') as out:
        out.write(response.audio_content)
        print('Audio content written to file "output.mp3"')
      
    

def main():
    
   
    commands = sys.argv[2:]
    
    print(commands)
    
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--device-model-id', '--device_model_id', type=str,
                        metavar='DEVICE_MODEL_ID', required=False,
                        help='the device model ID registered with Google')
    parser.add_argument('--project-id', '--project_id', type=str,
                        metavar='PROJECT_ID', required=False,
                        help='the project ID used to register this device')
    parser.add_argument('--device-config', type=str,
                        metavar='DEVICE_CONFIG_FILE',
                        default=os.path.join(
                            os.path.expanduser('~/.config'),
                            'googlesamples-assistant',
                            'device_config_library.json'
                        ),
                        help='path to store and read device configuration')
    parser.add_argument('--credentials', type=existing_file,
                        metavar='OAUTH2_CREDENTIALS_FILE',
                        default=os.path.join(
                            os.path.expanduser('~/.config'),
                            'google-oauthlib-tool',
                            'credentials.json'
                        ),
                        help='path to store and read OAuth2 credentials')
    parser.add_argument('-v', '--version', action='version',
                        version='%(prog)s ' + Assistant.__version_str__())

    args = parser.parse_args()
    with open(args.credentials, 'r') as f:
        credentials = google.oauth2.credentials.Credentials(token=None,
                                                            **json.load(f))

    device_model_id = None
    last_device_id = None
    try:
        with open(args.device_config) as f:
            device_config = json.load(f)
            device_model_id = device_config['model_id']
            last_device_id = device_config.get('last_device_id', None)
    except FileNotFoundError:
        pass

    if not args.device_model_id and not device_model_id:
        raise Exception('Missing --device-model-id option')

    # Re-register if "device_model_id" is given by the user and it differs
    # from what we previously registered with.
    should_register = (
        args.device_model_id and args.device_model_id != device_model_id)

    device_model_id = args.device_model_id or device_model_id

    with Assistant(credentials, device_model_id) as assistant:
        events = assistant.start()

        device_id = assistant.device_id
        #print('device_model_id:', device_model_id)
        #print('device_id:', device_id + '\n')

        # Re-register if "device_id" is different from the last "device_id":
        if should_register or (device_id != last_device_id):
            if args.project_id:
                register_device(args.project_id, credentials,
                                device_model_id, device_id)
                pathlib.Path(os.path.dirname(args.device_config)).mkdir(
                    exist_ok=True)
                with open(args.device_config, 'w') as f:
                    json.dump({
                        'last_device_id': device_id,
                        'model_id': device_model_id,
                    }, f)
            else:
                print(WARNING_NOT_REGISTERED)

        for event in events:
            text = ''
            text = process_event(event)
            #print("The list from event is {0}".format(text))
            
            if (text != ''):
                synthesize_ssml(GA_RESPONSE)
                
                        



if __name__ == '__main__':
    # parser = argparse.ArgumentParser()
    # --device_model_id talk-to-me-f6d3d-sdkpi-8k7r91
    # parser.add_argument('--speed', default='normal', choices=['slow', 'normal', 'fast'],  help='this will set the response speed')
    # parser.add_argument('--device_model_id', type=str, default='talk-to-me-f6d3d-sdkpi-8k7r91', help="")
    # args = parser.parse_args()
    # print(args)

    
    main()

