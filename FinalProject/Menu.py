import cv2
import face_recognition
import pickle
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
import openpyxl
from tkinter import *
from sklearn.model_selection import train_test_split
from tensorflow.keras.utils import to_categorical
import subprocess


cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://faceattendancerealtime-1a592-default-rtdb.firebaseio.com/",
    "storageBucket": "faceattendancerealtime-1a592.appspot.com"
})

root3 = Tk()
root3.title("MENU")
root3.geometry("1250x700+210+100")

all_lessons = ['Math', 'Science', 'History', 'English', 'Programming', 'Art']

# Load the PNG image
image2 = PhotoImage(file="ATTENDANCE.png")

# Create a Label widget to display the image
label2 = Label(root3, image=image2)
label2.place(x=0, y=0, relwidth=1, relheight=1)

# Bind the Label to the window resize event
def resize_image(event):
    new_width = event.width
    new_height = event.height
    image2.subsample(int(new_width / 100), int(new_height / 100))
    label2.config(image=image2)

def run_script(choosen_one):
    # Call the main.py file with the selected lesson
    exec(open('main.py').read(), {'choosen_one': choosen_one})

root3.bind("<Configure>", resize_image)

# Define functions for the scripts
def show_lessons():
    # Create a new window to display the lessons
    lesson_window = Toplevel(root3)
    lesson_window.title("Lessons")
    lesson_window.geometry("400x400")

    # Create a listbox to display the lessons
    lesson_listbox = Listbox(lesson_window, height=len(all_lessons))
    lesson_listbox.pack(fill=BOTH, expand=True)

    # Populate the listbox with the lessons
    for lesson in all_lessons:
        lesson_listbox.insert(END, lesson)

    # Create a button to launch the selected lesson
    launch_button = Button(lesson_window, text="Launch", command=lambda: run_script(lesson_listbox.get(ACTIVE)))
    launch_button.pack(side=BOTTOM, pady=10)



def run_add_data():
    exec(open('AddDataToDatabase.py').read())

def run_encoding():
    exec(open('EncodeGenerator.py').read())

def registration_system():
    # Call the StudentRegistrationSystem.py file
    subprocess.call(["python", "StudentRegistrationSystem.py"])

def cheat_detection():
    subprocess.run(["python", "venv/bin/Cheating.py"])

def exit():
    root3.destroy()

# Add other widgets to the window
Label(root3, text="MENU", width=30, height=2, bg="#c36464", fg='#fff', font='arial 20 bold').pack(side=TOP, fill=X)

Button(root3, text="ATTENDANCE", width=30, height=2, font="arial 14 bold", bg="lightblue", command=show_lessons).place(x=500, y=200)
Button(root3, text="ADD TO DATABASE", width=30, height=2, font="arial 14 bold", bg="lightgreen", command=run_add_data).place(x=500, y=280)
Button(root3, text="ENCODE GENERATOR", width=30, height=2, font="arial 14 bold", bg="lightpink", command=run_encoding).place(x=500, y=360)
Button(root3, text="STUDENT REGISTRATION SYSTEM", width=30, height=2, font="arial 14 bold", bg="lightgray", command=registration_system).place(x=500, y=440)
Button(root3, text="CHEAT DETECTOR", width=30, height=2, font="arial 14 bold", bg="yellow", command=cheat_detection).place(x=500, y=520)
Button(root3, text="EXIT", width=15, height=2, font="arial 14 bold", bg="red", command=exit).place(x=950, y=590)

root3.mainloop()
