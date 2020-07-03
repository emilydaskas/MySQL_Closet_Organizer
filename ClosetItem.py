
class ClosetItem:
    def __init__(self, id, name, color, brand, style, isClean, isDeleted, image):
        self.id = id
        self.name = name
        self.color = color
        self.brand = brand
        self.style = style
        self.isClean = isClean
        self.isDeleted = isDeleted
        self.image = image

    def getId(self):
        return self.id

    def getName(self):
        return self.name

    def getColor(self):
        return self.color

    def getBrand(self):
        return self.brand

    def getStyle(self):
        return self.style

    def getIsClean(self):
        return self.isClean

    def getIsDeleted(self):
        return self.isDeleted

    def getImage(self):
        return self.image

    def getItemTuple(self):
        return (self.id, self.name, self.color, self.brand, self.style, self.isClean, self.isDeleted, self.image,)

    def getItemInfo(self):
        return (self.name, self.style, self.brand,)
