import tkinter as tk
import math

WIDTH, HEIGHT = 800, 600
CENTER_X, CENTER_Y = WIDTH // 2, HEIGHT // 2
CAMERA_DISTANCE = 600

angle_x = 0
angle_y = 0

# =================================
# ВРАЩЕНИЕ и ПРОЕКЦИЯ
# =================================

def rotate_point(x, y, z, ax, ay):
    cos_y = math.cos(ay)
    sin_y = math.sin(ay)
    xz = x * cos_y - z * sin_y
    zz = x * sin_y + z * cos_y

    cos_x = math.cos(ax)
    sin_x = math.sin(ax)
    yz = y * cos_x - zz * sin_x
    zz = y * sin_x + zz * cos_x

    return xz, yz, zz

def project_point(x, y, z):
    if CAMERA_DISTANCE + z == 0:
        z += 0.001  # во избежание деления на 0
    factor = CAMERA_DISTANCE / (CAMERA_DISTANCE + z)
    x_proj = x * factor + CENTER_X
    y_proj = -y * factor + CENTER_Y
    return x_proj, y_proj

# =================================
# РУЧНАЯ ЗАКРАСКА ПОЛИГОНА
# =================================

def fill_polygon(canvas, pts, color='#add8e6'):
    # Преобразуем к целым
    pts = [(int(round(x)), int(round(y))) for x, y in pts]
    ys = [p[1] for p in pts]
    y_min = max(min(ys), 0)
    y_max = min(max(ys), HEIGHT - 1)

    for y in range(y_min, y_max + 1):
        intersections = []
        for i in range(len(pts)):
            x1, y1 = pts[i]
            x2, y2 = pts[(i + 1) % len(pts)]
            if y1 == y2:
                continue  # горизонтальное ребро
            if (y >= min(y1, y2)) and (y <= max(y1, y2)):
                t = (y - y1) / (y2 - y1)
                x_int = x1 + t * (x2 - x1)
                intersections.append(x_int)

        intersections.sort()
        for i in range(0, len(intersections) - 1, 2):
            x_start = int(intersections[i])
            x_end = int(intersections[i + 1])
            for x in range(x_start, x_end + 1):
                canvas.create_line(x, y, x + 1, y, fill=color, tags="surface")  # рисуем пиксели

# =================================
# ПОВЕРХНОСТЬ
# =================================

def helix_surface(u, v):
    r = 50 + 10 * math.sin(3 * v)
    x = r * math.cos(u)
    y = r * math.sin(u)
    z = 30 * v
    return x, y, z

def draw_surface(canvas, ax, ay):
    canvas.delete("surface")
    u_steps, v_steps = 60, 30
    u_min, u_max = 0, 2 * math.pi
    v_min, v_max = 0, 2 * math.pi

    u_range = [u_min + i * (u_max - u_min) / u_steps for i in range(u_steps + 1)]
    v_range = [v_min + j * (v_max - v_min) / v_steps for j in range(v_steps + 1)]

    points = [[rotate_point(*helix_surface(u, v), ax, ay) for v in v_range] for u in u_range]

    for i in range(u_steps):
        for j in range(v_steps):
            p1 = project_point(*points[i][j])
            p2 = project_point(*points[i + 1][j])
            p3 = project_point(*points[i + 1][j + 1])
            p4 = project_point(*points[i][j + 1])

            fill_polygon(canvas, [p1, p2, p3, p4])

# =================================
# ОСИ
# =================================

def draw_axes(canvas, ax, ay):
    canvas.delete("axes")
    origin = (0, 0, 0)
    x_axis = rotate_point(150, 0, 0, ax, ay)
    y_axis = rotate_point(0, 150, 0, ax, ay)
    z_axis = rotate_point(0, 0, 150, ax, ay)

    x0, y0 = project_point(*origin)

    for end, color in zip([x_axis, y_axis, z_axis], ['red', 'green', 'blue']):
        x1, y1 = project_point(*end)
        canvas.create_line(x0, y0, x1, y1, fill=color, width=2, tags="axes")

# =================================
# ВЗАИМОДЕЙСТВИЕ
# =================================

def redraw(canvas):
    canvas.delete("all")
    draw_axes(canvas, angle_x, angle_y)
    draw_surface(canvas, angle_x, angle_y)

def on_mouse_drag(event):
    global angle_x, angle_y, last_mouse_pos
    dx = event.x - last_mouse_pos[0]
    dy = event.y - last_mouse_pos[1]
    angle_y += dx * 0.01
    angle_x += dy * 0.01
    last_mouse_pos = (event.x, event.y)
    redraw(event.widget)

def on_mouse_down(event):
    global last_mouse_pos
    last_mouse_pos = (event.x, event.y)

# =================================
# ЗАПУСК
# =================================

def main():
    global canvas
    root = tk.Tk()
    root.title("Винтовая поверхность и 3D-оси")

    canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg='white')
    canvas.pack()

    canvas.bind("<Button-1>", on_mouse_down)
    canvas.bind("<B1-Motion>", on_mouse_drag)

    redraw(canvas)
    root.mainloop()

if __name__ == '__main__':
    main()
