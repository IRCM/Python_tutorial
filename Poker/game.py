from deck import Deck
from player import Player

deck = Deck()

deck.shuffle()

player1 = Player(deck.distributeCards())
player1.cards
player2 = Player(deck.distributeCards())
player2.cards

deck.flop()
deck.turn()
deck.river()