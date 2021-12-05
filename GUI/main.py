import tkinter as tk
import time
import random

spotlight_radius = 40


# Main Window
def create_animation_window():
    window = tk.Tk()
    window.attributes('-fullscreen', True)
    window.bind("<Key>", lambda e: window.destroy())
    window.title("On-Cue")
    return window


# Create Spotlight Animation Canvas
def spotlight_animation(window):
    canvas = tk.Canvas(window)
    canvas.configure(bg="#36594a")
    canvas.pack(fill="both", expand=True)
    return canvas


# Make Spotlight on Canvas
def make_spotlight(window, canvas):
    spotlight = canvas.create_oval(
        w / 5 - spotlight_radius,
        h / 2 - spotlight_radius,
        w / 5 + spotlight_radius,
        h / 2 + spotlight_radius,
        outline="white",
        tags="spotlight",
    )
    return spotlight


# Move Spotlight to Track Cue Ball
def move_spotlight(window, canvas, x, y):
    canvas.coords(
        "spotlight",
        x - spotlight_radius,
        y - spotlight_radius,
        x + spotlight_radius,
        y + spotlight_radius,
    )
    window.update()


def unnormalize_data(data):
    coordinate = data.split()
    x = float(coordinate[1]) * w
    y = float(coordinate[2]) * h
    return x, y


def scan_data(window, canvas):
    coordinates = open("data.txt", "r").readlines()

    for data in coordinates:
        x, y = unnormalize_data(data)
        move_spotlight(window, canvas, x, y)


def generate_data():
    file = open("data.txt", "a")
    inc_x = 0
    inc_y = 0

    for x in range(250):
        file.write("6 ")
        file.write(str(inc_x))
        file.write(" ")
        file.write(str(inc_y))
        file.write(" 0.035948 0.035948")
        file.write("\n")

        inc_x += random.uniform(0.001, 0.003)
        inc_y += random.uniform(0.001, 0.003)

    for x in range(180):
        file.write("6 ")
        file.write(str(inc_x))
        file.write(" ")
        file.write(str(inc_y))
        file.write(" 0.035948 0.035948")
        file.write("\n")

        inc_x += random.uniform(0.001, 0.001)
        inc_y -= random.uniform(0.001, 0.003)

    for x in range(200):
        file.write("6 ")
        file.write(str(inc_x))
        file.write(" ")
        file.write(str(inc_y))
        file.write(" 0.035948 0.035948")
        file.write("\n")

        inc_x += random.uniform(0.001, 0.001)
        inc_y += random.uniform(0.001, 0.003)

    file.close()


def main():
    generate_data()
    window = create_animation_window()
    global w, h
    w, h = window.winfo_screenwidth(), window.winfo_screenheight()
    spotlight_canvas = spotlight_animation(window)
    make_spotlight(window, spotlight_canvas)
    scan_data(window, spotlight_canvas)
    open('data.txt', 'w').close()

main()

CUE_STICK = 0
TARGET_BALL = 1
CUE_BALL = 2
POOL_TABLE = 3
STICK_TIP = 4


def unnormalize_coords(x1, y1):
    x = float(x1 * w)
    y = float(y1 * h)
    return x, y

def send_data(label, x1, y1, w1, h1, window, canvas):
    x, y = unnormalize_coords(x1, y1)

    if label == CUE_STICK:
        print("CUE_STICK Detected")
    elif label == TARGET_BALL:
        print("TARGET_BALL Detected")
    elif label == CUE_BALL:
        print("CUE_BALL Detected")
        move_spotlight(window, canvas, x, y)

    elif label == POOL_TABLE:
        print("POOL_TABLE Detected")
    elif label == CUE_STICK:
        print("CUE_STICK Detected")
    elif label == STICK_TIP:
        print("STICK_TIP Detected")
