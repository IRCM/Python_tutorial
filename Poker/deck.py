import random

class Deck:
    def __init__(self):
        self.deck = list()
        for rank in ["A", "2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K"]:
            for suit in ["h", "s", "c", "d"]:
                self.deck.append(rank + suit)
    def shuffle(self):
        random.shuffle(self.deck)
    def distributeCards(self):
        return self.deck.pop(), self.deck.pop()
    def flop(self):
        return self.deck.pop(), self.deck.pop(), self.deck.pop()
    def turn(self):
        return self.deck.pop()
    def river(self):
        return self.deck.pop()
