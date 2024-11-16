class Cards:
    def __init__(self, card_type, card_name, isStrike):
        self.card_type = card_type
        self.card_name = card_name
        self.strike = isStrike

    def __repr__(self):
        return f"Card(card_type={self.card_type}, card_name={self.card_name}, strike={self.strike})\n"