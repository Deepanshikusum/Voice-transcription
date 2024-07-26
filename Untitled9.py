#!/usr/bin/env python
# coding: utf-8

# In[ ]:


get_ipython().run_line_magic('pip', 'install ipywidgets')


# In[8]:


import ipywidgets as widgets
from IPython.display import display
from threading import Thread
from queue import Queue

messages=Queue()
recordings=Queue()

record_button=widgets.Button(
    description="Record",
    disabled=False,
    button_style="success",
    icon="microphone"
)
stop_button=widgets.Button(
    description="stop",
    disabled=False,
    button_style="warning",
    icon="microphone"
)
output=widgets.Output()

def sr(data):
    messages.put(True)
    
    with output:
        display("Starting Love..")
        record=Thread(target=record_microphone)
        record.start()
        transcribe=Thread(target=speech_recognition,args=(output,))
        transcribe.start()

def stop_recording(data):
    with output:
        messages.get()
        display("chup")

record_button.on_click(sr)
stop_button.on_click(stop_recording)

display(record_button,stop_button,output)


# In[ ]:


get_ipython().run_line_magic('pip', 'install pyaudio')


# In[ ]:


import pyaudio

p=pyaudio.PyAudio()
for i in range(p.get_device_count()):
    print(p.get_device_info_by_index(i))
p.terminate()


# In[13]:


CHANNELS=1
FRAME_RATE=16000
RECORD_SECONDS=20
AUDIO_FORMAT=pyaudio.paInt16
SAMPLE_SIZE=2

def record_microphone(chunk=1024):
    p=pyaudio.PyAudio()
    stream=p.open(format=AUDIO_FORMAT,
                 channels=CHANNELS,
                 rate=FRAME_RATE,
                 input=True,
                 input_divice_index=1,
                 frames_per_buffer=chunk)
    frames=[]
    while not messages.empty():
        data=stream.read(chunk)
        frames.append(data)
        
        if len(frames)>=(FRAME_RATE*RECORD_SECONDS)/chunk:
            recordings.put(frames.copy())
            frames=[]
    stream.stop_stream()
    stream.close()
    p.terminate()


# In[ ]:


import subprocess
import json
from vosk import Model,KaldiRecognizer

model=Model(model_name="")
rec=KaldiRecognizer(model,FRAME_RATE)
rec.SetWords(True)

def speech_recognition(output):
    while not messages.empty():
        frames=recordings.get()
        rec.AcceptWaveform(b''.join(frames))
        result=rec.Result()
        text=json.loads(result)["text"]
        
        cased=subprocess.check_output()
        output.append_stdout(cased)
        time.sleep(1)

