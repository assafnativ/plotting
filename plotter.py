from py_silhouette import SilhouetteDevice
import math

x_min = 10
y_min = 20
x_max = 190
y_max = 200

x_mid = (x_min + x_max) / 2
y_mid = (y_min + y_max) / 2

radius = 90


def make_circle_points(num_points, mid, r):
    step = (math.pi * 2) / num_points
    print(f"Step is: {step}")
    points = []
    for i in range(num_points):
        x = math.cos(step * i) * r + mid[0]
        y = math.sin(step * i) * r + mid[1]
        print(f"New point: {x}, {y}")
        points.append((x,y))
    return points


def setup_machine():
    d = SilhouetteDevice()
    d.set_tool_diameter(d.params.tool_diameters["Pen"])
    d.set_speed(d.params.tool_speed_max)
    d.set_force(1)
    return d

def draw():
    d = setup_machine()
    points = make_circle_points(197, (x_mid, y_mid), radius)
    d.move_to(points[0][0], points[0][1], False)
    point_index = 0
    for i in range(len(points)):
        point_index += 80
        point_index %= len(points)
        d.move_to(points[point_index][0], points[point_index][1], True)
        print(f"Moving to {point_index} ({points[point_index]})")
    d.move_home()
    d.flush()


draw()

