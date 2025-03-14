import pygame
import map

GRAVITY = 800  # Gravité en pixels par seconde^2
JUMP_FORCE = -300  # Force du saut (négatif car vers le haut)
PLAYER_WIDTH = 10  # Largeur approximative du joueur
PLAYER_HEIGHT = 10  # Hauteur approximative du joueur

SOLID_BLOCKS = {"bedrock", "stone", "dirt", "grass"}  # Accélère la recherche

class Physics:
    def __init__(self, player):
        self.player = player
        self.velocity_y = 0
        self.on_ground = False

    def apply_gravity(self, dt, world_map):
        """Applique la gravité et vérifie les collisions."""
        if not self.on_ground:
            self.velocity_y += GRAVITY * dt

        self.player.pos.y += self.velocity_y * dt

        # Empêcher la chute infinie (hors de la carte)
        if self.player.pos.y > (map.MaxGen - 1) * map.BLOCK_SIZE:
            self.player.pos.y = (map.MaxGen - 1) * map.BLOCK_SIZE
            self.velocity_y = 0
            self.on_ground = True
            return

        self.check_collisions(world_map)

    def jump(self):
        """Permet au joueur de sauter s'il est au sol."""
        if self.on_ground:
            self.velocity_y = JUMP_FORCE
            self.on_ground = False

    def is_solid(self, world_map, x, y):
        """Vérifie si un bloc est solide sans dépasser les limites de la carte."""
        if 0 <= y < len(world_map) and 0 <= x < len(world_map[0]):
            return world_map[y][x] in SOLID_BLOCKS
        return False

    def check_collisions(self, world_map):
        """Vérifie et ajuste les collisions avec le sol et les murs."""
        block_x = int(self.player.pos.x // map.BLOCK_SIZE)
        block_y = int(self.player.pos.y // map.BLOCK_SIZE)

        # Vérifier la collision avec le sol
        if self.is_solid(world_map, block_x, block_y + 1):
            self.player.pos.y = block_y * map.BLOCK_SIZE
            self.velocity_y = 0
            self.on_ground = True
        else:
            self.on_ground = False

        # Vérifier les collisions latérales
        self.check_horizontal_collisions(world_map)

    def check_horizontal_collisions(self, world_map):
        """Empêche le joueur de traverser les blocs solides horizontalement."""
        block_x_left = int((self.player.pos.x - PLAYER_WIDTH / 2) // map.BLOCK_SIZE)
        block_x_right = int((self.player.pos.x + PLAYER_WIDTH / 2) // map.BLOCK_SIZE)
        block_y = int(self.player.pos.y // map.BLOCK_SIZE)

        # Vérifier la collision à gauche et à droite
        for offset in range(1, 3):  # Vérifier deux blocs à gauche et deux blocs à droite
            if self.is_solid(world_map, block_x_left - offset, block_y):
                self.player.pos.x = (block_x_left + offset) * map.BLOCK_SIZE
            elif self.is_solid(world_map, block_x_right + offset, block_y):
                self.player.pos.x = (block_x_right - offset) * map.BLOCK_SIZE - PLAYER_WIDTH

    def check_ground(self, world_map):
        """Vérifie si le joueur a toujours un sol en dessous."""
        block_x = int(self.player.pos.x // map.BLOCK_SIZE)
        block_y = int((self.player.pos.y + PLAYER_HEIGHT) // map.BLOCK_SIZE)

        if self.is_solid(world_map, block_x, block_y + 1):
            self.on_ground = True
        else:
            self.on_ground = False

    def apply_background(self, world_map, block_x, block_y):
        """Applique le dégradé ou la couleur de grotte en fonction de l'exposition à la lumière."""
        if world_map[block_y][block_x] == "sky":
            return

        # Vérifier s'il y a de la lumière du jour
        is_daylight = True
        for y in range(block_y - 1, -1, -1):
            if world_map[y][block_x] not in {"sky", "cave"}:
                is_daylight = False
                break

        if is_daylight:
            world_map[block_y][block_x] = "gradient_sky_cave"
        else:
            world_map[block_y][block_x] = "cave_background"

    def break_block(self, world_map, block_x, block_y):
        """Casser un bloc à la position spécifiée."""
        if 0 <= block_y < len(world_map) and 0 <= block_x < len(world_map[0]):
            # Empêcher de casser les blocs de grotte
            if world_map[block_y][block_x] != "cave":
                world_map[block_y][block_x] = "sky"  # Changer la couleur de fond en ciel pour les blocs cassés
                self.apply_background(world_map, block_x, block_y)
                self.check_ground(world_map)  # Vérifie si le joueur a toujours un sol en dessous après avoir cassé un bloc
                self.apply_gravity(0, world_map)  # Appliquer la gravité immédiatement
            elif world_map[block_y][block_x] in {"diamond", "iron", "coal"}:
                world_map[block_y][block_x] = "sky"  # Permet de casser les minerais mais non les blocs de grotte
                self.apply_background(world_map, block_x, block_y)
                self.check_ground(world_map)  # Vérifie si le joueur a toujours un sol en dessous après avoir cassé un bloc
                self.apply_gravity(0, world_map)  # Appliquer la gravité immédiatement
