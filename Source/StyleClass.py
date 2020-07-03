class StyleClass:
    def __init__(self, id, style):
        self.id = id
        self.style = style

    def getId(self):
        return self.id

    def getName(self):
        return self.style

    def getStyleTuple(self):
        return (self.id, self.style,)

