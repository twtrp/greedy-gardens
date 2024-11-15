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

        # # comment if want to test card or deck
        # if self.deck_type == 'path':
        #     self.organize_deck()

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
            name = ['fruit_blueberry', 'fruit_coconut', 'fruit_grape', 'fruit_orange', 'fruit_peach', 'fruit_strawberry']
        # elif self.deck_type == 'path':
        #     for i in range(6):
        #         name.append('path_WS')
        #         name.append('path_ES')
        #         name.append('path_WE')
        #         name.append('path_NS')
        #         name.append('path_NW')
        #         name.append('path_NE')
        #     for i in range(3):
        #         name.append('path_strike_WS')
        #         name.append('path_strike_ES')
        #         name.append('path_strike_WE')
        #         name.append('path_strike_NS')
        #         name.append('path_strike_NW')
        #         name.append('path_strike_NE')
        #     name.append('path_WES')
        #     name.append('path_NWS')
        #     name.append('path_NES')
        #     name.append('path_NWE')
        #     name.append('path_strike_WE')
        #     name.append('path_strike_NWS')
        #     name.append('path_strike_NES')
        #     name.append('path_strike_NWE')
        # elif self.deck_type == 'event':
        #     for i in range(2):
        #         name.append('event_free')
        #         name.append('event_keep')
        #         name.append('event_merge')
        #         name.append('event_point')
        #         name.append('event_redraw')
        #         name.append('event_remove')
        #         name.append('event_reveal')
        #         name.append('event_swap')

        # For Testing cards
        elif self.deck_type == 'path':
            for i in range(25):
                name.append('path_strike_WS')
                name.append('path_strike_WES')
        elif self.deck_type == 'event':
            for i in range(16):
                name.append('event_swap')

        for i in name:
            if not 'strike' in i:
                self.cards.append(Cards(self.deck_type, i, False))
            else:
                self.cards.append(Cards(self.deck_type, i, True))
    
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

    def not_all_duplicate(self):
        for i in range(1,len(self)):
            card1 = self[0].card_name
            card2 = self[i].card_name
            if card1[-3:] != card2[-3:]:
                return True
        return False       

        