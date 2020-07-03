
class BrandClass:
    def __init__(self, id, brand):
        self.id = id
        self.brand = brand

    def getId(self):
        return self.id

    def getName(self):
        return self.brand

    def getBrandTuple(self):
        return (self.id, self.brand,)
