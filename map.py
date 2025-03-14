import pygame
import random
import math

BLOCK_SIZE = 10  # Taille d'un bloc en pixels
MaxGen = 128  # Hauteur de la carte (en nombre de blocs)
MinColonne = -512  # Début des colonnes
MaxColonne = 512  # Fin des colonnes

# Liste des types de blocs
Blocks = {
    "bedrock": "black",
    "stone": "grey",
    "diamond": "cyan",
    "iron": "white",
    "coal": "black",
    "dirt": "brown",
    "grass": "green",
    "sky": "skyblue",
    "cave": (64, 64, 64),  # Couleur pour assombrir les blocs de la grotte
    "mountain": "darkgrey",  # Couleur pour les montagnes
    "snow": "white"  # Couleur pour la neige
}

CaveMinerals = {
    "diamond": "darkcyan",  # Assombrir la couleur du diamant
    "iron": "darkgrey",  # Assombrir la couleur du fer
    "coal": "darkslategray",  # Assombrir la couleur du charbon
}

cave_chance = 0.45  # Augmenter le pourcentage de grotte
cave_start_depth = 90  # Set the depth at which caves should start

def generateMap():
    """Génère la carte sous forme de liste 2D avec des montagnes, des grottes et des minerais"""
    world_map = []
    amplitude = 3  # Réduire l'amplitude pour des montagnes plus petites
    frequency = 0.005  # Réduire la fréquence pour des montagnes plus étroites

    for c in range(MaxGen):  # Générer du bas vers le haut
        row = []
        for col in range(MinColonne, MaxColonne + 1):  # De -512 à 512
            if abs(col) >= 500:  # Ne pas générer autour de la colonne 512
                block_type = "sky"
            else:
                a = random.randint(1, 300)
                depth = MaxGen - c  # Inverser la numérotation des couches

                # Generate terrain elevation using a simple sinusoidal function
                elevation = amplitude * math.sin(frequency * col) + MaxGen // 2

                if depth <= 2:
                    block_type = "bedrock"
                elif depth <= 6:
                    block_type = "stone"
                elif depth <= 10:
                    block_type = "diamond" if a <= 4 else "stone"
                elif depth <= 20:
                    block_type = "stone"
                elif depth <= 30:
                    block_type = "iron" if a <= 7 else "stone"
                elif depth <= 35:
                    block_type = "coal" if a <= 3 else ("iron" if a <= 6 else "stone")
                elif depth <= 39:
                    block_type = "coal" if a <= 11 else "stone"
                elif depth <= 40:
                    block_type = "stone"
                elif depth <= elevation:
                    block_type = "mountain" if elevation > MaxGen // 2 else "grass"
                elif depth <= elevation + 1:  # Réduire la hauteur de l'herbe
                    block_type = "grass"
                elif depth <= elevation + 4:
                    block_type = "snow" if elevation > MaxGen // 2 else "grass"
                else:
                    block_type = "sky"

            row.append(block_type)
        world_map.append(row)

    generateCaves(world_map)
    return world_map

def generateCaves(world_map):
    """Génère des grottes et des minerais en assombrissant certains blocs."""
    for y in range(cave_start_depth, MaxGen - 10):  # Profondeur des grottes
        for x in range(MinColonne, MaxColonne + 1):
            if random.random() < cave_chance:
                world_map[y][x - MinColonne] = "cave"

    for _ in range(3):  # Applique les règles de l'automate cellulaire pour raffiner les grottes
        refineCaves(world_map)

    # Ajouter des minerais dans les grottes
    for y in range(cave_start_depth, MaxGen - 10):
        for x in range(MinColonne, MaxColonne + 1):
            if world_map[y][x - MinColonne] == "cave":
                if random.random() < 0.02:  # Réduire la probabilité de spawn de diamant
                    world_map[y][x - MinColonne] = "diamond"
                elif random.random() < 0.05:
                    world_map[y][x - MinColonne] = "iron"
                elif random.random() < 0.05:
                    world_map[y][x - MinColonne] = "coal"

def refineCaves(world_map):
    """Raffine les grottes en appliquant des règles de l'automate cellulaire."""
    for y in range(cave_start_depth, MaxGen - 1):  # Start refining from cave_start_depth
        for x in range(1, MaxColonne - MinColonne):
            neighbors = countCaveNeighbors(world_map, x, y)
            if world_map[y][x] == "cave":
                if neighbors < 4:
                    world_map[y][x] = "stone"
            else:
                if neighbors > 4:
                    world_map[y][x] = "cave"

def countCaveNeighbors(world_map, x, y):
    """Compte le nombre de voisins qui sont des grottes."""
    neighbors = 0
    for j in range(-1, 2):
        for i in range(-1, 2):
            if i == 0 and j == 0:
                continue
            if 0 <= y + j < MaxGen and 0 <= x + i < len(world_map[0]):
                if world_map[y + j][x + i] == "cave":
                    neighbors += 1
    return neighbors

def findPlayerSpawn(world_map):
    """Trouve une position de spawn pour le joueur au-dessus du premier bloc de gazon."""
    for y in range(MaxGen):
        for x in range(len(world_map[0])):
            if world_map[y][x] == "grass":
                return x * BLOCK_SIZE, (y - 1) * BLOCK_SIZE  # Spawner au-dessus du bloc de gazon
    return 0, 0  # Si aucun bloc de gazon n'est trouvé, retourner (0, 0)

def drawMap(screen, world_map, camera_x, camera_y):
    """Affiche uniquement la partie visible de la carte."""
    rows = len(world_map)
    cols = len(world_map[0])

    screen_width, screen_height = screen.get_size()
    blocks_x_visible = screen_width // BLOCK_SIZE
    blocks_y_visible = screen_height // BLOCK_SIZE

    for y in range(blocks_y_visible + 1):
        for x in range(blocks_x_visible + 1):
            map_x = int(x + camera_x // BLOCK_SIZE) + MinColonne  # Décalage avec MinColonne
            map_y = int(y + camera_y // BLOCK_SIZE)

            if MinColonne <= map_x <= MaxColonne and 0 <= map_y < rows:
                block_type = world_map[map_y][map_x - MinColonne]  # Décalage pour accéder à la liste
                if block_type in ["diamond", "iron", "coal"] and map_y >= cave_start_depth:
                    block_color = CaveMinerals[block_type]  # Assombrir uniquement dans les grottes
                else:
                    block_color = Blocks[block_type]
                pygame.draw.rect(screen, block_color,
                                 pygame.Rect(x * BLOCK_SIZE - int(camera_x % BLOCK_SIZE),
                                             y * BLOCK_SIZE - int(camera_y % BLOCK_SIZE),
                                             BLOCK_SIZE, BLOCK_SIZE))
