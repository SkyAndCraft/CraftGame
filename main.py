import pygame
import map
import physic

# Initialisation pygame
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True
dt = 0

class Player:
    def __init__(self, x, y):
        self.pos = pygame.Vector2(x, y)
        self.speed = 300

# Générer la carte sous forme de liste
world_map = map.generateMap()

# Trouver une position de spawn pour le joueur
spawn_x, spawn_y = map.findPlayerSpawn(world_map)

# Initialiser le joueur à la position trouvée
player = Player(map.MaxColonne*10, 310)

# Initialiser la physique
physics = physic.Physics(player)

# Calculer la position initiale de la caméra
camera_x = player.pos.x - screen.get_width() / 2
camera_y = player.pos.y - screen.get_height() / 2

# Boucle du jeu
while running:
    dt = clock.tick(60) / 1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                physics.jump()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                mouse_x, mouse_y = pygame.mouse.get_pos()
                block_x = int((mouse_x + camera_x) // map.BLOCK_SIZE)
                block_y = int((mouse_y + camera_y) // map.BLOCK_SIZE)
                physics.break_block(world_map, block_x, block_y)

    # Gestion des touches
    keys = pygame.key.get_pressed()
    if keys[pygame.K_q]:
        player.pos.x -= player.speed * dt
    if keys[pygame.K_d]:
        player.pos.x += player.speed * dt

    # Mettre à jour la caméra pour suivre le joueur
    camera_x = player.pos.x - screen.get_width() / 2
    camera_y = player.pos.y - screen.get_height() / 2

    # Effacer l'écran
    screen.fill("white")

    # Afficher la carte optimisée
    map.drawMap(screen, world_map, camera_x, camera_y)

    # Appliquer la gravité et vérifier les collisions
    physics.apply_gravity(dt, world_map)

    # Dessiner le joueur au centre de l'écran
    pygame.draw.circle(screen, "red", (screen.get_width() // 2, screen.get_height() // 2), 10)

    # Mise à jour de l'affichage
    pygame.display.flip()

    # Maintien des FPS
    dt = clock.tick(60) / 1000

pygame.quit()
