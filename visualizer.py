from tkinter import Canvas

import numpy

class AudioVisualizer(Canvas):
    def __init__(self, master, **kw):
        Canvas.__init__(self, master, kw)

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


class VolumeBar(Canvas):
    def __init__(self, master=None, **kw):
        Canvas.__init__(self, master, kw)

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
