import numpy as np
from GUI import settings
from GUI.calculations import get_slope, does_circle_intersect, unnormalize_coords, unit_vector, angle_between
from GUI.setup import make_laser, make_spotlight

CUE_STICK = "cue-stick"
TARGET_BALL = "target-ball"
CUE_BALL = "cue-ball"
POOL_TABLE = "pool-table"
STICK_TIP = "stick-tip"

spotlight_radius = 40
x_cue, y_cue, cue_radius, target_radius, target_spot_radius, x_target, y_target = 0, 0, 0, 0, 0, 0, 0

settings.init()

def get_coordinate(m, b, coord, val):
    # return point of intersection of equation y = mx+b and coord, val. coord = x, val = 1 means x = 1
    # line can either be x = 0, x = 1, y = 0 or y = 1
    if coord == "x":
        return m*val + b
    else:
        if m != 0:
            return (val - b)/m
        else:
            return b

def get_intersection_point(m, b, case):
    if case == "bottom_right":
        y = get_coordinate(m, b, "x", 1)
        x = get_coordinate(m, b, "y", 1)
        print(case, y, x)
        if x > 1:
            return 1, y
        elif y > 1:
            return x, 1
        elif m == 0:
            return 1, y
        else:
            return x, 1
    elif case == "bottom_left":
        y = get_coordinate(m, b, "x", 0)
        x = get_coordinate(m, b, "y", 1)
        print(case, y, x)
        if x < 0:
            return 0, y
        elif y > 1:
            return x, 1
        elif m == 0:
            return 0, y
        else:
            return x, 1

    elif case == "top_right":
        y = get_coordinate(m, b, "x", 1)
        x = get_coordinate(m, b, "y", 0)
        print(case, y, x)
        if x > 1:
            return 1, y
        elif y < 0:
            return x, 0
        else:
            return x, 0

    elif case == "top_left":
        y = get_coordinate(m, b, "x", 0)
        x = get_coordinate(m, b, "y", 0)
        print(case, y, x)
        if x < 0:
            return 0, y
        elif y < 0:
            return x, 0
        else:
            return 0, x

def get_new_laser_coordinates(mid_x, mid_y, tip_x, tip_y):
    m, b = get_slope(mid_x, mid_y, tip_x, tip_y)
    # Set it to last m and b values, which are stored as global variable
    if m is None and b is None:
        m = settings.m
        b = settings.b
    else:
        settings.m = m
        settings.b = b
    print("m = ", m)
    print("b = ", b)
    #determine which way the stick is pointing
    if tip_x >= mid_x and tip_y >= mid_y:
        #pointing towards bottom right, m +ve
        print("case bottom right")
        #will point towards one of two walls, bottom or right
        case = "bottom_right"
        return get_intersection_point(m, b, case)


    elif tip_x <= mid_x and tip_y >= mid_y:
        #pointing towards bottom left, m-ve
        print("case bottom left")
        # will point towards one of two walls, bottom or left
        case = "bottom_left"
        return get_intersection_point(m, b, case)

    elif tip_x >= mid_x and tip_y <= mid_y:
        #pointing towards top right, m-ve
        print("case top right")
        # will point towards one of two walls, top or right
        case = "top_right"
        return get_intersection_point(m, b, case)

    elif tip_x <= mid_x and tip_y <= mid_y:
        #pointing towards top left, m+ve
        print("case top left")
        # will point towards one of two walls, top or left
        case = "top_left"
        return get_intersection_point(m, b, case)

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

def base_line(canvas, x1, y1, x2, y2):
    make_laser(canvas, x1, y1, x2, y2, "base-line")

#Need to make laser from target ball to wall.
def normal_line(canvas, w, h, x1, y1, x2, y2):
    print("Creating normal laser", settings.num_lasers, x1, y1, x2, y2)
    if settings.num_lasers <= 4:
        make_laser(canvas, w*x1, h*y1, w*x2, h*y2, "projection-line")
    else:
        canvas.coords("projection-line", w*x1, h*y1, w*x2, h*y2)

def find_slope_v(target_x, target_y, endL_x, endL_y, phi, L_magn):
    diff_x = endL_x - target_x
    diff_y = endL_y - target_y

    new_phi = np.arctan(diff_y/diff_x) - phi
    # print("test find_slope_v", new_phi, diff_x, diff_y, np.tan(new_phi))
    return np.tan(new_phi)


def oblique_line(l, d, canvas, w, h, theta, x_w, y_w, x_t, y_t, base_end_x, base_end_y, end_x, end_y):
    #(x_w, y_w) -> cue (x_t,y_t) -> target (base_end_x, base_end_y) -> end base line (end_x, end_y) -> End of target line
    #Need this line going from target ball to a wall, at an angle φ = θ − sin−1((p + 1) sin θ), where p = l/2r. Theta is in rads
    p = float(l/d)
    phi = theta - np.arcsin(np.clip((p + 1) * np.sin(theta), -1.0, 1.0))
    phi_deg = phi*180/np.pi
    print("test phi", phi, theta*180/np.pi, p, phi_deg)

    a = np.array((x_t, y_t))
    b = np.array((base_end_x, base_end_y))
    L_magn = np.linalg.norm(b - a)

    # The below calculates the slope of the new v vector, which is from the target ball to a wall depending on phi (angle between L and v vector)
    m_v = find_slope_v(x_t, y_t, base_end_x, base_end_y, phi, L_magn)
    m_L, b_L = get_slope(x_t, y_t, base_end_x, base_end_y)
    b_v = x_t*(m_L - m_v) + b_L
    m_u, b_u = get_slope(x_w, y_w, end_x, end_y)
    x_c = (b_v - b_u)/(m_u-m_v)
    y_c = (m_u*x_c) + b_u
    end_x3, end_y3 = get_new_laser_coordinates(x_c, y_c, x_t, y_t)

    print("Creating oblique laser", "cue = ", x_w, y_w, "target = ", x_t, y_t, "base end = ",base_end_x, base_end_y, "calc points = ", end_x3, end_y3, "end = ", end_x, end_y, "slope_v", m_v)

    #This block of shit doesn't really work
    # if phi_deg > 0:
    #     X_magn = abs(L_magn*np.cos(phi))
    #     Y_magn = abs(L_magn*np.sin(phi))
    # else:
    #     Y_magn = abs(L_magn*np.cos(phi))
    #     X_magn = abs(L_magn*np.sin(phi))

    #X_magn = sqrt((x2-x0)^2 + (y2-y0)^2), Y_magn = sqrt((x2-x1)^2 + (y2-y1)^2). 2 equations, 2 unknowns, need to solve for x2, y2
    #This is a mangled formula I got from wolfram alpha
    # if phi_deg < 0:
    #     c = (x1*(-np.power(X_magn, 2) + np.power(Y_magn, 2) + np.power(x1, 2) - np.power(x2, 2)))/(x1-x2)
    #     d = np.power((-np.power(X_magn, 2) + np.power(Y_magn, 2) + np.power(x1,2) - np.power(x2,2)),2)/(4*np.power(x1-x2,2))
    #     # # print("gyp", X_magn, Y_magn,c ,d, x0 , y0, L_magn)
    #     y3 = 0.5*(2*np.sqrt([abs((np.power(X_magn,2) - np.power(x1,2) + c - d))]) + 2*y1)
    #     # # x3 doesn't require index idk why
    #     x3 = np.sqrt(abs(np.power(Y_magn,2) - np.power(y3[0]-y2,2))) + x2
    # else:
    #     c = (x2*(-np.power(X_magn, 2) + np.power(Y_magn, 2) + np.power(x2, 2) - np.power(x1, 2)))/(x2-x1)
    #     d = np.power((-np.power(X_magn, 2) + np.power(Y_magn, 2) + np.power(x2,2) - np.power(x1,2)),2)/(4*np.power(x2-x1,2))
    #     y3 = 0.5*(2*np.sqrt([abs((np.power(X_magn,2) - np.power(x2,2) + c - d))]) + 2*y2)
    #     x3 = np.sqrt(abs(np.power(Y_magn,2) - np.power(y3[0]-y1,2))) + x1

    if settings.num_lasers <= 4:
        make_laser(canvas, w*x_t, h*y_t, w*end_x3, h*end_y3, "projection-line")
    else:
        canvas.coords("projection-line", w*x_t, h*y_t, w*end_x3, h*end_y3)

def projection_line(l, canvas, w, h, x_w, y_w, x_t, y_t, end_x, end_y, base_end_x, base_end_y):
    #All coords are from 0 to 1 and correspond to the following
    #(x_w, y_w) -> cue, (x_t, y_t) -> target ball, (end_x, end_y) -> end_x, end_y. (base_end_x, base_end_y) -> base_end_x, base_end_y
    d = cue_radius + target_radius
    theta_crit = np.arcsin(d/(l+d))
    u_vector = (end_x-x_w, end_y-y_w)
    L_vector = (base_end_x-x_w, base_end_y-y_w)
    # need to determine when theta should be negative
    theta_rad = angle_between(u_vector, L_vector)
    print("test theta1", theta_crit, theta_rad)

    # Convert the angles from radians to degrees
    theta_crit *= 180 / np.pi
    theta_deg = theta_rad*180/np.pi
    print("test theta2", theta_crit, theta_deg)

    p = float(l/d)
    phi = theta_rad - np.arcsin((p+1)*np.sin(theta_rad))
    print("test theta69", theta_rad*180/np.pi, p, phi*180/np.pi)

    # normal collision, just draw the base line
    if (theta_deg > -3) and (theta_deg < 3):
        normal_line(canvas, w, h, x_t, y_t, end_x, end_y)
    # elif theta_deg == theta_crit:
    #     tangential_line(canvas, w, h, theta_rad, )
    else:
        oblique_line(l, d, canvas, w, h, theta_rad, x_w, y_w, x_t, y_t, base_end_x, base_end_y, end_x, end_y)

def move_laser(window, w, h, canvas, mid_x, mid_y, tip_x, tip_y):
    global x_cue, y_cue, cue_radius, spotlight_radius, target_radius, x_target, y_target
    new_x, new_y = get_new_laser_coordinates(mid_x, mid_y, tip_x, tip_y)
    print(new_x, new_y)
    does_intersect_cue_ball, x1_cue_inter, y1_cue_inter, x2_cue_inter, y2_cue_inter = does_circle_intersect(mid_x, mid_y, tip_x, tip_y, cue_radius, x_cue, y_cue)

    if does_intersect_cue_ball:
        print("Cue intersected", new_x, new_y)
        end_x, end_y = new_x, new_y
        new_x = x1_cue_inter
        new_y = y1_cue_inter

    #Update the laser coming out of the cue stick
    canvas.coords("laser1", w*tip_x, h*tip_y, w*new_x, h*new_y)

    #If there's a cue intersection, need to also check if that same line is intersecting with a target ball
    if does_intersect_cue_ball:
        print("cucks",
              settings.num_lasers, target_radius, cue_radius)
        #Draw another laser coming out of the cue ball
        #must calculate the new x1 and y1 based on y = mx + b formula
        does_collide_target_ball, x1_tg_inter, y1_tg_inter, x2_tg_inter, y2_tg_inter = does_circle_intersect(x2_cue_inter, y2_cue_inter, end_x, end_y, 1.8*target_radius, x_target, y_target)
        is_cue_stick_alligned, x1_temp, y1_temp, x2_temp, y2_temp = does_circle_intersect(x2_cue_inter, y2_cue_inter, end_x, end_y, 0.25*cue_radius, x_cue, y_cue)
        print(is_cue_stick_alligned, does_collide_target_ball)

        #Regardless of intersection, need to draw that line from center of cue ball to end point
        if not does_collide_target_ball:
            x1 = w * (x2_cue_inter)
            y1 = h * (y2_cue_inter)
            x2 = w * end_x
            y2 = h * end_y
            canvas.itemconfigure("laser2", state='hidden')
            #delete both the base and projection line if they are existent
            if settings.num_lasers == 4:
                canvas.delete("base-line")
                settings.num_lasers = 3
            elif settings.num_lasers == 5:
                canvas.delete("base-line")
                canvas.delete("projection-line")
                settings.num_lasers = 3

            if settings.num_targ_spotlights != 0:
                canvas.delete("target_ball" + str(settings.num_targ_spotlights - 1))
                settings.num_targ_spotlights = 0
        else:
            #Need to swap x1 and y1 cuz of how does_circle_intersect compares the intersections. That's why its x2_tg and y2_tg
            x1 = w * (x2_cue_inter)
            y1 = h * (y2_cue_inter)
            x2 = w * x2_tg_inter
            y2 = h * y2_tg_inter
            canvas.coords("laser2", x_cue * w, y_cue * h, x2, y2)
            canvas.itemconfigure("laser2", state='normal')
            # might not even need this base line, but good to visualize
            if settings.num_lasers == 3:
                base_line(canvas, w*x_cue, h*y_cue, w*x_target, h*y_target)
            #Calculate theta to determine type of collision
            if settings.num_lasers >= 4:
                canvas.coords("base-line", w*x_cue, h*y_cue, w*x_target, h*y_target)
                if is_cue_stick_alligned:
                    #Find the end points of the base line. Used to determine the projection vector
                    base_end_x, base_end_y = get_new_laser_coordinates(x_cue, y_cue, x_target, y_target)
                    a = np.array((x_cue, y_cue))
                    b = np.array((x_target, y_target))
                    l_distance = abs(np.linalg.norm(a-b) - cue_radius - target_radius)
                    projection_line(l_distance, canvas, w, h, x_cue, y_cue, x_target, y_target, end_x, end_y, base_end_x, base_end_y)
                else:
                    if settings.num_lasers == 5:
                        canvas.delete("base-line")
                        canvas.delete("projection-line")
                        settings.num_lasers = 3
        #Create laser if there isn't one
        if settings.num_lasers == 2:
            make_laser(canvas, x1, y1, x2, y2, 0)
        #Otherwise just move the laser
        else:
            canvas.itemconfigure("laser3", state='normal')
            canvas.coords("laser3", x1, y1, x2, y2)

    elif not does_intersect_cue_ball:
        canvas.itemconfigure("laser2", state='hidden')
        if (settings.num_lasers != 1 or settings.num_lasers != 2):
            canvas.itemconfigure("laser3", state='hidden')

    window.update()


def send_data(label, x1, y1, w1, h1, stick_coords, window, canvas):
    x, y = unnormalize_coords(x1, y1)
    global x_cue, y_cue, cue_radius, spotlight_radius, target_radius, target_spot_radius, x_target, y_target

    print("GUIGUI", label)
    if label == CUE_BALL:
        print("CUE_BALL Detected")
        # for use with drawing the line in cases the line intersects the cue-ball
        # also resizing the all depending on how far away camera is

        x_cue = float(x / settings.w)
        y_cue = float(y / settings.h)
        cue_radius = float((float(h1 / 2) + float(w1 / 2)) /2)
        spotlight_radius = cue_radius * settings.h
        print(spotlight_radius,cue_radius)
        move_spotlight(window, canvas, x, y, spotlight_radius, "cue_ball")

    elif label == CUE_STICK or label == STICK_TIP:

        print("CUE_STICK OR STICK_TIP Detected")
        if -1 not in stick_coords:
            move_laser(window, settings.w, settings.h, canvas, stick_coords[0], stick_coords[1], stick_coords[2], stick_coords[3])

    if label == TARGET_BALL:
        print("TARGET_BALL Detected", stick_coords)
        target_radius = float((float(h1 / 2) + float(w1 / 2)) /2)
        target_spot_radius = target_radius * settings.h
        does_collide_target_ball = False
        does_intersect_cue_ball = False
        if -1 not in stick_coords:
            does_intersect_cue_ball, x1_tg_inter, y1_tg_inter, x2_tg_inter, y2_tg_inter = does_circle_intersect(stick_coords[0], stick_coords[1], stick_coords[2], stick_coords[3], cue_radius, x_cue, y_cue)
            does_collide_target_ball, x1_tg_inter, y1_tg_inter, x2_tg_inter, y2_tg_inter = does_circle_intersect(stick_coords[0], stick_coords[1], stick_coords[2], stick_coords[3], target_radius*1.8, x1, y1)
        print("gyper", settings.num_targ_spotlights,  does_collide_target_ball, does_intersect_cue_ball)
        if does_intersect_cue_ball and does_collide_target_ball:
            x_target, y_target = x1, y1
            #Determine if ball is already a spotlight
            if settings.num_targ_spotlights == 0:
                print("Test movement1", x_target, y_target, target_spot_radius)
                make_spotlight(canvas, x_target, y_target, target_spot_radius, False)
            else:
                print("Test movement2", x, y, target_spot_radius)
                move_spotlight(window, canvas, x, y, target_spot_radius, "target_ball" + str(settings.num_targ_spotlights - 1))
        else:
             # need to account for case where ball is being detected, but not intersecting and there is already a ball intersecting
            if settings.num_targ_spotlights == 0:
                print("deleting target ball and projection/base lasers", settings.num_targ_spotlights, x_target, y_target)
                canvas.delete("base-line")
                canvas.delete("projection-line")
                settings.num_lasers = 3
                canvas.delete("target_ball" + str(settings.num_targ_spotlights - 1))
                settings.num_targ_spotlights = 0