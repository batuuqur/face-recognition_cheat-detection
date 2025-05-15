import tkinter as tk
from PIL import Image, ImageTk
import webbrowser
import subprocess

all_lessons = ['Math', 'Science', 'History', 'English', 'Programming', 'Art']

def run_script():
    # Call the main.py file
    subprocess.call(["python", "StudentRegistrationSystem.py"])

def run_script2():
    # Call the main.py file
    subprocess.call(["python", "main.py"])

# Define the PNG file path
image_path = "ATTENDANCE.png"

# Define a function to open the PNG file in the default web browser
def open_image():
    webbrowser.open(image_path)

# Define a custom function to create rounded rectangles using the create_polygon function of the canvas
def create_rounded_rectangle(canvas, x1, y1, x2, y2, radius, **kwargs):
    points = [x1 + radius, y1,
              x1 + radius, y1,
              x2 - radius, y1,
              x2 - radius, y1,
              x2, y1,
              x2, y1 + radius,
              x2, y1 + radius,
              x2, y2 - radius,
              x2, y2 - radius,
              x2, y2,
              x2 - radius, y2,
              x2 - radius, y2,
              x1 + radius, y2,
              x1 + radius, y2,
              x1, y2,
              x1, y2 - radius,
              x1, y2 - radius,
              x1, y1 + radius,
              x1, y1 + radius,
              x1, y1]

    return canvas.create_polygon(points, smooth=True, **kwargs)


# Create a Tkinter window
root = tk.Tk()
root.geometry("1280x720")

# Load the PNG image
image = Image.open(image_path)
photo = ImageTk.PhotoImage(image)

# Create a canvas to display the image and buttons
canvas = tk.Canvas(root, width=image.width, height=image.height)
canvas.pack()

# Create a label to display the image
canvas.create_image(0, 0, anchor=tk.NW, image=photo)

# Define a function to change the color of a button when it's clicked
def button_clicked(button, color):
    canvas.itemconfig(button, fill=color)
    root.update()
    canvas.after(100, lambda: canvas.itemconfig(button, fill="#007bff"))

popup_menu = tk.Menu(root, tearoff=0)

# Create rounded rectangle buttons that open the PNG file and popup menu when clicked
def open_popup_menu(widget):
    popup_menu.post(1050, widget.winfo_rooty() + 310)

def set_x(value):
    global x
    x = value

popup_menu = tk.Menu(root, tearoff=0)
for i, lesson in enumerate(all_lessons):
    popup_menu.add_command(label=lesson, command=lambda value=lesson: set_x(value))




button_a = tk.Button(canvas, text="Button A")
button_a_background = create_rounded_rectangle(canvas, 600, 165, 900, 268, radius=10, fill="#007bff", outline="#007bff", width=0)
button_a_text = canvas.create_text(700, 225, text="Button A", fill="white", font=("Arial", 14, "bold"))
canvas.tag_bind(button_a_background, "<Button-1>", lambda event: open_popup_menu(button_a))



button_b_background = create_rounded_rectangle(canvas, 600, 308, 900, 410, radius=10, fill="#dc3545", outline="#dc3545", width=0)
button_b_text = canvas.create_text(700, 325, text="Button B", fill="white", font=("Arial", 14, "bold"))
canvas.tag_bind(button_b_background, "<Button-1>", lambda event: (button_clicked(button_b_background, "#a71d2a"), run_script()))



button_c_background = create_rounded_rectangle(canvas, 600, 450, 900, 552, radius=10, fill="#28a745", outline="#28a745", width=0)
button_c_text = canvas.create_text(700, 500, text="Button C", fill="white", font=("Arial", 14, "bold"))
canvas.tag_bind(button_c_background, "<Button-1>", lambda event: (button_clicked(button_c_background, "#a71d2a"), exec(open(open_image()).read())))

# Define a function to exit the application
def exit_app():
    root.destroy()

# Create an exit button that closes the application when clicked
exit_button_background = create_rounded_rectangle(canvas, 1150, 640, 1250, 690, radius=10, fill="#6c757d", outline="#6c757d", width=0)
exit_button_text = canvas.create_text(1200, 665, text="Exit", fill="white", font=("Arial", 14, "bold"))
canvas.tag_bind(exit_button_background, "<Button-1>", lambda event: exit_app())

# Start the Tkinter event loop
root.mainloop()
