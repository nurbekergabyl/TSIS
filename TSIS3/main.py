import pygame
import os
import random
# Төмендегі импорттар сенің файлдарыңның атына сәйкес болуы керек
from ui import Button, draw_text, draw_title, get_text_input, BIG_FONT, FONT
from ui import BLACK, BLUE, GREEN, RED
from persistence import load_settings, save_settings, load_leaderboard
from racer import RacerGame, WIDTH, HEIGHT

# --- Инициализация миксера (Звуковая система) ---
pygame.init()
pygame.mixer.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TSIS3 Racer Game")
clock = pygame.time.Clock()

def leaderboard_screen():
    """Экран таблицы лидеров"""
    back_button = Button("Back", (200, 690, 200, 50), RED)
    while True:
        screen.fill((240, 240, 240))
        draw_title(screen, "Leaderboard Top 10", WIDTH)
        scores = load_leaderboard()
        
        y = 160
        if not scores:
            draw_text(screen, "No scores yet", WIDTH // 2, 250, BLACK, FONT, center=True)
        else:
            for i, item in enumerate(scores[:10], start=1):
                draw_text(screen, f"{i}. {item['name']} - {item['score']}", WIDTH // 2, y, BLACK, FONT, center=True)
                y += 45

        back_button.draw(screen)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "quit"
            if back_button.is_clicked(event): return "menu"
        
        pygame.display.flip()
        clock.tick(60)

def settings_screen(settings):
    """Экран настроек звука и цвета"""
    sound_button = Button("", (180, 190, 240, 50), BLUE)
    back_button = Button("Back", (200, 500, 200, 55), RED)

    while True:
        screen.fill((235, 235, 235))
        draw_title(screen, "Settings", WIDTH)

        # Текст кнопки зависит от настроек
        sound_button.text = f"Sound: {'ON' if settings['sound'] else 'OFF'}"
        sound_button.draw(screen)
        back_button.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "quit"
            
            if sound_button.is_clicked(event):
                settings["sound"] = not settings["sound"]
                save_settings(settings)
                # Включаем или выключаем музыку сразу
                if settings["sound"]:
                    try:
                        pygame.mixer.music.play(-1)
                    except: pass
                else:
                    pygame.mixer.music.stop()

            if back_button.is_clicked(event):
                return "menu"

        pygame.display.flip()
        clock.tick(60)

def main_menu(settings):
    """Главное меню"""
    buttons = {
        "play": Button("Play", (200, 220, 200, 55), GREEN),
        "leaderboard": Button("Leaderboard", (200, 295, 200, 55), BLUE),
        "settings": Button("Settings", (200, 370, 200, 55), BLUE),
        "quit": Button("Quit", (200, 445, 200, 55), RED),
    }

    while True:
        screen.fill((230, 230, 230))
        draw_title(screen, "TSIS3 Racer", WIDTH)

        for button in buttons.values():
            button.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "quit"
            for name, button in buttons.items():
                if button.is_clicked(event):
                    return name

        pygame.display.flip()
        clock.tick(60)

def main():
    settings = load_settings()

    # Попытка загрузить музыку при старте
    try:
        path = os.path.join("assets", "background.wav")
        if os.path.exists(path):
            pygame.mixer.music.load(path)
            if settings.get("sound", True):
                pygame.mixer.music.play(-1)
    except Exception as e:
        print(f"Ошибка звука: {e}")

    while True:
        action = main_menu(settings)
        
        if action == "quit":
            break
        elif action == "play":
            # Запрашиваем имя игрока
            name = get_text_input(screen, clock, WIDTH, HEIGHT)
            if name:
                game = RacerGame(screen, clock, settings, name)
                status, score, dist, coins = game.run()
                if status == "quit": break
        elif action == "leaderboard":
            if leaderboard_screen() == "quit": break
        elif action == "settings":
            if settings_screen(settings) == "quit": break

    pygame.quit()

if __name__ == "__main__":
    main()