# External Imports
from tkinter import filedialog

import time
import re

# Internal Imports

from player import *

class Song():
    def __init__(self, fileid, filename, duration, coverImg = None):
        self.fileid = fileid
        self.filename = filename
        
        self.coverImg = coverImg
        self.duration = duration #(hours, minutes, seconds)
        
class FakeEvent(): #to send to listbox
    def __init__(self, y):
        self.y = y

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
