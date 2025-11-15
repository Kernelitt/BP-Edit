import pygame
import os
from simple_framework import SimplePygameButton, SimplePygameContextMenu
import tkinter as tk
from tkinter import filedialog
from objects import OBJECT_NAME

# Constants
SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 900
BASE_CELL_SIZE = 40

# Colors
BLACK = (0, 0, 15)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Save directory
SAVE_DIR = os.path.join(os.environ['APPDATA'], '..', 'LocalLow', '_Imaginary_', 'Bad Piggies__Rebooted', 'contraptionsB')

def load_save_file(filename):
    filepath = os.path.join(SAVE_DIR, filename)
    objects = []
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            for line in f:
                parts = line.strip().split(',')
                if len(parts) >= 5:
                    obj_type = int(parts[0])
                    skin = int(parts[1])
                    x = int(parts[2])
                    y = int(parts[3])
                    rotation = int(parts[4])
                    objects.append({'type': obj_type, 'skin': skin, 'x': x, 'y': y, 'rotation': rotation})
    return objects

def save_save_file(filename, objects):
    filepath = os.path.join(SAVE_DIR, filename)
    with open(filepath, 'w') as f:
        for obj in objects:
            rotation = obj.get('rotation', 0)
            line = f"{obj['type']},{obj['skin']},{obj['x']},{obj['y']},{rotation},0,0,0\n"
            f.write(line)

def draw_grid(screen, camera_x, camera_y, cell_size):
    import math
    # Calculate starting positions to align grid with world coordinates
    start_x = (math.floor(camera_x / cell_size) * cell_size) - camera_x
    start_y = (math.floor(camera_y / cell_size) * cell_size) - camera_y
    for x in range(int(start_x), SCREEN_WIDTH + int(cell_size), int(cell_size)):
        pygame.draw.line(screen, GRAY, (x, 0), (x, SCREEN_HEIGHT))
    for y in range(int(start_y), SCREEN_HEIGHT + int(cell_size), int(cell_size)):
        pygame.draw.line(screen, GRAY, (0, y), (SCREEN_WIDTH, y))

def draw_objects(screen, objects, camera_x, camera_y, cell_size, max_y, texture_atlas):
    from collections import defaultdict
    cell_objects = defaultdict(list)
    for obj in objects:
        cell_objects[(obj['x'], obj['y'])].append(obj)
    
    for (gx, gy), objs in cell_objects.items():
        x = int(gx * cell_size - camera_x)
        y = int((max_y - gy) * cell_size - camera_y)  # Invert Y
        if 0 <= x < SCREEN_WIDTH and 0 <= y < SCREEN_HEIGHT:
            # Draw up to 2 objects
            for i,obj in enumerate(objs[:2]):
                if obj['type'] in texture_atlas:
                    tex = texture_atlas[obj['type']]
                    # Stretch to fit the half-cell
                    scaled_tex = pygame.transform.smoothscale(tex, (cell_size, cell_size)).convert_alpha()
                    rotation = obj.get('rotation', 0) * 90
                    if rotation:
                        scaled_tex = pygame.transform.rotate(scaled_tex, rotation)
                    screen.blit(scaled_tex, (x, y))
                else:
                    # Fallback to color
                    color = BLUE if obj['type'] == 1 else RED
                    pygame.draw.rect(screen, color, (x, y, cell_size // 2, cell_size))
                    font = pygame.font.SysFont(None, int(18 * (cell_size / BASE_CELL_SIZE)))
                    text = font.render(str(obj['type']), True, WHITE)
                    screen.blit(text, (x + 2, y + 2))

def load_file():
    root = tk.Tk()
    root.withdraw()
    filename = filedialog.askopenfilename(initialdir=SAVE_DIR, title="Select save file")
    root.destroy()
    if filename:
        return os.path.basename(filename)
    return None

def save_file():
    root = tk.Tk()
    root.withdraw()
    filename = filedialog.asksaveasfilename(initialdir=SAVE_DIR, title="Save save file")
    root.destroy()
    if filename:
        return os.path.basename(filename)
    return None

def add_object(objects, x, y):
    cell_objs = [obj for obj in objects if obj['x'] == x and obj['y'] == y]
    if not cell_objs:
        objects.append({'type': 1, 'skin': 0, 'x': x, 'y': y})
    elif len(cell_objs) == 1 and cell_objs[0]['type'] not in [6, 7]:
        # Can add 6 or 7, but not both, and not if already have one
        has_6 = any(obj['type'] == 6 for obj in cell_objs)
        has_7 = any(obj['type'] == 7 for obj in cell_objs)
        if not has_6 and not has_7:
            objects.append({'type': 6, 'skin': 0, 'x': x, 'y': y})  # Add 6 first
        elif has_6 and not has_7:
            objects.append({'type': 7, 'skin': 0, 'x': x, 'y': y})  # Add 7 if 6 is there
        # If has_7, don't add 6; if both, don't add

def remove_object(objects, x, y):
    objects[:] = [obj for obj in objects if not (obj['x'] == x and obj['y'] == y)]

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("BP:Edit")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 24)

    # Load texture atlas
    texture_atlas = {}
    atlas_img = pygame.image.load('Textures/parts.png')
    atlas_width, atlas_height = atlas_img.get_size()
    tile_size = 108
    cols = atlas_width // tile_size
    rows = atlas_height // tile_size
    i = 1
    for r in range(rows):
        for c in range(cols):
            x = c * tile_size
            y = r * tile_size
            if x + tile_size <= atlas_width and y + tile_size <= atlas_height and i <= 11:
                texture_atlas[i] = atlas_img.subsurface((x, y, tile_size, tile_size))
                i += 1
            else:
                break

    # Load a sample save file (replace with file selection logic)
    current_file = 'no'
    objects = load_save_file(current_file)

    # Find max Y for inversion
    max_y = max((obj['y'] for obj in objects), default=0)

    # Camera variables
    camera_x = 0
    camera_y = 0
    zoom = 1.0
    cell_size = BASE_CELL_SIZE * zoom

    # Hotbar
    hotbar_items = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]  # Available types
    selected_item = 1
    hotbar_height = 60
    hotbar_y = SCREEN_HEIGHT - hotbar_height

    # Buttons
    load_button = SimplePygameButton((10, 10), (100, 30), [("Load", (10, 5))], lambda: load_file_action(objects), GREEN)
    save_button = SimplePygameButton((120, 10), (100, 30), [("Save", (10, 5))], lambda: save_file_action(objects), BLUE)

    # Selection
    selected_cells = set()
    drag_start = None
    selection_start = None
    selection_end = None
    initial_positions = {}

    # Info display
    info_text = ""
    info_pos = (0, 0)

    def load_file_action(objects):
        nonlocal current_file, max_y
        filename = load_file()
        if filename:
            current_file = filename
            objects[:] = load_save_file(current_file)
            max_y = max((obj['y'] for obj in objects), default=0)

    def save_file_action(objects):
        filename = save_file()
        if filename:
            save_save_file(filename, objects)

    def draw_hotbar(screen, font):
        pygame.draw.rect(screen, GRAY, (0, hotbar_y, SCREEN_WIDTH, hotbar_height))
        for i, item in enumerate(hotbar_items):
            x = i * 60 + 10
            y = hotbar_y + 10
            if item == selected_item:
                pygame.draw.rect(screen, WHITE, (x-2, y-2, 44, 44))
            pygame.draw.rect(screen, BLACK, (x, y, 40, 40))
            if item in texture_atlas:
                tex = texture_atlas[item]
                scaled_tex = pygame.transform.scale(tex, (40, 40))
                screen.blit(scaled_tex, (x, y))
            else:
                text = font.render(str(item), True, WHITE)
                screen.blit(text, (x + 15, y + 15))

    running = True
    left_mouse_held = False
    while running:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if mouse_y < hotbar_y:
            grid_x = int((mouse_x + camera_x) / cell_size)
            grid_y = int((max_y - (mouse_y + camera_y) / cell_size))  # Invert Y
            cell_objs = [obj for obj in objects if obj['x'] == grid_x and obj['y'] == grid_y]
            if cell_objs:
                info_text = f"Cell ({grid_x}, {grid_y}): " + ", ".join(f"{OBJECT_NAME.get(obj['type'], str(obj['type']))} Skin {obj['skin']} Rot {obj.get('rotation', 0)}" for obj in cell_objs)
                info_pos = (mouse_x + 10, mouse_y - 10)
            else:
                info_text = ""
        else:
            info_text = ""

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    if mouse_y >= hotbar_y:
                        # Hotbar selection
                        for i, item in enumerate(hotbar_items):
                            x = i * 60 + 10
                            if x <= mouse_x <= x + 40:
                                selected_item = item
                                break
                    elif mouse_y >= 100:
                        grid_x = int((mouse_x + camera_x) / cell_size)
                        grid_y = int((max_y - (mouse_y + camera_y) / cell_size))
                        if pygame.key.get_mods() & pygame.KMOD_CTRL:
                            # Start selection rectangle
                            selection_start = (grid_x, grid_y)
                            selection_end = (grid_x, grid_y)
                            left_mouse_held = True
                        else:
                            # Paint or move
                            if selected_cells:
                                # Start drag
                                drag_start = (mouse_x, mouse_y)
                                left_mouse_held = True
                                # Store initial positions
                                initial_positions = {(obj['x'], obj['y']): (obj['x'], obj['y']) for obj in objects if (obj['x'], obj['y']) in selected_cells}
                            else:
                                # Add selected item if not already there
                                cell_objs = [obj for obj in objects if obj['x'] == grid_x and obj['y'] == grid_y]
                                if not any(obj['type'] == selected_item for obj in cell_objs):
                                    if selected_item in [5, 6]:
                                        # Special logic for frames
                                        if not cell_objs:
                                            objects.append({'type': selected_item, 'skin': 0, 'x': grid_x, 'y': grid_y, 'rotation': 0})
                                        elif len(cell_objs) == 1 and cell_objs[0]['type'] not in [5, 6]:
                                            has_5 = any(obj['type'] == 5 for obj in cell_objs)
                                            has_6 = any(obj['type'] == 6 for obj in cell_objs)
                                            if not has_5 and not has_6:
                                                objects.append({'type': selected_item, 'skin': 0, 'x': grid_x, 'y': grid_y, 'rotation': 0})
                                    else:
                                        if len(cell_objs) < 2 and not any(obj['type'] == selected_item for obj in cell_objs):
                                            objects.append({'type': selected_item, 'skin': 0, 'x': grid_x, 'y': grid_y, 'rotation': 0})
                                left_mouse_held = True
                elif event.button == 3:  # Right click
                    if mouse_y < hotbar_y:
                        grid_x = int((mouse_x + camera_x) / cell_size)
                        grid_y = int((max_y - (mouse_y + camera_y) / cell_size))
                        objects[:] = [obj for obj in objects if not (obj['x'] == grid_x and obj['y'] == grid_y)]
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    left_mouse_held = False
                    if selection_start and selection_end:
                        # Finalize selection
                        min_x = min(selection_start[0], selection_end[0])
                        max_x = max(selection_start[0], selection_end[0])
                        min_y_sel = min(selection_start[1], selection_end[1])
                        max_y_sel = max(selection_start[1], selection_end[1])
                        selected_cells = set()
                        for obj in objects:
                            if min_x <= obj['x'] <= max_x and min_y_sel <= obj['y'] <= max_y_sel:
                                selected_cells.add((obj['x'], obj['y']))
                        selection_start = None
                        selection_end = None
                    drag_start = None
            elif event.type == pygame.MOUSEMOTION:
                if left_mouse_held and mouse_y < hotbar_y:
                    if selection_start:
                        # Update selection rectangle
                        grid_x = int((mouse_x + camera_x) / cell_size)
                        grid_y = int((max_y - (mouse_y + camera_y) / cell_size))
                        selection_end = (grid_x, grid_y)
                    elif selected_cells and drag_start:
                        dx = mouse_x - drag_start[0]
                        dy = mouse_y - drag_start[1]
                        grid_dx = int(dx / cell_size)
                        grid_dy = -int(dy / cell_size)  # Invert Y
                        if grid_dx or grid_dy:
                            # Reset to initial positions and apply new offset
                            for obj in objects[:]:
                                if (obj['x'], obj['y']) in initial_positions:
                                    init_x, init_y = initial_positions[(obj['x'], obj['y'])]
                                    obj['x'] = init_x + grid_dx
                                    obj['y'] = init_y + grid_dy
                            # Update selected_cells to new positions
                            selected_cells = {(x + grid_dx, y + grid_dy) for x, y in selected_cells}
                            # Update initial_positions for next move
                            initial_positions = {(obj['x'], obj['y']): (obj['x'], obj['y']) for obj in objects if (obj['x'], obj['y']) in selected_cells}
                            drag_start = (mouse_x, mouse_y)
                    elif not selected_cells:
                        grid_x = int((mouse_x + camera_x) / cell_size)
                        grid_y = int((max_y - (mouse_y + camera_y) / cell_size))
                        cell_objs = [obj for obj in objects if obj['x'] == grid_x and obj['y'] == grid_y]
                        if not any(obj['type'] == selected_item for obj in cell_objs):
                            if selected_item in [6, 7]:
                                if not cell_objs:
                                    objects.append({'type': selected_item, 'skin': 0, 'x': grid_x, 'y': grid_y, 'rotation': 0})
                                elif len(cell_objs) == 1 and cell_objs[0]['type'] not in [6, 7]:
                                    has_6 = any(obj['type'] == 6 for obj in cell_objs)
                                    has_7 = any(obj['type'] == 7 for obj in cell_objs)
                                    if not has_6 and not has_7:
                                        objects.append({'type': selected_item, 'skin': 0, 'x': grid_x, 'y': grid_y, 'rotation': 0})
                                    elif has_6 and selected_item == 7:
                                        objects.append({'type': 7, 'skin': 0, 'x': grid_x, 'y': grid_y, 'rotation': 0})
                            else:
                                if len(cell_objs) < 2 and not any(obj['type'] == selected_item for obj in cell_objs):
                                    objects.append({'type': selected_item, 'skin': 0, 'x': grid_x, 'y': grid_y, 'rotation': 0})
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    camera_x -= 50
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    camera_x += 50
                elif event.key == pygame.K_UP or event.key == pygame.K_w:
                    camera_y -= 50
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    camera_y += 50
                elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                    zoom *= 1.25
                    cell_size = BASE_CELL_SIZE * zoom
                elif event.key == pygame.K_r:
                    for obj in objects:
                        grid_x = int((mouse_x + camera_x) / cell_size)
                        grid_y = int((max_y - (mouse_y + camera_y) / cell_size))
                        if obj['x'] == grid_x and obj['y'] == grid_y:
                            obj['rotation'] = (obj.get('rotation', 0) + 1) % 4
                elif event.key == pygame.K_MINUS:
                    zoom /= 1.25
                    cell_size = BASE_CELL_SIZE * zoom
                    if cell_size < 10:
                        cell_size = 10
                        zoom = cell_size / BASE_CELL_SIZE

            load_button.update(event)
            save_button.update(event)

        screen.fill(BLACK)
        draw_grid(screen, camera_x, camera_y, cell_size)
        draw_objects(screen, objects, camera_x, camera_y, cell_size, max_y, texture_atlas)
        # Draw selected cells
        for gx, gy in selected_cells:
            x = int(gx * cell_size - camera_x)
            y = int((max_y - gy) * cell_size - camera_y)
            if 0 <= x < SCREEN_WIDTH and 0 <= y < SCREEN_HEIGHT:
                pygame.draw.rect(screen, GREEN, (x, y, cell_size, cell_size), 2)
        # Draw selection rectangle
        if selection_start and selection_end:
            min_grid_x = min(selection_start[0], selection_end[0])
            max_grid_x = max(selection_start[0], selection_end[0])
            min_grid_y = min(selection_start[1], selection_end[1])
            max_grid_y = max(selection_start[1], selection_end[1])
            screen_x = int(min_grid_x * cell_size - camera_x)
            screen_y = int((max_y - max_grid_y) * cell_size - camera_y)
            width = int((max_grid_x - min_grid_x + 1) * cell_size)
            height = int((max_grid_y - min_grid_y + 1) * cell_size)
            pygame.draw.rect(screen, BLUE, (screen_x, screen_y, width, height), 2)
        draw_hotbar(screen, font)
        load_button.draw(screen, font)
        save_button.draw(screen, font)
        if info_text:
            info_surface = font.render(info_text, True, WHITE)
            screen.blit(info_surface, info_pos)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
