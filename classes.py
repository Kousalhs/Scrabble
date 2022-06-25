from copy import copy
from os.path import exists
from time import strftime
from random import shuffle
from abc import ABC, abstractmethod
from itertools import permutations
import json


# REFACTOR PLEASE
class SakClass:
    letterDictionary = {'Α': [12, 1], 'Β': [1, 8], 'Γ': [2, 4], 'Δ': [2, 4], 'Ε': [8, 1],
                        'Ζ': [1, 10], 'Η': [7, 1], 'Θ': [1, 10], 'Ι': [8, 1], 'Κ': [4, 2],
                        'Λ': [3, 3], 'Μ': [3, 3], 'Ν': [6, 1], 'Ξ': [1, 10], 'Ο': [9, 1],
                        'Π': [4, 2], 'Ρ': [5, 2], 'Σ': [7, 1], 'Τ': [8, 1], 'Υ': [4, 2],
                        'Φ': [1, 8], 'Χ': [1, 8], 'Ψ': [1, 10], 'Ω': [3, 3]}

    # Constructor
    def __init__(self):
        self.sak = []
        self.CreateSak()

    # Returns a string as a representation of the object
    def __repr__(self):
        return repr('Στο σακουλάκι έχει μέσα: ' + str(len(self.sak)) + " γράμματα.")

    # Adds all the letters in a list
    def CreateSak(self):
        for letter in self.letterDictionary:
            for i in range(self.letterDictionary[letter][0]):
                self.sak.append(letter)

    # Shuffles letters in the Sak
    def RandomizeSak(self):
        shuffle(self.sak)

    def getSpecificLetters(self, n, player):
        if len(self.sak) >= n:
            self.RandomizeSak()
            for i in range(n):
                player.hand.append(self.sak.pop())

    def PutLetterBackToSak(self, player):
        for letter in player.hand:
            self.sak.append(letter)
        player.hand.clear()


class Player(ABC):

    # Constructor
    def __init__(self, name):
        self.score = 0
        self.name = name
        self.hand = []

    # **kwargs is used to pass Keyword  arguments
    # We use **kwargs as our function's argument when we have doubts about the number of arguments we should pass
    @abstractmethod
    def play(self, **kwargs):
        pass

    def addScore(self, pts):
        self.score = self.score + pts


class Computer(Player):

    # Constructor
    def __init__(self, mode):
        super(Computer, self).__init__("Υπολογιστής")
        self.mode = mode

    def play(self, validWords, sak):
        if self.mode == 'min':
            for i in range(2, 8):
                perms = list(map("".join, permutations(self.hand, i)))
                for perm in perms:
                    index = perm[0]
                    if perm.strip() in validWords[index]:
                        return perm
        if self.mode == 'max':
            for i in reversed(range(2, 8)):
                perms = list(map("".join, permutations(self.hand, i)))
                # print(perms)
                for perm in perms:
                    index = perm[0]
                    if perm.strip() in validWords[index]:
                        return perm
        if self.mode == 'smart':
            maxPoints = 0
            bestWord = None
            for i in range(2, 8):
                perms = list(map("".join, permutations(self.hand, i)))
                for perm in perms:
                    index = perm[0]
                    if perm.strip() in validWords[index]:
                        points = Game.CountAnswerPoints(perm)
                        if points > maxPoints:
                            maxPoints = points
                            bestWord = perm
            if bestWord is not None:
                return bestWord


class Game:

    # Constructor
    def __init__(self, humanName, mode):
        self.validWords = {}
        self.humanName = humanName
        self.human = None
        self.computer = None
        self.mode = mode
        self.sak = SakClass()
        self.Setup()

    def ComputerHasMove(self):
        return True

    def MakeValidWordDictionary(self):
        with open('greek7.txt', 'r', encoding="utf8") as f:
            words = f.readlines()  # PRWTH GRAMMH , PAIRNEI OLA TA A KAI TA VAZEI SE DICT
            index = 'Α'
            dictionaryWords = []
            for w in words:
                w = w.rstrip()  # KATHARIZEI
                if w[0] == index:  # AN PRWTO GRAMMA = ME PX A
                    dictionaryWords.append(w)
                else:
                    self.validWords[index] = dictionaryWords  # DHMIOURGEI NEO KEY
                    dictionaryWords = []
                    index = w[0]

            self.validWords[index] = dictionaryWords

    def CreatePlayers(self):
        self.human = Human(self.humanName)
        self.computer = Computer(self.mode)

    def Setup(self):
        self.MakeValidWordDictionary()
        self.CreatePlayers()

    def ShowAvailableLetters(self, player):
        print(player.name + ' -Διαθέσιμα γράμματα:', end='')
        for letter in player.hand:
            print('[' + letter + ',' + str(self.sak.letterDictionary[letter][1]) + ']', end='')

    def SaveScores(self):
        if not exists("scores.json"):
            open("scores.json", 'x')

        with open("scores.json", 'r+') as outf:
            matchScore = {
                'Human:': self.human.score,
                'Computer': self.computer.score
            }
            data = json.load(outf)
            data[strftime("%d/%m/%Y %H:%M:%S")] = matchScore
            outf.seek(0)
            json.dump(data, outf)

    def RemoveUsedLetters(self, player, answer):
        hand = copy(player.hand)

        # If the answer is correct then remove used letters
        for char in answer:
            once = False
            for letter in player.hand:
                if char == letter and once == False:
                    hand.remove(letter)
                    once = True
        player.hand = copy(hand)

    def CheckGivenAnswer(self, player, answer):

        # creates all string permutations of current hand
        all_perms = list(map("".join, permutations(player.hand)))

        # checks if the answer is a substring of any of the string permutations in hand
        for perm in all_perms:
            if answer in perm:
                # checks if answer exists in valid words
                index = answer[0]
                if answer.strip() in self.validWords[index]:
                    return True
        return False

    def PlayerPass(self, player, answer):
        if answer == 'p':
            print("Ο {} πήγε πάσο, σειρά του Υπολογιστή".format(player.name))
            self.sak.PutLetterBackToSak(player)
            self.sak.getSpecificLetters(7, player)

    # plays out a game
    def run(self):
        check = True
        while len(self.sak.sak) >= 7 and check:
            # Human
            self.sak.getSpecificLetters(7 - len(self.human.hand), self.human)
            print(repr(self.sak))
            self.ShowAvailableLetters(self.human)
            answer = self.human.play()
            if answer == 'q':
                print("Τερματισμός παιχνιδιού!", end='')
                break
            while answer == '':
                print("Ο κενός χαρακτήρας δεν αποτελεί λέξη. Προσπάθησε ξανά δημιουργώντας μια λέξη", end='')
                answer = self.human.play()
            wordIsOk = True
            quit = False
            passs = False
            if answer != 'p':
                for letter in answer:
                    if not (letter in self.human.hand):
                        wordIsOk = False
                        break
            while wordIsOk is False:
                for letter in answer:
                    if not (letter in self.human.hand):
                        answer = input("Η λέξη περιέχει γράμμα που δεν ανήκει στα διαθέσιμα γράμματα. "
                                       "\n Πληκτρολόγησε άλλη λέξη: ")
                        if answer == 'q':
                            quit = True
                            break
                        if answer == 'p':
                            passs = True
                            break
                        wordIsOk = False
                        continue
                    wordIsOk = True
                if quit is True or passs is True:
                    break
            if answer == 'q' or quit:
                print("Τερματισμός παιχνιδιού!", end='')
                break
            self.PlayerPass(self.human, answer)
            if self.CheckGivenAnswer(self.human, answer):
                humanPoints = self.CountAnswerPoints(answer)
                self.human.addScore(humanPoints)
                self.RemoveUsedLetters(self.human, answer)
                print('Αποδεκτή Λέξη: ' + answer + ' Πόντοι: ' + str(humanPoints) + ' Σύνολο: ' + str(self.human.score))
            elif answer != 'p' and not (self.CheckGivenAnswer(self.human, answer)):
                print("Μη αποδεκτή λέξη! Σειρά του Υπολογιστή")

            # Computer
            self.sak.getSpecificLetters(7 - len(self.computer.hand), self.computer)
            print(repr(self.sak))
            self.ShowAvailableLetters(self.computer)
            computerAnswer = self.computer.play(self.validWords, self.sak)
            if computerAnswer == "none":
                self.PlayerPass(self.computer, 'p')
                print(self.computer.name + " passed !\n Game over!")
                check = False
            else:
                computerPoints = self.CountAnswerPoints(computerAnswer)
                self.computer.addScore(computerPoints)
                print("\nΛέξη:{}".format(computerAnswer))
                self.RemoveUsedLetters(self.computer, computerAnswer)
                print('Αποδεκτή Λέξη: ' + computerAnswer + ' Πόντοι: ' + str(computerPoints) + ' Σύνολο: ' + str(
                    self.computer.score))

                self.sak.getSpecificLetters(7 - len(self.computer.hand), self.computer)
                print("=======================================================")
                print("\n Τέλος παρτίδας")
                print("=======================================================")

        self.SaveScores()

    @classmethod
    def RetrieveScores(cls):
        with open("scores.json", 'r') as outf:
            data = json.load(outf)
            for game in data:
                print(game)
                print(data[game])

    @classmethod
    def CountAnswerPoints(cls, answer):
        return sum(SakClass.letterDictionary[char][1] for char in answer)


class Human(Player):
    def __init__(self, name):
        super(Human, self).__init__(name)

    def play(self):
        answer = input('\nΛέξη:')
        return answer
