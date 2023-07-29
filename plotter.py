from py_silhouette import SilhouetteDevice
import pygame
from pygame.locals import QUIT, MOUSEBUTTONDOWN, MOUSEMOTION, VIDEORESIZE, MOUSEBUTTONUP, KEYDOWN
import math
from point2d import Point2D

x_min = 10
y_min = 20
x_max = 190
y_max = 200

radius = (x_max - (2 * x_min)) // 2

WHITE = (0,0,0)
PEN_COLOR = (255,255,255)
WIDTH = x_min + x_max
HEIGHT = y_min + y_max

def setup_machine():
    dev = SilhouetteDevice()
    dev.set_tool_diameter(dev.params.tool_diameters["Pen"])
    dev.set_speed(dev.params.tool_speed_max)
    dev.set_force(1)
    return dev

def setup_pygame():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("Plotter")
    screen.fill(PEN_COLOR)
    return screen

class plotter:
    def __init__(self, dev_type):
        self.dev_type = dev_type
        if 'pygame' == dev_type:
            self.dev = setup_pygame()
            self.move_to = self.pygame_move_to
            self.flush = self.pygame_flush
            self.x_min = 0
            self.y_min = 0
            self.x_max = 190
            self.y_max = 200
        elif 'silhouette' == dev_type:
            self.dev = setup_machine()
            self.move_to = self.silhouette_move_to
            self.flush = self.silhouette_flush
            self.x_min = 0
            self.y_min = 0
            self.x_max = 480
            self.y_max = 640
        else:
            raise Exception(f"Unknown dev type {dev_type}")
        self.pos = Point2D(0,0)
        self.home_pos = self.pos
        self.points = []

    def get_dim(self):
        return Point2D(self.x_max, self.y_max)

    def silhouette_move_to(self, target, pen_on):
        self.dev.move_to(target.x, target.y, pen_on)
        self.pos = target

    def pygame_move_to(self, target, pen_on):
        if pen_on:
            pygame.draw.line(self.dev, WHITE, self.pos.cartesian(), target.cartesian())
        self.pos = target
        self.points.append((self.pos, pen_on))

    def silhouette_flush(self):
        self.dev.flush()
    def pygame_flush(self):
        pygame.display.flip()
        running = True
        zoom_level = 1.0
        zoom_change = 0.2
        dragging = False
        last_drag_pos = Point2D(0,0)
        display_offset = Point2D(0,0)
        width = WIDTH
        height = HEIGHT

        while running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                elif event.type == MOUSEBUTTONDOWN:
                    if event.button == 4:
                        zoom_level += zoom_change
                    elif event.button == 5:
                        zoom_level -= zoom_change
                        if zoom_level < zoom_change:
                            zoom_level = zoom_change
                    elif event.button == 1:
                        dragging = True
                        last_drag_pos = Point2D(event.pos[0], event.pos[1])
                elif event.type == MOUSEMOTION:
                    if dragging:
                        current_point = Point2D(event.pos[0], event.pos[1])
                        delta = current_point - last_drag_pos
                        display_offset += delta
                        #print(f"Delta: {display_offset.cartesian()} changed by {delta.cartesian()} ({last_drag_pos.cartesian()} - {current_point.cartesian()})")
                        last_drag_pos = current_point
                elif event.type == MOUSEBUTTONUP:
                    if event.button == 1:
                        dragging = False
                elif event.type == KEYDOWN:
                    if event.key == pygame.K_s and event.mod & pygame.KMOD_CTRL:
                        pygame.image.save(self.dev, "screenshot.png")
                        print("Screenshot saved to screenshot.png")
                elif event.type == VIDEORESIZE:
                    width, height = event.w, event.h
                    self.dev = pygame.display.set_mode((width, height), pygame.RESIZABLE)

            self.dev.fill(WHITE)

            temp_surface = pygame.Surface((width, height))
            temp_surface.fill(WHITE)

            pos = self.home_pos
            for target, pen_on in self.points:
                if pen_on:
                    start = (pos + display_offset) * zoom_level
                    end   = (target + display_offset) * zoom_level
                    thikness = int(max(1.0, (zoom_level//1.8)))
                    pygame.draw.line(temp_surface, PEN_COLOR, start.cartesian(),end.cartesian(), width=thikness)
                pos = target
            self.dev.blit(pygame.transform.scale(temp_surface, (width, height)), (0,0))

            pygame.display.flip()
        pygame.quit()

    def move_home(self):
        if 'silhouette' == self.dev_type:
            self.dev.move_home()
        self.pos = Point2D(0,0)

def make_circle_points(num_points, mid, r):
    step = (math.pi * 2) / num_points
    #print(f"Step is: {step}")
    points = []
    for i in range(num_points):
        x = math.cos(step * i) * r + mid[0]
        y = math.sin(step * i) * r + mid[1]
        #print(f"New point: {x}, {y}")
        points.append(Point2D(x,y))
    return points

def draw_symmetric_strings(dev_type="pygame"):
    dev = plotter(dev_type)
    dim = dev.get_dim()
    x_mid = dim.x // 2
    y_mid = dim.y // 2
    radius = min(x_mid, y_mid) - 40
    points = make_circle_points(197, (x_mid, y_mid), radius)
    dev.move_to(points[0], False)
    point_index = 0
    for i in range(len(points)):
        point_index += 80
        point_index %= len(points)
        dev.move_to(points[point_index], True)
        #print(f"Moving to {point_index} ({points[point_index]})")
    dev.move_home()
    dev.flush()

def draw_with_strings(dev_type='pygame'):
    dev = plotter(dev_type)
    dim = dev.get_dim()
    x_mid = dim.x // 2
    y_mid = dim.y // 2
    radius = min(x_mid, y_mid) - 40
    points = make_circle_points(197, (x_mid, y_mid), radius)
    dev.move_to(points[0], False)


draw_symmetric_strings(dev_type='pygame')


