import tkinter as tk

from GUI import settings

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
    canvas = tk.Canvas(window, highlightthickness=0)
    # canvas.configure(bg="#36594a")
    canvas.configure(bg="black")
    canvas.pack(fill="both", expand=True)
    # Creates those rectangles on startup
    return canvas


# Create Spotlight Animation Canvas
def laser_animation(window):
    canvas = tk.Canvas(window)
    canvas.configure(bg="#ffffff")
    canvas.pack(fill="both", expand=True)
    return canvas


# Make Spotlight on Canvas. Takes in x1, y1 norm'd between 0 and 1. radius is not.
def make_spotlight(canvas, x1, y1, target_radius, cue):
    if cue:
        spotlight = canvas.create_oval(
            settings.w / 5 - spotlight_radius,
            settings.h / 2 - spotlight_radius,
            settings.w / 5 + spotlight_radius,
            settings.h / 2 + spotlight_radius,
            outline="white",
            width=4,
            tags="cue_ball",
        )
    else:
        id = "target_ball" + str(settings.num_targ_spotlights)
        print("making spotlight, ", id)
        spotlight = canvas.create_oval(
            x1*settings.w - target_radius,
            y1*settings.w - target_radius,
            x1*settings.w + target_radius,
            y1*settings.w + target_radius,
            outline="#FF69B4",
            width=4,
            tags=id,
        )
        settings.num_targ_spotlights += 1
    return spotlight


# Make Pocket on Canvas
def make_pocket(canvas, x, y, scale, ):
    pocket = canvas.create_oval(
        x - scale * spotlight_radius,
        y - scale * spotlight_radius,
        x + scale * spotlight_radius,
        y + scale * spotlight_radius,
        fill="white",
        outline="white",
        width=3,
        tags="pocket",
    )
    return pocket


# Make Laser on Canvas
def make_laser(canvas, w1, h1, w2, h2, id):
    if id == "base-line" or id == "projection-line":
        tag = id
    else:
        print("making laser:", settings.num_lasers)
        tag = "laser" + str((settings.num_lasers + 1))

    if settings.num_lasers == 0 or settings.num_lasers == 1:
        temp_rad = spotlight_radius
        if settings.num_lasers == 0:
            #cue stick yellow line
            color = "yellow"
        elif settings.num_lasers == 1:
            temp_rad = 0
            #not centered white line
            color = "white"

        laser = canvas.create_line(
            settings.w/5 + temp_rad,
            settings.h/2,
            3.5*settings.w/5 - spotlight_radius,
            settings.h/2,
            fill=color,
            tags=tag,
            width=3
            #dash=(5, 4)
        )
        settings.num_lasers += 1
        return laser
    else:
        if settings.num_lasers == 2:
            color = "yellow"
        else:
            if id == "projection-line":
                color = "#CC0000"
            else:
                color = "black"
        print("making new laser", settings.num_lasers, w1, h1, w2, h2, color)
        laser = canvas.create_line(
            w1,
            h1,
            w2,
            h2,
            fill=color,
            tags=tag,
            width=3
            #dash=(5, 4)
        )
        settings.num_lasers += 1
        return laser


# Move Spotlight to Track Cue Ball
def move_spotlight(window, canvas, x, y, radius, id):
    canvas.coords(
        id,
        x - radius,
        y - radius,
        x + radius,
        y + radius,
    )
    window.update()


# Instantiate GUI
def setup_gui():
    window = create_animation_window()
    # settings.w, settings.h = window.winfo_screenwidth(), window.winfo_screenheight()
    settings.w, settings.h = 1920*0.8*7/8, 1080*(4/5)*(9/8)
    canvas = spotlight_animation(window)
    make_pocket(canvas, 0, 0, 2.1)
    make_pocket(canvas, settings.w/2, 0, 1.7)
    make_pocket(canvas, settings.w, 0, 2.1)
    make_pocket(canvas, 0, settings.h, 2.1)
    make_pocket(canvas, settings.w/2, settings.h, 1.7)
    make_pocket(canvas, settings.w, settings.h, 2.1)
    make_spotlight(canvas, 0, 0, 0, True)
    #Make 2 lasers, one from tip of ball to end of table, second from center of cue ball to end of tip of first
    make_laser(canvas, settings.w, settings.h, 0, 0, 0)
    make_laser(canvas, settings.w, settings.h, 0, 0, 1)
    canvas.create_rectangle(0, settings.h, 1920, 1080, outline="black", fill="black")
    canvas.create_rectangle(settings.w, 0, 1920, 1080, outline="black", fill="black")
    return window, canvas
