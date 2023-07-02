from tkinter import *
from tkinter import ttk
from tkinter import filedialog
import tkinter as Tkinter
from tkinterdnd2 import *

from PIL import ImageTk, Image
from ttkwidgets import TickScale



import threading
import os
import audioread
import pyaudio
import wave
from pydub import AudioSegment #convert mp3 to wav
import soundfile #convert to 16-bit depth

import numpy

import time

import random

import re

# Music Player

class Song():
    def __init__(self, fileid, filename, duration, coverImg = None):
        self.fileid = fileid
        self.filename = filename
        
        self.coverImg = coverImg
        self.duration = duration #(hours, minutes, seconds)
        
class FakeEvent(): #to send to listbox
    def __init__(self, y):
        self.y = y
    
class MusicPlayerWindow(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.currentSongName = StringVar()
        self.currentSongName.set('No song playing')
        self.manager = SongManager(self.currentSongName)
        self.progressVar = DoubleVar()
        self.progressVar.set(0)
        self.volumeVar = IntVar()
        self.volumeVar.set(100)
        self.manager.player.progressVar = self.progressVar

        self.timeStampString = StringVar()
        self.timeStampString.set('00:00 // 00:00')

        self.songlistVar = StringVar()

        self.geometry('800x800')
        self.iconbitmap("icon.ico")
        self.title("VisualPlayer")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)
        self.backgroundColor = 'white'
        self['bg'] = self.backgroundColor
            
        

        self.manager.currentSongVar = self.currentSongName
        self.manager.window = self

        self.manager.songlistVar = self.songlistVar

        #Image files
        
        self.anime = [self.process_image('render.png', 400, 334), self.process_image('doro.png', 200, 200)]
        self.defaultCover = self.process_image('music-note.jpg', 200, 200)
        self.playImage = self.process_image('play.png', 50, 50)
        self.pauseImage = self.process_image('pause.png', 50, 50)
        self.nextImage = self.process_image('next.png', 25, 25)
        self.previousImage = self.process_image('previous.png', 25, 25)
        self.shuffleImage = self.process_image('shuffle.png', 25, 25)
        self.greenShuffleImage = self.process_image('shuffle_green.png', 25, 25)
        self.repeatImage = self.process_image('repeat.png', 25, 25)
        self.greenRepeatImage = self.process_image('repeat_green.png', 25, 25)
        self.addImage = self.process_image('add.png', 25, 25)
        self.deleteImage = self.process_image('delete.png', 25, 25)
        self.volumeImage = self.process_image('volume.png', 25, 25)
        #Label(self, image=self.anime[0]).place(x=350, y=350)
        #Label(self, image=self.anime[1], bg=self.backgroundColor).place(x=160, y=210)
        
        #info for custom scale
        trough = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x02\x00\x00\x00\x02\x08\x06\x00\x00\x00r\xb6\r$\x00\x00\x00\tpHYs\x00\x00\x0e\xc3\x00\x00\x0e\xc3\x01\xc7o\xa8d\x00\x00\x00\x19tEXtSoftware\x00www.inkscape.org\x9b\xee<\x1a\x00\x00\x00\x15IDAT\x08\x99c\\\xb5j\xd5\x7f\x06\x06\x06\x06&\x06(\x00\x00.\x08\x03\x01\xa5\\\x04^\x00\x00\x00\x00IEND\xaeB`\x82'
        self.img_trough = PhotoImage(master=self, data=trough)
        self.img_slider = PhotoImage(master=self, width=10, height=30)
        self.fill(self.img_slider, (0,0,0))

        
        

        self.songItemColor = 'white'
        self.selectedSongItemColor = 'blue'
        self.playingSongItemColor = 'black'

        # Create Custom Scale


        

        #Bindings

        self.bind('<space>', lambda e: self.toggleBtn.invoke())
        self.bind("<Return>", lambda e: self.manager.play(self.manager.songlist[self.songlist.curselection()[0]]))
        self.bind("<Down>", lambda e: self.songlist.setCurrent(e, factor=1))
        self.bind("<Up>", lambda e: self.songlist.setCurrent(e, factor=-1))
        self.bind("<Delete>", self.manager.delete_song)

        #Draw Window

        self.create_scale_style()
        self.draw_window()

        

        self.manager.player.playImage = self.playImage
        self.manager.player.pauseImage = self.pauseImage
        self.manager.player.btn = self.toggleBtn
        self.manager.player.timeStampString = self.timeStampString
        self.manager.player.volume = self.volumeVar

    def fill(self,image, color):
        """Fill image with a color=(r,g,b)."""
        r,g,b = color
        width = image.width()
        height = image.height()
        hexcode = "#%02x%02x%02x" % (r,g,b)
        horizontal_line = "{" + " ".join([hexcode]*width) + "}"
        image.put(" ".join([horizontal_line]*height))

    def process_image(self, imagefile, width, height):
        #Load an image in the script
        img= (Image.open(imagefile))

        #Resize the Image using resize method
        resized_image= img.resize((width,height), Image.ANTIALIAS)
        new_image= ImageTk.PhotoImage(resized_image)

        return new_image

    def create_scale_style(self):
        # create images used for the theme (instead of using the data option, it is 
        # also possible to use .gif or .png files)

        style = ttk.Style(self)
        # create scale elements
        style.element_create('custom.Scale.trough', 'image', self.img_trough)
        style.element_create('custom.Scale.slider', 'image', self.img_slider)
        # create custom layout
        style.layout('custom.Horizontal.TScale',
                     [('custom.Scale.trough', {'sticky': 'ew'}),
                      ('custom.Scale.slider',
                       {'side': 'left', 'sticky': ''
                        })])
        style.configure('custom.Horizontal.TScale', background=self.backgroundColor)


    def draw_window(self):

        
        self.songFrame = Frame(self, bg=self.backgroundColor)
        self.songFrame.grid(column=0,row=0, sticky='EW', padx=80, pady=40)
        self.songlistFrame = Frame(self, bg=self.backgroundColor)
        self.songlistFrame.grid(column=0, row=1, sticky='NSW', padx=80)
        self.audioVisualizerFrame = Frame(self, bg=self.backgroundColor, bd=0)
        self.audioVisualizerFrame.grid(column=0, row=1, sticky='NSE')

        self.songFrame.columnconfigure(0, weight=6)
        self.songFrame.columnconfigure(1, weight=1)
        self.songFrame.columnconfigure(2, weight=1)
        self.songFrame.rowconfigure(0, weight=1)
        self.songFrame.rowconfigure(1, weight=1)
        self.songFrame.rowconfigure(2, weight=1)
        
        self.currentCover = ttk.Label(self.songFrame, image=self.defaultCover, borderwidth=5, relief='groove')
        self.currentCover.grid(column=0, row=0, rowspan=2)

        self.songInfoFrame = Frame(self.songFrame, bg=self.backgroundColor)
        self.songInfoFrame.grid(column=2, row=0)

        self.songVolumeFrame = Frame(self.songFrame, bg=self.backgroundColor)
        self.songVolumeFrame.grid(column=3, row=0)
                
        self.currentSongLabel = Label(self.songInfoFrame, textvariable=self.currentSongName, width=32, bg=self.backgroundColor)
        self.currentSongLabel.grid(column=2, row=0, sticky='N')
        Label(self.songInfoFrame, textvariable = self.timeStampString, bg=self.backgroundColor).grid(column=2, row=2)

        self.progress = CustomScale(self.songInfoFrame, orient='horizontal', variable=self.progressVar, length=200, from_=0.0, to=100.0, command=self.jump_to_pos, style='custom.Horizontal.TScale')
        self.progress.grid(column=2, row=1)


        for child in self.songInfoFrame.winfo_children(): 
            child.grid_configure(padx=10, pady=10)

        self.hotbarFrame = Frame(self.songFrame, borderwidth=2, relief='groove', bg=self.backgroundColor)
        self.hotbarFrame.grid(column=2,row=1)
        
        self.toggleBtn = Button(self.hotbarFrame, image=self.playImage, bd = 0, command=self.toggle_play_button, bg=self.backgroundColor)
        self.toggleBtn.grid(column=2, row=0)
        self.previousSongBtn = Button(self.hotbarFrame, image=self.previousImage, bd=0, bg=self.backgroundColor, command=lambda:self.manager.change_song(-1))
        self.previousSongBtn.grid(column=1, row=0, sticky='E', padx=20)
        self.nextSongBtn = Button(self.hotbarFrame, image=self.nextImage, bd=0, bg=self.backgroundColor, command=lambda:self.manager.change_song(1))
        self.nextSongBtn.grid(column=3, row=0, sticky='W', padx=20)

        #self.volumeBar = Scale(self.songFrame, orient=VERTICAL, variable=self.volumeVar, length=100, from_=100, to=0, bg=self.backgroundColor)
        self.volumeBar = VolumeBar(self.songVolumeFrame, width = 20, height = 100)
        self.volumeBar.variable = self.volumeVar
        self.volumeBar.window = self
        self.volumeBar.draw()
        self.volumeBar.grid(column=0, row=0)
        Label(self.songVolumeFrame, image=self.volumeImage, bd=0, bg=self.backgroundColor).grid(column=0, row=1)

        self.draw_songlist()

        self.audioVisualizer = AudioVisualizer(self.audioVisualizerFrame, width = 250, height = 350, bg=self.backgroundColor, bd=0, highlightthickness=0)
        self.audioVisualizer.grid(column=0, row=0)
        self.manager.player.visualizer = self.audioVisualizer

        #Label(self.songlistFrame, image=self.anime).grid()

    def draw_songlist(self):
        Label(master=self.songlistFrame, text='SONG LIST', bg=self.backgroundColor).grid(column=0, row=0, sticky=NW)
        self.listFrame = ttk.Frame(self.songlistFrame)
        self.listFrame.grid(column=0, row=1)
        songQueue = []
        for song in self.manager.songlist:
            songQueue.append(song.filename + ' - ' + str(song.duration))
        self.songlistVar.set(songQueue)
        self.songlist = DragDropListbox(self.listFrame, height=20, width = 60, listvariable=self.songlistVar, selectmode='browse', activestyle='none')
        self.songlist.grid(column=0,row=0)
        self.songlist.bind("<Double-1>", lambda e: self.manager.play(self.manager.songlist[self.songlist.curselection()[0]]))
        self.songlist.window = self
        self.manager.listbox = self.songlist

        self.songlistScroll = Scrollbar(self.listFrame, orient=VERTICAL, command=self.songlist.yview, bg=self.backgroundColor)
        self.songlistScroll.grid(column=1, row=0, sticky='NS')
        self.songlist.config(yscrollcommand = self.songlistScroll.set)

        #Shuffle and Repeat
        self.songlistOptionsFrame = Frame(self.songlistFrame, bg=self.backgroundColor)
        
        self.shuffleBtn = Button(self.songlistOptionsFrame, image=self.shuffleImage, bd = 0, command=self.toggle_shuffle, bg=self.backgroundColor)
        self.shuffleBtn.grid(column=0, row=0)
        self.repeatBtn = Button(self.songlistOptionsFrame, image=self.repeatImage, bd = 0, command=self.toggle_repeat, bg=self.backgroundColor)
        self.repeatBtn.grid(column=1, row=0)

        #Add and Delete
        self.songlistEditFrame = Frame(self.songlistFrame, bg=self.backgroundColor)
        self.addBtn = Button(self.songlistEditFrame, image=self.addImage, command=self.manager.ask_add_song, bg=self.backgroundColor, bd=0)
        self.addBtn.grid(column=0, row=0)
        self.deleteBtn = Button(self.songlistEditFrame, image=self.deleteImage, command=self.manager.delete_song, bg=self.backgroundColor, bd=0)
        self.deleteBtn.grid(column=1,row=0)

        for child in self.songlistOptionsFrame.winfo_children(): 
            child.grid_configure(padx=5)
        for child in self.songlistEditFrame.winfo_children(): 
            child.grid_configure(padx=5)

        self.songlistOptionsFrame.grid(column=0, row=2, sticky=W)
        self.songlistEditFrame.grid(column=0, row=2, sticky=E)

        # register the listbox as a drop target
        self.songlist.drop_target_register(DND_FILES)
        self.songlist.dnd_bind('<<Drop>>', lambda e: self.manager.add_song(e.data, event=e))

    def toggle_repeat(self):
        if self.manager.repeat == False:
            self.repeatBtn['image'] = self.greenRepeatImage
            self.manager.repeat = True
        else:
            self.repeatBtn['image'] = self.repeatImage
            self.manager.repeat = False

    def toggle_shuffle(self):
        #clear selection  
        self.songlist.selection_clear(0, len(self.manager.songlist)-1)
        
        
        if self.manager.shuffle == False:
            self.shuffleBtn['image'] = self.greenShuffleImage
            self.manager.shuffle = True

            random.shuffle(self.manager.songlist)
            self.manager.update_songlist()
        else:
            self.shuffleBtn['image'] = self.shuffleImage
            self.manager.shuffle = False

            names, self.manager.songlist = (list(t) for t in zip(*sorted(zip((song.filename for song in self.manager.songlist), self.manager.songlist))))
            self.manager.update_songlist()
            print(self.manager.songlist[0].filename)
            
        #apply blackstripe
        self.songlist.update_list_color()
    
    def toggle_play_button(self):
        self.manager.player.playing = not self.manager.player.playing
        if self.manager.player.playing == True:
            self.manager.player.event.clear()
            self.toggleBtn['image'] = self.pauseImage
            startingPos = self.progressVar.get()/100 * self.manager.player.audioDuration
            self.manager.play(self.manager.songlist[self.manager.songlist.index(self.manager.currentSong)], start=startingPos, toggledButton = True)
        else:
            self.manager.player.pause()

    def jump_to_pos(self, progress):
        start = self.progressVar.get()/100 * self.manager.player.audioDuration
        if self.manager.player.playing == True:
            self.manager.player.wf.setpos(int(start * self.manager.player.wf.getframerate()))   
        self.manager.player.chunktotal = self.chunktotal = 0 + int(start * self.manager.player.wf.getframerate())
        self.manager.player.progress = int(self.progressVar.get()/100)    
        self.manager.player.secondsProgress = self.chunktotal/float(self.manager.player.wf.getframerate())
        self.manager.player.timeStampString.set(time.strftime("%M:%S", time.gmtime(self.manager.player.secondsProgress)) + ' / ' + time.strftime("%M:%S", time.gmtime(self.manager.player.audioDuration)))
            
        

class SongManager():
    def __init__(self, songstring):
        self.window = None
        self.listbox = None
        self.repeat = False
        self.shuffle = False
        self.songdir = 'C:\\'
        self.songlist = []
        self.songlistVar = None
        self.get_songlist()
        self.currentSong = None
        self.currentSongString = songstring
        self.player = AudioPlayer()
        self.player.songStringVar = self.currentSongString
        self.player.manager = self        

    def ask_add_song(self):
        files = filedialog.askopenfilenames(filetypes=[('Wave file', '*.wav'), ('All Files', '*.*')], defaultextension=[('Wave file', '*wav'), ('All Files', '*.*')])
        print(files)
        if files == '' or files == None: return False
        self.add_song(files)


    def add_song(self, filepath, event=None):
        if event != None:
            print('event y')
            print(event.y_root)
            print('listbox y')
            print(self.listbox.winfo_rooty())
            y = event.y_root - int(self.listbox.winfo_rooty())
            #filepath = filepath.replace('{' , '')
            
            spacedFiles = re.findall(r'{(.*?)}', filepath)
            print('spaced files:')
            print(spacedFiles)
            for file in spacedFiles:
                filepath = filepath.replace('{' + file + '}', '')

            filepath = filepath.split(' ')
            
            ind=0
            print(filepath)
            while '' in filepath:
                filepath.remove('')
            filelist = filepath + spacedFiles

            print(filepath)
        else:
            
            filelist = filepath
            
        for filepath in filelist:
            fileid = os.popen(f"fsutil file queryfileid \"{filepath}\"").read()
            fileid = fileid.split(': ')[1]
            fileid.replace('\n', '')
            print(fileid)
            file = filepath.split('/')[-1]
            print('file: ' + file)

            #convert to 16bit wav file
            data, samplerate = soundfile.read(filepath.replace('\n', ''))
            print(soundfile.read(filepath.replace('\n', '')))

            #if samplerate != 44100 and samplerate != 48000:
                #soundfile.write(filepath.replace('\n', ''), data, samplerate, subtype='PCM_16')
            print('sample rate: ' + str(samplerate))
            
            with audioread.audio_open(filepath) as f:

                # totalsec contains the length in float
                totalsec = f.duration
                dur = time.strftime("%M:%S", time.gmtime(totalsec))
            
            song = Song(fileid, file, dur)
            print(song.filename, song.duration)

            replace = -1
            if event!=None:
                replace = self.listbox.get_index_replace(FakeEvent(y))

            if replace != -1: self.songlist.insert(replace, song)
            else: self.songlist.append(song)
        
        self.update_songlist()

        self.listbox.update_list_color()


    def delete_song(self, event=None):
        sel = self.listbox.curselection()
        print(sel[0])
        #if self.player.playing == True and self.songlist[sel[0]] == self.currentSong: return False
        
        if self.currentSong != None:
            if self.songlist.index(self.currentSong) == sel[0]:
                self.listbox.itemconfigure(sel[0], background='white')
                self.listbox.itemconfigure(sel[0], foreground='black')
                self.listbox['selectbackground'] = 'blue'
                self.listbox['selectforeground'] = 'white'
                
        if sel[0] == None: return False
        del self.songlist[sel[0]]

        if self.currentSong not in self.songlist:
            #if len(self.songlist)-1 > sel[0]: self.currentSong = self.songlist[sel[0]]
            #elif len(self.songlist) > 0: self.currentSong = self.songlist[-1]
            #else: self.player.clear_player()
            #self.player.setAudioFile(self.currentSong.fileid, self.songdir[:3])
            self.currentSong = None
            self.player.clear_player()
            self.player.pause()

        self.listbox.update_list_color()
        
        self.update_songlist()


        
    def play(self, song, start=0, toggledButton=False): #function guarantees that song plays properly and only if player is unpaused, and sets black stripe
        if self.currentSong == song and toggledButton == False: #if double clicked on file and not used the play button, do not interrupt the song
            return False
        #if want it to start playing even when paused, use this
        self.player.playing = True
        self.player.btn['image'] = self.player.pauseImage
        
        #play song
        if(self.player.playing == True):
            self.player.event.set()

            self.window.after(100, lambda:self.play_song(song, start=start))
        else:
            self.currentSong = song
            self.currentSongString.set(self.currentSong.filename)
            self.player.setAudioFile(self.currentSong.fileid, self.songdir)
            self.player.secondsProgress = 0
            self.player.progress = 0
            self.player.timeStampString.set('00:00 / ' + song.duration)
            
            self.listbox.playingIndex = self.songlist.index(song)
            self.listbox.update_list_color()
        
        


    def play_song(self, song, start=0):
        self.player.event.clear()
        self.currentSong = song
        self.currentSongString.set(self.currentSong.filename)
        self.player.setAudioFile(song.fileid, self.songdir[:3])
        self.player.playAudioFile(start)
        
        self.listbox.playingIndex = self.songlist.index(song)
        self.listbox.update_list_color()
    
    def get_songlist(self):
        self.songlist = []
        entries = os.listdir(self.songdir)
        for file in entries:
            if file.endswith('.mp3') or file.endswith('.wav'):
                filepath = self.songdir + '\\' + file
                print(filepath)
                fileid = os.popen(f"fsutil file queryfileid \"{filepath}\"").read()
                fileid = fileid.split(': ')[1]
                fileid.replace('\n', '')
                print(fileid)

                #convert to 16bit wav file
                data, samplerate = soundfile.read(filepath.replace('\n', ''))

                #if samplerate != 44100 and samplerate != 48000:
                    #soundfile.write(filepath.replace('\n', ''), data, samplerate, subtype='PCM_16')
                print('sample rate: ' + str(samplerate))
                
                with audioread.audio_open(filepath) as f:
    
                    # totalsec contains the length in float
                    totalsec = f.duration
                    dur = time.strftime("%M:%S", time.gmtime(totalsec))
                
                song = Song(fileid, file, dur)
                self.songlist.append(song)
        return self.songlist

    def update_songlist(self):
        newList = []
        for song in self.songlist:
            newList.append(song.filename + ' - ' + song.duration)
        self.songlistVar.set(newList)

    def change_song(self, factor):
        currentInd = self.songlist.index(self.currentSong)
        self.listbox.selection_clear(currentInd)
        
        currentInd = currentInd + factor
        if currentInd > len(self.songlist)-1:
            currentInd = 0
        if currentInd < 0:
            currentInd = len(self.songlist)-1
        self.play(self.songlist[currentInd], toggledButton = True)
        

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

class AudioVisualizer(Tkinter.Canvas):
    def __init__(self, master, **kw):
        Tkinter.Canvas.__init__(self, master, kw)

        self.width = self.cget('width')
        self.height = self.cget('height')
        print(self.width, self.height)
        self.color = 'black'

        self.numBars = 8
        self.bars = []
        self.barWidth = 20 #int(self.width)/self.numBars #40 does the trick
        self.padding = 5
        self.maxAbsoluteAmplitude = 32768

        for i in range(self.numBars):
            rectangle = self.create_rectangle(0,0,0,0, fill=self.color, outline=self.color)
            self.bars.append(rectangle)

    def show_audio_data(self, data):
        data = [abs(ele) for ele in data]
        split_data = numpy.array_split(data, self.numBars)
        for i in range(self.numBars):
            absoluteAverage = sum(split_data[i]) / len(split_data[i])
            factor = absoluteAverage / self.maxAbsoluteAmplitude
            #print(self.height)
            #print(factor)
            x1, y1, x2, y2= i*(self.barWidth+self.padding), self.height, i*(self.barWidth+self.padding)+self.barWidth, int(self.height) - (int(self.height)*factor)
            #self.create_rectangle(i*self.barWidth, (i*self.barWidth)+self.barWidth+self.padding, 0, self.height*factor, fill='white', outline=self.color)
            self.coords(self.bars[i], x1, y1, x2, y2)
            #print(self.coords(self.bars[i]))

class DragDropListbox(Tkinter.Listbox):
    """ A Tkinter listbox with drag'n'drop reordering of entries. """
    def __init__(self, master, **kw):
        kw['selectmode'] = Tkinter.SINGLE
        Tkinter.Listbox.__init__(self, master, kw)
        self.bind('<Button-1>', self.setCurrent)
        self.bind('<Motion>', self.setHover)
        self.bind('<B1-Motion>', self.shiftSelection)
        self.bind('<Leave>', self.clear_hover)
        self.bind("<Left>", lambda e: "break") # Disables the left arrow key
        self.bind("<Right>", lambda e: "break") # Disables the left arrow key
        #self.bind("<Left>", lambda f: self.window.manager.change_song(factor=-1))
        #self.bind("<Right>", lambda f: self.window.manager.change_song(factor=1))
        self.curIndex = None
        self.playingIndex = None
        self.lastHoverInd = None
        self.hoverColor = "#ADD8E6"

        self['selectbackground'] = 'Blue'
        self['selectforeground'] = 'White'
        
    def setCurrent(self, event, factor=None):
        if factor == None: self.curIndex = self.nearest(event.y)
        elif self.curIndex + factor >= 0 and self.curIndex + factor <= self.size()-1: self.curIndex += factor

        self.selection_clear(0, self.size()-1)
        self.selection_set(self.curIndex)
        self.update_list_color()

    def shiftSelection(self, event):
        i = self.nearest(event.y)
        if i == self.curIndex: return False
        self.clear_hover()
        
        if i < self.curIndex:
            
            x = self.get(i)
            self.delete(i)
            self.insert(i+1, x)
            self.window.manager.songlist[i+1], self.window.manager.songlist[i] = self.window.manager.songlist[i], self.window.manager.songlist[i+1]
            self.curIndex = i
                
        elif i > self.curIndex:
            
            x = self.get(i)
            self.delete(i)
            self.insert(i-1, x)
            self.window.manager.songlist[i-1], self.window.manager.songlist[i] = self.window.manager.songlist[i], self.window.manager.songlist[i-1]
            self.curIndex = i
            

        #self.itemconfigure(self.playingIndex, background='white')
        #self.itemconfigure(self.playingIndex, foreground='black')
        
        #self.playingIndex = self.window.manager.songlist.index(self.window.manager.currentSong)
        
        #self.itemconfigure(self.playingIndex, background='black')
        #self.itemconfigure(self.playingIndex, foreground='white')

        self.update_list_color()

    def setHover(self, event):

        
        self.lastHoverInd = self.nearest(event.y)



        self.update_list_color()
    

    def get_index_replace(self, event):
        i = self.nearest(event.y) #item to get position replaced

        if self.get(i) == self.get(END): return -1

        return i
        
    def update_list_color(self):
        if self.window.manager.currentSong == None:
            self.playingIndex = None
        else:
            self.playingIndex = self.window.manager.songlist.index(self.window.manager.currentSong)

        for i in range(len(self.window.manager.songlist)):
            if i == self.playingIndex:
                self.itemconfigure(self.playingIndex, background='black')
                self.itemconfigure(self.playingIndex, foreground='white')
            elif i == self.lastHoverInd:
                self.itemconfigure(i, background = self.hoverColor)
                self.itemconfigure(i, foreground = 'black')
            else:
                self.itemconfigure(i, background = self.window.backgroundColor)
                self.itemconfigure(i, foreground = 'black')

        if self.playingIndex in self.curselection():
            self['selectbackground'] = 'black'
            self['selectforeground'] = 'white'
        else:
            self['selectbackground'] = 'Blue'
            self['selectforeground'] = 'White'

    def clear_hover(self, ev=None):
        self.lastHoverInd = None
        self.update_list_color()

class CustomScale(ttk.Scale):
    def __init__(self, master=None, **kw):
        kw.setdefault("orient", "horizontal")
        self.variable = kw.pop('variable', DoubleVar(master))
        ttk.Scale.__init__(self, master, variable=self.variable, **kw)
        self._style_name = '{}.custom.{}.TScale'.format(self, kw['orient'].capitalize()) # unique style name to handle the text
        self['style'] = self._style_name

class VolumeBar(Tkinter.Canvas):
    def __init__(self, master=None, **kw):
        Tkinter.Canvas.__init__(self, master, kw)

        self.width = int(self.cget('width'))
        self.height = int(self.cget('height'))
        
        self.variable = None
        self.window = None

        self.active = False

        self.bind("<Button-1>", self.activate)
        self.bind("<B1-Motion>", self.change_value)
        self.bind("<B1-ButtonRelease>", self.disable)

    def draw(self):
        #self.rectangle = self.create_rectangle(0,0,self.width,self.height - (self.height * (self.variable.get()/100)), fill="black", outline="black")
        self.rectangle = self.create_rectangle(self.width,self.height,0,self.height - (self.height * self.variable.get()/100), fill="black", outline="white")

    def activate(self, event):
        self.active = True
        self.change_value(FakeEvent(event.y))

    def disable(self, event):
        self.active = False

    def change_value(self, event):
        print(event.y) 
        if self.active == False: return False
        if event.y > 0 and event.y < self.height:
            newValueFactor = (self.height-event.y)/self.height
            self.variable.set(int(100 * newValueFactor))
        else:
            if event.y >= self.width: self.variable.set(0)
            else: self.variable.set(100)
        print(self.variable.get())
        self.coords(self.rectangle, self.width,self.height,0,self.height - (self.height * self.variable.get()/100))
        


window = MusicPlayerWindow()
window.mainloop()
