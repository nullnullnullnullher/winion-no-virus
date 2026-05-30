import random

class Winion:
    def __init__(self, name):
        self.name = name
        self.age = 0          # Возраст (растет со временем)
        self.max_age = 1000   # Предел жизни
        self.health = 100     # Здоровье
        self.hunger = 0       # Голод (0 - сыт, 100 - умирает)
        self.is_alive = True
        
        # Мозг из 1000 секторов (инициализируем случайными связями/весами)
        self.brain = [random.uniform(-1.0, 1.0) for _ in range(1000)]
        
        # Словарный запас для общения
        self.vocabulary = ["привет", "ням", "бабах", "играть", "хочу"]

    def live_turn(self):
        """Один тик жизни существа"""
        if not self.is_alive:
            return
            
        self.age += 1
        self.hunger += 1 # Голод растет каждый тик
        
        # Влияние мозга на поведение (симуляция секторов)
        # Сектор 50 отвечает за реакцию на голод
        if self.hunger > 50:
            self.brain[50] += 0.1 # Мозг активирует сектор поиска еды
            
        # Условия смерти
        if self.hunger >= 100 or self.age >= self.max_age:
            self.die()

    def eat(self, item):
        """Взаимодействие с предметом: еда"""
        if item == "яблоко":
            self.hunger = max(0, self.hunger - 30)
            # Обучение: сектор 250 (память о яблоке) связывается с удовольствием
            self.brain[250] += 0.5 
            return f"{self.name} съел яблоко и запомнил, что это вкусно!"

    def chat(self, player_word):
        """Система простейшего общения"""
        # Анализируем слово игрока через сектора мозга (например, 800-810)
        brain_trigger = sum(self.brain[800:810])
        
        if "привет" in player_word.lower():
            return f"{self.name} говорит: {random.choice(self.vocabulary)}! (Связи мозга: {brain_trigger:.2f})"
        elif "кушай" in player_word.lower():
            self.brain[850] += 0.2 # Учится реагировать на команду еды
            return f"{self.name} смотрит на вас и ищет еду."
        else:
            return f"{self.name} издает непонятные звуки..."

    def die(self):
        self.is_alive = False
        print(f"Увы, {self.name} покинул этот мир от старости или голода.")

# --- Тест механики ---
pet = Winion(name="Нео")
print(f"Родился питомец {pet.name}!")
print(pet.chat("Привет, малыш!"))
print(pet.eat("яблоко"))
