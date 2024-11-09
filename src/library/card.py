class card:
    def __init__(self, card_type, card_name):
        self.card_type = card_type
        self.card_name = card_name

    def __repr__(self):
        return f"Card({self.card_type})"