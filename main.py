import pygame
import random

pygame.init()

# Constants
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

PLAYER_RADIUS = 40
PLAYER_SPEED = 300
CHASE_DISTANCE = 300
NUM_ENEMIES = 5
ENEMY_SPEED = 50

# Colors
WHITE = "white"
BLACK = "black"
GREEN = "green"
RED = "red"
YELLOW = "yellow"

# Screen Setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()


# Classes
class Player:
    def __init__(self, x, y):
        self.position = pygame.Vector2(x, y)
        self.radius = PLAYER_RADIUS
        self.color = GREEN
        self.speed = PLAYER_SPEED

    def move(self, keys, dt):
        if keys[pygame.K_w] and self.position.y - self.radius >= 0:
            self.position.y -= self.speed * dt
        if keys[pygame.K_s] and self.position.y + self.radius <= SCREEN_HEIGHT:
            self.position.y += self.speed * dt
        if keys[pygame.K_a] and self.position.x - self.radius >= 0:
            self.position.x -= self.speed * dt
        if keys[pygame.K_d] and self.position.x + self.radius <= SCREEN_WIDTH:
            self.position.x += self.speed * dt

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, self.position, self.radius)


class Enemy:
    def __init__(self, x, y, radius, speed):
        self.position = pygame.Vector2(x, y)
        self.radius = radius
        self.color = RED
        self.speed = speed
        self.direction = pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize()
        self.roam_timer = random.uniform(1, 3)

    def update(self, player_position, dt):
        if self.position.distance_to(player_position) < CHASE_DISTANCE:
            self.move_towards(player_position, dt)
        else:
            self.roam(dt)
            self.update_roam_timer(dt)

    def move_towards(self, target, dt):
        direction = (target - self.position).normalize()
        self.position += direction * self.speed * dt

    def roam(self, dt):
        new_position = self.position + self.direction * self.speed * dt

        if new_position.x - self.radius < 0 or new_position.x + self.radius > SCREEN_WIDTH:
            self.direction.x *= -1
        if new_position.y - self.radius < 0 or new_position.y + self.radius > SCREEN_HEIGHT:
            self.direction.y *= -1

        self.position += self.direction * self.speed * dt

    def update_roam_timer(self, dt):
        self.roam_timer -= dt
        if self.roam_timer <= 0:
            self.direction = pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize()
            self.roam_timer = random.uniform(1, 3)

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, self.position, self.radius)


class Projectile:
    def __init__(self, x, y, target):
        self.position = pygame.Vector2(x, y)
        self.radius = 10
        self.color = YELLOW
        self.speed = 500
        self.direction = (target - self.position).normalize()

    def update(self, dt):
        self.position += self.direction * self.speed * dt

    def off_screen(self):
        return (self.position.x < 0 or self.position.x > SCREEN_WIDTH
                or self.position.y < 0 or self.position.y > SCREEN_HEIGHT)

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, self.position, self.radius)


class LevelManager:
    def __init__(self, initial_enemies=5, initial_enemy_speed=50, enemy_growth=5, speed_growth=20):
        self.current_level = 1
        self.num_enemies = initial_enemies
        self.enemy_speed = initial_enemy_speed
        self.enemy_growth = enemy_growth
        self.speed_growth = speed_growth

    def level_up(self):
        self.current_level += 1
        self.num_enemies += self.enemy_growth
        self.enemy_speed += self.speed_growth
        self.display_level_up_message()

    def display_level_up_message(self):
        font = pygame.font.Font(None, 50)
        message = f"Level {self.current_level - 1} completed! Moving to Level {self.current_level}!"
        text_render = font.render(message, True, "white")
        text_rect = text_render.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

        screen.fill("black")
        screen.blit(text_render, text_rect)
        pygame.display.flip()
        pygame.time.delay(2000)


# Helper functions
def check_collision(obj1, obj2):
    return obj1.position.distance_to(obj2.position) < obj1.radius + obj2.radius


def game_over():
    font = pygame.font.Font(None, 74)
    render_text(screen, "Game Over", font, WHITE)
    pygame.quit()


def render_text(surface, text, font, color):
    text_render = font.render(text, True, color)
    rect = text_render.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    surface.fill(BLACK)
    surface.blit(text_render, rect)
    pygame.display.flip()
    pygame.time.delay(2000)


def pause_game(screen, clock):
    pause_font = pygame.font.Font(None, 74)
    paused = True
    while paused:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    paused = False

        screen.fill(BLACK)
        pause_text = pause_font.render("Paused - Press ESC to Resume", True, WHITE)
        screen.blit(pause_text, pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)))
        pygame.display.flip()
        clock.tick(10)


def prepare_for_next_level(player, enemies, font):
    countdown_start = pygame.time.get_ticks()
    countdown_duration = 2000  # 2 seconds
    in_countdown = True

    while in_countdown:
        current_time = pygame.time.get_ticks()
        elapsed_time = current_time - countdown_start

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        screen.fill(BLACK)
        player.draw(screen)
        for enemy in enemies:
            enemy.draw(screen)

        countdown_seconds = 2 - int(elapsed_time / 1000)
        if countdown_seconds > 0:
            countdown_text = font.render(f"Get Ready! {countdown_seconds}", True, WHITE)
            text_rect = countdown_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(countdown_text, text_rect)

        pygame.display.flip()
        clock.tick(FPS)

        if elapsed_time >= countdown_duration:
            in_countdown = False


# Main game loop
def main():
    player = Player(SCREEN_WIDTH / 10, SCREEN_HEIGHT / 2)
    level_manager = LevelManager()
    enemies = [Enemy(random.randint(SCREEN_WIDTH // 2, SCREEN_WIDTH - 30),
                     random.randint(30, SCREEN_HEIGHT - 30),
                     random.randint(10, 30),
                     level_manager.enemy_speed)
               for _ in range(NUM_ENEMIES)]
    total_enemies_killed = 0
    projectiles = []
    paused = False

    font = pygame.font.Font(None, 36)

    running = True
    while running:
        dt = clock.tick(FPS) / 1000
        screen.fill(BLACK)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_position = pygame.Vector2(pygame.mouse.get_pos())
                projectiles.append(Projectile(player.position.x, player.position.y, mouse_position))

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pause_game(screen, clock)

        keys = pygame.key.get_pressed()
        player.move(keys, dt)

        for enemy in enemies[:]:
            enemy.update(player.position, dt)
            if check_collision(player, enemy):
                game_over()
                return
            enemy.draw(screen)

        for projectile in projectiles[:]:
            projectile.update(dt)
            if projectile.off_screen():
                projectiles.remove(projectile)
            else:
                for enemy in enemies[:]:
                    if check_collision(projectile, enemy):
                        enemies.remove(enemy)
                        projectiles.remove(projectile)
                        total_enemies_killed += 1
                        break
            projectile.draw(screen)

        if not enemies:
            level_manager.level_up()
            enemies = [Enemy(random.randint(SCREEN_WIDTH // 2, SCREEN_WIDTH - 30),
                             random.randint(30, SCREEN_HEIGHT - 30),
                             random.randint(10, 30),
                             level_manager.enemy_speed)
                       for _ in range(level_manager.num_enemies)]
            projectiles.clear()
            player.position = pygame.Vector2(SCREEN_WIDTH / 10, SCREEN_HEIGHT / 2)
            prepare_for_next_level(player, enemies, font)

        player.draw(screen)

        enemies_killed_text = font.render(f"Enemies Killed: {total_enemies_killed}", True, WHITE)
        screen.blit(enemies_killed_text, (10, 10))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()