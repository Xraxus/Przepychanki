class Pawn():
    def __init__(self, color, pawn_id):
        self.color = color
        self.pawn_id = color + str(pawn_id)

    def __repr__(self):
        return "Pawn: %s" % (self.pawn_id)
