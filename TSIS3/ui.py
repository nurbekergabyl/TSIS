import pygame

# Инициализация шрифтов
pygame.font.init()

# Определяем шрифты для разных целей
FONT = pygame.font.SysFont("Arial", 26)
BIG_FONT = pygame.font.SysFont("Arial", 48)
SMALL_FONT = pygame.font.SysFont("Arial", 20)

# Цветовая палитра
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (190, 190, 190)
DARK_GRAY = (80, 80, 80)
BLUE = (50, 130, 230)
GREEN = (40, 180, 80)
RED = (220, 60, 60)
YELLOW = (230, 210, 50)

class Button:
    def __init__(self, text, rect, color=BLUE):
        self.text = text
        self.rect = pygame.Rect(rect)
        self.color = color

    def draw(self, screen):
        # Эффект наведения: если мышка над кнопкой, она становится светлее
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            color = (
                min(self.color[0] + 30, 255),
                min(self.color[1] + 30, 255),
                min(self.color[2] + 30, 255)
            )
        else:
            color = self.color

        # Рисуем саму кнопку и рамку
        pygame.draw.rect(screen, color, self.rect, border_radius=10)
        pygame.draw.rect(screen, BLACK, self.rect, 2, border_radius=10)

        # Рисуем текст по центру кнопки
        text_surface = FONT.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def is_clicked(self, event):
        # Проверка нажатия левой кнопкой мыши (button 1) по кнопке
        return (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(event.pos)
        )

def draw_text(screen, text, x, y, color=BLACK, font=FONT, center=False):
    """Универсальная функция для отрисовки текста"""
    surface = font.render(str(text), True, color)
    if center:
        rect = surface.get_rect(center=(x, y))
        screen.blit(surface, rect)
    else:
        screen.blit(surface, (x, y))

def draw_title(screen, text, width):
    """Рисует заголовок в верхней части экрана"""
    draw_text(screen, text, width // 2, 80, BLACK, BIG_FONT, center=True)

def get_text_input(screen, clock, width, height):
    """Экран ввода имени игрока"""
    name = ""
    while True:
        screen.fill((235, 235, 235))

        draw_text(screen, "Enter your name", width // 2, 180, BLACK, BIG_FONT, center=True)
        draw_text(screen, name + "|", width // 2, 280, BLACK, FONT, center=True)
        draw_text(screen, "Press ENTER to start", width // 2, 340, DARK_GRAY, SMALL_FONT, center=True)
        draw_text(screen, "Press ESC to go back", width // 2, 380, DARK_GRAY, SMALL_FONT, center=True)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if name.strip():
                        return name.strip()
                    return "Player"
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                elif event.key == pygame.K_ESCAPE:
                    return None
                else:
                    # Ограничение по длине имени и только печатные символы
                    if len(name) < 12 and event.unicode.isprintable():
                        name += event.unicode

        pygame.display.flip()
        clock.tick(60)