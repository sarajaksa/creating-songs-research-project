import subprocess
import random
import math
import os

FNULL = open(os.devnull, 'w')

class FindSong():

    def __init__(self, song="", learning_rate=0.97, first_generation=100, mutation_rate=10, stop=0, mutation_type="random", generation_size=0, selection="normal", remove_duplicate=True, filename="song.ly", duration=10, type_of_evaluvation=None):
        """
        Class capable of evolutionary evolving a song to be the same as the one inputed in
        
        :paras song: the song that serves as a standard
        :paras learning_rate: the propability, that the song will mutate
        :paras first_generation: the size of the first generation
        :paras mutation_rate: the number of musics created by mutation from each song
        :paras stop: stopping criteria (0 => complete match)
        :paras mutation_type: the types of mutation (random => learning rate decides the changes each part of the song is mutated, certain => one mutation per song happens each time)
        :paras generation_size: the size of generation in each iteration (if 0, then generation_size is the same as first_generation size)
        :paras selection: the criteria used for selecting the people in new generation (elite => only the best elements are selected, normal => best x elements is selected, where x is the generation_size)
        :paras remove_duplicate: removes duplicates from the generation
        :paras filename: the name of the file with the lilypond results (.ly)
        """
        
        self.notes_to_numbers = {"c": 1, "des": 2, "d": 3, "ees":4, "e": 5, "f": 6, "ges":7, "g": 8, "aes":9, "a": 10, "hes":11, "h": 12, "pause": 13}
        self.numbers_to_notes = {1: "c", 2: "des", 3: "d", 4:"ees", 5: "e", 6: "f", 7: "ges", 8: "g", 9: "aes", 10: "a", 11: "hes", 12: "h", 13: "r"}
        self.keys = [set([1,5,8,6,12,3,13]),set([3,12,7,10,8,2,5,13]),set([6,10,1,11,3,5,8,13]), set([8,10,3,1,5,7,10,13]), set([10,2,5,3,7,9,12,13]),set([5,9,12,10,2,4,7,13])]
        self.keys_names = ["C", "D", "F", "G", "A", "E"]
        
        self.cords_c = [set([1,5,8, 13]),set([6,10,1,13]),set([8,12,3,13]),set([10,1,5,13])]
        
        self.all_file_names = []
        if song:
            self.algoritm = "known"
            self.final_song = self.change_representation_to_number(song.split(" "))
            self.final_song_lilypond = song
            self.songs = [self.create_random_sound(len(self.final_song)) for i in range(first_generation)]
            self.current_evaluvation = max([self.cost_evaluvation(song, self.final_song) for song in self.songs])
        else:
            self.algoritm = "unknown"
            if type_of_evaluvation:
                self.type_of_evaluvation = type_of_evaluvation
            else:
                self.type_of_evaluvation = None
            self.duration = duration
            self.songs = [self.create_random_sound(self.duration) for i in range(first_generation)]
            if self.type_of_evaluvation == "C Key Cords":
                self.current_evaluvation = max([self.cost_c_try(song) for song in self.songs])
            else:
                self.current_evaluvation = max([self.cost_first_try(song) for song in self.songs])
        self.iteration = 0
        self.learning_rate = learning_rate
        self.first_generation = first_generation
        self.mutation_rate = mutation_rate
        self.stop = stop
        self.mutation_type = mutation_type
        if generation_size == 0:
            self.generation_size = first_generation
        else:
            self.generation_size = generation_size
        self.selection = selection
        self.remove_duplicate = remove_duplicate
        self.filename = filename
        
        
    def evolving(self):
        if self.stop == 0:
            while self.current_evaluvation > 0:
                self.evolutionary_algoritm()
        else:
            while self.iteration < self.stop:
                self.evolutionary_algoritm()
                
    def evolutionary_algoritm(self):
        """
        The main function of the evolutionary algoritm.
        
        :return: None
        """
        self.iteration += 1
        songs_crossover = self.crossover(self.songs)
        songs = self.generation(songs_crossover + self.songs, self.learning_rate, self.mutation_rate) + self.songs + songs_crossover
        if self.algoritm == "known":
            if self.selection == "elite":
                cut_rate = min(sorted([self.cost_evaluvation(song, self.final_song) for song in songs])[:self.generation_size])
            else:
                cut_rate = max(sorted([self.cost_evaluvation(song, self.final_song) for song in songs])[:self.generation_size])
            self.songs = [song for song in songs if self.cost_evaluvation(song, self.final_song) < cut_rate]
            if not self.songs:
                self.songs = [song for song in songs if self.cost_evaluvation(song, self.final_song) <= cut_rate][:self.generation_size]
        if self.algoritm == "unknown":
            if self.type_of_evaluvation == "C Key Cords":
                if self.selection == "elite":
                    cut_rate = min(sorted([self.cost_c_try(song) for song in songs])[:self.generation_size])
                else:
                    cut_rate = max(sorted([self.cost_c_try(song) for song in songs])[:self.generation_size])
                self.songs = [song for song in songs if self.cost_c_try(song) < cut_rate]
                if not self.songs:
                    self.songs = [song for song in songs if self.cost_c_try(song) <= cut_rate][:self.generation_size]
            else:
                if self.selection == "elite":
                    cut_rate = min(sorted([self.cost_first_try(song) for song in songs])[:self.generation_size])
                else:
                    cut_rate = max(sorted([self.cost_first_try(song) for song in songs])[:self.generation_size])
                self.songs = [song for song in songs if self.cost_first_try(song) < cut_rate]
                if not self.songs:
                    self.songs = [song for song in songs if self.cost_first_try(song) <= cut_rate][:self.generation_size]
        if self.remove_duplicate:
            #Find a way to remove duplicates
            pass
        if self.algoritm == "known":
            current_evaluvation = min([self.cost_evaluvation(song, self.final_song) for song in self.songs])
        if self.algoritm == "unknown":
            if self.type_of_evaluvation == "C Key Cords":
                current_evaluvation = min([self.cost_c_try(song) for song in self.songs])
            else:
                current_evaluvation = min([self.cost_first_try(song) for song in self.songs])
        if self.current_evaluvation > current_evaluvation:
            self.current_evaluvation = current_evaluvation
            if self.algoritm == "known":
                self.write_music_to_file(self.filename, self.create_new_song(self.change_representation_to_lilypond([song for song in self.songs if self.cost_evaluvation(song, self.final_song) == self.current_evaluvation][0])))
            if self.algoritm == "unknown":
                if self.type_of_evaluvation == "C Key Cords":
                    self.write_music_to_file(self.filename, self.create_new_song(self.change_representation_to_lilypond([song for song in self.songs if self.cost_c_try(song) == self.current_evaluvation][0])))
                else:
                    self.write_music_to_file(self.filename, self.create_new_song(self.change_representation_to_lilypond([song for song in self.songs if self.cost_first_try(song) == self.current_evaluvation][0])))
        subprocess.call(["lilypond", "--png", self.filename], stdout=FNULL, stderr=subprocess.STDOUT)

    def crossover(self, songs):
        """
        Creates the new population by crossover of two elements from the parent generation.
        
        :paras songs: list of songs in the parrent generation
        :return: list of the songs in the ofspring generation
        """
        newsongs = []
        if len(songs[0])-1 == 0:
            return songs
        crossover_point = random.randint(1, len(songs[0])-1)
        while len(songs) > 1:
            song1, song2 = songs.pop(), songs.pop(0)
            newsongs.append(song1[:crossover_point] + song2[crossover_point:])
            newsongs.append(song2[:crossover_point] + song1[crossover_point:])
        return newsongs
        
    def distance_between_points_2D(self, point1, point2):
        """
        Calculate the distance of two point in the 2D space. 
        
        :paras point1: the tuple of the point1, with x and y values
        :paras point2: the tuple of the point2, with x and y values
        :return: the equidian distance of two points
        """
        return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)

        
    def cost_first_try(self, song):
        cost = 0
        #add the cost of two notes repeating the pitch
        cost = cost + sum([1 for note1, note2 in zip(song[:-1], song[1:]) if note1[0] == note2[0]])
        #add the cost of notes having too big of a pitch
        cost = cost + sum([abs(note1[0] - note2[0])**2 for note1, note2 in zip(song[:-1], song[1:]) if not abs(note1[0] - note2[0]) == 1])
        #add cost of notes having too big of a difference in duration
        cost = cost + sum([abs(note1[1] - note2[1]) for note1, note2 in zip(song[:-1], song[1:]) if abs(note1[1] - note2[1]) > 1])
        #add cost of long notes
        cost = cost + sum([1/note1[1] if not note1[1] == 0 else 2 for note1 in song])
        #add cost for cords
        for key in self.keys:
            if set([note[0] for note in song]) in key:
                cost = cost - 20
                break
        return cost  
        
    def cost_c_try(self, song):
        cost = 0
        #add the cost of two notes repeating the pitch
        cost = cost + 10*sum([1 for note1, note2 in zip(song[:-1], song[1:]) if note1[0] == note2[0]])
        #add the cost of notes having too big of a pitch
        cost = cost + sum([abs(note1[0] - note2[0])**2 for note1, note2 in zip(song[:-1], song[1:]) if not abs(note1[0] - note2[0]) == 1])
        #add cost of notes having too big of a difference in duration
        cost = cost + sum([abs(note1[1] - note2[1]) if abs(note1[1] - note2[1]) > 1 else 1 for note1, note2 in zip(song[:-1], song[1:])])
        #add cost of long notes
        cost = cost + 2*sum([1/note1[1] if not note1[1] == 0 else 2 for note1 in song])
        #add cost for keys
        cost = cost + sum([25 for note in song if note[0] not in self.keys[0]])
        #add cost for cords
        duration = 0
        current_notes = []
        for pitch, dur in song:
            if dur == 0 and duration != 0:
                cost = cost + 50
                break
            elif dur != 0:
                duration = duration + 1/dur**2
            if dur == 0 and duration == 0:
                duration == 1
            current_notes.append(pitch)
            if duration > 1:
                cost = cost + 50
                break
            if duration == 1:
                for cords in self.cords_c:
                    if set(current_notes) in set(cords):
                        cost = cost - 10
                        break
            duration = 0
            current_notes = []
        return cost  

    def cost_article2_try1(self, song, final_song=None):
        #Based on Article: Evolutionary Music and Fitness Functions by E. Bilotta, P. Pantano, and V. Talarico
        cost = sum([1/((self.notes_values[note1[0]] + self.notes_values[note2[0]])/(self.notes_values[note1[0]]*self.notes_values[note2[0]])) for note1, note2 in zip(song[:-1], song[1:]) if note1[0] != 13 and note2[0] != 13])
        #add cost of long notes
        cost = cost + sum([1/note1[1] if not note1[1] == 0 else 2 for note1 in song])
        #add cost for pauses
        cost = cost + sum([1 for note1 in song if note1[0] == 13])
        return cost

    def cost_article1_try(self, song, final_song=None):
        # Based on article: Minimal Fitness Functions in Genetic Algorithms for the Composition of Piano Music by Rodney Waschka II
        cost = 0
        duration = 0
        for pitch, dur in song:
            if dur == 0 and duration != 0:
                cost = cost + 50
                break
            elif dur != 0:
                duration = duration + 1/dur**2
            if dur == 0 and duration == 0:
                duration == 1
            if duration > 1:
                cost = cost + 50
                break
            if duration == 1:
                duration == 0
                continue
        pitches = [pitch for pitch, dur in song]
        if not set(pitches).intersection(set([2,4,7,9,11])):
            cost = cost + 50
        if 1 in [dur for pitch, dur in song]:
            cost = cost + 50
        if not 4 in [dur for pitch, dur in song]:
            cost = cost + 50
        if 7 in pitches or 9 in pitches:
            cost = cost + 50
        return cost
        
    def cost_evaluvation(self, song, final_song):
        """
        Calculate the distance of two songs in space. The more the songs are different, the higher the number.
        
        :paras song: the song evaluvated
        :paras final_song: the song that serves as the stadard
        :return: distance of the two songs
        """
        result = [self.distance_between_points_2D(s, f) for s, f in zip(song, final_song)]
        return sum(result)/len(result)
        
    def generation(self, songs, learning_rate, mutation_rate):
        """
        Takes the list of multiple songs and preform the mutation on them.
        
        :paras songs: list of songs in the numerical form
        :paras learning_rate: the threshold for the mutation to happen
        :paras mutation_rate: number of mutated songs created from each song
        :return: list of mutatated songs
        """
        all_songs = songs[:]
        new_songs = []
        while all_songs:
            song = all_songs.pop()
            for i in range(mutation_rate):
                if self.mutation_type == "random":
                    song_new = self.mutation_random(song, learning_rate)
                else:
                    song_new = self.mutation_certain(song)
                new_songs.append(song_new)
        return new_songs
    
    def mutation_random(self, song, learning_rate):
        """
        Takes the song, and then for each note element in it (like pitch, duration) create a random mutation, if the random number is higher than learning rate
        
        :paras song: original song in the numerical form
        :paras learning_rate: the threshold for the change to happen
        :return: mutated song
        """
        mutated_song = []
        for note, duration in song:
            if random.random() > learning_rate:
                if random.random() > 0.5:
                    if note != 13:
                        note = 1
                else: 
                    if note != 1:
                        note = 13
            if random.random() > learning_rate:
                if random.random() > 0.5:
                    if note != 4:
                        duration = 0
                else: 
                    if note != 0:
                        duration = 4
            mutated_song.append((note, duration))
        return mutated_song
        
    def mutation_certain(self, song):
        """
        Takes the song and it creates a random mutation in it
        
        :param song: original song in the numerical form
        :return: mutated song in the numberical form
        """
        random_position, random_type, random_change = random.randint(0,len(song)-1), random.randint(0,1), random.randint(1,2)
        if random_type == 0 and random_change == 1 and song[random_position][random_type] != 1:
            song[random_position] = (song[random_position][0], song[random_position][1] -1)
        elif random_type == 1 and random_change == 1 and song[random_position][random_type] != 1:
            song[random_position] = (song[random_position][0], song[random_position][1] - 1)
        elif random_type == 0 and random_change == 2 and song[random_position][random_type] != 7:
            song[random_position] = (song[random_position][0], song[random_position][1] + 1)
        elif random_type == 1 and random_change == 2 and song[random_position][random_type] != 3:
            song[random_position] = (song[random_position][0], song[random_position][1] + 1)
        return song
        
        
    def change_representation_to_number(self, song_lilypond):
        """
        Takes the lilypond representation of the song, and change it into the numerical form
        
        :param song_lilypond: the song in the lilypond form
        :return: song in the numerical form
        """
        return [(int(self.notes_to_numbers[i[0]]), int(math.log2(int(i[1])))) for i in song_lilypond]
        
    def change_representation_to_lilypond(self, song_lilypond):
        """
        Takes the numerical representation of music and put it in the lilypond musical sequence.
        
        :param song_lilypond: song in its numerical form
        :return: song in a lilypond form
        """
        
        return " ".join(["".join([n, d]) for n, d in [(str(self.numbers_to_notes[i[0]]), str(2**i[1])) for i in song_lilypond]])
        
    def create_lilypond_colored_representation(self, song_lilypond, final_song_lilypond):
        """
        Compares the two lilypond songs and colors the notes that differ
        
        :paras song_lilypond: the song in the lilypond format
        :paras final_song_lilypond: the song in the lilypond format, that serves as comparions
        :return: the colored song in lilypond format
        """
        final_song = []
        song_lilypond = song_lilypond.split(" ")
        final_song_lilypond = final_song_lilypond.split(" ")
        for s, f in zip(song_lilypond, final_song_lilypond):
            if s != f:
                final_song.append("\once \override NoteHead.color = #red \once \override Stem.color = #red")
            final_song.append(s)
        return " ".join(final_song)

    def create_new_colored_song(self, song, iteration):
        self.create_new_song(self.create_lilypond_colored_representation(song, self.final_song_lilypond), iteration)
        
    def create_new_song(self, song, iteration=None):
        """
        Takes the music and formates it in the lilypond style.
        
        :param song: song in its numerical form
        :param iteration: the number that is used to create the title for this part of lilypond fragment
        :return: Music formated as lilypond fragment
        """
        music = '\\version "2.18.2"\n\n'
        if iteration:
            music += "\markup {\\fill-line {\\column \\bold  {\line { Iteration: " + str(iteration) + "}}}}\n\n"
        music += 'symbols = {' + song + '}\n'
        music += "\score {\n<<\n\\new Staff { \\relative c' \\symbols }\n>>\n\midi { }\n\layout { }\n}\n\n\n"
        return music
        
    def write_music_to_file(self, filename, music):
        """
        Writes content to the lilypond file with name song_(iteration number).ly.
        
        :param interation: the number used in the filename
        :param music: content to be written in a file
        :return: None
        """
        with open(filename, "w") as write:
            write.write(music)
            
    def create_random_sound(self, length):
        """
        Function that creates a random sequences of notes, by choosing random values for notes duration and pitch of specified duration, described by number of notes that are created. 
        
        :param length: the number of notes in the music created
        :return: list of notes, defined by tuples of number indicating the pitch and number indicating the duration
        """
        song = [(random.randint(1,13), random.randint(0,4)) for i in range(length)]
        return song 
