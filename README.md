# MySQL_Closet_Organizer
Uses MySQL to create a closet inventory and organization tool. Final Project for Database Management, CS408.

***In order to run, you would need to connect to an existing MySQL database!***

### To run:

install the following packages:

Pip install pandas
pip install mysql-connector-python
pip install pillow

  In order to run, you would need to connect to an existing MySQL database, and fill in the database, user, password, and host fields before running the program.     
  Program will not run if this is not done.

  Prior to running the program, run the console_closet.sql file to create tables and indices.
  In the command line, run 'python ClosetMain.py' from within its directory.
  
  
  
### Video preview of the program
  
  To view a preview of some of the functionality of the program, download and play the ClosetDemo.mov file. This shows a quick preview of adding an item to the db, adding a new style, and filtering items by different features. You can download the preview here.
  https://github.com/daska102/MySQL_Closet_Organizer/blob/master/Preview%20Files/ClosetDemo.mov
  
  
  
### Screenshot of the program
  
  ![Image of Program](https://github.com/daska102/MySQL_Closet_Organizer/blob/master/Preview%20Files/ScreenShotCloset.png)
 
 
 
### Database Schema

![Image of Schema](https://github.com/daska102/MySQL_Closet_Organizer/blob/master/Preview%20Files/ClosetDBSchema.png)


### Project Functionality

 - Add items to your closet, either with or without an image (all other fields required).
 - Add new brands, colors, and/or styles of clothes to the closet when adding a new item.
 - Delete items from the database/closet (this is a soft delete).
 - Mark clothes as clean/dirty and search by only clean clothes.
 - Notifies you if you have 6 or more dirty 'White', 'Black', or colorful items to tell you it is time to do the laundry.
 - When exiting the program, it gives you an option to generate a report of all of the changes you have made.
*/

Created August 2019 for Database Management, CS408

### Contact
Emily Daskas
emilydaskas@gmail.com
