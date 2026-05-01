import pygame
import sys
from datetime import datetime
from tools import draw_shape, flood_fill


# Запускаем pygame
pygame.init()

# ---------------- НАСТРОЙКИ ----------------
WIDTH = 1000
HEIGHT = 700
TOOLBAR_HEIGHT = 90

# Создаём главное окно
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TSIS2 Paint Application")

# Область рисования начинается ниже панели инструментов
CANVAS_RECT = pygame.Rect(0, TOOLBAR_HEIGHT, WIDTH, HEIGHT - TOOLBAR_HEIGHT)

# Создаём canvas, где будет рисунок
canvas = pygame.Surface((WIDTH, HEIGHT - TOOLBAR_HEIGHT))
canvas.fill((255, 255, 255))

clock = pygame.time.Clock()

# ---------------- ЦВЕТА ----------------
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (210, 210, 210)
LIGHT_BLUE = (180, 210, 255)

# Доступные цвета
colors = [
    BLACK,
    (255, 0, 0),
    (0, 180, 0),
    (0, 0, 255),
    (255, 255, 0),
    (255, 120, 0),
    (160, 0, 200),
    WHITE
]

# ---------------- ШРИФТЫ ----------------
font = pygame.font.SysFont("Arial", 20)
small_font = pygame.font.SysFont("Arial", 16)
text_font = pygame.font.SysFont("Arial", 28)

# ---------------- СОСТОЯНИЕ ПРОГРАММЫ ----------------
current_color = BLACK
brush_size = 5
current_tool = "pencil"

drawing = False
start_pos = None
last_pos = None

text_mode = False
text_pos = None
text_input = ""

tool_buttons = {}
color_buttons = []


# Переводим координаты экрана в координаты canvas
def canvas_pos(pos):
    return pos[0], pos[1] - TOOLBAR_HEIGHT


# Проверяем, находится ли мышь внутри canvas
def inside_canvas(pos):
    return CANVAS_RECT.collidepoint(pos)


# Рисуем кнопку инструмента
def draw_button(rect, label, active=False):
    button_color = LIGHT_BLUE if active else GRAY

    pygame.draw.rect(screen, button_color, rect)
    pygame.draw.rect(screen, BLACK, rect, 2)

    text = small_font.render(label, True, BLACK)
    text_rect = text.get_rect(center=rect.center)
    screen.blit(text, text_rect)


# Рисуем верхнюю панель с инструментами и цветами
def draw_toolbar():
    global tool_buttons, color_buttons

    tool_buttons = {}
    color_buttons = []

    pygame.draw.rect(screen, (235, 235, 235), (0, 0, WIDTH, TOOLBAR_HEIGHT))
    pygame.draw.line(screen, BLACK, (0, TOOLBAR_HEIGHT), (WIDTH, TOOLBAR_HEIGHT), 2)

    # Список инструментов
    tools = [
        ("pencil", "Pencil"),
        ("line", "Line"),
        ("rect", "Rect"),
        ("circle", "Circle"),
        ("square", "Square"),
        ("right_triangle", "R-Tri"),
        ("eq_triangle", "Eq-Tri"),
        ("rhombus", "Rhombus"),
        ("eraser", "Eraser"),
        ("fill", "Fill"),
        ("text", "Text"),
    ]

    x = 10
    y = 10
    button_width = 78
    button_height = 30

    # Создаём кнопки инструментов
    for tool_name, label in tools:
        rect = pygame.Rect(x, y, button_width, button_height)
        draw_button(rect, label, current_tool == tool_name)
        tool_buttons[tool_name] = rect
        x += button_width + 6

    x = 10
    y = 52

    # Создаём кнопки цветов
    for color in colors:
        rect = pygame.Rect(x, y, 30, 30)
        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, BLACK, rect, 2)

        # Показываем выбранный цвет
        if color == current_color:
            pygame.draw.rect(screen, (0, 0, 0), rect, 4)

        color_buttons.append((rect, color))
        x += 38

    # Показываем текущий размер кисти и подсказки
    size_text = font.render(
        f"Brush: {brush_size}px | 1=small 2=medium 3=large | Ctrl+S=Save",
        True,
        BLACK
    )
    screen.blit(size_text, (350, 55))


# Сохраняем canvas как PNG-файл
def save_canvas():
    filename = datetime.now().strftime("paint_%Y%m%d_%H%M%S.png")
    pygame.image.save(canvas, filename)
    print(f"Saved as {filename}")


# Показываем текст во время ввода
def draw_text_preview():
    if text_mode and text_pos is not None:
        preview = text_font.render(text_input + "|", True, current_color)
        screen.blit(preview, (text_pos[0], text_pos[1] + TOOLBAR_HEIGHT))


# Обработка кликов по панели инструментов
def handle_toolbar_click(pos):
    global current_tool, current_color
    global text_mode, text_input, text_pos

    # Проверяем нажатие на инструмент
    for tool_name, rect in tool_buttons.items():
        if rect.collidepoint(pos):
            current_tool = tool_name
            text_mode = False
            text_input = ""
            text_pos = None
            return True

    # Проверяем нажатие на цвет
    for rect, color in color_buttons:
        if rect.collidepoint(pos):
            current_color = color
            return True

    return False


# ---------------- ГЛАВНЫЙ ЦИКЛ ----------------
running = True

while running:
    screen.fill(WHITE)
    screen.blit(canvas, (0, TOOLBAR_HEIGHT))
    draw_toolbar()

    # Предпросмотр линии и фигур во время перетаскивания мыши
    if drawing and start_pos is not None:
        mouse_pos = pygame.mouse.get_pos()

        if inside_canvas(mouse_pos):
            end_pos = canvas_pos(mouse_pos)

            preview_surface = screen.copy()

            # Предпросмотр прямой линии
            if current_tool == "line":
                pygame.draw.line(
                    preview_surface,
                    current_color,
                    (start_pos[0], start_pos[1] + TOOLBAR_HEIGHT),
                    mouse_pos,
                    brush_size
                )

            # Предпросмотр фигур
            elif current_tool in [
                "rect",
                "circle",
                "square",
                "right_triangle",
                "eq_triangle",
                "rhombus"
            ]:
                shape_preview = pygame.Surface(canvas.get_size(), pygame.SRCALPHA)
                draw_shape(
                    shape_preview,
                    current_tool,
                    start_pos,
                    end_pos,
                    current_color,
                    brush_size
                )
                preview_surface.blit(shape_preview, (0, TOOLBAR_HEIGHT))

            screen.blit(preview_surface, (0, 0))

    draw_text_preview()

    # Обрабатываем события pygame
    for event in pygame.event.get():
        # Закрытие окна
        if event.type == pygame.QUIT:
            running = False

        # Обработка клавиатуры
        elif event.type == pygame.KEYDOWN:
            keys = pygame.key.get_pressed()

            # Сохранение через Ctrl + S
            if event.key == pygame.K_s and (keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]):
                save_canvas()

            # Размеры кисти
            elif event.key == pygame.K_1:
                brush_size = 2

            elif event.key == pygame.K_2:
                brush_size = 5

            elif event.key == pygame.K_3:
                brush_size = 10

            # Ввод текста
            if text_mode:
                if event.key == pygame.K_RETURN:
                    final_text = text_font.render(text_input, True, current_color)
                    canvas.blit(final_text, text_pos)

                    text_mode = False
                    text_pos = None
                    text_input = ""

                elif event.key == pygame.K_ESCAPE:
                    text_mode = False
                    text_pos = None
                    text_input = ""

                elif event.key == pygame.K_BACKSPACE:
                    text_input = text_input[:-1]

                else:
                    text_input += event.unicode

        # Нажатие кнопки мыши
        elif event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()

            # Если клик был по панели, меняем инструмент или цвет
            if handle_toolbar_click(pos):
                continue

            # Если клик был внутри canvas
            if inside_canvas(pos):
                cpos = canvas_pos(pos)

                # Заливка области
                if current_tool == "fill":
                    flood_fill(canvas, cpos, current_color)

                # Начинаем ввод текста
                elif current_tool == "text":
                    text_mode = True
                    text_pos = cpos
                    text_input = ""

                # Начинаем рисование
                else:
                    drawing = True
                    start_pos = cpos
                    last_pos = cpos

        # Движение мыши
        elif event.type == pygame.MOUSEMOTION:
            pos = pygame.mouse.get_pos()

            if drawing and inside_canvas(pos):
                cpos = canvas_pos(pos)

                # Свободное рисование карандашом
                if current_tool == "pencil":
                    pygame.draw.line(canvas, current_color, last_pos, cpos, brush_size)
                    last_pos = cpos

                # Ластик рисует белым цветом
                elif current_tool == "eraser":
                    pygame.draw.line(canvas, WHITE, last_pos, cpos, brush_size)
                    last_pos = cpos

        # Отпускание кнопки мыши
        elif event.type == pygame.MOUSEBUTTONUP:
            pos = pygame.mouse.get_pos()

            if drawing and inside_canvas(pos):
                end_pos = canvas_pos(pos)

                # Финально рисуем линию
                if current_tool == "line":
                    pygame.draw.line(canvas, current_color, start_pos, end_pos, brush_size)

                # Финально рисуем выбранную фигуру
                elif current_tool in [
                    "rect",
                    "circle",
                    "square",
                    "right_triangle",
                    "eq_triangle",
                    "rhombus"
                ]:
                    draw_shape(
                        canvas,
                        current_tool,
                        start_pos,
                        end_pos,
                        current_color,
                        brush_size
                    )

            drawing = False
            start_pos = None
            last_pos = None

    # Обновляем экран
    pygame.display.flip()

    # Ограничиваем FPS
    clock.tick(60)


# Завершаем pygame
pygame.quit()
sys.exit()