from src.library.card import Card
import pygame
import random

class Deck:
    def __init__(self, card_type):
        self.deck_type = card_type
        self.cards = []

        self.build_deck()
        random.shuffle(self.cards)
        if self.deck_type == 'path':
            self.organize_deck()

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
    def build_deck(self):
        name = []
        if self.deck_type == 'fruit':
            name = ['blueberry', 'coconut', 'grape', 'orange', 'peach', 'strawberry']
        elif self.deck_type == 'path':
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
        elif self.deck_type == 'event':
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
            if not 'strike' in i:
                self.cards.append(Card(self.deck_type, i, False))
            else:
                self.cards.append(Card(self.deck_type, i, True))
    
    # This function make sure that there will be no 3 strike cards in a row at the start of a day
    def organize_deck(self):
        disorganized = True
        while disorganized:
            strike_index = []   
            strike_consecutive_count = 0    # This count strikes that are consecutive
            strike_count = 0    # This count strikes to keep track of days
            start_of_today_index = 0    # This keep track of the strike index at the start of today
            start_of_next_day_index = 0   # This keep track of the strike index at the start of the next day
            disorganized = False # The deck is clean until proven otherwise
            for i, card in enumerate(self.cards):
                if card.strike:
                    strike_count += 1
                    strike_consecutive_count += 1
                    strike_index.append(i)
                    # The third strike has been reached, update the start of the day
                    if strike_count == 3:
                        start_of_today_index = start_of_next_day_index
                        start_of_next_day_index = i + 1
                        strike_count = 0
                    # The third strike has been reached consecutively
                    if strike_consecutive_count == 3:
                        # if it is at the start of the day, reshuffle and restart
                        if strike_index[0] == start_of_today_index:
                            random.shuffle(self.cards)
                            disorganized = True
                            break
                        else:
                            strike_index = []
                            strike_consecutive_count = 0
                else:
                    strike_index = []
                    strike_consecutive_count = 0

    def verify_consecutive_strike(self):
        strike_indices = []
        for i, card in enumerate(self.cards):
            if card.strike:
                strike_indices.append(i)
        return strike_indices
                        
        