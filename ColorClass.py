
class ColorClass :
    def __init__(self, id, color):
        self.id = id
        self.color = color

    def getId(self):
        return self.id

    def getName(self):
        return self.color

    def getColorTuple(self):
        return (self.id, self.color,)

