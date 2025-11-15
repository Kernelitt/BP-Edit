import math,random,os,json,pygame
import tkinter as tk
from tkinter import ttk


class SimpleFW:
    def __init__(self,key=b'aVV1rKC-_l1OxB2ym3AwR-FsHDW79OJnPr-Ppcr9W9w=',save_base=dict()):
        try:
            from cryptography.fernet import Fernet
            self.key = key  # Замените на ваш сгенерированный ключ
            self.cipher = Fernet(self.key)          
            self.save_base = dict(save_base)
        except Exception as e:
            print("error SimpleFW __init__() --",e)

    def generate_name(self,lenght):
        letters = "ABCDEFGHJKLMNOPQRSTUVWXYZ"
        ret_str = str("")
        for i in range(lenght):
            ret_str += str(random.choice(letters))
        return f"{ret_str}-{random.randint(1000, 9999)}"
    
    def random_color(self):
        return (random.randint(0,255),random.randint(0,255),random.randint(0,255))
    
    def screen_dif(self,width1,height1,width2,height2):
        return [round((width1 / width2),1),round((height1 / height2),1)]    

    def load_data(self):
        try:
            if os.path.exists("save_data.data"):
                with open("save_data.data", 'rb') as f:
                    encrypted_data = f.read()
                    decrypted_data = self.cipher.decrypt(encrypted_data)
                    return json.loads(decrypted_data)
            else:  
                return self.save_base
        except Exception as e:
            print("error SimpleFW load_data() --",e)

    def save_data(self, data):
        try:
            existing_data = self.load_data()

            for key, value in data.items():
                if isinstance(value, dict):
                    existing_data[key] = existing_data.get(key, {})
                    existing_data[key].update(value)
                else:
                    existing_data[key] = value
            json_data = json.dumps(existing_data).encode()
            encrypted_data = self.cipher.encrypt(json_data)
            with open("save_data.data", 'wb') as f:
                f.write(encrypted_data)
        except Exception as e:
            print("error SimpleFW save_data() -",e)

class SimpleNoise:
    def __init__(self, seed=None):
        self.seed = seed if seed is not None else random.randint(0, 999999)
        
    def noise(self, x, y=0):
        x = x * 0.1
        y = y * 0.1
        value = math.sin(x * 127.1 + y * 311.7 + self.seed) * 43758.5453
        return value - math.floor(value)
    
class SimpleCamera:
    def __init__(self,x=0,y=0,smoothness=0,speed=2,cameramove=False):
        self.x = x
        self.y = y
        self.target_x = 0
        self.target_y = 0
        self.smoothness = smoothness
        self.speed = speed
        self.cameramove = cameramove
    
    def update(self, target_x, target_y):
        self.target_x = target_x
        self.target_y = target_y
        self.x += (self.target_x - self.x) * self.smoothness
        self.y += (self.target_y - self.y) * self.smoothness
        if self.cameramove:
            for event in pygame.event.get():
                if event.key == pygame.K_LEFT:
                    self.x -= self.speed
                elif event.key == pygame.K_RIGHT:
                    self.x += self.speed
                elif event.key == pygame.K_UP:
                    self.y -= self.speed
                elif event.key == pygame.K_DOWN:
                    self.y += self.speed
        else:
            pass #закреплённая камера

    def get_pos(self):
        return (self.x, self.y)
    
class SimplePygameButton:
    def __init__(self, position, size, texts, action, color, pre_action=None, texture=None):
        self.position = position  # (x, y)
        self.size = size  # (width, height)
        self.texts = texts
        self.action = action
        self.color = color
        self.texture = texture
        self.click_start = False
        self.pre_action = pre_action

    def draw(self, window, font):
        if self.texture:
            texture_scaled = pygame.transform.scale(self.texture, self.size)
            window.blit(texture_scaled, self.position)
        else:
            pygame.draw.rect(window, self.color, (self.position[0], self.position[1], self.size[0], self.size[1]))
        for i, (text, offset) in enumerate(self.texts):
            text_surface = font.render(text, True, (255, 255, 255))
            window.blit(text_surface, (self.position[0] + offset[0], self.position[1] + offset[1]))

        pos = pygame.mouse.get_pos()
        if self.position[0] < pos[0] < self.position[0] + self.size[0] and self.position[1] < pos[1] < self.position[1] + self.size[1] and self.pre_action != None:
            self.pre_action()

    def update(self, event):
        if event.type == pygame.MOUSEBUTTONUP:
            self.click_start = False
            if self.position[0] < event.pos[0] < self.position[0] + self.size[0] and self.position[1] < event.pos[1] < self.position[1] + self.size[1]:
                self.action()

class SimplePygameSlider:
    def __init__(self, position, size, min_value, max_value, start_value, color_bg, color_fg, knob_color, action=None):
        self.position = position  # (x, y)
        self.size = size  # (width, height)
        self.min_value = min_value
        self.max_value = max_value
        self.value = start_value
        self.color_bg = color_bg
        self.color_fg = color_fg
        self.knob_color = knob_color
        self.action = action
        self.dragging = False
        self.knob_radius = self.size[1] // 2

    def draw(self, window,font=None):
        # Draw background bar
        pygame.draw.rect(window, self.color_bg, (self.position[0], self.position[1] + self.size[1] // 4, self.size[0], self.size[1] // 2))
        # Calculate knob position
        knob_x = self.position[0] + int((self.value - self.min_value) / (self.max_value - self.min_value) * self.size[0])
        knob_y = self.position[1] + self.size[1] // 2
        # Draw foreground bar
        pygame.draw.rect(window, self.color_fg, (self.position[0], self.position[1] + self.size[1] // 4, knob_x - self.position[0], self.size[1] // 2))
        # Draw knob
        pygame.draw.circle(window, self.knob_color, (knob_x, knob_y), self.knob_radius)

    def update(self, event):
        pos = pygame.mouse.get_pos()
        knob_x = self.position[0] + int((self.value - self.min_value) / (self.max_value - self.min_value) * self.size[0])
        knob_y = self.position[1] + self.size[1] // 2
        dist = math.hypot(pos[0] - knob_x, pos[1] - knob_y)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if dist <= self.knob_radius:
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.dragging and self.action:
                self.action(self.value)
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                # Clamp position within slider range
                new_x = max(self.position[0], min(pos[0], self.position[0] + self.size[0]))
                # Update value based on knob position
                self.value = self.min_value + (new_x - self.position[0]) / self.size[0] * (self.max_value - self.min_value)
                if self.action:
                    self.action(self.value)

    def get_value(self):
        return self.value


class SimpleSettingsWindow:
    def __init__(self):
        self.settings = {'width': 800, 'height': 600, 'aspect': '4:3'}
        self.resolutions = {
            '4:3': ['640x480', '800x600', '1024x768', '1280x960'],
            '16:9': ['1280x720', '1366x768', '1600x900', '1920x1080']
        }

    def run(self):
        root = tk.Tk()
        root.title("Pre-Launch Settings")
        root.geometry("300x250")

        tk.Label(root, text="Screen Format:").grid(column=0,row=0)
        aspect_var = tk.StringVar(value=self.settings['aspect'])
        aspect_combo = ttk.Combobox(root, textvariable=aspect_var, values=['4:3', '16:9'])
        aspect_combo.grid(column=1,row=0)

        tk.Label(root, text="Screen Resolution:").grid(column=0,row=1)
        res_var = tk.StringVar(value='800x600')
        res_combo = ttk.Combobox(root, textvariable=res_var, values=self.resolutions[aspect_var.get()])
        res_combo.grid(column=1,row=1,pady=5)

        def update_resolutions(*args):
            res_combo['values'] = self.resolutions[aspect_var.get()]
            res_combo.set(self.resolutions[aspect_var.get()][0])  # Set to first option

        aspect_var.trace('w', update_resolutions)

        def start_program():
            res = res_var.get()
            if 'x' in res:
                w, h = res.split('x')
                try:
                    self.settings['width'] = int(w)
                    self.settings['height'] = int(h)
                    self.settings['aspect'] = aspect_var.get()
                    root.destroy()
                except ValueError:
                    pass

        tk.Button(root, text="Launch", command=start_program).grid(column=1,row=2,pady=20)

        root.mainloop()
        return self.settings


class SimpleWindowScaler:
    def __init__(self, base_width, base_height, current_width, current_height):
        self.base_width = base_width
        self.base_height = base_height
        self.current_width = current_width
        self.current_height = current_height
        self.scale_x_factor = current_width / base_width
        self.scale_y_factor = current_height / base_height

    def scale_x(self, x):
        return int(x * self.scale_x_factor)

    def scale_y(self, y):
        return int(y * self.scale_y_factor)

    def scale(self, x, y):
        return self.scale_x(x), self.scale_y(y)


class SimplePygameField:
    def __init__(self, position, size, bg_color=(200, 200, 200), bg_image=None):
        self.position = position  # (x, y)
        self.size = size  # (width, height)
        self.bg_color = bg_color
        self.bg_image = bg_image
        self.elements = []
        self.texts = []  # list of (text, pos, color)

    def add_element(self, element):
        self.elements.append(element)

    def add_text(self, text, pos, color=(0, 0, 0)):
        self.texts.append((text, pos, color))

    def draw(self, window, font):
        # Draw background
        if self.bg_image:
            bg_scaled = pygame.transform.scale(self.bg_image, self.size)
            window.blit(bg_scaled, self.position)
        else:
            pygame.draw.rect(window, self.bg_color, (self.position[0], self.position[1], self.size[0], self.size[1]))

        # Draw texts
        for text, pos, color in self.texts:
            text_surface = font.render(text, True, color)
            window.blit(text_surface, (self.position[0] + pos[0], self.position[1] + pos[1]))

        # Draw elements
        for element in self.elements:
            element.draw(window,font)

    def update(self, event):
        for element in self.elements:
            if hasattr(element,"update"):
                element.update(event)


class SimplePygameContextMenu:
    def __init__(self, options, font_size=24, bg_color=(255, 255, 255), text_color=(0, 0, 0), hover_color=(200, 200, 200)):
        self.options = options  # list of (text, action) tuples
        self.font_size = font_size
        self.bg_color = bg_color
        self.text_color = text_color
        self.hover_color = hover_color
        self.visible = False
        self.position = (0, 0)
        self.hovered_index = -1
        self.item_height = font_size + 10
        self.padding = 10

    def show(self, x, y):
        self.position = (x, y)
        self.visible = True
        self.hovered_index = -1

    def hide(self):
        self.visible = False
        self.hovered_index = -1

    def draw(self, window, font):
        if not self.visible:
            return
        num_options = len(self.options)
        menu_width = max(len(text) for text, _ in self.options) * (self.font_size // 2) + 2 * self.padding
        menu_height = num_options * self.item_height + 2 * self.padding
        pygame.draw.rect(window, self.bg_color, (self.position[0], self.position[1], menu_width, menu_height))
        pygame.draw.rect(window, (0, 0, 0), (self.position[0], self.position[1], menu_width, menu_height), 2)  # border
        for i, (text, _) in enumerate(self.options):
            item_rect = (self.position[0] + self.padding, self.position[1] + self.padding + i * self.item_height, menu_width - 2 * self.padding, self.item_height)
            if i == self.hovered_index:
                pygame.draw.rect(window, self.hover_color, item_rect)
            text_surface = font.render(text, True, self.text_color)
            window.blit(text_surface, (item_rect[0] + 5, item_rect[1] + 5))

    def update(self, event):
        if not self.visible:
            return
        pos = pygame.mouse.get_pos()
        num_options = len(self.options)
        menu_width = max(len(text) for text, _ in self.options) * (self.font_size // 2) + 2 * self.padding
        menu_height = num_options * self.item_height + 2 * self.padding
        menu_rect = pygame.Rect(self.position[0], self.position[1], menu_width, menu_height)
        if menu_rect.collidepoint(pos):
            self.hovered_index = (pos[1] - self.position[1] - self.padding) // self.item_height
            if self.hovered_index >= num_options:
                self.hovered_index = -1
        else:
            self.hovered_index = -1
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:  # left click
            if self.hovered_index >= 0 and self.hovered_index < num_options:
                _, action = self.options[self.hovered_index]
                action()
            self.hide()
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 3:  # right click outside
            if not menu_rect.collidepoint(pos):
                self.hide()


class SimplePygameProgressBar:
    def __init__(self, position, size, min_value=0, max_value=100, start_value=0, bg_color=(200, 200, 200), fg_color=(0, 255, 0), fg_color2=None, border_color=(0, 0, 0)):
        self.position = position  # (x, y)
        self.size = size  # (width, height)
        self.min_value = min_value
        self.max_value = max_value
        self.value = start_value
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.fg_color2 = fg_color2  # Second color for two-color style
        self.border_color = border_color

    def set_value(self, value):
        self.value = max(self.min_value, min(self.max_value, value))

    def draw(self, window,font):
        # Draw background
        pygame.draw.rect(window, self.bg_color, (self.position[0], self.position[1], self.size[0], self.size[1]))
        # Draw foreground based on value
        progress_width = int((self.value - self.min_value) / (self.max_value - self.min_value) * self.size[0])
        if self.fg_color2 and progress_width > 0:
            # Two-color style: top half fg_color, bottom half fg_color2
            half_height = self.size[1] // 2
            pygame.draw.rect(window, self.fg_color, (self.position[0], self.position[1], progress_width, half_height))
            pygame.draw.rect(window, self.fg_color2, (self.position[0], self.position[1] + half_height, progress_width, self.size[1] - half_height))
        else:
            pygame.draw.rect(window, self.fg_color, (self.position[0], self.position[1], progress_width, self.size[1]))
        # Draw border
        pygame.draw.rect(window, self.border_color, (self.position[0], self.position[1], self.size[0], self.size[1]), 2)


class SimplePygameInputField:
    def __init__(self, position, size, font, max_length=100, bg_color=(255, 255, 255), text_color=(0, 0, 0), border_color=(0, 0, 0), placeholder=""):
        self.position = position  # (x, y)
        self.size = size  # (width, height)
        self.font = font
        self.max_length = max_length
        self.bg_color = bg_color
        self.text_color = text_color
        self.border_color = border_color
        self.placeholder = placeholder
        self.text = ""
        self.active = False
        self.cursor_visible = True
        self.cursor_timer = 0

    def set_text(self, text):
        self.text = text[:self.max_length]

    def get_text(self):
        return self.text

    def draw(self, window,font):
        # Draw background
        pygame.draw.rect(window, self.bg_color, (self.position[0], self.position[1], self.size[0], self.size[1]))
        # Draw border
        pygame.draw.rect(window, self.border_color, (self.position[0], self.position[1], self.size[0], self.size[1]), 2)

        # Draw text
        display_text = self.text if self.text else self.placeholder
        text_color = self.text_color if self.text else (150, 150, 150)
        text_surface = self.font.render(display_text, True, text_color)
        window.blit(text_surface, (self.position[0] + 5, self.position[1] + (self.size[1] - text_surface.get_height()) // 2))

        # Draw cursor if active
        if self.active and self.cursor_visible:
            cursor_x = self.position[0] + 5 + text_surface.get_width()
            cursor_y = self.position[1] + (self.size[1] - text_surface.get_height()) // 2
            pygame.draw.line(window, self.text_color, (cursor_x, cursor_y), (cursor_x, cursor_y + text_surface.get_height()), 2)

    def update(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.position[0] < event.pos[0] < self.position[0] + self.size[0] and self.position[1] < event.pos[1] < self.position[1] + self.size[1]:
                self.active = True
            else:
                self.active = False
        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                self.active = False
            elif len(self.text) < self.max_length:
                self.text += event.unicode
        elif event.type == pygame.USEREVENT:  # For cursor blinking
            self.cursor_visible = not self.cursor_visible


class SimplePygameCheckbox:
    def __init__(self, position, size, text, font, checked=False, bg_color=(255, 255, 255), box_color=(200, 200, 200), check_color=(0, 0, 0), text_color=(0, 0, 0), border_color=(0, 0, 0), action=None):
        self.position = position  # (x, y)
        self.size = size  # (width, height)
        self.text = text
        self.font = font
        self.checked = checked
        self.bg_color = bg_color
        self.box_color = box_color
        self.check_color = check_color
        self.text_color = text_color
        self.border_color = border_color
        self.action = action
        self.rect = pygame.Rect(position[0], position[1], size[0], size[1])

    def draw(self, window,font):
        # Draw background
        pygame.draw.rect(window, self.bg_color, self.rect)
        # Draw box
        box_size = self.size[1] - 10
        box_rect = pygame.Rect(self.position[0] + 5, self.position[1] + 5, box_size, box_size)
        pygame.draw.rect(window, self.box_color, box_rect)
        pygame.draw.rect(window, self.border_color, box_rect, 2)
        # Draw check mark if checked
        if self.checked:
            pygame.draw.line(window, self.check_color, (box_rect.left + 3, box_rect.centery), (box_rect.centerx, box_rect.bottom - 3), 3)
            pygame.draw.line(window, self.check_color, (box_rect.centerx, box_rect.bottom - 3), (box_rect.right - 3, box_rect.top + 3), 3)
        # Draw text
        text_surface = self.font.render(self.text, True, self.text_color)
        window.blit(text_surface, (self.position[0] + box_size + 10, self.position[1] + (self.size[1] - text_surface.get_height()) // 2))

    def update(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.checked = not self.checked
                if self.action:
                    self.action(self.checked)







