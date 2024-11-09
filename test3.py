# Kram testing site

from src.library.deck import deck

event_deck = deck('path')
print(event_deck.verify_consecutive_strike())