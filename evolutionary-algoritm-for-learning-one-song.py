import random
import math

class FindSong():

    def __init__(self, song, learning_rate, first_generation, mutation_rate):
        
        self.notes_to_numbers = {"c": 1, "d": 2, "e": 3, "f": 4, "g": 5, "a": 6, "h": 7}
        self.numbers_to_notes = {1: "c", 2: "d", 3: "e", 4: "f", 5: "g", 6: "a", 7: "h"}
        
        self.final_song = self.change_representation_to_number(song.split(" "))
        self.songs = [self.create_random_sound(len(self.final_song)) for i in range(first_generation)]
        self.iteration = 0
        self.current_evaluvation = max([self.cost_evaluvation(song, self.final_song) for song in self.songs])
        self.learning_rate = learning_rate
        self.first_generation = first_generation
        self.mutation_rate = mutation_rate
        
        while self.current_evaluvation > 0:
            self.songs = self.generation(self.songs, self.learning_rate, self.mutation_rate)
            self.current_evaluvation = max([self.cost_evaluvation(song, self.final_song) for song in self.songs])
            self.iteration += 1
            print(str(self.iteration) + ": " + str(self.current_evaluvation) + ", " + str(len(self.songs)))
            if self.current_evaluvation == 0:
                break
        
    def distance_between_points_2D(self, point1, point2):
        return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)
        
    def cost_evaluvation(self, song, final_song):
        result = [self.distance_between_points_2D(s, f) for s, f in zip(song, final_song)]
        return sum(result)/len(result)
        
    def generation(self, songs, learning_rate, mutation_rate):
        all_songs = songs[:]
        new_songs = []
        while all_songs:
            song = all_songs.pop()
            for i in range(mutation_rate):
                song_new = self.mutation(song, learning_rate)
                if self.cost_evaluvation(song_new, self.final_song) <= self.current_evaluvation:
                    new_songs.append(song_new)
        return new_songs
    
    def mutation(self, song, learning_rate):
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
        
    def change_representation_to_number(self, song_lilypond):
        return [(int(self.notes_to_numbers[i[0]]), int(math.log2(int(i[1])))) for i in song_lilypond]

    def change_representation_to_song(self, song_numbers):
        return [(str(self.numbers_to_notes[i[0]]), str(2**i[1])) for i in song_numbers]
        
    def change_representation_to_lilypond(self, song_lilypond):
        return " ".join(["".join([n, d]) for n, d in song_lilypond])
        
    def create_new_song(self, song):
        music = '\\version "2.18.2"\n'
        music += 'symbols = {' + self.change_representation_to_lilypond(self.change_representation_to_song(song)) + '}\n'
        music += "\score {\n<<\n\\new Staff { \\relative c' \\symbols }\n>>\n}\n"
        return music
        
    def write_music_to_file(self, iteration, music):
        with open("song_" + str(iteration) + ".ly", "w") as write:
            write.write(music)
            
    def create_random_sound(self, length):
        song = [(random.randint(1,7), random.randint(1,3)) for i in range(length)]
        return song

#FindSong("d8 d8 d8 d8 e8 e8 e8 e8 f8 f8 e8 e8 d8 d8 d4", 0.7)
FindSong("d8 d8 d8 d8 e8 e8 e8 e8 f8 f8 e8 e8 d8 d8 d4", 0.7, 1000, 20)