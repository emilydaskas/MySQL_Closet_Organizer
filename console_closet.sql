CREATE TABLE IF NOT EXISTS Brands (
        Id INTEGER PRIMARY KEY NOT NULL AUTO_INCREMENT,
        BrandName VARCHAR(30)
    );

CREATE TABLE  IF NOT EXISTS Colors (
        Id INTEGER PRIMARY KEY NOT NULL AUTO_INCREMENT,
        Color VARCHAR(10)
    );

CREATE TABLE  IF NOT EXISTS Category (
        Id INTEGER PRIMARY KEY NOT NULL AUTO_INCREMENT,
        CategoryName VARCHAR (15)
    );

CREATE TABLE IF NOT EXISTS Item (
        Id INTEGER PRIMARY KEY NOT NULL AUTO_INCREMENT,
        ItemName VARCHAR(30),
        StyleId INTEGER,
        BrandId INTEGER,
        IsClean BOOLEAN,
        IsDeleted TIMESTAMP DEFAULT NULL NULL,
        Photo BLOB,
        FOREIGN KEY (StyleId) REFERENCES Category(Id),
        FOREIGN KEY (BrandId) REFERENCES Brands(Id)
    );
    
CREATE TABLE IF NOT EXISTS ItemColor (
        ItemId INTEGER,
        ColorId INTEGER,
        FOREIGN KEY (ItemId) REFERENCES Item(Id),
        FOREIGN KEY (ColorId) REFERENCES  Colors(Id),
        UNIQUE (ItemId, ColorId)
    );


CREATE INDEX color_id_idx ON Colors(Id);

CREATE INDEX category_id_idx ON Category(Id);

CREATE INDEX brand_id_idx ON Brands(Id);

CREATE INDEX item_style_idx ON Item(StyleId);

CREATE INDEX item_brand_idx ON Item(BrandId);

CREATE INDEX item_isClean_idx ON Item(IsClean);

CREATE INDEX item_isDeleted_idx ON Item(IsDeleted);

CREATE INDEX ic_colorid_id ON ItemColor(ColorId);

CREATE INDEX ic_itemid_idx ON ItemColor(ItemId);
    