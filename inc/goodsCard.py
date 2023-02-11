class GoodsCard():
    def __init__(self, category, name, description):
        self.category = category
        self.name = name
        self.description = description

    def __repr__(self):
        return '(%s, %s [%s])' % (self.name, self.description, self.category)

