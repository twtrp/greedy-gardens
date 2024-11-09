from src.library.card import card
import pygame
import random

class deck:
    def __init__(self, card_type, card_names):
        self.cards = [card(card_type, name) for name in card_names]
        random.shuffle(self.cards)

    def draw_card(self):
        if self.cards:
            return self.cards.pop()
        else:
            return None
        
    def remaining_cards(self):
        return len(self.cards)