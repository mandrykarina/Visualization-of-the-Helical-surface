import tkinter as tk
import math

# Параметры окна
WIDTH, HEIGHT = 800, 600
CENTER_X, CENTER_Y = WIDTH // 2, HEIGHT // 2
CAMERA_DISTANCE = 600

angle_x = 0
angle_y = 0

# === Алгоритм Брезенхэма ===
def bresenham_line(canvas, x0, y0, x1, y1, color, tag):
    x0, y0 = int(round(x0)), int(round(y0))
    x1, y1 = int(round(x1)), int(round(y1))

    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy

    while True:
        canvas.create_line(x0, y0, x0 + 1, y0, fill=color, tags=tag)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy

# === Вращение (матрицы) ===
def rotate_point(x, y, z, ax, ay):
    cos_y = math.cos(ay)
    sin_y = math.sin(ay)
    x1 = x * cos_y + z * sin_y
    y1 = y
    z1 = -x * sin_y + z * cos_y

    cos_x = math.cos(ax)
    sin_x = math.sin(ax)
    x2 = x1
    y2 = y1 * cos_x - z1 * sin_x
    z2 = y1 * sin_x + z1 * cos_x

    return x2, y2, z2

# === Проекция 3D -> 2D ===
def project_point(x, y, z):
    factor = CAMERA_DISTANCE / (CAMERA_DISTANCE + z)
    x_proj = x * factor + CENTER_X
    y_proj = -y * factor + CENTER_Y
    return x_proj, y_proj

# === Построение осей ===
def draw_axes(canvas, ax, ay):
    canvas.delete("axes")
    origin = (0, 0, 0)
    x_axis = rotate_point(150, 0, 0, ax, ay)
    y_axis = rotate_point(0, 150, 0, ax, ay)
    z_axis = rotate_point(0, 0, 150, ax, ay)

    x0, y0 = project_point(*origin)
    for end, color in zip([x_axis, y_axis, z_axis], ['red', 'green', 'blue']):
        x1, y1 = project_point(*end)
        bresenham_line(canvas, x0, y0, x1, y1, color=color, tag="axes")

# === Параметрическая поверхность ===
def helix_surface(u, v):
    r = 50 + 10 * math.sin(3 * v)
    x = r * math.cos(u)
    y = r * math.sin(u)
    z = 30 * v
    return x, y, z

# === Закраска полигона (сканлайн) ===
def fill_polygon_scanline(canvas, points, color="#add8e6"):
    pts = [(int(p[0]), int(p[1])) for p in points]
    ys = [p[1] for p in pts]
    y_min, y_max = max(min(ys), 0), min(max(ys), HEIGHT - 1)

    for y in range(y_min, y_max + 1):
        intersections = []
        for i in range(4):
            (x1, y1), (x2, y2) = pts[i], pts[(i + 1) % 4]
            if y1 == y2:
                continue
            if (y1 <= y <= y2) or (y2 <= y <= y1):
                t = (y - y1) / (y2 - y1)
                x_int = x1 + t * (x2 - x1)
                intersections.append(x_int)
        intersections.sort()
        for i in range(0, len(intersections), 2):
            if i + 1 < len(intersections):
                x_start = int(intersections[i])
                x_end = int(intersections[i + 1])
                canvas.create_line(x_start, y, x_end, y, fill=color, tags="surface")

# === Построение поверхности ===
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
            p1 = points[i][j]
            p2 = points[i + 1][j]
            p3 = points[i + 1][j + 1]
            p4 = points[i][j + 1]

            p1_2d = project_point(*p1)
            p2_2d = project_point(*p2)
            p3_2d = project_point(*p3)
            p4_2d = project_point(*p4)

            fill_polygon_scanline(canvas, [p1_2d, p2_2d, p3_2d, p4_2d])

# === Обновление сцены ===
def redraw(canvas):
    canvas.delete("all")
    draw_axes(canvas, angle_x, angle_y)
    draw_surface(canvas, angle_x, angle_y)

# === Обработка мыши ===
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

# === Запуск приложения ===
def main():
    global canvas
    root = tk.Tk()
    root.title("Ручная 3D-визуализация винтовой поверхности")

    canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg='white')
    canvas.pack()

    canvas.bind("<Button-1>", on_mouse_down)
    canvas.bind("<B1-Motion>", on_mouse_drag)

    redraw(canvas)
    root.mainloop()

if __name__ == '__main__':
    main()
