# External Imports

import threading
import os
import audioread
import pyaudio
import wave
from pydub import AudioSegment #convert mp3 to wav
import soundfile #convert to 16-bit depth

import numpy

# Internal Imports

from manager import *
from visualizer import *

class AudioPlayer(pyaudio.PyAudio):
    def __init__(self):
        super().__init__()
        self.playing = False
        self.audioPlaying = ''
        self.audioDuration = 0
        self.progress = 0 #percentage
        self.secondsProgress = 0 #seconds
        self.audioThread = None
        self.event = threading.Event()
        self.progressVar = None
        self.songStringVar = None
        self.wf = None
        self.chunktotal = 0

        self.manager = None
        self.visualizer = None

        self.volume = None

        #GUI STuff
        self.btn = None
        self.playImage = None
        self.pauseImage = None

        self.timeStampString = None

    def clear_player(self):
        self.playing = False
        self.audioPlaying = ''
        self.manager.currentSongString.set('No song playing')
        self.progress = 0
        self.secondsProgress = 0
        self.btn['image'] = self.playImage
        self.event.set()

    def pause(self):
        self.playing = False
        self.btn['image'] = self.playImage
        self.event.set()


    def setAudioFile(self, fileid, directory):
        self.event.set()
        print(fileid)
        filepath = os.popen(fr"fsutil file queryfilenamebyid {directory} {fileid}").read()
        filepath = filepath.split('?\\')[1]
        filepath.replace('\n', '')
        
        self.audioPlaying = filepath
        self.audioDuration = 0
        

    def playAudioFile(self, start=0):
        # Allow
        self.event.clear()

        #Convert mp3 to wav first
        if self.audioPlaying.endswith('.mp3'):
            sound = AudioSegment.from_mp3(self.audioPlaying)
            self.audioPlaying = sound.export(format="wav")
        
        self.audioThread = threading.Thread(target=self.playAudio, args = (start,))
        self.audioThread.start()
    
    def playAudio(self, start=0):
        print('ran through here')
        self.playing = True
        # Set chunk size of 1024 samples per data frame
        chunk = 1024
        #storing how much we have read already
        print(self.audioPlaying)
        # Open the sound file 
        self.wf = wave.open(self.audioPlaying.replace('\n', ''), 'rb')

        self.chunktotal = 0 + int(start * self.wf.getframerate())
        
        #Get total duration in seconds
        self.audioDuration = self.wf.getnframes() / float(self.wf.getframerate())
        print(self.audioDuration)
        
        # Open a .Stream object to write the WAV file to
        # 'output = True' indicates that the sound will be played rather than recorded
        stream = self.open(format = self.get_format_from_width(self.wf.getsampwidth()),
                        channels = self.wf.getnchannels(),
                        rate = self.wf.getframerate(),
                        output = True)

        # skip unwanted frames
        n_frames = int(start * self.wf.getframerate())
        self.wf.setpos(n_frames)
        
        # Read data in chunks
        data = self.wf.readframes(chunk)
        print(chunk)

        # Play the sound by writing the audio data to the stream
        while self.progress < 100:
            #volume stuff
            sound_level = self.volume.get() / 100
            data = numpy.frombuffer(data, numpy.int16)
            data = data * sound_level
            data_int = data.astype(numpy.int16)
            data = data_int.tobytes()

            
            #main 
            stream.write(data)
            
            self.visualizer.show_audio_data(data_int)
            
            self.chunktotal = self.chunktotal + chunk
            #calculating the percentage
            self.progress = (self.chunktotal/self.wf.getnframes())*100
            self.progressVar.set(self.progress)
            
            #calculating the current seconds
            self.secondsProgress = self.chunktotal/float(self.wf.getframerate())

            #update timestamp string
            self.timeStampString.set(time.strftime("%M:%S", time.gmtime(self.secondsProgress)) + ' / ' + time.strftime("%M:%S", time.gmtime(self.audioDuration)))

            
            data = self.wf.readframes(chunk)

            #Gtfo if its paused; should update later to check if song has been changed otherwise do not break out of the loop for performance sake
            if self.event.is_set():
                return False


        self.progress = 100
        self.secondsProgress = self.audioDuration

        print('Finished playing song')
        #self.playing = False
        #self.btn['image'] = self.playImage
        self.progress = 0
        self.progressVar.set(0)
        if self.manager.repeat == False:
            self.manager.change_song(1)
        else:
            self.manager.change_song(0)
        
        # Close and terminate the stream
        stream.close()
        #self.terminate()
