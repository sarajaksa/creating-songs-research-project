import random
import math

class FindSong():

    def __init__(self, song, learning_rate, first_generation, mutation_rate, stop=0, mutation_type="random", generation_size=0, selection="normal", remove_duplicate=True):
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
        """
        
        self.notes_to_numbers = {"c": 1, "d": 2, "e": 3, "f": 4, "g": 5, "a": 6, "h": 7}
        self.numbers_to_notes = {1: "c", 2: "d", 3: "e", 4: "f", 5: "g", 6: "a", 7: "h"}
        
        self.final_song = self.change_representation_to_number(song.split(" "))
        self.final_song_lilypond = song
        self.songs = [self.create_random_sound(len(self.final_song)) for i in range(first_generation)]
        self.iteration = 0
        self.current_evaluvation = max([self.cost_evaluvation(song, self.final_song) for song in self.songs])
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
        songs_crossover = self.crossover(self.songs)
        songs = self.generation(songs_crossover + self.songs, self.learning_rate, self.mutation_rate) + self.songs + songs_crossover
        if self.selection == "elite":
            cut_rate = min(sorted([self.cost_evaluvation(song, self.final_song) for song in songs])[:self.generation_size])
        else:
            cut_rate = max(sorted([self.cost_evaluvation(song, self.final_song) for song in songs])[:self.generation_size])
        self.songs = [song for song in songs if self.cost_evaluvation(song, self.final_song) < cut_rate]
        if not self.songs:
            self.songs = [song for song in songs if self.cost_evaluvation(song, self.final_song) <= cut_rate][:self.generation_size]
        if self.remove_duplicate:
            #Find a way to remove duplicates
            pass
        current_evaluvation = min([self.cost_evaluvation(song, self.final_song) for song in self.songs])
        if self.current_evaluvation > current_evaluvation:
            self.current_evaluvation = current_evaluvation
            self.write_music_to_file(7, self.create_new_song([song for song in self.songs if self.cost_evaluvation(song, self.final_song) == self.current_evaluvation][0], self.iteration))
        self.iteration += 1
        print(str(self.iteration) + ": " + str(self.current_evaluvation) + ", " + str(len(self.songs)))

    def crossover(self, songs):
        """
        Creates the new population by crossover of two elements from the parent generation.
        
        :paras songs: list of songs in the parrent generation
        :return: list of the songs in the ofspring generation
        """
        newsongs = []
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
                    if note != 7:
                        note = note + 1
                else: 
                    if note != 1:
                        note = note - 1
            if random.random() > learning_rate:
                if random.random() > 0.5:
                    if note != 3:
                        duration = duration + 1
                else: 
                    if note != 1:
                        duration = duration - 1
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
        
    def create_new_song(self, song, iteration):
        """
        Takes the music and formates it in the lilypond style.
        
        :param song: song in its numerical form
        :param iteration: the number that is used to create the title for this part of lilypond fragment
        :return: Music formated as lilypond fragment
        """
        music = '\\version "2.18.2"\n'
        music += "\markup {\\fill-line {\\column \\bold  {\line { Iteration: " + str(iteration) + "}}}}\n\n"
        music += 'symbols = {' + self.create_lilypond_colored_representation(self.change_representation_to_lilypond(song), self.final_song_lilypond) + '}\n'
        music += "\score {\n<<\n\\new Staff { \\relative c' \\symbols }\n>>\n\midi { }\n\layout { }\n}\n\n\n"
        return music
        
    def write_music_to_file(self, iteration, music):
        """
        Writes content to the lilypond file with name song_(iteration number).ly.
        
        :param interation: the number used in the filename
        :param music: content to be written in a file
        :return: None
        """
        with open("song_" + str(iteration) + ".ly", "a") as write:
            write.write(music)
            
    def create_random_sound(self, length):
        """
        Function that creates a random sequences of notes, by choosing random values for notes duration and pitch of specified duration, described by number of notes that are created. 
        
        :param length: the number of notes in the music created
        :return: list of notes, defined by tuples of number indicating the pitch and number indicating the duration
        """
        song = [(random.randint(1,7), random.randint(1,3)) for i in range(length)]
        return song

FindSong("d8 d8 d8 d8 e8 e8 e8 e8 f8 f8 e8 e8 d8 d8 d4", 0.95, 100, 10)
#FindSong("e4 e4 f4 g4 g4 f4 e4 d4 c4 c4 d4 e4 e4 d4 d2 e4 e4 f4 g4 g4 f4 e4 d4 c4 c4 d4 e4 d4 c4 c2 d4 d4 e4 c4 d4 f4 e4 c4 d4 f4 e4 d4 c4 d4 g2 e4 e4 f4 g4 g4 f4 e4 d4 c4 c4 d4 e4 d4 c4 c2", 0.97, 100, 10, stop=0, mutation_type="random", generation_size=0, remove_duplicate=True)
