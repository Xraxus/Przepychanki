class SupplyCard():
    def __init__(self, category, amount):
        self.category = category
        self.amount = amount

    def __repr__(self):
        return '(Category: %s, Amount: %d)' % (self.category, self.amount)