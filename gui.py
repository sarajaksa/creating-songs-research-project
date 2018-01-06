import sys
import time
import math
import subprocess
#from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PIL import Image
#from PIL import ImageChops
from evo import FindSong


class GenerateMusic(QtWidgets.QDialog):

    def __init__(self, parent=None):
    
        self.notes_to_numbers = {"c": 1, "des": 2, "d": 3, "ees":4, "e": 5, "f": 6, "ges":7, "g": 8, "aes":9, "a": 10, "hes":11, "h": 12, "pause": 13}
        self.numbers_to_notes = {1: "c", 2: "des", 3: "d", 4:"ees", 5: "e", 6: "f", 7: "ges", 8: "g", 9: "aes", 10: "a", 11: "hes", 12: "h", 13: "pause"}
        
        self.songs = [("None", ""), ("Kuza Pazi", "d8 d8 d8 d8 e8 e8 e8 e8 f8 f8 e8 e8 d8 d8 d4"), ("Ode of Joy", "e4 e4 f4 g4 g4 f4 e4 d4 c4 c4 d4 e4 e4 d4 d2 e4 e4 f4 g4 g4 f4 e4 d4 c4 c4 d4 e4 d4 c4 c2 d4 d4 e4 c4 d4 f4 e4 c4 d4 f4 e4 d4 c4 d4 g2 e4 e4 f4 g4 g4 f4 e4 d4 c4 c4 d4 e4 d4 c4 c2")]
        
        super(GenerateMusic, self).__init__(parent)
        #self.resize(800,600)
        self.setWindowTitle("Create Music My Using Evolutionary Algoritms")
        layout = QtWidgets.QVBoxLayout()
        self.differentSongs = QtWidgets.QComboBox()
        self.differentSongs.addItems([s[0] for s in self.songs])
        layout.addWidget(self.differentSongs)
        self.addingMusic = QtWidgets.QLineEdit("Add the music in Lilypond syntax")
        self.final_song_lilypond = ""
        layout.addWidget(self.addingMusic)
        self.imageLabel = QtWidgets.QLabel()
        layout.addWidget(self.imageLabel)
        self.final_song_notes = QtGui.QImage("beginning.png")
        self.imageLabel.setPixmap(QtGui.QPixmap.fromImage(self.final_song_notes))
        self.evolveExistingSong = QtWidgets.QPushButton("Evolve Existing Song")
        layout.addWidget(self.evolveExistingSong)
        self.typesOfMusic = QtWidgets.QComboBox()
        layout.addWidget(self.typesOfMusic)
        self.lengthOfMusic = QtWidgets.QDoubleSpinBox()
        self.lengthOfMusic.setRange(1, 30)
        self.lengthOfMusic.setValue(8)
        layout.addWidget(self.lengthOfMusic)
        self.evolveNewSong = QtWidgets.QPushButton("Evolve New Song")
        layout.addWidget(self.evolveNewSong)
        
        self.imageEvolving = QtWidgets.QLabel()
        layout.addWidget(self.imageEvolving)
        self.evolvingSongNotes = QtGui.QImage("beginning.png")
        self.imageEvolving.setPixmap(QtGui.QPixmap.fromImage(self.evolvingSongNotes))
        
        self.iteration = QtWidgets.QPushButton("Next Iteration")
        layout.addWidget(self.iteration)
        
        self.stop = False
        self.stopButton = QtWidgets.QPushButton("Stop Evolving")
        layout.addWidget(self.stopButton)

        self.setLayout(layout)
        
        self.addingMusic.returnPressed.connect(self.checkInputedMusic)
        self.differentSongs.currentIndexChanged.connect(self.changeSong)
        self.stopButton.clicked.connect(self.stopLearning)
        self.evolveExistingSong.clicked.connect(self.startEvolving)
        #self.evolvingSongNotes.notFinished.connect(self.oneIteration)
        self.iteration.clicked.connect(self.oneIteration)
        
        
        
        #when end of iteration:
        #element.iteration.connect(what to do at this time)
        
        self.evolutionAlgoritm = FindSong()
        
    def changeImage(self):
        self.crop_image("song_final.png")
        self.evolvingSongNotes = QtGui.QImage("song_final.png")
        self.imageEvolving.setPixmap(QtGui.QPixmap.fromImage(self.evolvingSongNotes))
        
    def stopLearning(self):
        self.stop = True
        
        
    def startEvolving(self):
        self.evolutionAlgoritm = FindSong(song=self.final_song_lilypond, filename="song_final.ly")
        self.oneIteration()
                    
    def oneIteration(self):
        if self.stop == True:
            return None
        self.evolutionAlgoritm.evolutionary_algoritm()
        self.changeImage()
        
    def changeSong(self, index):
        self.addingMusic.setText(self.songs[index][1])
        self.checkInputedMusic()

    def crop_image(self, name):
        image = Image.open(name)
        image = image.crop((30, 20, 800, 190))
        image.save(name)
        
    def checkInputedMusic(self):
        self.final_song_lilypond = self.addingMusic.text()
        music = self.evolutionAlgoritm.create_new_song(self.final_song_lilypond, 0)
        self.evolutionAlgoritm.write_music_to_file("song.ly", music)
        subprocess.call(["lilypond", "--png", "song.ly"])
        self.crop_image("song.png")
        self.final_song_notes = QtGui.QImage("song.png")
        self.imageLabel.setPixmap(QtGui.QPixmap.fromImage(self.final_song_notes))
        
    def endOfIteration(self):
        self.emit(SIGNAL("iteration"))
        

app = QtWidgets.QApplication(sys.argv)
musicGenerationApp = GenerateMusic()
musicGenerationApp.show()
app.exec_()
