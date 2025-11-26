from src.library.essentials import *
from src.template.BaseTutorialModule import BaseTutorialModule


class Module_ManipulateDeck(BaseTutorialModule):
    def __init__(
        self,
        deck_type: str,
        card_name: str,
        tutorial_state = None,
    ):
        """
        Initialize deck manipulation module
        
        deck_type: Type of deck to manipulate ('fruit', 'path', or 'event')
        card_name: Name of the card to move to the top of the deck
        tutorial_state: Reference to Tutorial_PlayState for accessing decks
        """
        super().__init__(fade_duration=0)
        
        if deck_type not in ['fruit', 'path', 'event']:
            raise ValueError(f"deck_type must be 'fruit', 'path', or 'event', got '{deck_type}'")
        
        self.surface = None
        self.deck_type = deck_type
        self.card_name = card_name
        self.tutorial_state = tutorial_state
        self.manipulated = False
    
    def _update_inject(self, dt, events):
        # Execute manipulation once when module becomes visible
        if not self.manipulated and self.tutorial_state is not None:
            self.manipulated = True
            self._manipulate_deck()
    
    def _manipulate_deck(self):
        """Move the specified card to the top of the chosen deck"""
        # Get the appropriate deck
        deck = None
        if self.deck_type == 'fruit':
            deck = self.tutorial_state.deck_fruit
        elif self.deck_type == 'path':
            deck = self.tutorial_state.deck_path
        elif self.deck_type == 'event':
            deck = self.tutorial_state.deck_event
        
        if deck is None:
            print(f"Warning: Could not find {self.deck_type} deck")
            return
        
        # Find the card in the deck
        card_index = None
        for i, card in enumerate(deck.cards):
            if card.card_name == self.card_name:
                card_index = i
                break
        
        # If card not found, print warning and do nothing
        if card_index is None:
            print(f"Warning: Card '{self.card_name}' not found in {self.deck_type} deck")
            return
        
        # If card is already at the top (last position), do nothing
        if card_index == len(deck.cards) - 1:
            return
        
        # Remove the card from its current position and add it to the top
        card = deck.cards.pop(card_index)
        deck.cards.append(card)
        
        print(f"Moved '{self.card_name}' to top of {self.deck_type} deck")
