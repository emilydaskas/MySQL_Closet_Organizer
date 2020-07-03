import tkinter as tk
import pandas as pd
from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
import time
import datetime
from PIL import Image,ImageTk
import mysql.connector
from ClosetItem import ClosetItem
from ColorClass import ColorClass
from StyleClass import StyleClass
from BrandClass import BrandClass
from Scrollable import Scrollable
import os

imagePath = ""

#global variables
imageArray = []
iconImage = None
newPhoto = None


#used for generating excel file at the end
openingTime = time.time()
openingTimeStamp = datetime.datetime.fromtimestamp(openingTime).strftime('%Y-%m-%d %H:%M:%S')

insertColorSQL = "INSERT INTO Colors(Color) VALUES(%s)"
insertBrandSQL = "INSERT INTO Brands(BrandName) VALUES(%s)"
insertStyleSQL = "INSERT INTO Category(CategoryName) VALUES(%s)"

root = Tk()
root.rowconfigure(1, weight = 0)
root.grid_columnconfigure(1, weight = 3, minsize = 600)
root.grid_columnconfigure(2, weight = 1)
root.grid_columnconfigure(0, weight=0, minsize = 200)
root.grid_rowconfigure(0, weight = 1, minsize = 200)


# open database connection
mydb = mysql.connector.connect(
    host="HOST",
    user="USER",
    passwd="PASSWD",
    database="DATABASE",
    use_pure = True
)

mycursor = mydb.cursor()


    
# Functions to get image and connvert into blob to send to mysql

def convertToBinaryData(filename):
    # Convert digital data to binary format
    with open(filename, 'rb') as file:
        binaryData = file.read()
    return binaryData
    
    
    

# functions to get image blobs from mysql database and read
def write_file(data, filename):
    # Convert binary data to proper format and write it on Hard Disk
    with open(filename, 'wb') as file:
        file.write(data)




# clothing item cell class
# sets up the layout of the clothing item cell
# propogate the cell with data
# gives functionality to the cell

class ClothingItemCell(tk.Frame):
    def __init__(self, frame, closetItem):
        tk.Frame.__init__(self, frame)
        cleanVar = tk.IntVar(value = closetItem.getIsClean())

        #time stamp used for soft deleting image from database
        ts = time.time()
        timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

        containerCell = Frame(frame, highlightbackground="grey", highlightcolor="grey", highlightthickness=0)
        containerCell.grid(sticky=(N, W), padx=5, pady=5)

        canvas = Canvas(containerCell, width=135, height=135, bg="white")
        canvas.grid(column=0, row=0, rowspan=4, pady= 3, padx = 3)

        # when the cell is checked it is clean, unchecked it is not clean
        # updates the the cewll to either display all items or onyl cleann items
        # updates laundry list accordingly
        def itemChecked():
            updateItem(closetItem.getId(), cleanVar.get())
            getLaundryResults()

        # soft deletes item from database
        # updates laundry list accordingly
        def deleteClicked():
            deleteItem(closetItem.getId(), timestamp)
            getLaundryResults()

        # if the item does not have an image, do not display
        if closetItem.image is None:
            canvas.grid(column = 2)
            canvas.create_image(0, 0, anchor=NW, image=iconImage)
            imageArray.append(iconImage)

        # if there is an item, display it, adjusts size to fit cell
        else:
            readBLOB(closetItem.getId(), "{}.jpeg".format(closetItem.getId()))
            canvas.config(bg="pink")
            readBLOB(closetItem.getId(), "{}.jpeg".format(closetItem.getId()))

            theImage = Image.open("{}.jpeg".format(closetItem.getId()))
            new_image = theImage.resize((140,140))
            img = ImageTk.PhotoImage(new_image)
            canvas.create_image(0, 0, anchor=NW, image=img)
            imageArray.append(img)

        # sets up the rest of the widgets layouts
        deleteButton = Button(containerCell, text = "X", highlightthickness = 0, borderwidth = 0, command = deleteClicked)
        isCleanCheck = Checkbutton(containerCell, text="Clean", variable=cleanVar, command=itemChecked)
        clothingNameLabel = Label(containerCell, text= closetItem.getName(), font=("Helvetica Bold", 16), width=40, anchor=W)
        clothingBrandLabel = Label(containerCell, text="Brand: {}".format(closetItem.getBrand()))
        clothingCategoryLabel = Label(containerCell, text="Style: {}".format(closetItem.getStyle()))
        clothingColorLabel = Label(containerCell, text="Color: {}".format(closetItem.getColor()))

        deleteButton.grid(column = 3, row = 0, sticky= (E), padx = 10)
        isCleanCheck.grid(column=3, row=3, sticky=E, padx = 10)
        clothingNameLabel.grid(column=1, row=0, sticky=W)
        clothingBrandLabel.grid(column=1, row=1, sticky=W)
        clothingCategoryLabel.grid(column=1, row=2, sticky=W)
        clothingColorLabel.grid(column=1, row=3, sticky=W)



def readBLOB(id, photo):
    print("Reading BLOB data from python_employee table")
    try:
        sql_fetch_blob_query = """SELECT Id, Photo from Item where Id = %s"""
        print(">>")
        mycursor.execute(sql_fetch_blob_query, (id,))
        print("ADF")
        record = mycursor.fetchall()
        print("!")
        print(record)
        for row in record:
            print(row[1])
            print("Id = ", row[0], )
            image = row[1]
            print("Storing employee image and bio-data on disk \n")
            write_file(image, photo)
    except mysql.connector.Error as error:
        print("Failed to read BLOB data from MySQL table {}".format(error))
    finally:
        print("MySQL connection is closed")
        
# update item's isclean attribute
def updateItem(itemId, isClean):
    mycursor.execute("UPDATE Item SET IsClean = %s WHERE Id = %s", (isClean, itemId))
    mydb.commit()


# soft deletes item with a timestamp
def deleteItem(itemId, timeStamp):
    mycursor.execute("UPDATE Item SET IsDeleted = %s WHERE Id = %s", (timeStamp, itemId))
    mydb.commit()
    updateClosetItemList()


# gets all items from the closet and puts into an array of ClosetItem class
def getAllClosetItems():
    mycursor.execute("SELECT Item.Id, Item.ItemName, C2.Color, B.BrandName, C3.CategoryName, Item.IsClean, Item.IsDeleted, Item.Photo FROM Item "
                     "JOIN ItemColor IC on Item.Id = IC.ItemId "
                     "JOIN Colors C2 on IC.ColorId = C2.Id "
                     "JOIN Brands B on Item.BrandId = B.Id "
                     "JOIN Category C3 on Item.StyleId = C3.Id WHERE IsDeleted IS NULL")

    items = mycursor.fetchall()
    itemsArray = []

    for item in items:
        closetItem = ClosetItem(item[0], item[1], item[2], item[3], item[4], item[5], item[6], item[7])
        itemsArray.append(closetItem)
    return itemsArray


# get a single item from closet based on id
def getClosetItem(id):
    mycursor.execute("SELECT Item.Id, Item.ItemName, C2.Color, B.BrandName, C3.CategoryName, Item.Photo FROM Item "
                     "JOIN ItemColor IC on Item.Id = IC.ItemId "
                     "JOIN Colors C2 on IC.ColorId = C2.Id "
                     "JOIN Brands B on Item.BrandId = B.Id "
                     "JOIN Category C3 on Item.StyleId = C3.Id "
                     "WHERE Item.Id = %s AND IsDeleted IS NULL", (id,))
    item = mycursor.fetchone()
    return item


# sql query functions
def getAllBrands() :
    brandArray = []
    mycursor.execute("SELECT * FROM Brands")
    brands = mycursor.fetchall()
    for brand in brands:
        thebrand = BrandClass(brand[0], brand[1])
        brandArray.append(thebrand)
    return brandArray


# get all colors and put into array of Color class
def getAllColors():
    colorArray = []
    mycursor.execute("SELECT * FROM Colors")
    colors = mycursor.fetchall()
    for color in colors:
        thecolor = ColorClass(color[0], color[1])
        colorArray.append(thecolor)
    return colorArray



# get all styles and put into array of style class
def getAllStyles():
    styleArray = []
    mycursor.execute("SELECT * FROM Category")
    styles = mycursor.fetchall()
    for style in styles:
        thestyle = StyleClass(style[0], style[1])
        styleArray.append(thestyle)
    return styleArray


# insert into one of the filter tables, takes in sql strings to be used for multiple tables
def insertIntoTable(sql, value) :
    mycursor.execute(sql, (value,))
    return mycursor.lastrowid
    

# queries to get laundry black and white
def queryCountBlackWhiteLaundry():
    mycursor.execute("SELECT DISTINCT Color, Count(Color) FROM Colors "
                     "JOIN ItemColor IC on Colors.Id = IC.ColorId "
                     "JOIN Item I on IC.ItemId = I.Id "
                     "WHERE isClean = 0 AND IsDeleted IS NULL "
                     "GROUP BY Color HAVING Color = 'White' OR Color = 'Black'")
    results = mycursor.fetchall()
    return results


# gets count of all colorful laundry
def queryCountAllColorfulLaundry():
    mycursor.execute("SELECT Count(*) FROM Item JOIN ItemColor IC on Item.Id = IC.ItemId "
                     "WHERE Item.IsDeleted IS NULL AND NOT Item.IsClean "
                     "AND ColorId NOT IN "
                     "(SELECT Colors.Id FROM Colors WHERE Colors.Color = 'White' OR Colors.Color = 'Black')")
    results = mycursor.fetchone()
    return results

# insert a new item into the database


def insertNewItem(name, style, brand, color, photo):
    global addImageToDB
    if addImageToDB == True:
        image = convertToBinaryData(photo)
        addImageToDB = False
    else:
        image = None
        
    mycursor.execute("INSERT INTO Item(ItemName, StyleId, BrandId, IsClean, Photo) "
                     "VALUES (%s, %s, %s, %s, %s)",
                     (name, style, brand, True, image))
    itemId = mycursor.lastrowid
    mycursor.execute("INSERT INTO ItemColor(ItemId, ColorId) "
                      "VALUES (%s, %s)",
                      (itemId, color,))

    mydb.commit()
    updateFilterOptions()
    updateClosetItemList()
    #reset views
    canvas.delete('imageTag')
    imageWarningLabel.config(text="")



items = getAllClosetItems()
brands = getAllBrands()
colors = getAllColors()
styles = getAllStyles()


# when the user adds a new style, brand, or color, update views accordingly
def updateFilterOptions():

    global brands
    global colors
    global styles

    brands = getAllBrands()
    colors = getAllColors()
    styles =  getAllStyles()

    global brandDisplay
    global colorDisplay
    global styleDisplay

    brandDisplay = createSubDisplay(sideBar, brands, 0, chooseBrandFilterVar, "V", "B R A N D", 30)
    colorDisplay = createSubDisplay(sideBar, colors, 1, chooseColorFilterVar, "V", "C O L O R", 15)
    styleDisplay = createSubDisplay(sideBar, styles, 2, chooseStyleFilterVar, "V", "S T Y L E", 15)

    brandDisplay = createSubDisplay(filterContainer, brands, 0, chooseBrandVar, "H", "", 30)
    colorDisplay = createSubDisplay(filterContainer, colors, 1, chooseColorVar, "H", "", 15)
    styleDisplay = createSubDisplay(filterContainer, styles, 2, chooseStyleVar, "H", "", 15)

    chooseBrandVar.set(None)
    chooseStyleVar.set(None)
    chooseColorVar.set(None)

    nameEntry.delete(0, 'end')
    brandDisplay.delete(0, 'end')
    colorDisplay.delete(0, 'end')
    styleDisplay.delete(0, 'end')


def updateClosetItemList():
    global items
    global scrollable_body

    items = getAllClosetItems()

    style = chooseStyleFilterVar.get()
    brand = chooseBrandFilterVar.get()
    color = chooseColorFilterVar.get()

    chooseBrandFilterVar.set(0)
    chooseColorFilterVar.set(0)
    chooseStyleFilterVar.set(0)

    items = []
    items = filterClosetBy(brand, color, style)

    filterViewBody.grid_forget()

    newFilterViewBody = Frame(root)
    newFilterViewBody.grid(row = 3, column = 1, sticky = (N, S, E, W))

    scrollable_body = Scrollable(newFilterViewBody, width=20)

    for i in range(len(items)):
        ClothingItemCell(scrollable_body, items[i])

    scrollable_body.update()



# function to set up displays of brand, style, and color for both creating a new item and filtering
def createSubDisplay(frame, array, containerPosition, variable, orientation, title, limit):
    array = array

    # for filtering. displays veritically and includes label
    if orientation == "V":
        position = 0

        containerCell = Frame(frame)
        containerCell.grid(row=containerPosition, column=0, sticky=(N, S, E, W))

        label = Label(containerCell, text= title, width=22, anchor=W, font=("Helvitica", 12, "bold"))
        label.grid(row=0, sticky = (N, W))

        optionsContainer = Frame(containerCell)
        optionsContainer.grid(row=1, column=0, sticky=(N, S, E, W))

        # add each item from array into a list of displayed radio buttons
        for item in array:
            position = position + 1
            newOption = Radiobutton(optionsContainer, text=item.getName(), variable=variable, value=position)
            newOption.grid(row=position, column=0, sticky=(N, W))

    # for filtering displays horizontally and has an Entry for adding new item to db
    elif orientation == "H" :
        position = 0

        containerCell = Frame(frame)
        containerCell.grid(row=1, column=containerPosition, sticky=(N, S, E, W))

        def limitEntryLength(*args):
            value = entryVal.get()
            if len(value) > limit: entryVal.set(value[:limit])

        entryVal = StringVar()
        entryVal.trace('w', limitEntryLength)

        entry = Entry(containerCell, textvariable = entryVal)
        entry.grid(row= 1, column= 0, sticky = (N,S,E,W))
        entry.grid_remove()

        position = position + 1
        optionsContainer = Frame(containerCell)
        optionsContainer.grid(row=2, column=0, sticky=(N, S, E, W))

        # display and remove entry accordingly based on if user selected "add new" or not
        def getRadioButtonSelected():
            x = variable.get()
            if x == 1:
                entry.grid()
            else:
                entry.grid_remove()

        # radio button for add new
        newOption = Radiobutton(optionsContainer, text="Add New", variable=variable, value=position,
                                 command = getRadioButtonSelected)
        newOption.grid(row=position, column=0, sticky=(N, W))

        for item in array:
            position = position + 1
            newOption = Radiobutton(optionsContainer, text=item.getName(), variable=variable, value=position,
                                    command= getRadioButtonSelected)
            newOption.grid(row=position, column=0, sticky=(N, W))
        return entry


# checks if user filled out all entries for creating a new closet item
# returns true if yes, false if there is still empty entries
def isFormComplete():
    itemsToSave = [checkNameEntry(),
                   getSelection(chooseBrandVar, brandDisplay, brandLabel),
                   getSelection(chooseColorVar, colorDisplay, colorLabel),
                   getSelection(chooseStyleVar, styleDisplay, styleLabel)]
    isComplete = False
    for item in itemsToSave:
        if item == False:
            isComplete = False
            break
        else:
            isComplete = True
    if isComplete == False:
        return False
    else:
        return True


# saves item to database
# creates a new entry if needed
def saveItem():
    if isFormComplete() == True:
        name = nameEntry.get()
        if chooseBrandVar.get() > 1:
            brand = brands[chooseBrandVar.get() - 2].getId()
        else:
            brand = newDatabaseItemFromEntry(chooseBrandVar, brandDisplay, insertBrandSQL)

        if chooseColorVar.get() > 1:
            color = colors[chooseColorVar.get() - 2].getId()
        else:
            color = newDatabaseItemFromEntry(chooseColorVar, colorDisplay, insertColorSQL)

        if chooseStyleVar.get() > 1:
            style = styles[chooseStyleVar.get() -2].getId()
        else:
            style = newDatabaseItemFromEntry(chooseStyleVar, styleDisplay, insertStyleSQL)

        insertNewItem(name, style, brand, color, imagePath)


# check that name entry is completed:
# if yes return true, if not return false
def checkNameEntry():
    if len(nameEntry.get()) == 0:
        nameLabel.config(fg = "#FF8680")
        return False
    else:
        nameLabel.config(fg = "black")
        return True

#
def getSelection(variable, entry, label):
    selection = variable.get()
    if selection == 0:
        label.config(fg = "#FF8680")
        return False
    elif selection == 1:
        if len(entry.get()) == 0:
            label.config(fg = "#FF8680")
            return False
        else:
            print(entry.get())
            label.config(fg="black")
            return True
    else:
        print(selection)
        label.config(fg="black")
        return True


# rename this is makes no sense
def newDatabaseItemFromEntry(variable, entry, sql):
    if (variable.get() == 1) :
        id = insertIntoTable(sql, entry.get())
        return id

# function to filer closet by 1, 2, 3, or 4 different filters
def filterClosetBy(brand, color, style):

    isChecked = cleanVar.get()
    brandId = brands[brand-1].getId()
    colorId = colors[color-1].getId()
    styleId = styles[style - 1].getId()

    itemsArray = []

    if brand == 0 and color == 0 and style == 0 and cleanVar.get() == 0:
        print("no filter")
        itemsArray = getAllClosetItems()

    elif brand == 0 and color == 0 and style == 0 and cleanVar.get() == 1 :
        print("no filter")

        sql = "SELECT Item.Id, Item.ItemName, C2.Color, B.BrandName, C3.CategoryName, Item.IsClean, Item.IsDeleted, Item.Photo FROM Item " \
                    "JOIN ItemColor IC on Item.Id = IC.ItemId " \
                    "JOIN Colors C2 on IC.ColorId = C2.Id " \
                    "JOIN Brands B on Item.BrandId = B.Id " \
                    "JOIN Category C3 on Item.StyleId = C3.Id " \
                    "WHERE IsClean = %s AND IsDeleted IS NULL"
        filters = (isChecked,)

        mycursor.execute(sql, filters)
        items = mycursor.fetchall()

        for item in items:
            closetItem = ClosetItem(item[0], item[1], item[2], item[3], item[4], item[5], item[6], item[7])
            itemsArray.append(closetItem)

    else:
        if isChecked == 1:
            if brand != 0 and color != 0 and style != 0:
                sql = "WHERE B.Id = %s AND ColorId = %s AND StyleId = %s AND IsDeleted IS NULL AND isClean = %s"
                filters = (brandId, colorId, styleId, isChecked,)
            elif brand != 0 and color != 0:
                sql = "WHERE B.Id = %s AND ColorId = %s AND IsDeleted IS NULL AND isClean = %s"
                filters = (brandId, colorId, isChecked,)
            elif color != 0 and style != 0:
                sql = "WHERE ColorId = %s AND StyleId = %s AND IsDeleted IS NULL AND isClean = %s"
                filters = (colorId, styleId, isChecked,)
            elif brand != 0 and style != 0:
                sql = "WHERE B.Id = %s AND StyleId = %s AND IsDeleted IS NULL AND isClean = %s"
                filters = (brandId, styleId, isChecked,)
            elif brand != 0:
                sql = "WHERE B.Id = %s AND IsDeleted IS NULL AND isClean = %s"
                filters = (brandId, isChecked,)
            elif style != 0:
                sql = "WHERE StyleId = %s AND IsDeleted IS NULL AND isClean = %s"
                filters = (styleId, isChecked,)
            elif color != 0:
                sql = "WHERE ColorId = %s AND IsDeleted IS NULL AND isClean = %s"
                filters = (colorId, isChecked,)
        else:
            if brand != 0 and color != 0 and style != 0:
                sql = "WHERE B.Id = %s AND ColorId = %s AND StyleId = %s AND IsDeleted IS NULL"
                filters = (brandId, colorId, styleId, )
            elif brand != 0 and color != 0:
                sql = "WHERE B.Id = %s AND ColorId = %s AND IsDeleted IS NULL"
                filters = (brandId, colorId,)
            elif color != 0 and style != 0:
                sql = "WHERE ColorId = %s AND StyleId = %s AND IsDeleted IS NULL"
                filters = (colorId, styleId,)
            elif brand != 0 and style != 0:
                sql = "WHERE B.Id = %s AND StyleId = %s AND IsDeleted IS NULL"
                filters = (brandId, styleId,)
            elif brand != 0:
                sql = "WHERE B.Id = %s AND IsDeleted IS NULL"
                filters = (brandId,)
            elif style != 0:
                sql = "WHERE StyleId = %s AND IsDeleted IS NULL"
                filters = (styleId,)
            elif color != 0:
                sql = "WHERE ColorId = %s AND IsDeleted IS NULL"
                filters = (colorId,)


        sqlString = "SELECT Item.Id, Item.ItemName, C2.Color, B.BrandName, C3.CategoryName, Item.IsClean, Item.IsDeleted, Item.Photo FROM Item " \
                    "JOIN ItemColor IC on Item.Id = IC.ItemId " \
                    "JOIN Colors C2 on IC.ColorId = C2.Id " \
                    "JOIN Brands B on Item.BrandId = B.Id " \
                    "JOIN Category C3 on Item.StyleId = C3.Id "

        finalquery = sqlString+" "+sql

        mycursor.execute(finalquery, filters)
        items = mycursor.fetchall()

        for item in items:
            closetItem = ClosetItem(item[0], item[1], item[2], item[3], item[4], item[5], item[6], item[7])
            itemsArray.append(closetItem)
    return itemsArray


# fix this so that if you filter by nothing all will display
def filterButtonClicked():
    global items

    style = chooseStyleFilterVar.get()
    brand = chooseBrandFilterVar.get()
    color = chooseColorFilterVar.get()

    items = []
    items = filterClosetBy(brand, color, style )

    filterViewBody.grid_forget()

    newFilterViewBody = Frame(root)
    newFilterViewBody.grid(row = 3, column = 1, sticky = (N, S, E, W))
    scrollable_body = Scrollable(newFilterViewBody, width=20)

    for i in range(len(items)):
        ClothingItemCell(scrollable_body, items[i])
        print(items[i].getItemTuple())

    scrollable_body.update()

    addNewItemToClosetLabel.grid()

#clears filters
def clearFilters():
    chooseBrandFilterVar.set(0)
    chooseColorFilterVar.set(0)
    chooseStyleFilterVar.set(0)
    cleanVar.set(0)
    updateClosetItemList()


# displays the laundry that needs to be done after a specific amount of dirty items of different colors
# called each time an item is checked clean or unclean
def getLaundryResults():
    laundryInfo = ""
    colorCount = queryCountAllColorfulLaundry()
    bwResults = queryCountBlackWhiteLaundry()

    for result in bwResults:
        if result[1] > 5:
            if laundryInfo == "":
                laundryInfo = "T I M E   F O R   L A U N D R Y: You have "
            laundryInfo = laundryInfo + "{} {} items".format(result[1], result[0])

    if colorCount[0] > 5:
        if laundryInfo == "":
            laundryInfo = "Laundry info: You have "
        laundryInfo = laundryInfo + "{} colorful items".format(colorCount[0])

    if laundryInfo != "":
        laundryInfo += " to be washed"

    laundryLabel.config(text = laundryInfo)


# MARK: Main part program.
# sets up views

titleLabel = Label(root, text = "E M I L Y ' S   C L O S E T", bg = "#FFDEE5", fg = "#FF8680", font= ("Times", 30, "bold"))
titleLabel.grid(column = 0, columnspan = 10, sticky = (N, S, E, W))


# layout for filtering and viewing items (left side of screenn

searchClosetLabel = Label(root, text="S E A R C H   C L O S E T", font=("Helvitica", 14, "bold"), bg ="#FF8680", fg ="white")
searchClosetLabel.grid(row=1, column=0, columnspan=2, sticky=(N, S, E, W))

filterViewBody = Frame(root)
filterViewBody.grid(row = 3, column = 1, sticky = (N, S, E, W))

scrollable_body = Scrollable(filterViewBody, width= 20)

for i in range(len(items)):
    cell = ClothingItemCell(scrollable_body, items[i])
    print(items[i])

scrollable_body.update()

laundryLabel = Label(root, text = "THIS IS WHERE THE LAUNDRY ALERT WILL GO!", bg = "#FF8680", fg = "white")
laundryLabel.grid(row = 4, column = 0, columnspan = 4, sticky = "N, S, E, W")

sideBar = Frame(root)
sideBar.grid(row = 3, column = 0, sticky = (N, S, E, W), padx = 10, pady = 10)
root.grid_rowconfigure(1, weight = 2)

chooseBrandFilterVar = tk.IntVar()
brandDisplay = createSubDisplay(sideBar, brands, 0, chooseBrandFilterVar, "V", "B R A N D", 30)

chooseColorFilterVar = tk.IntVar()
colorDisplay = createSubDisplay(sideBar, colors, 1, chooseColorFilterVar, "V", "C O L O R", 15)

chooseStyleFilterVar = tk.IntVar()
styleDisplay = createSubDisplay(sideBar, styles, 2, chooseStyleFilterVar, "V", "S T Y L E", 15)

cleanVar = tk.IntVar()
cleanCheck = Checkbutton(sideBar, text= "View Only Clean Items", pady = 10, variable = cleanVar)
cleanCheck.grid(row = 3, sticky = (N, W))

filterButton = Button(sideBar, text= "S E A R C H", command = filterButtonClicked)
filterButton.grid(row = 4, sticky = (N, S, E , W))

clearFilterButton = Button(sideBar, text = "C L E A R   F I L T E R S", command = clearFilters)
clearFilterButton.grid(row = 5, sticky = (N,S,E,W))


# layout for creating a new item (right side of screen)
addNewItemToClosetLabel = Label(root, text="A D D   N E W   I T E M   T O   C L O S E T",
                                font=("Helvitica", 14, "bold"), bg = "#FF8680", fg = "white")
addNewItemToClosetLabel.grid(row=1, column=2, columnspan=2, sticky=(N, S, E, W))

newItemContainer = Frame(root)
newItemContainer.grid(column = 2, row = 3, sticky = (N, S, E , W), pady = 10, padx = 10)

canvas = Canvas(newItemContainer, bg="white", bd = 1, height=300, width=300)
canvas.grid(column=0, columnspan=3, row=1)


imageContainer = Frame(newItemContainer)
imageContainer.grid(row = 2, rowspan = 1, sticky = (N, E, S, W))

addImageToDB = False

# has user select an image file
def chooseImage():
    global addImageToDB
    global imagePath
    global newPhoto
    imagePath = None
    newPhoto = None
    newPhoto = filedialog.askopenfilename(title="Choose Photo", filetypes= ('image files', ('.png', '.jpg')))

    if (not os.path.exists(newPhoto)):
        addImageToDB = False
        print("OOPS!")
    else:
        imagePath = newPhoto
        if os.path.getsize(imagePath) > 65535:
            imageWarningLabel.config(text="This image is too large. Try again or post item without image.")

            addImageToDB = False
            imagePath = None
            newPhoto = None
        else:
            theImage = Image.open(imagePath)
            new_image = theImage.resize((310, 310))
            img = ImageTk.PhotoImage(new_image)
            addImageToDB = True
            canvas.create_image(0, 0, anchor=NW, image=img, tags='imageTag')
            imageArray.append(img)
            imageWarningLabel.config(text = "")
    return newPhoto


imagePathButton = Button(imageContainer, text = "A D D   I M A G E", command = chooseImage)
imagePathButton.grid(row = 0, column = 0, columnspan = 1, sticky = (N, S, E, W))

imageWarningLabel = Label(imageContainer, text= "warning will go here", fg = 'red')
imageWarningLabel.grid(row = 0, column = 2, sticky= (N, S, E, W))
imageWarningLabel.config(text = "")

nameContainer = Frame(newItemContainer)
nameContainer.grid(row = 3, sticky = (W))

nameLabel = Label(nameContainer, text="I T E M   N A M E", font=("Helvitica", 12, "bold"))
nameLabel.grid(row = 0, column=0, sticky= (N, W))

# limits the length of an entry
def limitEntryLength(*args):
    value = entryVal.get()
    if len(value) > 40: entryVal.set(value[:40])

entryVal = StringVar()
entryVal.trace('w', limitEntryLength)

nameEntry = Entry(nameContainer, width=52, textvariable = entryVal)
nameEntry.grid(row = 0, column=1, columnspan = 3, sticky=(N, W, E, S))

filterContainer = Frame(newItemContainer)
filterContainer.grid(row= 4)

chooseBrandVar = tk.IntVar()
brandLabel = Label(filterContainer, text = "C H O O S E   B R A N D", width = 24, anchor = W, font = ("Helvitica", 12, "bold"))
brandLabel.grid(column = 0, row = 0)
brandDisplay = createSubDisplay(filterContainer, brands, 0, chooseBrandVar, "H", "", 30)

chooseColorVar = tk.IntVar()
colorLabel = Label(filterContainer, text = "C H O O S E   C O L O R", width = 24, anchor = W, font = ("Helvitica", 12, "bold"))
colorLabel.grid(column = 1, row = 0)
colorDisplay = createSubDisplay(filterContainer, colors, 1, chooseColorVar, "H", "", 15)

chooseStyleVar = tk.IntVar()
styleLabel = Label(filterContainer, text = "C H O O S E   S T Y L E", width = 24, anchor = W, font = ("Helvitica", 12, "bold"))
styleLabel.grid(column = 2, row = 0)
styleDisplay = createSubDisplay(filterContainer, styles, 2, chooseStyleVar, "H", "", 15)

saveNewItemButton = Button(filterContainer, text="S A V E", bg="pink", command = saveItem)
saveNewItemButton.grid(column=0, columnspan=3, row=4, sticky=(N, S, E, W))

getLaundryResults()

def generateReports():

    # show all current items
    df = pd.read_sql_query("SELECT Item.ItemName AS 'Item Name', C2.Color AS 'Color', B.BrandName AS 'Brand', C3.CategoryName AS 'Style', Item.IsClean AS 'Clean' FROM Item "
                     "JOIN ItemColor IC on Item.Id = IC.ItemId "
                     "JOIN Colors C2 on IC.ColorId = C2.Id "
                     "JOIN Brands B on Item.BrandId = B.Id "
                     "JOIN Category C3 on Item.StyleId = C3.Id WHERE IsDeleted IS NULL ORDER BY Item.isClean;", mydb)

    writer = pd.ExcelWriter('ClosetReport.xlsx', engine='xlsxwriter')
    df.to_excel(writer, sheet_name='Current Closet Items')

    # show all items deleted during current session
    df = pd.read_sql_query("SELECT ItemName AS 'Deleted Item', IsDeleted AS 'Time Deleted' FROM Item WHERE IsDeleted > %s ORDER BY IsDeleted ASC;", mydb , params=(openingTimeStamp,))
    df.to_excel(writer, sheet_name ='Deleted During This Session')

    df = pd.read_sql_query("SELECT DISTINCT BrandName AS 'Brand', Count(BrandName) AS 'Item Count' FROM Brands JOIN Item ON Item.brandId = Brands.Id WHERE isDeleted IS NULL "
                           "GROUP BY BrandName;", mydb)
    df.to_excel(writer, sheet_name= 'Current Brands in Closet')

    df = pd.read_sql_query("SELECT DISTINCT CategoryName AS 'Style', Count(CategoryName) AS 'Item Count' FROM Category JOIN Item ON Item.StyleId = Category.Id WHERE isDeleted IS NULL "
                           "GROUP BY CategoryName;", mydb)
    df.to_excel(writer, sheet_name= 'Current Styles in Closet')

    df = pd.read_sql_query("SELECT DISTINCT Color , Count(Color) AS 'Item Count' FROM Colors "
                           "Join ItemColor ON ItemColor.ColorId = Colors.Id "
                           "JOIN Item ON Item.Id = ItemColor.ItemId "
                           "WHERE IsDeleted IS NULL "
                           "GROUP BY Color;", mydb)
    df.to_excel(writer, sheet_name= 'Current Colors in Closet')

    writer.save()


def on_closing():
    if messagebox.askyesno("Generate Report", "Would you like to generate a report of the current closet state before quitting?"):
        generateReports()
        root.destroy()
    else:
        root.destroy()


root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()

mycursor.close()
