from src.library.essentials import *
from src.classes.Cards import Cards
import random

class Deck:
    def __init__(self, card_type, seed):
        self.deck_type = card_type
        self.seed = seed
        self.cards = []

        random.seed(self.seed)

        self.build_deck()
        random.shuffle(self.cards)

        self.developer_mode = True

        # # comment if want to test card or deck
        if self.deck_type == 'path':
            self.organize_deck()

    def add_card_to_top(self, card_name, is_strike=False):
        """Add a card to the top of the deck (for developer mode)"""
        self.cards.append(Cards(self.deck_type, card_name, is_strike))

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
      - 8 normal 3 ways paths
    - event has 18 cards (9 types of events)
    '''
    def build_deck(self):
        name = []
        if self.deck_type == 'fruit':
            name = ['fruit_blueberry', 'fruit_coconut', 'fruit_grape', 'fruit_orange', 'fruit_peach', 'fruit_strawberry']
            
        elif self.deck_type == 'path':
            for i in range(6):
                name.append('path_WS')
                name.append('path_ES')
                name.append('path_WE')
                name.append('path_NS')
                name.append('path_NW')
                name.append('path_NE')
            for i in range(3):
                name.append('path_strike_WS')
                name.append('path_strike_ES')
                name.append('path_strike_WE')
                name.append('path_strike_NS')
                name.append('path_strike_NW')
                name.append('path_strike_NE')
            for i in range(1):
                name.append('path_WES')
                name.append('path_NWS')
                name.append('path_NES')
                name.append('path_NWE')
            for i in range(1):
                name.append('path_strike_WES')
                name.append('path_strike_NWS')
                name.append('path_strike_NES')
                name.append('path_strike_NWE')
        # For Testing path
            # for i in range(16):
            #     name.append('path_strike_WES')
            #     name.append('path_strike_NWS')
            #     name.append('path_NES')
            #     name.append('path_NWE') # Should always have a non-strike card or it will freeze

        elif self.deck_type == 'event':
            for i in range(2):
                name.append('event_free')
                name.append('event_move')
                name.append('event_merge')
                name.append('event_point')
                name.append('event_redraw')
                name.append('event_remove')
                name.append('event_reveal')
                name.append('event_swap')
        # For Testing events
            # for i in range(16):
            #     name.append('event_reveal')




        for i in name:
            if not 'strike' in i:
                self.cards.append(Cards(self.deck_type, i, False))
            else:
                self.cards.append(Cards(self.deck_type, i, True))
    
    # This function ensures there are no 3 consecutive strike cards anywhere in the deck
    def organize_deck(self):
        while self.has_three_consecutive_strikes():
            random.shuffle(self.cards)
        
        self.cards.reverse()
    
    def has_three_consecutive_strikes(self):
        """Check if there are 3 consecutive strike cards anywhere in the deck"""
        consecutive_strikes = 0
        
        for card in self.cards:
            if card.strike:
                consecutive_strikes += 1
                if consecutive_strikes >= 3:
                    return True
            else:
                consecutive_strikes = 0
        
        return False

    def verify_consecutive_strike(self):
        strike_indices = []
        for i, card in enumerate(self.cards):
            if card.strike:
                strike_indices.append(i)
        return strike_indices

    def not_all_duplicate(self):
        copied_array = copy.deepcopy(self)
        cleaned_copy = [path.card_name.replace('path_', '').replace('strike_', '') for path in copied_array]
        for i in range(1,len(cleaned_copy)):
            card1 = self[0].card_name
            card2 = self[i].card_name
            if card1 != card2:
                return True
        return False 
        