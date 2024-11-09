from src.library.card import card
import pygame
import random

class deck:
    def __init__(self, card_type):
        self.deck_type = card_type
        self.cards = self.build_deck(card_type)
        random.shuffle(self.cards)

    def draw_card(self):
        if self.cards:
            return self.cards.pop()
        else:
            return None
        
    def remaining_cards(self):
        return len(self.cards)
    
    '''
    Specified type to build the deck
    - fruit has 6 cards
    - path has 62 cards
      - 36 normal + 18 strike 2 ways paths
      - 4 normal + 4 strike 3 ways paths
    - event has 18 cards (9 types of events)
    '''
    def build_deck(self, type):
        print('start building')
        deck = []
        name = []
        if type == 'fruit':
            name = ['blueberry', 'coconut', 'grape', 'orange', 'peach', 'strawberry']
        elif type == 'path':
            for i in range(6):
                name.append('card_path_WS')
                name.append('card_path_ES')
                name.append('card_path_WE')
                name.append('card_path_NS')
                name.append('card_path_NW')
                name.append('card_path_NE')
            for i in range(3):
                name.append('card_path_strike_WS')
                name.append('card_path_strike_ES')
                name.append('card_path_strike_WE')
                name.append('card_path_strike_NS')
                name.append('card_path_strike_NW')
                name.append('card_path_strike_NE')
            name.append('card_path_WES')
            name.append('card_path_NWS')
            name.append('card_path_NES')
            name.append('card_path_NWE')
            name.append('card_path_strike_WE')
            name.append('card_path_strike_NWS')
            name.append('card_path_strike_NES')
            name.append('card_path_strike_NWE')
        elif type == 'event':
            for i in range(2):
                name.append('card_event_free')
                name.append('card_event_keep')
                name.append('card_event_merge')
                name.append('card_event_point')
                name.append('card_event_redraw')
                name.append('card_event_remove')
                name.append('card_event_reveal')
                name.append('card_event_swap')
        for i in name:
            deck.append(card(type, i))
        print(f"finish building {type}")
        return deck
        