import pygame
import sys
import math
import random
import os

# =====================================================================
# ЧАСТЬ 1: ПОЛНОЭКРАННЫЕ НАСТРОЙКИ, КУРСОР И СИСТЕМА ОБУЧЕНИЯ
# =====================================================================

pygame.init()
pygame.font.init()

# Автоматически определяем разрешение твоего монитора
infoObject = pygame.display.Info()
WIDTH = infoObject.current_w
HEIGHT = infoObject.current_h

# Запуск в настоящем полноэкранном режиме
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Winion Life Simulator")
clock = pygame.time.Clock()

# Шрифты и цвета оформления
FONT = pygame.font.SysFont("Arial", 16)
BIG_FONT = pygame.font.SysFont("Arial", 22)
TEXT_COLOR = (240, 240, 240)
PANEL_COLOR = (35, 38, 50)

# Папка для безопасного сохранения данных Ионов
SAVE_DIR = "winions_data"
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

def draw_custom_cursor(surface, pos):
    """Стильный хай-тек прицел-сканер мыслей"""
    x, y = pos
    pygame.draw.circle(surface, (0, 255, 200), (x, y + 10), 12, 1)
    pygame.draw.line(surface, (0, 255, 200), (x - 18, y + 10), (x + 18, y + 10), 1)
    pygame.draw.line(surface, (0, 255, 200), (x, y - 8), (x, y + 28), 1)
    pygame.draw.polygon(surface, (230, 190, 150), [(x, y + 3), (x - 5, y + 12), (x + 5, y + 12)])
    pygame.draw.circle(surface, (255, 50, 50), (x, y), 3)

class ContextMenu:
    """Контекстное меню действий и создания предметов"""
    def __init__(self, x, y, options):
        self.x = x
        self.y = y
        self.options = options
        self.width = 160
        self.height = len(options) * 28

    def draw(self, surface):
        # Защита от выхода меню за границы полного экрана
        draw_x = min(self.x, WIDTH - self.width)
        draw_y = min(self.y, HEIGHT - self.height)
        pygame.draw.rect(surface, (50, 52, 70), (draw_x, draw_y, self.width, self.height), 0, 4)
        pygame.draw.rect(surface, (90, 95, 120), (draw_x, draw_y, self.width, self.height), 1, 4)
        for i, opt in enumerate(self.options):
            t = FONT.render(opt, True, TEXT_COLOR)
            surface.blit(t, (draw_x + 10, draw_y + 6 + (i * 28)))

    def get_choice(self, m_pos):
        # Исправлено: Разделяем кортеж позиции мыши на отдельные числа X и Y
        mx, my = m_pos
        draw_x = min(self.x, WIDTH - self.width)
        draw_y = min(self.y, HEIGHT - self.height)
        
        # Сравниваем координаты правильно
        if draw_x <= mx <= draw_x + self.width:
            if draw_y <= my <= draw_y + self.height:
                return self.options[(my - draw_y) // 28]
        return None

class TutorialWindow:
    """Интерактивное окно туториала для новичков"""
    def __init__(self):
        self.step = 0
        self.width = 450
        self.height = 140
        self.x = WIDTH // 2 - self.width // 2
        self.y = HEIGHT // 2 - self.height // 2
        self.active = True
        
        # Тексты шагов обучения
        self.messages = [
            "Привет! Добро пожаловать в симулятор Ионов. Нажми кнопку ниже.",
            "ШАГ 1: Нажми ПКМ на пустом месте и выбери 'Вода', а затем 'Мука'.",
            "ШАГ 2: Кликни ЛКМ по созданному предмету и выбери 'Положить на Кухню'.",
            "ШАГ 3: Положи так оба ингредиента. Затем нажми ЛКМ по Столу -> 'Приготовить'.",
            "ОТЛИЧНО! Ты скрафтил Тесто и получил Яйцо! Подожди 5 минут до вылупления!"
        ]

    def draw(self, surface):
        if not self.active: return
        # Рисуем рамку туториала
        pygame.draw.rect(surface, (30, 45, 60), (self.x, self.y, self.width, self.height), 0, 8)
        pygame.draw.rect(surface, (0, 255, 200), (self.x, self.y, self.width, self.height), 2, 8)
        
        # Заголовок и текст инструкции
        title = BIG_FONT.render("🎓 ОБУЧЕНИЕ:", True, (0, 255, 200))
        surface.blit(title, (self.x + 20, self.y + 15))
        
        msg = FONT.render(self.messages[self.step], True, TEXT_COLOR)
        surface.blit(msg, (self.x + 20, self.y + 50))
        
        # Кнопка "ДAЛЕЕ"
        self.btn_rect = pygame.Rect(self.x + self.width - 120, self.y + self.height - 45, 100, 30)
        pygame.draw.rect(surface, (0, 180, 140), self.btn_rect, 0, 4)
        btn_txt = FONT.render("Далее", True, TEXT_COLOR)
        surface.blit(btn_txt, (self.x + self.width - 95, self.y + self.height - 40))

    def check_click(self, m_pos):
        if not self.active: return False
        if self.btn_rect.collidepoint(m_pos):
            if self.step < len(self.messages) - 1:
                self.step += 1
            else:
                self.active = False # Закрываем туториал
            return True
        return False

# =====================================================================
# ЧАСТЬ 2: ОБЪЕКТЫ МИРА, ТЕКСТУРЫ ПОЛОВ И УМНОЕ ЯЙЦО
# =====================================================================

def draw_background_textures(surface):
    """Генерация красивых текстур комнат прямо через код под весь экран"""
    # 1. Игровая комната (Мягкий плиточный ковролин)
    surface.fill((28, 33, 46))
    for x in range(0, WIDTH, 32):
        for y in range(0, HEIGHT, 32):
            if (x + y) % 64 == 0:
                pygame.draw.rect(surface, (32, 38, 53), (x, y, 32, 32))

    # 2. Кухонная зона (Уютный деревянный паркет справа вверху)
    kitchen_zone = pygame.Rect(WIDTH - 300, 0, 300, 350)
    pygame.draw.rect(surface, (115, 74, 44), kitchen_zone)
    # Линии досок паркета
    for y in range(0, 350, 25):
        pygame.draw.line(surface, (80, 48, 25), (WIDTH - 300, y), (WIDTH, y), 1)
    for x in range(WIDTH - 300, WIDTH, 50):
        pygame.draw.line(surface, (80, 48, 25), (x, 0), (x, 350), 1)
    # Металлический порожек кухни
    pygame.draw.line(surface, (140, 140, 150), (WIDTH - 300, 0), (WIDTH - 300, 350), 2)
    pygame.draw.line(surface, (140, 140, 150), (WIDTH - 300, 350), (WIDTH, 350), 2)

class Item:
    """Класс съедобных ресурсов"""
    def __init__(self, x, y, name="Яблоко"):
        self.x = x
        self.y = y
        self.name = name
        self.radius = 12
        self.is_forbidden = False

    def draw(self, surface):
        color = (200, 50, 50) if self.is_forbidden else ITEM_TYPES.get(self.name, {"color": (255,90,50)})["color"]
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), self.radius)
        
        status_label = " (НЕЛЬЗЯ!)" if self.is_forbidden else ""
        txt = FONT.render(f"{self.name}{status_label}", True, TEXT_COLOR)
        surface.blit(txt, (self.x - 25, self.y - 30))

class Egg:
    """Таймерное яйцо Иона: вылупляется ровно через 5 минут реального времени"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius_w = 22
        self.radius_h = 30
        
        # 5 минут при 60 кадрах в секунду = 18 000 кадров игрового цикла
        self.total_frames = 5 * 60 * 60 
        self.current_frame = 0
        
        self.sprite = None
        sprite_path = os.path.join("ion_animate", "egg_ion.png")
        if os.path.exists(sprite_path):
            img = pygame.image.load(sprite_path).convert_alpha()
            self.sprite = pygame.transform.scale(img, (self.radius_w * 2, self.radius_h * 2))

    def update(self):
        self.current_frame += 1
        return self.current_frame >= self.total_frames

    def draw(self, surface):
        if self.sprite:
            surface.blit(self.sprite, (self.x - self.radius_w, self.y - self.radius_h))
        else:
            egg_rect = pygame.Rect(self.x - self.radius_w, self.y - self.radius_h, self.radius_w * 2, self.radius_h * 2)
            pygame.draw.ellipse(surface, (245, 215, 120), egg_rect)
            pygame.draw.ellipse(surface, (190, 150, 70), egg_rect, 2)
        
        # Расчет оставшихся минут и секунд
        progress = self.current_frame / self.total_frames
        frames_left = self.total_frames - self.current_frame
        minutes_left = max(0, int(frames_left / 60 / 60))
        seconds_left = max(0, int((frames_left / 60) % 60))
        
        # Индикатор созревания скорлупы
        pygame.draw.rect(surface, (40, 40, 50), (self.x - 30, self.y - 45, 60, 6))
        pygame.draw.rect(surface, (0, 255, 150), (self.x - 30, self.y - 45, int(60 * progress), 6))
        
        time_txt = FONT.render(f"{minutes_left:02d}:{seconds_left:02d}", True, (255, 255, 255))
        surface.blit(time_txt, (self.x - time_txt.get_width() // 2, self.y - 65))

def check_mouse_gestures(mouse_history, current_item, winions):
    """Распознавание приказов 'МОЖНО' и 'НЕЛЬЗЯ' по траектории курсора"""
    if not current_item or len(mouse_history) < 40: return

    x_crossings = 0
    near_item = True
    for i in range(1, len(mouse_history)):
        mx, my = mouse_history[i]
        prev_mx, prev_my = mouse_history[i-1]
        
        if math.hypot(mx - current_item.x, my - current_item.y) > 100:
            near_item = False
            break
        if (prev_mx < current_item.x and mx > current_item.x) or \
           (prev_mx > current_item.x and mx < current_item.x):
            x_crossings += 1

    # Машем влево-вправо — активируем запрет
    if near_item and x_crossings >= 4:
        current_item.is_forbidden = True
        for w in winions:
            if w.alive:
                w.thoughts = "Хозяин сердится. Это НЕЛЬЗЯ кушать!"
                # Обучаем именно Сектор №400 (Послушание/Запреты) внутри списка мозга
                w.brain[400] = min(1.0, w.brain[400] + 0.4)
        mouse_history.clear()
        return

    # Крутим круги — разрешаем кушать
    l = sum(1 for p in mouse_history if p[0] < current_item.x)
    r = sum(1 for p in mouse_history if p[0] > current_item.x)
    u = sum(1 for p in mouse_history if p[1] < current_item.y)
    d = sum(1 for p in mouse_history if p[1] > current_item.y)
    if l > 8 and r > 8 and u > 8 and d > 8:
        current_item.is_forbidden = False
        for w in winions:
            if w.alive:
                w.target_x, w.target_y = current_item.x, current_item.y
                w.thoughts = "Хозяин разрешил! Иду обедать!"
                # Усиливаем Сектор №300 (Желание идти на зов) внутри списка мозга
                w.brain[300] = min(1.0, w.brain[300] + 0.3)
        mouse_history.clear()
# =====================================================================
# ЧАСТЬ 3: КЛАСС ВИНИОНА С АНИМАЦИЕЙ ШАГА И КУЛИНАРИЯ
# =====================================================================

ITEM_TYPES = {
    "Яблоко": {"color": (255, 90, 50), "nutr": 35},
    "Вода": {"color": (50, 150, 255), "nutr": 10},
    "Мука": {"color": (220, 220, 200), "nutr": 5},
    "Yагода": {"color": (200, 30, 100), "nutr": 20},
    "Тесто": {"color": (240, 210, 160), "nutr": 15},
    "Пирог": {"color": (150, 75, 0), "nutr": 80}
}

RECIPES = {
    ("Вода", "Мука"): "Тесто",
    ("Тесто", "Ягода"): "Пирог",
    ("Тесто", "Яблоко"): "Пирог"
}

class KitchenTable:
    """Разделочный стол на кухне для смешивания ингредиентов"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 160
        self.height = 100
        self.slots = []

    def draw(self, surface):
        pygame.draw.rect(surface, (140, 90, 55), (self.x, self.y, self.width, self.height), 0, 6)
        pygame.draw.rect(surface, (230, 230, 240), (self.x + 5, self.y + 5, self.width - 10, self.height - 10), 0, 4)
        
        t = FONT.render("РАЗДЕЛОЧНЫЙ СТОЛ", True, (60, 40, 20))
        surface.blit(t, (self.x + 10, self.y + 10))
        slots_txt = f"Внутри: {', '.join(self.slots) if self.slots else 'Пусто'}"
        st = FONT.render(slots_txt, True, (80, 80, 90))
        surface.blit(st, (self.x + 10, self.y + 45))

class Winion:
    """Существо Ион с искусственным мозгом и физиологией"""
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
        self.age = 0
        self.hunger = 20
        self.fatigue = 5
        self.thoughts = "Привет! Я вылупился!"
        
        self.punishment_mode = None
        self.animation_frame = 0
        self.is_moving = False
        
        # Мозг: 1000 секторов весов связей
        self.brain = [random.uniform(-1.0, 1.0) for _ in range(1000)]
        self.brain[100] = 0.5  # Инстинкт голода
        self.brain[400] = 0.1  # Инстинкт послушания запретам
        
        self.folder_path = os.path.join(SAVE_DIR, self.name)
        if not os.path.exists(self.folder_path):
            os.makedirs(self.folder_path)
            self.save_to_folder()

    def save_to_folder(self):
        try:
            with open(os.path.join(self.folder_path, "stats.txt"), "w", encoding="utf-8") as f:
                f.write(f"Name: {self.name}\nAge: {self.age:.2f}\nHunger: {self.hunger:.2f}\nFatigue: {self.fatigue:.2f}\nSize: {self.radius}\n")
            with open(os.path.join(self.folder_path, "brain.txt"), "w") as f:
                f.write(",".join(map(str, self.brain)))
        except Exception as e:
            print(f"Ошибка сохранения Иона: {e}")

    def update(self, mouse_pos, current_item):
        if not self.alive: return False

        self.age += 0.02
        self.hunger += 0.01
        self.fatigue += 0.004
        
        if self.radius < self.max_radius and int(self.age) % 5 == 0:
            self.radius = min(self.max_radius, self.radius + 0.08)

        if random.random() < 0.005: self.save_to_folder()

        if self.hunger >= 100 or self.age >= 1000:
            self.alive = False
            self.thoughts = "Умер от голода..."
            self.save_to_folder()
            return False

        if self.punishment_mode == "corner":
            self.thoughts = "Стою в углу..."
            self.target_x, self.target_y = 50, 50
            self.move_towards_target()
            return False

        if current_item:
            food_drive = self.hunger * self.brain[100]
            inhibition_drive = self.brain[400] * 60 if current_item.is_forbidden else 0.0

            if food_drive > inhibition_drive:
                self.target_x, self.target_y = current_item.x, current_item.y
                self.thoughts = "Я голоден, ворую еду!" if current_item.is_forbidden else "Иду к тарелке!"
                
                if math.hypot(current_item.x - self.x, current_item.y - self.y) < self.radius + current_item.radius:
                    nutr = ITEM_TYPES.get(current_item.name, {"nutr": 20})["nutr"]
                    self.hunger = max(0, self.hunger - nutr)
                    self.thoughts = f"Съел {current_item.name}."
                    return True
            else:
                self.thoughts = "Я хочу есть, но помню жест 'НЕЛЬЗЯ'!"
        else:
            if random.random() < 0.01:
                self.target_x = random.randint(80, WIDTH - 350)
                self.target_y = random.randint(80, HEIGHT - 160)
                self.thoughts = "Исследую ковролин..."

        self.move_towards_target()
        return False

    def move_towards_target(self):
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        dist = math.hypot(dx, dy)
        if dist > 3:
            self.x += (dx / dist) * self.speed
            self.y += (dy / dist) * self.speed
            self.is_moving = True
            self.animation_frame += 1
        else:
            self.is_moving = False

    def draw(self, surface):
        current_size = int(self.radius * 2)
        sprite_loaded = False
        
        if not self.alive:
            path = os.path.join("ion_animate", "ion_dead.png")
            if os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
                surface.blit(pygame.transform.scale(img, (current_size, current_size)), (int(self.x - self.radius), int(self.y - self.radius)))
                sprite_loaded = True
        elif self.is_moving:
            frame_name = "ion1.png" if (self.animation_frame // 12) % 2 == 0 else "ion2.png"
            path = os.path.join("ion_animate", frame_name)
            if os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
                surface.blit(pygame.transform.scale(img, (current_size, current_size)), (int(self.x - self.radius), int(self.y - self.radius)))
                sprite_loaded = True
        else:
            path = os.path.join("ion_animate", "ion1.png")
            if os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
                surface.blit(pygame.transform.scale(img, (current_size, current_size)), (int(self.x - self.radius), int(self.y - self.radius)))
                sprite_loaded = True

        if not sprite_loaded:
            color = (0, 255, 180) if self.alive else (120, 120, 120)
            pygame.draw.circle(surface, color, (int(self.x), int(self.y)), int(self.radius))
            pygame.draw.circle(surface, (255,255,255), (int(self.x)-5, int(self.y)-4), 3)
            pygame.draw.circle(surface, (255,255,255), (int(self.x)+5, int(self.y)-4), 3)

        t_txt = FONT.render(self.thoughts, True, (255, 255, 160))
        surface.blit(t_txt, (self.x - t_txt.get_width() // 2, self.y - self.radius - 22))
# =====================================================================
# ЧАСТЬ 4: ГЛАВНЫЙ ИГРОВОЙ ЦИКЛ И КУЛИНАРИЯ
# =====================================================================

def main():
    pygame.mouse.set_visible(False)
    
    tutorial = TutorialWindow()
    winions = []
    eggs = []  
    kitchen = KitchenTable(WIDTH - 230, 60)
    current_item = None
    
    menu = None
    selected_winion = None
    mouse_history = []
    
    has_cooked_first_dish = False
    spawnable_items = ["Яблоко", "Вода", "Мука", "Ягода"]

    while True:
        mouse_pos = pygame.mouse.get_pos()
        mx, my = mouse_pos # Разделяем позицию мыши на отдельные координаты X и Y
        draw_background_textures(screen)

        if current_item:
            mouse_history.append(mouse_pos)
            if len(mouse_history) > 40: mouse_history.pop(0)
            check_mouse_gestures(mouse_history, current_item, winions)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                for w in winions: w.save_to_folder()
                pygame.quit()
                sys.exit()
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    for w in winions: w.save_to_folder()
                    pygame.quit()
                    sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if tutorial.active:
                    if tutorial.check_click(mouse_pos):
                        continue
                
                if menu:
                    choice = menu.get_choice(mouse_pos)
                    if choice:
                        if choice == "Наказать":
                            menu = ContextMenu(mx, my, ["В угол"])
                            continue
                        elif choice == "Ласка":
                            menu = ContextMenu(mx, my, ["Погладить", "Дать поспать"])
                            continue
                        elif choice == "В угол":
                            selected_winion.punishment_mode = "corner"
                            menu = None
                        elif choice == "Погладить":
                            selected_winion.thoughts = "*Рад поглаживанию*"
                            menu = None
                        elif choice == "Дать поспать":
                            selected_winion.fatigue = 0
                            menu = None
                        elif choice in spawnable_items:
                            current_item = Item(menu.x, menu.y, choice)
                            menu = None
                        elif choice == "Положить на Кухню":
                            if current_item and len(kitchen.slots) < 2:
                                kitchen.slots.append(current_item.name)
                                current_item = None
                            menu = None
                        elif choice == "Очистить Стол":
                            kitchen.slots.clear()
                            menu = None
                        elif choice == "Приготовить":
                            if len(kitchen.slots) == 2:
                                combo = tuple(sorted(kitchen.slots))
                                result = RECIPES.get(combo)
                                if result:
                                    current_item = Item(kitchen.x + 70, kitchen.y + 130, result)
                                    if not has_cooked_first_dish:
                                        eggs.append(Egg(WIDTH // 3, HEIGHT // 2))
                                        has_cooked_first_dish = True
                                kitchen.slots.clear()
                            menu = None
                    else:
                        menu = None
                    continue

                # ЛКМ — Взаимодействие
                if event.button == 1:
                    clicked_w = None
                    for w in winions:
                        if math.hypot(mx - w.x, my - w.y) <= w.radius:
                            clicked_w = w
                            break
                    
                    if clicked_w and clicked_w.alive:
                        selected_winion = clicked_w
                        menu = ContextMenu(mx, my, ["Наказать", "Ласка"])
                    elif (kitchen.x <= mx <= kitchen.x + kitchen.width and 
                          kitchen.y <= my <= kitchen.y + kitchen.height):
                        options = ["Приготовить", "Очистить Стол"] if len(kitchen.slots) == 2 else ["Очистить Стол"]
                        menu = ContextMenu(mx, my, options)
                    elif current_item and math.hypot(mx - current_item.x, my - current_item.y) <= current_item.radius:
                        menu = ContextMenu(mx, my, ["Положить на Кухню"])

                # ПКМ — Спавн меню ресурсов (Теперь передаем mx, my вместо mouse_pos)
                elif event.button == 3:
                    menu = ContextMenu(mx, my, spawnable_items)

        for egg in eggs[:]:
            if egg.update():
                winions.append(Winion(egg.x, egg.y))
                eggs.remove(egg)

        for w in winions:
            if w.update(mouse_pos, current_item):
                current_item = None

        # Отрисовка
        kitchen.draw(screen)
        for egg in eggs: egg.draw(screen)
        if current_item: current_item.draw(screen)
        for w in winions: w.draw(screen)
        if menu: menu.draw(screen)
        
        tutorial.draw(screen)

        # Таблица крафта
        pygame.draw.rect(screen, (30, 35, 45), (10, 10, 240, 95), 0, 4)
        pygame.draw.rect(screen, (70, 75, 90), (10, 10, 240, 95), 1, 4)
        screen.blit(FONT.render("📖 РЕЦЕПТЫ КУХНИ ДЛЯ ИОНА:", True, (255, 215, 0)), (20, 15))
        screen.blit(FONT.render("• Вода + Мука = Тесто", True, TEXT_COLOR), (20, 35))
        screen.blit(FONT.render("• Тесто + Ягода/Яблоко = Пирог сытный", True, TEXT_COLOR), (20, 55))

        if not has_cooked_first_dish:
            screen.blit(FONT.render("🔒 КВЕСТ: Скрафти еду ради Яйца Иона!", True, (255, 100, 100)), (20, 75))
        else:
            screen.blit(FONT.render("🔓 Яйцо получено! Жди вылупления.", True, (100, 255, 100)), (20, 75))

        # Статусбар
        pygame.draw.rect(screen, PANEL_COLOR, (0, HEIGHT - 95, WIDTH, 95))
        info = f"Ионов на коврике: {len(winions)} | Яиц греется: {len(eggs)} | Папки данных: /{SAVE_DIR} | Нажми ESC для выхода"
        screen.blit(BIG_FONT.render(info, True, TEXT_COLOR), (20, HEIGHT - 85))
        screen.blit(FONT.render("УПРАВЛЕНИЕ: ПКМ по ковру — спавн ресурсов. ЛКМ по предмету — унести на Разделочный стол.", True, (170, 170, 170)), (20, HEIGHT - 50))

        draw_custom_cursor(screen, mouse_pos)
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
