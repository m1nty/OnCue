import math
import tkinter as tk
import random
import numpy as np
from numpy import ones, vstack
from numpy.linalg import lstsq

spotlight_rad = 40
spotlight_radius = 40
x_cue, y_cue, cue_radius, num_lasers, target_radius, target_spot_radius, x_target, y_target = 0, 0, 0, 0, 0, 0, 0, 0

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

# Create Spotlight Animation Canvas
def laser_animation(window):
    canvas = tk.Canvas(window)
    canvas.configure(bg="#ffffff")
    canvas.pack(fill="both", expand=True)
    return canvas


# Make Spotlight on Canvas
def make_spotlight(canvas, w, h, cue):
    if cue == 1:
        spotlight = canvas.create_oval(
            w / 5 - spotlight_rad,
            h / 2 - spotlight_rad,
            w / 5 + spotlight_rad,
            h / 2 + spotlight_rad,
            outline="white",
            width=3,
            tags="cue_ball",
        )
    else:
        spotlight = canvas.create_oval(
            3.5*w / 5 - spotlight_rad,
            h / 2 - spotlight_rad,
            3.5*w / 5 + spotlight_rad,
            h / 2 + spotlight_rad,
            outline="red",
            width=3,
            tags="target_ball",
        )

    return spotlight


def make_laser(canvas, w1, h1, w2, h2, id):
    global num_lasers
    if id == "base-line" or id == "projection-line":
        print("print2",id, num_lasers)
        tag = id
    else:
        tag = "laser" + str((num_lasers + 1))

    if num_lasers == 0 or num_lasers == 1:
        temp_rad = spotlight_rad
        if num_lasers == 0:
            color = "yellow"
        elif num_lasers == 1:
            temp_rad = 0
            color = "white"

        laser = canvas.create_line(
            w/5 + temp_rad,
            h/2,
            3.5*w/5 - spotlight_rad,
            h/2,
            fill=color,
            tags=tag,
            width=1
            #dash=(5, 4)
        )
        num_lasers += 1
        return laser
    else:
        if num_lasers == 2:
            color = "yellow"
        else:
            if id == "projection-line":
                color = "pink"
            else:
                color = "black"
        print("making new laser", num_lasers, w1, h1, w2, h2, color)
        laser = canvas.create_line(
            w1,
            h1,
            w2,
            h2,
            fill=color,
            tags=tag,
            width=1
            #dash=(5, 4)
        )
        num_lasers += 1
        return laser

def get_slope(mid_x, mid_y, tip_x, tip_y):
    #m will be positive for +ve delta_x & +ve delta_y or -ve delta_x & -ve delta_y
    #m will be negative for only one of delta_x or delta_y being -ve
    delta_y = tip_y-mid_y
    delta_x = tip_x-mid_x
    if delta_x != 0:
        m = delta_y/delta_x
        b = mid_y - m*mid_x #y = mx + b
        return m,b
    else:
        return None, None

def get_wall(slope, ratio,case_num):
    #top wall = 1, left wall = 2, right wall = 3, bottom wall = 4
    #bottom right
    if case_num == 1:
        if ratio > slope:
            return 4
        else:
            return 3
    #bottom left
    elif case_num == 2:
        if ratio > slope:
            return 2
        else:
            return 4
    #top right
    elif case_num == 3:
        if ratio < slope:
            return 3
        else:
            return 1
    #top left
    elif case_num == 4:
        if ratio > slope:
            return 1
        else:
            return 2

def get_new_laser_coordinates(mid_x, mid_y, tip_x, tip_y):
    wall = 0
    m, b = get_slope(mid_x, mid_y, tip_x, tip_y)
    print("m= ", m)
    print("b= ", b)
    #Because of the coordinate system, we really need to solve like this: x = ym + b
    #determine which way the stick is pointing
    if tip_x >= mid_x and tip_y >= mid_y:
        #pointing towards bottom right, m +ve
        print("case 1")
        #will point towards one of two walls, bottom or right
        case = 1
        ratio = (1-tip_x)/(1-tip_y)
        wall = get_wall(m, ratio, case)
        if wall == 4:
            print("bottom wall")
            return (1-b)/m, 1
        elif wall == 3:
            print("right wall")
            return 1, m+b

    elif tip_x <= mid_x and tip_y >= mid_y:
        #pointnig towards bottom left, m-ve
        print("case 2")
        # will point towards one of two walls, bottom or left
        case = 2
        ratio = -(tip_x)/(1-tip_y)
        wall = get_wall(m, ratio, case)
        if wall == 2:
            print("left wall")
            return 0, b
        elif wall == 4:
            print("bottom wall")
            if m == 0:
                return b, 1
            return (1-b)/m, 1

    elif tip_x >= mid_x and tip_y <= mid_y:
        #pointing towards top right, m-ve
        print("case 3")
        # will point towards one of two walls, top or right
        case = 3
        ratio = -(1-tip_x)/(tip_y)
        wall = get_wall(m, ratio, case)
        if wall == 1:
            print("top wall")
            return -b/m, 0
        elif wall == 3:
            print("right wall")
            return 1, m+b

    elif tip_x <= mid_x and tip_y <= mid_y:
        #pointing towards top left, m+ve
        print("case 4")
        # will point towards one of two walls, top or left
        case = 4
        ratio = tip_x/tip_y
        wall = get_wall(m, ratio, case)
        if wall == 1:
            print("top wall")
            if m == 0:
                return -b, 0
            return -b/m, 0
        elif wall == 2:
            print("left wall")
            return 0, b
    print("somethings fucked",tip_x, mid_x, tip_y, mid_y, wall)

# Move Spotlight to Track Cue Ball
def move_spotlight(window, canvas, x, y, radius, id):
    print("jews",id)
    canvas.coords(
        id,
        x - radius,
        y - radius,
        x + radius,
        y + radius,
    )
    print("cucklord",
          radius)
    window.update()

def circle_intersection(mid_x, mid_y, tip_x, tip_y, r, x_cir, y_cir):
    x_first_int, x_second_int, y_first_int, y_second_int, intersection = 0, 0, 0, 0, 0
    tangent_tol = 1e-9
    mid, tip, cue = (mid_x, mid_y), (tip_x, tip_y), (x_cir, y_cir)

    (p1x, p1y), (p2x, p2y), (cx, cy) = mid, tip, cue
    (x1, y1), (x2, y2) = (p1x - cx, p1y - cy), (p2x - cx, p2y - cy)
    dx, dy = (x2 - x1), (y2 - y1)
    dr = (dx ** 2 + dy ** 2)**.5
    big_d = x1 * y2 - x2 * y1
    discriminant = r ** 2 * dr ** 2 - big_d ** 2

    if discriminant >= 0:  # There may be 0, 1, or 2 intersections with the segment
        intersections = [
            (cx + (big_d * dy + sign * (-1 if dy < 0 else 1) * dx * discriminant ** .5) / dr ** 2,
             cy + (-big_d * dx + sign * abs(dy) * discriminant ** .5) / dr ** 2)
            for sign in ((1, -1) if dy < 0 else (-1, 1))]  # This makes sure the order along the segment is correct
        if len(intersections) == 2 and abs(discriminant) <= tangent_tol:  # If line is tangent to circle, return just one point (as both intersections have same location)
            x_first_int = intersections[0][0]
            y_first_int = intersections[0][1]
            x_second_int, y_second_int = x_first_int, y_first_int
            intersections = 1
        else:
            if abs(tip_x - intersections[0][0]) < abs(tip_x - intersections[1][0]):
                x_first_int = intersections[0][0]
                y_first_int = intersections[0][1]
                x_second_int = intersections[1][0]
                y_second_int = intersections[1][1]
            else:
                x_first_int = intersections[1][0]
                y_first_int = intersections[1][1]
                x_second_int = intersections[0][0]
                y_second_int = intersections[0][1]
            intersection = 1
    else:
        intersection = 0

    return intersection, x_first_int, y_first_int, x_second_int, y_second_int

def base_line(canvas, x1, y1, x2, y2):
    make_laser(canvas, x1, y1, x2, y2, "base-line")

#Need to make laser from target ball to wall.
def normal_line(canvas, w, h, x1, y1, x2, y2):
    global num_lasers
    print("Creating normal laser", num_lasers, x1, y1, x2, y2)
    if num_lasers <= 4:
        make_laser(canvas, w*x1, h*y1, w*x2, h*y2, "projection-line")
    else:
        canvas.coords("projection-line", w*x1, h*y1, w*x2, h*y2)

def projection_line(l, canvas, w, h, x1, y1, x2, y2):
    d = cue_radius + target_radius
    print(l, d, d/(l+d))
    theta = np.arcsin(d/(l+d))
    print(theta)
    theta *= 180/np.pi
    print("test theta", theta)
    #normal collision, just draw the base line
    if (theta > -30) and (theta < 30):
        normal_line(canvas, w, h, x1, y1, x2, y2)

def move_laser(window, w, h, canvas, mid_x, mid_y, tip_x, tip_y):
    global x_cue, y_cue, cue_radius, num_lasers, spotlight_radius, target_radius, x_target, y_target
    new_x, new_y = get_new_laser_coordinates(mid_x, mid_y, tip_x, tip_y)
    cue_intersection, x1_cue_inter, y1_cue_inter, x2_cue_inter, y2_cue_inter = circle_intersection(mid_x, mid_y, tip_x, tip_y, cue_radius, x_cue, y_cue)

    if cue_intersection == 1:
        print("Cue intersected", new_x, new_y)
        end_x, end_y = new_x, new_y
        new_x = x1_cue_inter
        new_y = y1_cue_inter

    #Update the laser coming out of the cue stick
    canvas.coords("laser1", w*tip_x, h*tip_y, w*new_x, h*new_y)

    #If there's a cue intersection, need to also check if that same line is intersecting with a target ball
    if cue_intersection == 1:
        print("cucks",
              num_lasers)
        #Draw another laser coming out of the cue ball
        #must calculate the new x1 and y1 based on y = mx + b formula
        tg_intersection, x1_tg_inter, y1_tg_inter, x2_tg_inter, y2_tg_inter = circle_intersection(x2_cue_inter, y2_cue_inter, end_x, end_y, target_radius, x_target, y_target)

        #Regardless of intersection, need to draw that line from center of cue ball to end point
        if tg_intersection == 0:
            x1 = w * (x2_cue_inter)
            y1 = h * (y2_cue_inter)
            x2 = w * end_x
            y2 = h * end_y
            canvas.itemconfigure("laser2", state='hidden')
            #delete both the base and projection line if they are existent
            if num_lasers == 5:
                canvas.delete("base-line")
                canvas.delete("projection-line")
                num_lasers = 3
        else:
            #Need to swap x1 and y1 cuz of how circle_intersection compares the intersections. That's why its x2_tg and y2_tg
            canvas.itemconfigure("target_ball", state='normal')
            x1 = w * (x2_cue_inter)
            y1 = h * (y2_cue_inter)
            x2 = w * x2_tg_inter
            y2 = h * y2_tg_inter
            canvas.coords("laser2", x_cue * w, y_cue * h, x2, y2)
            canvas.itemconfigure("laser2", state='normal')
            # might not even need this base line, but good to visualize
            if num_lasers == 3:
                base_line(canvas, w*x_cue, h*y_cue, w*x_target, h*y_target)
            #Calculate theta to determine type of collision
            if num_lasers >= 4:
                canvas.coords("base-line", w*x_cue, h*y_cue, w*x_target, h*y_target)
                a = np.array((x_cue,y_cue))
                b = np.array((x_target,y_target))
                l_distance = np.linalg.norm(a-b) - cue_radius - target_radius
                projection_line(l_distance, canvas, w, h, x2_tg_inter, y2_tg_inter, end_x, end_y)

        #Create laser if there isn't one
        if num_lasers == 2:
            make_laser(canvas, x1, y1, x2, y2, 0)
        #Otherwise just move the laser
        else:
            canvas.itemconfigure("laser3", state='normal')
            canvas.coords("laser3", x1, y1, x2, y2)

    elif cue_intersection == 0:
        canvas.itemconfigure("laser2", state='hidden')
        if (num_lasers != 1 or num_lasers != 2):
            canvas.itemconfigure("laser3", state='hidden')

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
    print("main")
    generate_data()
    window = create_animation_window()
    global w, h
    w, h = window.winfo_screenwidth(), window.winfo_screenheight()
    canvas = spotlight_animation(window)
    #1 creates the cue-ball, 0 makes it a target-ball
    make_spotlight(canvas, w, h, 1)
    make_spotlight(canvas, w, h ,0)
    make_laser(canvas, w, h, 0, 0, 0)
    scan_data(window, canvas)


def setup_gui():
    window = create_animation_window()
    global w, h
    w, h = window.winfo_screenwidth(), window.winfo_screenheight()
    canvas = spotlight_animation(window)
    make_spotlight(canvas, w, h, 1)
    make_spotlight(canvas, w, h ,0)
    #Make 2 lasers, one from tip of ball to end of table, second from center of cue ball to end of tip of first
    make_laser(canvas, w, h, 0, 0, 0)
    make_laser(canvas, w, h, 0, 0, 0)
    return window, canvas


CUE_STICK = "cue-stick"
TARGET_BALL = "target-ball"
CUE_BALL = "cue-ball"
POOL_TABLE = 3
STICK_TIP = "stick-tip"


def unnormalize_coords(x1, y1):
    x = float(x1 * w)
    y = float(y1 * h)
    return x, y


def send_data(label, x1, y1, w1, h1, stick_coords, window, canvas):
    x, y = unnormalize_coords(x1, y1)
    global x_cue, y_cue, cue_radius, spotlight_radius, target_radius, target_spot_radius, x_target, y_target

    print("GUIGUI", label)
    if label == CUE_BALL:
        print("CUE_BALL Detected")
        # for use with drawing the line in cases the line intersects the cue-ball
        # also resizing the all depending on how far away camera is

        x_cue = float(x / w)
        y_cue = float(y / h)
        cue_radius = float((float(h1 / 2) + float(w1 / 2)) /2)
        spotlight_radius = cue_radius * h
        print(spotlight_radius,cue_radius)
        move_spotlight(window, canvas, x, y, spotlight_radius, "cue_ball")

    elif label == CUE_STICK or label == STICK_TIP:

        print("CUE_STICK OR STICK_TIP Detected")
        if -1 not in stick_coords:
            print("giggity")
            print(stick_coords,
                  x_cue,
                  y_cue,
                  spotlight_radius)
            move_laser(window, w, h, canvas, stick_coords[0], stick_coords[1], stick_coords[2], stick_coords[3])

    elif label == TARGET_BALL:
        print("TARGET_BALL Detected")
        target_radius = float((float(h1 / 2) + float(w1 / 2)) /2)
        target_spot_radius = target_radius * h
        x_target, y_target = float(x/w), float(y/h)
        print(spotlight_radius, cue_radius)
        move_spotlight(window, canvas, x, y, target_spot_radius, "target_ball")

