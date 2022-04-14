import numpy as np
from GUI import settings
import math

def unnormalize_coords(x1, y1):
    x = float(x1 * settings.w)
    y = float(y1 * settings.h)
    return x, y


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

def unit_vector(vector):
    """ Returns the unit vector of the vector.  """
    return vector / np.linalg.norm(vector)

def angle_between(v1, v2):
    """ Returns the angle in radians between vectors 'v1' and 'v2'::

            >>> angle_between((1, 0, 0), (0, 1, 0))
            1.5707963267948966
            >>> angle_between((1, 0, 0), (1, 0, 0))
            0.0
            >>> angle_between((1, 0, 0), (-1, 0, 0))
            3.141592653589793
    """
    v1_u = unit_vector(v1)
    v2_u = unit_vector(v2)
    # print("test angle between", v1_u, v2_u, v1, v2)
    # print("test dot product", np.cross(v1_u, v2_u), np.cross(v2_u, v1_u))
    # print("test angle", np.arcsin(np.clip(np.cross(v1_u, v2_u), -1.0, 1.0)), np.arcsin(np.clip(np.cross(v2_u, v1_u), -1.0, 1.0)))
    return np.arcsin(np.clip(np.cross(v1_u, v2_u), -1.0, 1.0))


def does_circle_intersect(mid_x, mid_y, tip_x, tip_y, r, x_cir, y_cir):
    x_first_int, x_second_int, y_first_int, y_second_int = 0, 0, 0, 0
    does_intersect = False
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
            does_intersect = True

    return does_intersect, x_first_int, y_first_int, x_second_int, y_second_int

# https://stackoverflow.com/questions/1073336/circle-line-segment-collision-detection-algorithm#:~:text=Then%20calculate%20the%20intersection%20point,voila%2C%20we%20have%20an%20intersection!
def distanceSegmentToPoint(x1, y1, x2, y2, xc, yc):
    # Compute vectors AC and AB
    AC = (xc-x1, yc-y1)
    AB = (x2-x1, y2-y1)

    # Get point D by taking the projection of AC onto AB then adding the offset of A
    dot1 = AC[0]*AB[0]+AC[1]*AB[1]
    dot2 = AB[0]*AB[0]+AB[1]*AB[1]
    temp = dot1/dot2
    D = (temp*AB[0] + x1, temp*AB[1] + y1)

    AD = (D[0] - x1, D[1] - y1)
    # D might not be on AB so calculate k of D down AB (aka solve AD = k * AB)
    # We can use either component, but choose larger value to reduce the chance of dividing by zero
    if abs(AB[0]) > abs(AB[1]):
        k = AD[0]/AB[0]
    else:
        k = AD[1]/AB[1]

    # Check if D is off either end of the line segment
    if (k <= 0):
        temp1 = (xc - x1, yc - y1)
        dot = temp1[0] * temp1[0] + temp1[1] * temp1[1]
        return np.sqrt(dot)
    elif (k >= 1):
        temp1 = (xc - x2, yc - y2)
        dot = temp1[0] * temp1[0] + temp1[1] * temp1[1]
        return np.sqrt(dot)

    temp1 = (xc - D[0], yc - D[1])
    dot = temp1[0] * temp1[0] + temp1[1] * temp1[1]
    return np.sqrt(dot)

def v1_does_circle_intersect(x1, y1, r, slope, y_int, tip_x):
    a = -2 * x1
    b = -2 * y1
    c = (r * r) - (x1 * x1) - (y1 * y1)
    #the x we want to draw to
    x_first_int = 0
    x_second_int = 0

    #equation of a circle is given by:
    # x^2 - (2*x1*x) + y^2 - (2*y1*y) = r^2-x1^2-y1^2
    # x^2 + ax + y^2 + by = c

    #eq'n for line is given as y=slope*x + y_int, so sub this in for y above
    #x^2 + ax + (slope*x + y_int)^2 + b(slope*x + y_int) = c
    #x^2 + ax + (slope^2*x^2 + 2*slope*x*y_int + y_int^2) + b*slope*x + b*y_int = c

    #rearranging yields:
    #x^2*(1 + slope^2) + x*(a + 2*slope*y_int + b*slope) - c + y_int^2 + b*y_int = 0
    #now we have A, B, C values for quadratic equation
    A = 1 + (slope*slope)
    B = a + (2*slope*y_int) + (b*slope)
    C = -c + (y_int*y_int) + b*y_int

    #calculate discriminant now, don't need to worry about complex case:
    discriminant = (B*B) - (4*A*C)
    sqrt_val = math.sqrt(abs(discriminant))
    coeff = [A,B,C]
    print(coeff)
    x1_sol, x2_sol = np.roots(coeff)


    if discriminant > 0:
        print(" real and different roots ")
        print(x1_sol)
        print(x2_sol)
        if abs(tip_x - x1_sol) < abs(tip_x - x2_sol):
            x_first_int = x1_sol
            x_second_int = x2_sol
        else:
            x_first_int = x2_sol
            x_second_int = x1_sol
        intersection = 1

    elif discriminant == 0:
        print(" real and same roots")
        print(x1_sol)
        x_first_int = -B / (2 * A)
        x_second_int = x_first_int
        intersection = 1

    else:
        print("Complex Roots, does not intersect")
        print(x1_sol)
        print(x2_sol)
        intersection = 0

    return x_first_int, x_second_int, intersection

def v1_get_new_laser_coordinates(mid_x, mid_y, tip_x, tip_y):
    wall = 0
    m, b = get_slope(mid_x, mid_y, tip_x, tip_y)
    # Set it to last m and b values, which are stored as global variable
    if m is None and b is None:
        m = settings.m
        b = settings.b
    else:
        settings.m = m
        settings.b = b
    print("m= ", m)
    print("b= ", b)
    #Because of the coordinate system, we really need to solve like this: x = ym + b
    #determine which way the stick is pointing
    if tip_x >= mid_x and tip_y >= mid_y:
        #pointing towards bottom right, m +ve
        print("case bottom right")
        #will point towards one of two walls, bottom or right
        case = 1
        ratio = (1-tip_x)/(1-tip_y)
        wall = v1_get_wall(m, ratio, case)
        if wall == 4:
            print("bottom wall")
            return (1-b)/m, 1
        elif wall == 3:
            print("right wall")
            return 1, m+b

    elif tip_x <= mid_x and tip_y >= mid_y:
        #pointing towards bottom left, m-ve
        print("case bottom left")
        # will point towards one of two walls, bottom or left
        case = 2
        ratio = -(tip_x)/(1-tip_y)
        wall = v1_get_wall(m, ratio, case)
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
        print("case top right")
        # will point towards one of two walls, top or right
        case = 3
        ratio = -(1-tip_x)/(tip_y)
        wall = v1_get_wall(m, ratio, case)
        if wall == 1:
            print("top wall")
            return -b/m, 0
        elif wall == 3:
            print("right wall")
            return 1, m+b

    elif tip_x <= mid_x and tip_y <= mid_y:
        #pointing towards top left, m+ve
        print("case top left")
        # will point towards one of two walls, top or left
        case = 4
        ratio = tip_x/tip_y
        wall = v1_get_wall(m, ratio, case)
        if wall == 1:
            print("top wall")
            if m == 0:
                return -b, 0
            return -b/m, 0
        elif wall == 2:
            print("left wall")
            return 0, b
    print("somethings fucked",tip_x, mid_x, tip_y, mid_y, wall)

def v1_get_wall(slope, ratio, case_num):
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