import pygame
import sys
import math
import random
import os
import time

# =====================================================================
# ЧАСТЬ 1: СИСТЕМНЫЕ НАСТРОЙКИ, ИНТЕРФЕЙС И ТУТОРИАЛ
# =====================================================================
pygame.init()
pygame.font.init()

# Автоматически определяем разрешение твоего монитора для полного экрана
infoObject = pygame.display.Info()
WIDTH = infoObject.current_w
HEIGHT = infoObject.current_h

screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Winion Life Simulator - Сохранение Времени")
clock = pygame.time.Clock()

FONT = pygame.font.SysFont("Arial", 16)
BIG_FONT = pygame.font.SysFont("Arial", 22)
TEXT_COLOR = (240, 240, 240)
PANEL_COLOR = (35, 38, 50)

# Безопасное сохранение в "Документы"
user_documents = os.path.join(os.environ.get('USERPROFILE', ''), 'Documents')
SAVE_DIR = os.path.join(user_documents, 'WinionLife_Saves')
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

# Данные предметов и рецепты
ITEM_TYPES = {
    "Яблоко": {"color": (255, 90, 50), "nutr": 35},
    "Вода": {"color": (50, 150, 255), "nutr": 10},
    "Мука": {"color": (220, 220, 200), "nutr": 5},
    "Ягода": {"color": (200, 30, 100), "nutr": 20},
    "Тесто": {"color": (240, 210, 160), "nutr": 15},
    "Пирог": {"color": (150, 75, 0), "nutr": 80}
}

RECIPES = {
    ("Вода", "Мука"): "Тесто",
    ("Мука", "Вода"): "Тесто",
    ("Тесто", "Ягода"): "Пирог",
    ("Ягода", "Тесто"): "Пирог",
    ("Тесто", "Яблоко"): "Пирог",
    ("Яблоко", "Тесто"): "Пирог"
}

def draw_custom_cursor(surface, pos):
    x, y = pos
    pygame.draw.circle(surface, (0, 255, 200), (x, y + 10), 12, 1)
    pygame.draw.line(surface, (0, 255, 200), (x - 18, y + 10), (x + 18, y + 10), 1)
    pygame.draw.line(surface, (0, 255, 200), (x, y - 8), (x, y + 28), 1)
    pygame.draw.polygon(surface, (230, 190, 150), [(x, y + 3), (x - 5, y + 12), (x + 5, y + 12)])
    pygame.draw.circle(surface, (255, 50, 50), (x, y), 3)

def draw_background_textures(surface):
    surface.fill((28, 33, 46))
    for x in range(0, WIDTH, 32):
        for y in range(0, HEIGHT, 32):
            if (x + y) % 64 == 0:
                pygame.draw.rect(surface, (32, 38, 53), (x, y, 32, 32))
    kitchen_zone = pygame.Rect(WIDTH - 300, 0, 300, 350)
    pygame.draw.rect(surface, (115, 74, 44), kitchen_zone)
    for y in range(0, 350, 25):
        pygame.draw.line(surface, (80, 48, 25), (WIDTH - 300, y), (WIDTH, y), 1)
    for x in range(WIDTH - 300, WIDTH, 50):
        pygame.draw.line(surface, (80, 48, 25), (x, 0), (x, 350), 1)
    pygame.draw.line(surface, (140, 140, 150), (WIDTH - 300, 0), (WIDTH - 300, 350), 2)
    pygame.draw.line(surface, (140, 140, 150), (WIDTH - 300, 350), (WIDTH, 350), 2)

class ContextMenu:
    def __init__(self, x, y, options):
        self.x = x
        self.y = y
        self.options = options
        self.width = 160
        self.height = len(options) * 28

    def draw(self, surface):
        draw_x = min(self.x, WIDTH - self.width)
        draw_y = min(self.y, HEIGHT - self.height)
        pygame.draw.rect(surface, (50, 52, 70), (draw_x, draw_y, self.width, self.height), 0, 4)
        pygame.draw.rect(surface, (90, 95, 120), (draw_x, draw_y, self.width, self.height), 1, 4)
        for i, opt in enumerate(self.options):
            t = FONT.render(opt, True, TEXT_COLOR)
            surface.blit(t, (draw_x + 10, draw_y + 6 + (i * 28)))

    def get_choice(self, m_pos):
        mx, my = m_pos
        draw_x = min(self.x, WIDTH - self.width)
        draw_y = min(self.y, HEIGHT - self.height)
        if draw_x <= mx <= draw_x + self.width:
            if draw_y <= my <= draw_y + self.height:
                return self.options[(my - draw_y) // 28]
        return None

class TutorialWindow:
    def __init__(self):
        self.step = 0
        self.width = 450
        self.height = 140
        self.x = WIDTH // 2 - self.width // 2
        self.y = HEIGHT // 2 - self.height // 2
        self.active = True
        self.messages = [
            "Привет! Давай вырастим Иона с сохранением времени. Нажми 'Далее'.",
            "ШАГ 1: Кликни ПКМ (правой кнопкой) на ковре, выбери Воду, а затем Муку.",
            "ШАГ 2: Нажми ЛКМ по предмету и выбери 'Положить на Кухню'. Отнеси оба.",
            "ШАГ 3: Нажми ЛКМ по Столу кухни -> 'Приготовить'. Скрафти Тесто!",
            "УРА! Таймер яйца теперь записывается на диск и никогда не сбросится!"
        ]

    def draw(self, surface):
        if not self.active: return
        pygame.draw.rect(surface, (30, 45, 60), (self.x, self.y, self.width, self.height), 0, 8)
        pygame.draw.rect(surface, (0, 255, 200), (self.x, self.y, self.width, self.height), 2, 8)
        surface.blit(BIG_FONT.render("🎓 ОБУЧЕНИЕ:", True, (0, 255, 200)), (self.x + 20, self.y + 15))
        surface.blit(FONT.render(self.messages[self.step], True, TEXT_COLOR), (self.x + 20, self.y + 50))
        self.btn_rect = pygame.Rect(self.x + self.width - 120, self.y + self.height - 45, 100, 30)
        pygame.draw.rect(surface, (0, 180, 140), self.btn_rect, 0, 4)
        surface.blit(FONT.render("Далее", True, TEXT_COLOR), (self.x - 95 + self.width, self.y + self.height - 40))

    def check_click(self, m_pos):
        if not self.active: return False
        if self.btn_rect.collidepoint(m_pos):
            if self.step < len(self.messages) - 1: self.step += 1
            else: self.active = False
            return True
        return False
# =====================================================================
# ЧАСТЬ 2: ОБЪЕКТЫ, КЛАСС ИОНА И УМНОЕ СОХРАНЕНИЕ ТАЙМЕРА
# =====================================================================

class Item:
    def __init__(self, x, y, name="Яблоко"):
        self.x = x
        self.y = y
        self.name = name
        self.radius = 12
        self.is_forbidden = False

    def draw(self, surface):
        color = (200, 50, 50) if self.is_forbidden else ITEM_TYPES.get(self.name, {"color": (255,90,50)})["color"]
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), self.radius)
        status = " (НЕЛЬЗЯ!)" if self.is_forbidden else ""
        surface.blit(FONT.render(f"{self.name}{status}", True, TEXT_COLOR), (self.x - 25, self.y - 30))

class Egg:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius_w = 22
        self.radius_h = 30
        self.total_seconds = 300 # 5 минут реального времени
        
        # Путь к файлу сохранения таймера на диске
        self.timer_file = os.path.join(SAVE_DIR, "egg_timer.txt")
        
        # Если файл уже есть — считываем, сколько времени осталось
        if os.path.exists(self.timer_file):
            try:
                with open(self.timer_file, "r") as f:
                    saved_time = float(f.read().strip())
                # Считаем, сколько секунд прошло с момента закрытия игры
                elapsed = time.time() - saved_time
                self.time_left = max(0.0, self.total_seconds - elapsed)
            except:
                self.time_left = self.total_seconds
        else:
            self.time_left = self.total_seconds
            self.save_time_to_disk()

        self.sprite = None
        path = os.path.join("ion_animate", "egg_ion.png")
        if os.path.exists(path):
            self.sprite = pygame.transform.scale(pygame.image.load(path).convert_alpha(), (self.radius_w * 2, self.radius_h * 2))

    def save_time_to_disk(self):
        """Запоминаем текущее системное время Windows"""
        try:
            with open(self.timer_file, "w") as f:
                # Записываем сколько секунд осталось до вылупления
                f.write(str(time.time() - (self.total_seconds - self.time_left)))
        except: pass

    def update(self):
        # Каждую секунду вычитаем время (1 кадр при 60 FPS = 1/60 секунды)
        if self.time_left > 0:
            self.time_left -= 1.0 / 60.0
            # Раз в секунду обновляем файл сохранения времени
            if random.random() < 0.01:
                self.save_time_to_disk()
            return False
        else:
            # Время вышло! Удаляем временный файл таймера
            if os.path.exists(self.timer_file):
                try: os.remove(self.timer_file)
                except: pass
            return True # Сигнал к вылуплению

    def draw(self, surface):
        if self.sprite: surface.blit(self.sprite, (self.x - self.radius_w, self.y - self.radius_h))
        else:
            pygame.draw.ellipse(surface, (245, 215, 120), pygame.Rect(self.x-self.radius_w, self.y-self.radius_h, self.radius_w*2, self.radius_h*2))
        
        progress = max(0.0, min(1.0, 1.0 - (self.time_left / self.total_seconds)))
        minutes = max(0, int(self.time_left // 60))
        seconds = max(0, int(self.time_left % 60))
        
        pygame.draw.rect(surface, (40, 40, 50), (self.x - 30, self.y - 45, 60, 6))
        pygame.draw.rect(surface, (0, 255, 150), (self.x - 30, self.y - 45, int(60 * progress), 6))
        surface.blit(FONT.render(f"{minutes:02d}:{seconds:02d}", True, (255, 255, 255)), (self.x - 15, self.y - 65))

def check_mouse_gestures(mouse_history, current_item, winions):
    if not current_item or len(mouse_history) < 40: return
    x_crossings = 0
    near_item = True
    for i in range(1, len(mouse_history)):
        mx, my = mouse_history[i]
        prev_mx, _ = mouse_history[i-1]
        if math.hypot(mx - current_item.x, my - current_item.y) > 100:
            near_item = False
            break
        if (prev_mx < current_item.x and mx > current_item.x) or (prev_mx > current_item.x and mx < current_item.x):
            x_crossings += 1
    if near_item and x_crossings >= 4:
        current_item.is_forbidden = True
        for w in winions:
            if w.alive:
                w.thoughts = "Запретили брать..."
                w.brain[400] = min(1.0, w.brain[400] + 0.4)
        mouse_history.clear()
        return
    l = sum(1 for p in mouse_history if p[0] < current_item.x)
    r = sum(1 for p in mouse_history if p[0] > current_item.x)
    u = sum(1 for p in mouse_history if p[1] < current_item.y)
    d = sum(1 for p in mouse_history if p[1] > current_item.y)
    if l > 8 and r > 8 and u > 8 and d > 8:
        current_item.is_forbidden = False
        for w in winions:
            if w.alive:
                w.target_x, w.target_y = current_item.x, current_item.y
                w.thoughts = "Разрешили! Бегу кушать!"
                w.brain[300] = min(1.0, w.brain[300] + 0.3)
        mouse_history.clear()

class KitchenTable:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 160
        self.height = 100
        self.slots = []

    def draw(self, surface):
        pygame.draw.rect(surface, (140, 90, 55), (self.x, self.y, self.width, self.height), 0, 6)
        pygame.draw.rect(surface, (230, 230, 240), (self.x + 5, self.y + 5, self.width - 10, self.height - 10), 0, 4)
        surface.blit(FONT.render("РАЗДЕЛОЧНЫЙ СТОЛ", True, (60, 40, 20)), (self.x + 10, self.y + 10))
        surface.blit(FONT.render(f"Внутри: {', '.join(self.slots) if self.slots else 'Пусто'}", True, (80, 80, 90)), (self.x + 10, self.y + 45))

class Winion:
    def __init__(self, x, y, name=None):
        self.x = x
        self.y = y
        self.target_x = x
        self.target_y = y
        self.radius = 18
        self.max_radius = 35
        self.speed = 2.2
        self.alive = True
        self.name = name if name else f"Ион_{random.randint(100, 999)}"
        self.age, self.hunger = 0, 20
        self.thoughts = "Привет! Я родился!"
        self.punishment_mode = None
        self.animation_frame = 0
        self.is_moving = False
        self.brain = [random.uniform(-1.0, 1.0) for _ in range(1000)]
        self.brain[100] = 0.5  # Инстинкт голода
        self.brain[400] = 0.1  # Инстинкт послушания
        self.folder_path = os.path.join(SAVE_DIR, self.name)
        if not os.path.exists(self.folder_path): os.makedirs(self.folder_path)
        self.save_to_folder()

    def save_to_folder(self):
        try:
            with open(os.path.join(self.folder_path, "stats.txt"), "w", encoding="utf-8") as f:
                f.write(f"Name: {self.name}\nAge: {self.age:.2f}\nHunger: {self.hunger:.2f}\n")
            with open(os.path.join(self.folder_path, "brain.txt"), "w") as f:
                f.write(",".join(map(str, self.brain)))
        except: pass

    def update(self, mouse_pos, current_item):
        if not self.alive: return False
        self.age += 0.02
        self.hunger += 0.01
        if self.radius < self.max_radius and int(self.age) % 5 == 0: self.radius += 0.08
        if self.hunger >= 100:
            self.alive = False
            self.thoughts = "Умер от голода..."
            return False
        if self.punishment_mode == "corner":
            self.thoughts = "В углу..."
            self.target_x, self.target_y = 50, 50
            self.move_towards_target()
            return False

        if current_item:
            food_drive = self.hunger * self.brain[100]
            inhibition = self.brain[400] * 60 if current_item.is_forbidden else 0.0
            if food_drive > inhibition:
                self.target_x, self.target_y = current_item.x, current_item.y
                self.thoughts = "Голод сильнее, ем!" if current_item.is_forbidden else "Иду кушать!"
                if math.hypot(current_item.x - self.x, current_item.y - self.y) < self.radius + current_item.radius:
                    self.hunger = max(0, self.hunger - ITEM_TYPES.get(current_item.name, {"nutr": 20})["nutr"])
                    self.thoughts = f"Съел {current_item.name}."
                    return True
            else: self.thoughts = "Нельзя трогать еду..."
        else:
            if random.random() < 0.01:
                self.target_x = random.randint(80, WIDTH - 350)
                self.target_y = random.randint(80, HEIGHT - 160)
                self.thoughts = "Исследую ковролин..."
        self.move_towards_target()
        return False

    def move_towards_target(self):
        dx, dy = self.target_x - self.x, self.target_y - self.y
        dist = math.hypot(dx, dy)
        if dist > 3:
            self.x += (dx / dist) * self.speed
            self.y += (dy / dist) * self.speed
            self.is_moving = True
            self.animation_frame += 1
        else: self.is_moving = False

    def draw(self, surface):
        size = int(self.radius * 2)
        loaded = False
        state = "ion_dead.png" if not self.alive else ("ion1.png" if not self.is_moving or (self.animation_frame // 12) % 2 == 0 else "ion2.png")
        path = os.path.join("ion_animate", state)
        if os.path.exists(path):
            surface.blit(pygame.transform.scale(pygame.image.load(path).convert_alpha(), (size, size)), (int(self.x-self.radius), int(self.y-self.radius)))
            loaded = True
        if not loaded:
            pygame.draw.circle(surface, (0, 255, 180) if self.alive else (120, 120, 120), (int(self.x), int(self.y)), int(self.radius))
        surface.blit(FONT.render(self.thoughts, True, (255, 255, 160)), (self.x - 30, self.y - self.radius - 22))

# =====================================================================
# ГЛАВНЫЙ ИГРОВОЙ ЦИКЛ
# =====================================================================
def main():
    pygame.mouse.set_visible(False)
    tutorial = TutorialWindow()
    winions, eggs = [], []
    kitchen = KitchenTable(WIDTH - 230, 60)
    current_item = None
    menu, selected_winion = None, None
    mouse_history = []
    
    # Авто-восстановление яйца, если оно было создано ранее
    timer_file = os.path.join(SAVE_DIR, "egg_timer.txt")
    has_cooked = os.path.exists(timer_file)
    if has_cooked:
        eggs.append(Egg(WIDTH // 3, HEIGHT // 2))

    spawnable = ["Яблоко", "Вода", "Мука", "Ягода"]

    while True:
        mouse_pos = pygame.mouse.get_pos()
        mx, my = mouse_pos
        draw_background_textures(screen)
        
        if current_item:
            mouse_history.append(mouse_pos)
            if len(mouse_history) > 40: 
                mouse_history.pop(0)
            check_mouse_gestures(mouse_history, current_item, winions)

        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                for w in winions: 
                    w.save_to_folder()
                for egg in eggs: 
                    egg.save_time_to_disk()
                pygame.quit()
                sys.exit()
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if tutorial.active and tutorial.check_click(mouse_pos): 
                    continue
                if menu:
                    choice = menu.get_choice(mouse_pos)
                    if choice:
                        if choice == "Наказать": 
                            menu = ContextMenu(mx, my, ["В угол"]); continue
                        elif choice == "Ласка": 
                            menu = ContextMenu(mx, my, ["Погладить", "Дать поспать"]); continue
                        elif choice == "В угол": 
                            selected_winion.punishment_mode = "corner"; menu = None
                        elif choice == "Погладить": 
                            selected_winion.thoughts = "*Мурчит*"; menu = None
                        elif choice == "Дать поспать": 
                            selected_winion.hunger = max(0, selected_winion.hunger - 10); menu = None
                        elif choice in spawnable: 
                            current_item = Item(menu.x, menu.y, choice); menu = None
                        elif choice == "Положить на Кухню" and current_item and len(kitchen.slots) < 2:
                            kitchen.slots.append(current_item.name); current_item = None; menu = None
                        elif choice == "Очистить Стол": 
                            kitchen.slots.clear(); menu = None
                        elif choice == "Приготовить" and len(kitchen.slots) == 2:
                            combo = tuple(sorted(kitchen.slots))
                            res = RECIPES.get(combo)
                            if res:
                                current_item = Item(kitchen.x + 70, kitchen.y + 130, res)
                                if not has_cooked:
                                    eggs.append(Egg(WIDTH // 3, HEIGHT // 2))
                                    has_cooked = True
                            kitchen.slots.clear(); menu = None
                    else: 
                        menu = None
                    continue
                    
                if event.button == 1:
                    for w in winions:
                        if math.hypot(mx - w.x, my - w.y) <= w.radius: 
                            selected_winion = w
                            menu = ContextMenu(mx, my, ["Наказать", "Ласка"])
                    if not menu and kitchen.x <= mx <= kitchen.x + kitchen.width and kitchen.y <= my <= kitchen.y + kitchen.height:
                        menu = ContextMenu(mx, my, ["Приготовить", "Очистить Стол"] if len(kitchen.slots) == 2 else ["Очистить Стол"])
                    elif not menu and current_item and math.hypot(mx - current_item.x, my - current_item.y) <= current_item.radius:
                        menu = ContextMenu(mx, my, ["Положить на Кухню"])
                elif event.button == 3: 
                    menu = ContextMenu(mx, my, spawnable)
        # Обновление вылупления яиц
        for egg in eggs[:]:
            if egg.update(): 
                winions.append(Winion(egg.x, egg.y))
                eggs.remove(egg)
        
        # Жизнедеятельность Ионов
        for w in winions:
            if w.update(mouse_pos, current_item): 
                current_item = None

        # Отрисовка всех слоев игры
        kitchen.draw(screen)
        for egg in eggs: egg.draw(screen)
        if current_item: current_item.draw(screen)
        for w in winions: w.draw(screen)
        if menu: menu.draw(screen)
        tutorial.draw(screen)

        # Окно подсказки рецептов крафта
        pygame.draw.rect(screen, (30, 35, 45), (10, 10, 240, 95), 0, 4)
        screen.blit(FONT.render("📖 РЕЦЕПТЫ КУХНИ:", True, (255, 215, 0)), (20, 15))
        screen.blit(FONT.render("• Вода + Мука = Тесто", True, TEXT_COLOR), (20, 35))
        screen.blit(FONT.render("• Тесто + Ягода/Яблоко = Пирог", True, TEXT_COLOR), (20, 55))
        screen.blit(FONT.render("🔒 КВЕСТ: Скрафти еду для получения Яйца!" if not has_cooked else "🔓 Яйцо получено!", True, (255, 100, 100) if not has_cooked else (100, 255, 100)), (20, 75))

        # Панель статуса внизу экрана
        pygame.draw.rect(screen, PANEL_COLOR, (0, HEIGHT - 95, WIDTH, 95))
        screen.blit(BIG_FONT.render(f"Ионов в комнате: {len(winions)} | Яиц: {len(eggs)} | Папка: Документы/WinionLife_Saves", True, TEXT_COLOR), (20, HEIGHT - 85))
        screen.blit(FONT.render("УПРАВЛЕНИЕ: ПКМ по полу — создать ресурсы. ЛКМ по ресурсу — отнести на стол. ESC — выход.", True, (170, 170, 170)), (20, HEIGHT - 50))

        # Вывод кастомного курсора поверх всего
        draw_custom_cursor(screen, mouse_pos)
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
