import pygame
import sys
import random

# Inicializar Pygame
pygame.init()

# Configuración de la pantalla
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Invaders")

# Colores
WHITE = (255, 255, 255) 
GREEN = (78, 255, 87)
RED = (237, 28, 36)

# Cargar imágenes
ship_img = pygame.image.load('images/ship.png').convert_alpha()
enemy_imgs = [
    pygame.transform.scale(pygame.image.load('images/enemy1_1.png').convert_alpha(), (30, 30)),
    pygame.transform.scale(pygame.image.load('images/enemy2_1.png').convert_alpha(), (30, 30)),
    pygame.transform.scale(pygame.image.load('images/enemy3_1.png').convert_alpha(), (30, 30))
]
bullet_img = pygame.image.load('images/laser.png').convert_alpha()
enemy_bullet_img = pygame.image.load('images/enemylaser.png').convert_alpha()
special_missile_img = pygame.image.load('images/misil.png').convert_alpha()
background_img = pygame.image.load('images/background.jpg').convert()
heart_img = pygame.transform.scale(pygame.image.load('images/heart.png').convert_alpha(), (30, 30))

# Clase para la nave del jugador
class Ship(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = ship_img
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        self.speed = 5

    def update(self, keys):
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += self.speed

# Clase para los enemigos
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, speed, img, powerful=False):
        super().__init__()
        self.image = img
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = speed
        self.powerful = powerful

    def update(self):
        self.rect.x += self.speed
        if self.rect.right >= SCREEN_WIDTH or self.rect.left <= 0:
            self.speed = -self.speed
            self.rect.y += 20

# Clase para las balas
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, img, direction):
        super().__init__()
        self.image = img
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 5 * direction

    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT:
            self.kill()

# Función para mostrar el menú
def show_menu():
    font = pygame.font.Font(None, 74)
    title_text = font.render("Space Invaders", True, WHITE)
    start_text = font.render("Vamos a jugar ahora", True, RED)

    while True:
        screen.fill((0, 0, 0))
        screen.blit(title_text, (200, 200))
        screen.blit(start_text, (150, 300))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                return

# Crear grupos de sprites
def create_game():
    player = Ship()
    player_group = pygame.sprite.Group(player)
    enemies = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    enemy_bullets = pygame.sprite.Group()
    special_missiles = pygame.sprite.Group()
    lives = 3
    phase = 0
    phase_start_time = pygame.time.get_ticks()
    enemies_killed = 0

    return player_group, enemies, bullets, enemy_bullets, special_missiles, lives, phase, phase_start_time, enemies_killed

# Bucle principal del juego
def main():
    show_menu()
    player_group, enemies, bullets, enemy_bullets, special_missiles, lives, phase, phase_start_time, enemies_killed = create_game()

    running = True
    while running:
        screen.blit(background_img, (0, 0))  # Dibujar imagen de fondo
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                bullet = Bullet(player_group.sprites()[0].rect.centerx, player_group.sprites()[0].rect.top, bullet_img, -1)
                bullets.add(bullet)

        player_group.update(keys)
        enemies.update()
        bullets.update()
        enemy_bullets.update()
        special_missiles.update()   

        for bullet in bullets:
            hits = pygame.sprite.spritecollide(bullet, enemies, True)
            if hits:
                bullet.kill()
                enemies_killed += 1

        if pygame.sprite.spritecollideany(player_group.sprites()[0], enemies) or pygame.sprite.spritecollideany(player_group.sprites()[0], enemy_bullets):
            lives -= 1
            if lives <= 0:
                running = False
            else:
                enemies.empty()
                bullets.empty()
                enemy_bullets.empty()
                special_missiles.empty()
                player_group.sprites()[0].rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)
                phase = 0
                phase_start_time = pygame.time.get_ticks()

        # Si el jugador es impactado por un misil especial, pierde todas las vidas
        if pygame.sprite.spritecollideany(player_group.sprites()[0], special_missiles):
            lives = 0
            running = False

        # Generar enemigos según la fase
        if len(enemies) == 0 or enemies_killed >= 10:
            enemies_killed = 0
            phase = (phase + 1) % len(enemy_imgs)
            for x in range(100, 700, 100):
                for y in range(50, 200, 50):
                    powerful = phase > 0
                    enemies.add(Enemy(x, y, 2, enemy_imgs[phase], powerful))

        # Enemigos disparan
        if random.random() < 0.01:
            enemy = random.choice(enemies.sprites())
            if phase == 1:  # Enemigos de segundo nivel disparan el misil especial
                special_missile = Bullet(enemy.rect.centerx, enemy.rect.bottom, special_missile_img, 1)
                special_missiles.add(special_missile)
            else:
                enemy_bullet = Bullet(enemy.rect.centerx, enemy.rect.bottom, enemy_bullet_img, 1)
                enemy_bullets.add(enemy_bullet)
                if enemy.powerful:
                    enemy_bullet2 = Bullet(enemy.rect.centerx - 10, enemy.rect.bottom, enemy_bullet_img, 1)
                    enemy_bullet3 = Bullet(enemy.rect.centerx + 10, enemy.rect.bottom, enemy_bullet_img, 1)
                    enemy_bullets.add(enemy_bullet2)
                    enemy_bullets.add(enemy_bullet3)

        player_group.draw(screen)
        enemies.draw(screen)
        bullets.draw(screen)
        enemy_bullets.draw(screen)
        special_missiles.draw(screen)

        # Mostrar vidas con corazones
        for i in range(lives):
            screen.blit(heart_img, (10 + i * 35, 10))

        pygame.display.flip()
        pygame.time.Clock().tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()