import pygame
from collections import deque


# Рисует разные фигуры на поверхности
def draw_shape(surface, tool, start, end, color, size):
    x1, y1 = start
    x2, y2 = end

    # Рисуем прямоугольник
    if tool == "rect":
        rect = pygame.Rect(
            min(x1, x2),
            min(y1, y2),
            abs(x2 - x1),
            abs(y2 - y1)
        )
        pygame.draw.rect(surface, color, rect, size)

    # Рисуем круг от начальной точки
    elif tool == "circle":
        radius = int(((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5)
        pygame.draw.circle(surface, color, start, radius, size)

    # Рисуем квадрат с равными сторонами
    elif tool == "square":
        side = min(abs(x2 - x1), abs(y2 - y1))

        if x2 < x1:
            side = -side

        rect = pygame.Rect(x1, y1, side, abs(side))
        pygame.draw.rect(surface, color, rect, size)

    # Рисуем прямоугольный треугольник
    elif tool == "right_triangle":
        points = [
            (x1, y1),
            (x1, y2),
            (x2, y2)
        ]
        pygame.draw.polygon(surface, color, points, size)

    # Рисуем равносторонний похожий треугольник
    elif tool == "eq_triangle":
        points = [
            ((x1 + x2) // 2, y1),
            (x1, y2),
            (x2, y2)
        ]
        pygame.draw.polygon(surface, color, points, size)

    # Рисуем ромб
    elif tool == "rhombus":
        cx = (x1 + x2) // 2
        cy = (y1 + y2) // 2

        points = [
            (cx, y1),
            (x2, cy),
            (cx, y2),
            (x1, cy)
        ]
        pygame.draw.polygon(surface, color, points, size)


# Инструмент заливки через get_at и set_at
def flood_fill(surface, start, fill_color):
    width, height = surface.get_size()
    x, y = start

    # Проверяем, что точка внутри поверхности
    if not (0 <= x < width and 0 <= y < height):
        return

    # Берём цвет пикселя, куда нажали
    target_color = surface.get_at((x, y))
    new_color = pygame.Color(fill_color)

    # Если цвет уже такой же, ничего не делаем
    if target_color == new_color:
        return

    # Очередь нужна для проверки соседних пикселей
    queue = deque()
    queue.append((x, y))

    while queue:
        px, py = queue.popleft()

        # Пропускаем пиксели вне поверхности
        if not (0 <= px < width and 0 <= py < height):
            continue

        # Пропускаем пиксели другого цвета
        if surface.get_at((px, py)) != target_color:
            continue

        # Меняем цвет текущего пикселя
        surface.set_at((px, py), new_color)

        # Добавляем соседние пиксели
        queue.append((px + 1, py))
        queue.append((px - 1, py))
        queue.append((px, py + 1))
        queue.append((px, py - 1))