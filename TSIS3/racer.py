import os
import random
import pygame

from persistence import add_score
from ui import draw_text, WHITE, BLACK, YELLOW


WIDTH = 600
HEIGHT = 800

ROAD_LEFT = 90
ROAD_RIGHT = 510
ROAD_WIDTH = ROAD_RIGHT - ROAD_LEFT

LANE_COUNT = 4
LANE_WIDTH = ROAD_WIDTH // LANE_COUNT

FINISH_DISTANCE = 3000
ASSET_DIR = "assets"


CAR_COLORS = {
    "blue": (40, 110, 230),
    "red": (220, 50, 50),
    "green": (40, 180, 80),
    "yellow": (230, 210, 40)
}


DIFFICULTY_CONFIG = {
    "easy": {
        "enemy_speed": 4,
        "spawn_delay": 75,
        "obstacle_delay": 130
    },
    "normal": {
        "enemy_speed": 5,
        "spawn_delay": 55,
        "obstacle_delay": 100
    },
    "hard": {
        "enemy_speed": 7,
        "spawn_delay": 38,
        "obstacle_delay": 75
    }
}


def load_image(name, size=None):
    path = os.path.join(ASSET_DIR, name)

    try:
        image = pygame.image.load(path).convert_alpha()
        if size is not None:
            image = pygame.transform.scale(image, size)
        return image
    except pygame.error:
        return None
    except FileNotFoundError:
        return None


def load_sound(name):
    path = os.path.join(ASSET_DIR, name)

    try:
        return pygame.mixer.Sound(path)
    except pygame.error:
        return None
    except FileNotFoundError:
        return None


class Player:
    def __init__(self, color):
        self.w = 48
        self.h = 80
        self.x = WIDTH // 2 - self.w // 2
        self.y = HEIGHT - 130
        self.speed = 7
        self.color = color
        self.image = load_image("Player.png", (self.w, self.h))
        self.rect = pygame.Rect(self.x, self.y, self.w, self.h)

    def update(self, keys, nitro_active=False):
        move_speed = self.speed + 4 if nitro_active else self.speed

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x -= move_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x += move_speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.y -= move_speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.y += move_speed

        self.x = max(ROAD_LEFT + 5, min(self.x, ROAD_RIGHT - self.w - 5))
        self.y = max(100, min(self.y, HEIGHT - self.h - 20))

        self.rect.topleft = (self.x, self.y)

    def draw(self, screen):
        if self.image:
            screen.blit(self.image, self.rect)
        else:
            pygame.draw.rect(screen, self.color, self.rect, border_radius=10)
            pygame.draw.rect(screen, BLACK, self.rect, 2, border_radius=10)
            pygame.draw.rect(screen, WHITE, (self.x + 10, self.y + 10, self.w - 20, 18), border_radius=4)


class EnemyCar:
    def __init__(self, lane, speed):
        self.w = 48
        self.h = 80
        self.x = ROAD_LEFT + lane * LANE_WIDTH + LANE_WIDTH // 2 - self.w // 2
        self.y = -self.h
        self.speed = speed
        self.image = load_image("Enemy.png", (self.w, self.h))
        self.rect = pygame.Rect(self.x, self.y, self.w, self.h)
        self.color = random.choice([(160, 30, 30), (30, 30, 160), (40, 150, 80), (180, 100, 20)])

    def update(self, scroll_speed):
        self.y += self.speed + scroll_speed
        self.rect.topleft = (self.x, self.y)

    def draw(self, screen):
        if self.image:
            screen.blit(self.image, self.rect)
        else:
            pygame.draw.rect(screen, self.color, self.rect, border_radius=8)
            pygame.draw.rect(screen, BLACK, self.rect, 2, border_radius=8)


class Coin:
    def __init__(self, lane):
        self.value = random.choice([1, 1, 1, 2, 2, 5])
        self.size = 35
        self.x = ROAD_LEFT + lane * LANE_WIDTH + LANE_WIDTH // 2
        self.y = -30
        self.speed = 5
        self.image = load_image("coin.png", (self.size, self.size))
        self.rect = pygame.Rect(self.x - self.size // 2, self.y - self.size // 2, self.size, self.size)

    def update(self, scroll_speed):
        self.y += self.speed + scroll_speed
        self.rect.center = (self.x, self.y)

    def draw(self, screen):
        if self.image:
            screen.blit(self.image, self.rect)
        else:
            pygame.draw.circle(screen, YELLOW, (self.x, int(self.y)), 15)
            pygame.draw.circle(screen, BLACK, (self.x, int(self.y)), 15, 2)

        draw_text(screen, self.value, self.rect.centerx - 6, self.rect.centery - 12, BLACK)


class Obstacle:
    def __init__(self, lane, kind):
        self.kind = kind
        self.x = ROAD_LEFT + lane * LANE_WIDTH + 12
        self.y = -45
        self.w = LANE_WIDTH - 24
        self.h = 38
        self.speed = 4
        self.rect = pygame.Rect(self.x, self.y, self.w, self.h)

    def update(self, scroll_speed):
        self.y += self.speed + scroll_speed
        self.rect.y = int(self.y)

    def draw(self, screen):
        if self.kind == "barrier":
            color = (220, 80, 30)
            label = "!"
        elif self.kind == "oil":
            color = (20, 20, 20)
            label = "~"
        else:
            color = (90, 60, 40)
            label = "O"

        pygame.draw.rect(screen, color, self.rect, border_radius=8)
        pygame.draw.rect(screen, BLACK, self.rect, 2, border_radius=8)
        draw_text(screen, label, self.rect.centerx - 5, self.rect.centery - 12, WHITE)


class PowerUp:
    def __init__(self, lane):
        self.kind = random.choice(["nitro", "shield", "repair"])
        self.x = ROAD_LEFT + lane * LANE_WIDTH + LANE_WIDTH // 2
        self.y = -30
        self.radius = 18
        self.speed = 5
        self.life = 360
        self.rect = pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)

    def update(self, scroll_speed):
        self.y += self.speed + scroll_speed
        self.life -= 1
        self.rect.center = (self.x, self.y)

    def draw(self, screen):
        colors = {
            "nitro": (0, 200, 255),
            "shield": (100, 100, 255),
            "repair": (50, 220, 90)
        }

        letters = {
            "nitro": "N",
            "shield": "S",
            "repair": "R"
        }

        pygame.draw.circle(screen, colors[self.kind], (self.x, int(self.y)), self.radius)
        pygame.draw.circle(screen, BLACK, (self.x, int(self.y)), self.radius, 2)
        draw_text(screen, letters[self.kind], self.x - 8, int(self.y) - 13, BLACK)


class RoadEvent:
    def __init__(self):
        self.kind = random.choice(["moving_barrier", "speed_bump", "nitro_strip"])
        self.y = -40
        self.speed = 4

        if self.kind == "moving_barrier":
            self.w = 100
            self.h = 35
            self.x = ROAD_LEFT + 10
            self.direction = 1
        else:
            self.w = ROAD_WIDTH - 40
            self.h = 25
            self.x = ROAD_LEFT + 20
            self.direction = 0

        self.rect = pygame.Rect(self.x, self.y, self.w, self.h)

    def update(self, scroll_speed):
        self.y += self.speed + scroll_speed

        if self.kind == "moving_barrier":
            self.x += self.direction * 3
            if self.x < ROAD_LEFT + 10 or self.x + self.w > ROAD_RIGHT - 10:
                self.direction *= -1

        self.rect.topleft = (int(self.x), int(self.y))

    def draw(self, screen):
        if self.kind == "moving_barrier":
            color = (230, 90, 30)
            label = "MOVING"
        elif self.kind == "speed_bump":
            color = (120, 80, 40)
            label = "BUMP"
        else:
            color = (0, 220, 255)
            label = "NITRO"

        pygame.draw.rect(screen, color, self.rect, border_radius=8)
        pygame.draw.rect(screen, BLACK, self.rect, 2, border_radius=8)
        draw_text(screen, label, self.rect.centerx - 38, self.rect.centery - 12, WHITE)


class RacerGame:
    def __init__(self, screen, clock, settings, player_name):
        self.screen = screen
        self.clock = clock
        self.settings = settings
        self.player_name = player_name

        difficulty = settings.get("difficulty", "normal")
        self.config = DIFFICULTY_CONFIG[difficulty]

        color_name = settings.get("car_color", "blue")
        self.player = Player(CAR_COLORS[color_name])

        self.road_image = load_image("AnimatedStreet.png", (ROAD_WIDTH, HEIGHT))

        self.sound_enabled = settings.get("sound", True)
        self.crash_sound = None

        if self.sound_enabled:
            try:
                pygame.mixer.init()
                background_path = os.path.join(ASSET_DIR, "background.wav")
                if os.path.exists(background_path):
                    pygame.mixer.music.load(background_path)
                    pygame.mixer.music.play(-1)

                self.crash_sound = load_sound("crash.wav")
            except pygame.error:
                self.sound_enabled = False
                self.crash_sound = None

        self.enemies = []
        self.coins = []
        self.obstacles = []
        self.powerups = []
        self.events = []

        self.frame = 0
        self.road_offset = 0
        self.distance = 0
        self.coins_count = 0
        self.score = 0

        self.enemy_speed = self.config["enemy_speed"]
        self.spawn_delay = self.config["spawn_delay"]
        self.obstacle_delay = self.config["obstacle_delay"]

        self.active_power = None
        self.power_timer = 0
        self.shield = False
        self.crashes = 0

        self.game_over = False
        self.finished = False

    def safe_lane(self):
        player_lane = int((self.player.rect.centerx - ROAD_LEFT) // LANE_WIDTH)
        lanes = list(range(LANE_COUNT))

        if random.random() < 0.7 and player_lane in lanes:
            lanes.remove(player_lane)

        return random.choice(lanes)

    def spawn_objects(self):
        scaling = max(0, self.distance // 500)

        enemy_delay = max(18, self.spawn_delay - scaling * 5)
        obstacle_delay = max(35, self.obstacle_delay - scaling * 6)

        if self.frame % enemy_delay == 0:
            self.enemies.append(EnemyCar(self.safe_lane(), self.enemy_speed + scaling))

        if self.frame % 70 == 0:
            self.coins.append(Coin(random.randint(0, LANE_COUNT - 1)))

        if self.frame % obstacle_delay == 0:
            kind = random.choice(["barrier", "oil", "pothole"])
            self.obstacles.append(Obstacle(self.safe_lane(), kind))

        if self.frame % 420 == 0:
            self.powerups.append(PowerUp(random.randint(0, LANE_COUNT - 1)))

        if self.frame % 550 == 0:
            self.events.append(RoadEvent())

    def update_power(self):
        if self.active_power == "nitro":
            self.power_timer -= 1
            if self.power_timer <= 0:
                self.active_power = None

        if self.active_power == "shield":
            self.shield = True

    def activate_powerup(self, kind):
        self.active_power = kind

        if kind == "nitro":
            self.power_timer = 240
            self.score += 50

        elif kind == "shield":
            self.shield = True
            self.power_timer = 0
            self.score += 30

        elif kind == "repair":
            self.crashes = max(0, self.crashes - 1)

            if self.obstacles:
                self.obstacles.pop(0)

            self.active_power = None
            self.score += 40

    def handle_collision(self, hit_type):
        if self.shield:
            self.shield = False
            self.active_power = None
            return

        if hit_type in ["enemy", "barrier", "moving_barrier"]:
            if self.crash_sound:
                self.crash_sound.play()
            self.game_over = True

        elif hit_type == "oil":
            self.player.speed = max(4, self.player.speed - 1)

        elif hit_type == "pothole":
            self.score = max(0, self.score - 20)

        elif hit_type == "speed_bump":
            self.distance = max(0, self.distance - 25)

        elif hit_type == "nitro_strip":
            self.activate_powerup("nitro")

    def update(self):
        self.frame += 1

        nitro_active = self.active_power == "nitro"
        scroll_speed = 5 + (3 if nitro_active else 0)

        keys = pygame.key.get_pressed()
        self.player.update(keys, nitro_active)

        self.road_offset = (self.road_offset + scroll_speed) % HEIGHT
        self.distance += scroll_speed // 2

        self.score = self.coins_count * 20 + self.distance + (50 if nitro_active else 0)

        self.update_power()
        self.spawn_objects()

        all_lists = [self.enemies, self.coins, self.obstacles, self.powerups, self.events]

        for obj_list in all_lists:
            for obj in obj_list:
                obj.update(scroll_speed)

        self.enemies = [e for e in self.enemies if e.y < HEIGHT + 100]
        self.coins = [c for c in self.coins if c.y < HEIGHT + 100]
        self.obstacles = [o for o in self.obstacles if o.y < HEIGHT + 100]
        self.powerups = [p for p in self.powerups if p.y < HEIGHT + 100 and p.life > 0]
        self.events = [e for e in self.events if e.y < HEIGHT + 100]

        for enemy in self.enemies[:]:
            if self.player.rect.colliderect(enemy.rect):
                self.handle_collision("enemy")
                self.enemies.remove(enemy)

        for coin in self.coins[:]:
            if self.player.rect.colliderect(coin.rect):
                self.coins_count += coin.value
                self.score += coin.value * 20
                self.coins.remove(coin)

        for obstacle in self.obstacles[:]:
            if self.player.rect.colliderect(obstacle.rect):
                self.handle_collision(obstacle.kind)
                self.obstacles.remove(obstacle)

        for powerup in self.powerups[:]:
            if self.player.rect.colliderect(powerup.rect):
                self.activate_powerup(powerup.kind)
                self.powerups.remove(powerup)

        for event in self.events[:]:
            if self.player.rect.colliderect(event.rect):
                self.handle_collision(event.kind)
                self.events.remove(event)

        if self.distance >= FINISH_DISTANCE:
            self.finished = True
            self.game_over = True

    def draw_road(self):
        self.screen.fill((60, 150, 70))

        if self.road_image:
            self.screen.blit(self.road_image, (ROAD_LEFT, self.road_offset))
            self.screen.blit(self.road_image, (ROAD_LEFT, self.road_offset - HEIGHT))
        else:
            pygame.draw.rect(self.screen, (55, 55, 55), (ROAD_LEFT, 0, ROAD_WIDTH, HEIGHT))

            for lane in range(1, LANE_COUNT):
                x = ROAD_LEFT + lane * LANE_WIDTH
                for y in range(-40, HEIGHT, 80):
                    pygame.draw.rect(self.screen, WHITE, (x - 3, y + self.road_offset, 6, 40))

        pygame.draw.line(self.screen, WHITE, (ROAD_LEFT, 0), (ROAD_LEFT, HEIGHT), 5)
        pygame.draw.line(self.screen, WHITE, (ROAD_RIGHT, 0), (ROAD_RIGHT, HEIGHT), 5)

    def draw_hud(self):
        remaining = max(0, FINISH_DISTANCE - self.distance)

        pygame.draw.rect(self.screen, (245, 245, 245), (0, 0, WIDTH, 80))
        pygame.draw.line(self.screen, BLACK, (0, 80), (WIDTH, 80), 2)

        draw_text(self.screen, f"Name: {self.player_name}", 10, 8)
        draw_text(self.screen, f"Score: {self.score}", 10, 35)
        draw_text(self.screen, f"Coins: {self.coins_count}", 170, 8)
        draw_text(self.screen, f"Distance: {self.distance}m", 170, 35)
        draw_text(self.screen, f"Remaining: {remaining}m", 360, 8)

        if self.active_power == "nitro":
            seconds = max(0, self.power_timer // 60)
            power_text = f"Power: Nitro {seconds}s"
        elif self.active_power == "shield" and self.shield:
            power_text = "Power: Shield"
        else:
            power_text = "Power: None"

        draw_text(self.screen, power_text, 360, 35)

    def draw(self):
        self.draw_road()

        for obj in self.coins:
            obj.draw(self.screen)

        for obj in self.powerups:
            obj.draw(self.screen)

        for obj in self.obstacles:
            obj.draw(self.screen)

        for obj in self.events:
            obj.draw(self.screen)

        for enemy in self.enemies:
            enemy.draw(self.screen)

        self.player.draw(self.screen)
        self.draw_hud()

    def run(self):
        while not self.game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    if self.sound_enabled:
                        pygame.mixer.music.stop()
                    return "quit", self.score, self.distance, self.coins_count

            self.update()
            self.draw()

            pygame.display.flip()
            self.clock.tick(60)

        if self.sound_enabled:
            pygame.mixer.music.stop()

        add_score(self.player_name, self.score, self.distance, self.coins_count)

        if self.finished:
            return "finished", self.score, self.distance, self.coins_count

        return "game_over", self.score, self.distance, self.coins_count