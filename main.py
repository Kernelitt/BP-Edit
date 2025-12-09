from objects import OBJECT_NAME
import pygame, sys, os
from tkinter import filedialog, Tk
import configparser
import os

config = configparser.ConfigParser(interpolation=None)
config.read('config.ini')

TEXTURES_DIRECTORY_PATH = config.get('Paths', 'texture_directory_path')
SAVEFILE_DIRECTORY = os.path.expandvars(config.get('Paths', 'savefile_directory'))  # Обрабатываем %APPDATA%
MOVE_SPEED = config.getint('Speeds', 'move_speed')
ZOOM_SPEED = config.getfloat('Speeds', 'zoom_speed')
HOTBAR_ROWS = config.getint('UI', 'hotbar_rows')
HOTBAR_SLOT_SIZE = config.getint('UI', 'hotbar_slot_size')
HOTBAR_OFFSET_X = config.getint('UI', 'hotbar_offset_x')
HOTBAR_OFFSET_Y = config.getint('UI', 'hotbar_offset_y')
SKIN_PANEL_WIDTH = config.getint('UI', 'skin_panel_width')
SKIN_PANEL_HEIGHT = config.getint('UI', 'skin_panel_height')
SKIN_PANEL_OFFSET_X = config.getint('UI', 'skin_panel_offset_x')
SCREEN_WIDTH = config.getint('Screen', 'screen_width')
SCREEN_HEIGHT = config.getint('Screen', 'screen_height')

class Part:
    def __init__(self, grid_x, grid_y, object_id, layer=0, rotation=0, mirror=False, skin=0):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.object_id = object_id
        self.layer = layer
        self.rotation = rotation
        self.mirror = mirror
        self.skin = skin

class App():
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
        pygame.display.set_caption("BP-Edit")
        self.clock = pygame.time.Clock()

        self.grid = Grid()
        self.selected_part_id = 1
        
        
        self.hotbar_cols = (len(self.grid.textures) + HOTBAR_ROWS - 1) // HOTBAR_ROWS
        
        self.hotbar_y = self.screen.get_height() - HOTBAR_ROWS * HOTBAR_SLOT_SIZE - HOTBAR_OFFSET_Y

        self.selected_skin = 0
        self.skin_panel_visible = False
        self.skin_button_size = 60
        self.skin_button_x = self.screen.get_width() - self.skin_button_size - 10
        self.skin_button_y = self.screen.get_height() - self.skin_button_size - 10
        
        
        self.skin_panel_x = self.skin_button_x + (self.skin_button_size - SKIN_PANEL_WIDTH) - SKIN_PANEL_OFFSET_X # Center horizontally
        self.skin_panel_y = self.skin_button_y - SKIN_PANEL_HEIGHT  # Above the button

        self.show_help = False
        self.font = pygame.font.SysFont(None, 24)

        self.tk = Tk(useTk=False)

    def run(self):
        self.running = True
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_o and (event.mod & pygame.KMOD_CTRL):
                        self.load_savefile()
                    elif event.key == pygame.K_s and (event.mod & pygame.KMOD_CTRL):
                        self.save_savefile()
                    elif event.key == pygame.K_i and (event.mod & pygame.KMOD_CTRL):
                        self.load_parts_from_file()
                    elif event.key == pygame.K_F1:
                        self.show_help = not self.show_help
                    else:
                        self.grid.handle_event(event, self.selected_part_id, self.selected_skin)
                elif event.type == pygame.KEYUP:
                    self.grid.handle_event(event, self.selected_part_id)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = event.pos
                    if self.is_skin_button_click(mouse_x, mouse_y):
                        if event.button == 1:
                            self.skin_panel_visible = not self.skin_panel_visible
                    elif self.skin_panel_visible and self.is_skin_panel_click(mouse_x, mouse_y):
                        if event.button == 1:
                            self.handle_skin_panel_click(mouse_x, mouse_y)
                    elif self.is_hotbar_click(mouse_x, mouse_y):
                        if event.button == 1:
                            self.handle_hotbar_click(mouse_x, mouse_y)
                    else:
                        self.grid.handle_event(event, self.selected_part_id, self.selected_skin)
                elif event.type == pygame.MOUSEMOTION:
                    self.grid.handle_event(event, self.selected_part_id)
                elif event.type == pygame.MOUSEBUTTONUP:
                    self.grid.handle_event(event, self.selected_part_id)

            self.grid.update()

            self.draw()
            self.clock.tick(60)

    def is_hotbar_click(self, mouse_x, mouse_y):
        return (HOTBAR_OFFSET_X <= mouse_x <= HOTBAR_OFFSET_X + self.hotbar_cols * HOTBAR_SLOT_SIZE and
                self.hotbar_y <= mouse_y <= self.hotbar_y + HOTBAR_ROWS * HOTBAR_SLOT_SIZE)

    def handle_hotbar_click(self, mouse_x, mouse_y):
        col = (mouse_x - HOTBAR_OFFSET_X) // HOTBAR_SLOT_SIZE
        row = (mouse_y - self.hotbar_y) // HOTBAR_SLOT_SIZE
        index = row * self.hotbar_cols + col
        if 0 <= index < len(self.grid.textures):
            self.selected_part_id = list(self.grid.textures.keys())[index][0]  # obj_id
            self.selected_skin = 0  # Reset to default skin

    def draw(self):
        self.screen.fill("#000768")

        # Draw grid here if needed
        self.grid.draw(self.screen)

        # Draw hotbar
        self.draw_hotbar()

        # Draw skin button
        self.draw_skin_button()

        # Draw skin panel if visible
        self.draw_skin_panel()

        # Draw help screen if enabled
        if self.show_help:
            self.draw_help()

        self.screen.blit(self.font.render("Press F1 to show controls", True, (255, 255, 255)), (200, 0))
        pygame.display.flip()

    def draw_hotbar(self):
        for i, part_id in enumerate(self.grid.textures.keys()):
            obj_id = part_id[0]  # part_id is (obj_id, 0)
            row = i // self.hotbar_cols
            col = i % self.hotbar_cols
            x = HOTBAR_OFFSET_X + col * HOTBAR_SLOT_SIZE
            y = self.hotbar_y + row * HOTBAR_SLOT_SIZE
            # Draw slot background
            color = (150, 150, 150) if obj_id == self.selected_part_id else (100, 100, 100)
            pygame.draw.rect(self.screen, color, (x, y, HOTBAR_SLOT_SIZE, HOTBAR_SLOT_SIZE))
            pygame.draw.rect(self.screen, (200, 200, 200), (x, y, HOTBAR_SLOT_SIZE, HOTBAR_SLOT_SIZE), 2)
            # Draw texture with default skin
            texture_key = (obj_id, 0)
            texture = self.grid.textures[texture_key]
            scaled_texture = pygame.transform.scale(texture, (HOTBAR_SLOT_SIZE - 4, HOTBAR_SLOT_SIZE - 4))
            self.screen.blit(scaled_texture, (x + 2, y + 2))

    def load_savefile(self):
        file_path = filedialog.askopenfilename(initialdir=SAVEFILE_DIRECTORY)
        if file_path:
            self.grid.load(file_path)

    def load_parts_from_file(self):
        file_path = filedialog.askopenfilename(initialdir=SAVEFILE_DIRECTORY)
        if file_path:
            loaded_parts = self.grid.load_parts_from_file(file_path)
            if loaded_parts:
                # Select the loaded parts
                self.grid.selected_parts = loaded_parts
                # Center the view on the loaded parts
                self.grid.center_on_parts(loaded_parts)

    def save_savefile(self):
        file_path = filedialog.asksaveasfilename(initialdir=SAVEFILE_DIRECTORY)
        if file_path:
            self.grid.save(file_path)

    def draw_help(self):
        help_lines = [
            "Controls:",
            "WASD - Move camera",
            "Arrow Up/Down - Zoom in/out",
            "Left Click - Place part / Select",
            "Right Click - Remove part",
            "Ctrl + Left Click - Start selection",
            "R - Rotate part",
            "T - Mirror part",
            "Shift+R - Rotate selected building counterclockwise",
            "Shift+T - Flip selected building horizontally",
            "Del - Delete selected building",
            "Ctrl+C - Copy selected parts",
            "Ctrl+V - Paste copied parts",
            "Ctrl+O - Load file",
            "Ctrl+S - Save file",
            "Ctrl+I - Load parts from file",
            "F1 - Toggle help"
        ]
        y = 10
        for line in help_lines:
            text_surface = self.font.render(line, True, (255, 255, 255))
            self.screen.blit(text_surface, (10, y))
            y += 30

    def draw_skin_button(self):
        # Draw skin button in bottom right
        color = (200, 200, 200) if self.skin_panel_visible else (150, 150, 150)
        pygame.draw.rect(self.screen, color, (self.skin_button_x, self.skin_button_y, self.skin_button_size, self.skin_button_size))
        pygame.draw.rect(self.screen, (255, 255, 255), (self.skin_button_x, self.skin_button_y, self.skin_button_size, self.skin_button_size), 2)
        # Draw current selected part with skin
        texture_key = (self.selected_part_id, self.selected_skin)
        if texture_key in self.grid.textures:
            texture = self.grid.textures[texture_key]
        else:
            texture = self.grid.textures[(self.selected_part_id, 0)]  # fallback
        scaled_texture = pygame.transform.scale(texture, (self.skin_button_size - 4, self.skin_button_size - 4))
        self.screen.blit(scaled_texture, (self.skin_button_x + 2, self.skin_button_y + 2))

    def draw_skin_panel(self):
        if not self.skin_panel_visible:
            return
        # Draw panel background
        pygame.draw.rect(self.screen, (50, 50, 50), (self.skin_panel_x, self.skin_panel_y, SKIN_PANEL_WIDTH, SKIN_PANEL_HEIGHT))
        pygame.draw.rect(self.screen, (255, 255, 255), (self.skin_panel_x, self.skin_panel_y, SKIN_PANEL_WIDTH, SKIN_PANEL_HEIGHT), 2)
        # Draw skin options
        if self.selected_part_id in self.grid.skin_dict:
            skins = self.grid.skin_dict[self.selected_part_id]
            skin_size = 40
            for i, skin_texture in enumerate(skins):
                x = self.skin_panel_x + 10 + (i % 4) * (skin_size + 5)
                y = self.skin_panel_y + 10 + (i // 4) * (skin_size + 5)
                if x + skin_size > self.skin_panel_x + SKIN_PANEL_WIDTH - 10:
                    continue  # Skip if out of bounds
                color = (200, 200, 200) if i == self.selected_skin else (100, 100, 100)
                pygame.draw.rect(self.screen, color, (x, y, skin_size, skin_size))
                pygame.draw.rect(self.screen, (255, 255, 255), (x, y, skin_size, skin_size), 1)
                scaled_texture = pygame.transform.scale(skin_texture, (skin_size - 4, skin_size - 4))
                self.screen.blit(scaled_texture, (x + 2, y + 2))

    def is_skin_button_click(self, mouse_x, mouse_y):
        return (self.skin_button_x <= mouse_x <= self.skin_button_x + self.skin_button_size and
                self.skin_button_y <= mouse_y <= self.skin_button_y + self.skin_button_size)

    def is_skin_panel_click(self, mouse_x, mouse_y):
        return (self.skin_panel_x <= mouse_x <= self.skin_panel_x + SKIN_PANEL_WIDTH and
                self.skin_panel_y <= mouse_y <= self.skin_panel_y + SKIN_PANEL_HEIGHT)

    def handle_skin_panel_click(self, mouse_x, mouse_y):
        if self.selected_part_id not in self.grid.skin_dict:
            return
        skins = self.grid.skin_dict[self.selected_part_id]
        skin_size = 40
        for i, skin_texture in enumerate(skins):
            x = self.skin_panel_x + 10 + (i % 4) * (skin_size + 5)
            y = self.skin_panel_y + 10 + (i // 4) * (skin_size + 5)
            if x <= mouse_x <= x + skin_size and y <= mouse_y <= y + skin_size:
                self.selected_skin = i  # skins are 0-indexed
                break


class Grid():
    def __init__(self):
        self.parts_in_grid = [[], []]  # Initialize as list of lists for layers
        self.cell_size = 50  # Size of each cell in pixels
        self.colored_cells = {}  # Dictionary to store colored cells: (grid_x, grid_y) -> color
        self.offset_x = 0
        self.offset_y = 0
        self.moving_up = False
        self.moving_down = False
        self.moving_left = False
        self.moving_right = False
        self.zoom = 1.0
        self.zooming_in = False
        self.zooming_out = False
        self.rotating = False
        self.selecting = False
        self.selection_start = None
        self.selection_rect = None
        self.selected_parts = []
        self.dragging = False
        self.drag_offset = None
        self.drag_start_grid = None
        self.drag_initial_positions = None
        self.copied_parts = []
        self.textures = {}
        self.skin_textures = {}
        # Load main texture atlas
        self.atlas = pygame.image.load(TEXTURES_DIRECTORY_PATH+"parts.png").convert_alpha()
        atlas_width, atlas_height = self.atlas.get_size()
        self.cols = atlas_width // 108
        self.rows = atlas_height // 108
        # Extract textures from main atlas (skin=0)
        for i in range(1, 47):
            col = (i - 1) % self.cols
            row = (i - 1) // self.cols
            x = col * 108
            y = row * 108
            subsurface = self.atlas.subsurface((x, y, 108, 108))
            # Skip empty surfaces
            if subsurface.get_bounding_rect().width > 0:
                self.textures[(i, 0)] = subsurface

        # Load skin atlases if available
        for obj_id in range(1, self.cols * self.rows + 1):
            skin_path = TEXTURES_DIRECTORY_PATH+"{obj_id}_skin.png"
            if os.path.exists(skin_path):
                skin_atlas = pygame.image.load(skin_path).convert_alpha()
                skin_atlas_width, skin_atlas_height = skin_atlas.get_size()
                skin_cols = skin_atlas_width // 108
                skin_rows = skin_atlas_height // 108
                for skin_i in range(1, skin_cols * skin_rows + 1):
                    col = (skin_i - 1) % skin_cols
                    row = (skin_i - 1) // skin_cols
                    x = col * 108
                    y = row * 108
                    subsurface = skin_atlas.subsurface((x, y, 108, 108))
                    # Skip empty surfaces
                    if subsurface.get_bounding_rect().width > 0:
                        self.skin_textures[(obj_id, skin_i)] = subsurface
        print(self.skin_textures)



        # Create skin dictionary: {obj_id: [list of skin textures]}
        self.skin_dict = {}
        for obj_id in range(1, 47):
            self.skin_dict[obj_id] = [self.textures[(obj_id, 0)]]  # Add default skin first
        for (obj_id, skin_i), texture in self.skin_textures.items():
            self.skin_dict[obj_id].append(texture)
        print(self.skin_dict)
        
    def draw(self, screen):
        width, height = screen.get_size()
        cell_size_zoomed = int(self.cell_size * self.zoom)
        # Draw vertical lines
        start_x = -self.offset_x % cell_size_zoomed
        for x in range(start_x, width + cell_size_zoomed, cell_size_zoomed):
            pygame.draw.line(screen, (100, 100, 100), (x, 0), (x, height))
        # Draw horizontal lines
        start_y = -self.offset_y % cell_size_zoomed
        for y in range(start_y, height + cell_size_zoomed, cell_size_zoomed):
            pygame.draw.line(screen, (100, 100, 100), (0, y), (width, y))
        # Draw axes
        width, height = screen.get_size()
        # Vertical axis (x=0)
        axis_x = -self.offset_x
        if 0 <= axis_x <= width:
            pygame.draw.line(screen, (255, 255, 255), (axis_x, 0), (axis_x, height), 2)
        # Horizontal axis (y=0)
        axis_y = -self.offset_y
        if 0 <= axis_y <= height:
            pygame.draw.line(screen, (255, 255, 255), (0, axis_y), (width, axis_y), 2)

        # Draw colored cells
        for (grid_x, grid_y), color in self.colored_cells.items():
            screen_x = grid_x * cell_size_zoomed - self.offset_x
            screen_y = grid_y * cell_size_zoomed - self.offset_y
            pygame.draw.rect(screen, color, (screen_x, screen_y, cell_size_zoomed, cell_size_zoomed))
        # Draw parts in layer order
        for layer in range(len(self.parts_in_grid)):
            for part in self.parts_in_grid[layer]:
                texture_key = (part.object_id, part.skin)
                if texture_key in self.textures:
                    texture = self.textures[texture_key]
                elif texture_key in self.skin_textures:
                    texture = self.skin_textures[texture_key]
                else:
                    continue  # Skip if no texture found
                screen_x = part.grid_x * cell_size_zoomed - self.offset_x
                screen_y = part.grid_y * cell_size_zoomed - self.offset_y
                scaled_texture = pygame.transform.smoothscale(texture, (cell_size_zoomed,cell_size_zoomed))
                if part.mirror:
                    scaled_texture = pygame.transform.flip(scaled_texture, True, False)
                rotated_texture = pygame.transform.rotate(scaled_texture, part.rotation * 90)
                screen.blit(rotated_texture, (screen_x, screen_y))
                # Highlight selected parts
                if part in self.selected_parts:
                    pygame.draw.rect(screen, (255, 255, 0), (screen_x, screen_y, cell_size_zoomed, cell_size_zoomed), 3)
        # Draw selection rectangle
        if self.selection_rect:
            pygame.draw.rect(screen, (255, 255, 0), self.selection_rect, 2)

    def update(self):
        if self.moving_up:
            self.offset_y -=    MOVE_SPEED
        if self.moving_down:
            self.offset_y +=    MOVE_SPEED
        if self.moving_left:
            self.offset_x -=    MOVE_SPEED
        if self.moving_right:
            self.offset_x +=    MOVE_SPEED
        if self.zooming_in:
            self.zoom += ZOOM_SPEED
            if self.zoom > 5.0:
                self.zoom = 5.0
        if self.zooming_out:
            self.zoom -= ZOOM_SPEED
            if self.zoom < 0.1:
                self.zoom = 0.1

    def screen_to_grid(self, screen_x, screen_y):
        cell_size_zoomed = int(self.cell_size * self.zoom)
        grid_x = (screen_x + self.offset_x) // cell_size_zoomed
        grid_y = (screen_y + self.offset_y) // cell_size_zoomed
        return grid_x, grid_y

    def save(self, filepath):
        with open(filepath, 'w') as f:
            for layer in self.parts_in_grid:
                for part in layer:
                    f.write(f"{part.object_id},{part.skin},{part.grid_x},{-part.grid_y},{part.rotation},{int(part.mirror)},0,0\n")

    def load(self, filepath):
        self.parts_in_grid = [[], []]  # Initialize as list of lists for layers
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    parts = line.split(',')
                    if len(parts) >= 6:
                        object_id = int(parts[0])
                        skin = int(parts[1])
                        grid_x = int(parts[2])
                        grid_y = -int(parts[3])
                        rotation = int(parts[4])
                        mirror = bool(int(parts[5]))
                        layer = 0 if object_id in [5, 6] else 1
                        new_part = Part(grid_x, grid_y, object_id, layer, rotation, mirror, skin)
                        if layer < len(self.parts_in_grid):
                            self.parts_in_grid[layer].append(new_part)

    def load_parts_from_file(self, filepath):
        loaded_parts = []
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    parts = line.split(',')
                    if len(parts) >= 6:
                        object_id = int(parts[0])
                        skin = int(parts[1])
                        grid_x = int(parts[2])
                        grid_y = -int(parts[3])
                        rotation = int(parts[4])
                        mirror = bool(int(parts[5]))
                        layer = 0 if object_id in [5, 6] else 1
                        new_part = Part(grid_x, grid_y, object_id, layer, rotation, mirror, skin)
                        # Add to grid without clearing
                        if layer < len(self.parts_in_grid):
                            self.parts_in_grid[layer].append(new_part)
                        loaded_parts.append(new_part)
        return loaded_parts

    def center_on_parts(self, parts):
        if not parts:
            return
        min_x = min(part.grid_x for part in parts)
        max_x = max(part.grid_x for part in parts)
        min_y = min(part.grid_y for part in parts)
        max_y = max(part.grid_y for part in parts)
        center_x = (min_x + max_x) / 2
        center_y = (min_y + max_y) / 2
        screen_width, screen_height = 1600, 900  # Assuming screen size
        cell_size_zoomed = int(self.cell_size * self.zoom)
        self.offset_x = int(center_x * cell_size_zoomed - screen_width / 2)
        self.offset_y = int(center_y * cell_size_zoomed - screen_height / 2)

    def move(self, dx, dy):
        pass

    def handle_event(self, event, selected_part_id=1, selected_skin=0):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                self.moving_up = True
            if event.key == pygame.K_s:
                self.moving_down = True
            if event.key == pygame.K_a:
                self.moving_left = True
            if event.key == pygame.K_d:
                self.moving_right = True
            if event.key == pygame.K_UP:
                self.zooming_in = True
            if event.key == pygame.K_DOWN:
                self.zooming_out = True
            if event.key == pygame.K_r:
                if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                    # Rotate selected building clockwise around its center
                    if self.selected_parts:
                        # Calculate center of selected parts
                        min_x = min(part.grid_x for part in self.selected_parts)
                        max_x = max(part.grid_x for part in self.selected_parts)
                        min_y = min(part.grid_y for part in self.selected_parts)
                        max_y = max(part.grid_y for part in self.selected_parts)
                        cx = (min_x + max_x) // 2
                        cy = (min_y + max_y) // 2
                        # Rotate positions and orientations
                        for part in self.selected_parts:
                            # Rotate position 90 degrees clockwise around center
                            dx = part.grid_x - cx
                            dy = part.grid_y - cy
                            new_dx = dy
                            new_dy = -dx
                            part.grid_x = round(cx + new_dx)
                            part.grid_y = round(cy + new_dy)
                            # Rotate part orientation counterclockwise
                            part.rotation = (part.rotation + 1) % 4
                        # After rotation, calculate new center and translate to keep it fixed
                        new_min_x = min(part.grid_x for part in self.selected_parts)
                        new_max_x = max(part.grid_x for part in self.selected_parts)
                        new_min_y = min(part.grid_y for part in self.selected_parts)
                        new_max_y = max(part.grid_y for part in self.selected_parts)
                        new_cx = (new_min_x + new_max_x) // 2
                        new_cy = (new_min_y + new_max_y) // 2
                        # Translate all parts to align new center with initial center
                        shift_x = round(cx - new_cx)
                        shift_y = round(cy - new_cy)
                        for part in self.selected_parts:
                            part.grid_x += shift_x
                            part.grid_y += shift_y
                else:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    grid_x, grid_y = self.screen_to_grid(mouse_x, mouse_y)
                    # Rotate the part at this position
                    for layer in self.parts_in_grid:
                        for part in layer:
                            if part.grid_x == grid_x and part.grid_y == grid_y:
                                part.rotation = (part.rotation - 1) % 4
                                break
            elif event.key == pygame.K_t: 
                if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                    # Flip selected building horizontally (180 degrees along x)
                    if self.selected_parts:
                        # Calculate center of selected parts
                        min_x = min(part.grid_x for part in self.selected_parts)
                        max_x = max(part.grid_x for part in self.selected_parts)
                        cx = (min_x + max_x) // 2
                    # Flip positions horizontally and adjust orientations
                    for part in self.selected_parts:
                        # Reflect over vertical axis through center
                        part.grid_x = round(2 * cx - part.grid_x)
                        # Adjust orientation for horizontal flip
                        if part.object_id in [33, 34, 35, 36]:
                            # Toggle mirror for mirrorable parts
                            part.mirror = not part.mirror
                        if part.object_id in [12,13,14,15,16,17,18,37]:
                            part.rotation = (4 - part.rotation) % 4 + 2
                        else:
                            part.rotation = (4 - part.rotation) % 4 
                    # After flip, calculate new center and translate to keep it fixed
                    new_min_x = min(part.grid_x for part in self.selected_parts)
                    new_max_x = max(part.grid_x for part in self.selected_parts)
                    new_cx = (new_min_x + new_max_x) // 2
                    # Translate all parts to align new center with initial center
                    shift_x = round(cx - new_cx)
                    for part in self.selected_parts:
                        part.grid_x += shift_x
                else:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    grid_x, grid_y = self.screen_to_grid(mouse_x, mouse_y)
                    # Mirror the part at this position
                    for layer in self.parts_in_grid:
                        for part in layer:
                            if part.grid_x == grid_x and part.grid_y == grid_y and part.object_id in [33, 34, 35, 36]:
                                part.mirror = not part.mirror
                                break
            elif event.key == pygame.K_c and pygame.key.get_mods() & pygame.KMOD_CTRL:
                # Copy selected parts
                self.copied_parts = []
                if self.selected_parts:
                    min_x = min(part.grid_x for part in self.selected_parts)
                    min_y = min(part.grid_y for part in self.selected_parts)
                    for part in self.selected_parts:
                        # Store relative positions
                        self.copied_parts.append((part.object_id, part.grid_x - min_x, part.grid_y - min_y, part.rotation, part.layer, part.mirror, part.skin))
            elif event.key == pygame.K_v and pygame.key.get_mods() & pygame.KMOD_CTRL:
                # Paste copied parts
                if self.copied_parts:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    base_grid_x, base_grid_y = self.screen_to_grid(mouse_x, mouse_y)
                    for obj_id, rel_x, rel_y, rot, layer, mirror, skin in self.copied_parts:
                        new_grid_x = base_grid_x + rel_x
                        new_grid_y = base_grid_y + rel_y
                        # Check if position is free
                        if not any(part.grid_x == new_grid_x and part.grid_y == new_grid_y for part in self.parts_in_grid[layer]):
                            new_part = Part(new_grid_x, new_grid_y, obj_id, layer, rot, mirror, skin)
                            self.parts_in_grid[layer].append(new_part)
            elif event.key == pygame.K_DELETE:
                if self.selected_parts:
                    for layer in range(len(self.parts_in_grid)):
                        self.parts_in_grid[layer] = [part for part in self.parts_in_grid[layer] if not ( part in self.selected_parts)]

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_w:
                self.moving_up = False
            if event.key == pygame.K_s:
                self.moving_down = False
            if event.key == pygame.K_a:
                self.moving_left = False
            if event.key == pygame.K_d:
                self.moving_right = False
            if event.key == pygame.K_UP:
                self.zooming_in = False
            if event.key == pygame.K_DOWN:
                self.zooming_out = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                mouse_x, mouse_y = event.pos
                if pygame.key.get_mods() & pygame.KMOD_CTRL:
                    # Start selection
                    self.selecting = True
                    self.selection_start = (mouse_x, mouse_y)
                    self.selected_parts = []
                else:
                    grid_x, grid_y = self.screen_to_grid(mouse_x, mouse_y)
                    # Check if clicking on a selected part to start dragging
                    clicked_part = None
                    for part in self.selected_parts:
                        if part.grid_x == grid_x and part.grid_y == grid_y:
                            clicked_part = part
                            break
                    if clicked_part:
                        self.dragging = True
                        self.drag_start_grid = (grid_x, grid_y)
                        self.drag_initial_positions = [(part.grid_x, part.grid_y) for part in self.selected_parts]
                    else:
                        layer = 0 if selected_part_id in [5, 6] else 1
                        # Check if there's already a part at this position on the layer
                        if not any(part.grid_x == grid_x and part.grid_y == grid_y for part in self.parts_in_grid[layer]):
                            # Create a new part at the clicked cell using selected_part_id
                            new_part = Part(grid_x, grid_y, selected_part_id, layer, skin=selected_skin)
                            self.parts_in_grid[layer].append(new_part)

            elif event.button == 3:  # Right mouse button
                mouse_x, mouse_y = event.pos
                grid_x, grid_y = self.screen_to_grid(mouse_x, mouse_y)
                # Remove parts at the clicked cell from all layers
                for layer in range(len(self.parts_in_grid)):
                    self.parts_in_grid[layer] = [part for part in self.parts_in_grid[layer] if not (part.grid_x == grid_x and part.grid_y == grid_y)]
        elif event.type == pygame.MOUSEMOTION:
            mouse_x, mouse_y = event.pos
            if self.selecting:
                start_x, start_y = self.selection_start
                self.selection_rect = pygame.Rect(min(start_x, mouse_x), min(start_y, mouse_y), abs(mouse_x - start_x), abs(mouse_y - start_y))
            elif self.dragging:
                current_grid_x, current_grid_y = self.screen_to_grid(mouse_x, mouse_y)
                dx = current_grid_x - self.drag_start_grid[0]
                dy = current_grid_y - self.drag_start_grid[1]
                for i, part in enumerate(self.selected_parts):
                    initial_x, initial_y = self.drag_initial_positions[i]
                    part.grid_x = initial_x + dx
                    part.grid_y = initial_y + dy
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                if self.selecting:
                    mouse_x, mouse_y = event.pos
                    start_x, start_y = self.selection_start
                    min_x = min(start_x, mouse_x)
                    max_x = max(start_x, mouse_x)
                    min_y = min(start_y, mouse_y)
                    max_y = max(start_y, mouse_y)
                    start_grid_x, start_grid_y = self.screen_to_grid(min_x, min_y)
                    end_grid_x, end_grid_y = self.screen_to_grid(max_x, max_y)
                    for layer in self.parts_in_grid:
                        for part in layer:
                            if start_grid_x <= part.grid_x <= end_grid_x and start_grid_y <= part.grid_y <= end_grid_y:
                                if part not in self.selected_parts:
                                    self.selected_parts.append(part)
                    self.selecting = False
                    self.selection_rect = None
                elif self.dragging:
                    self.dragging = False
                    self.drag_start_grid = None
                    self.drag_initial_positions = None

if __name__ == "__main__":
   app = App()
   app.run()
