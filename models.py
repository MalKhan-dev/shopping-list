import os
from abc import ABC, abstractmethod
from datetime import datetime

DATE_FORMAT = "%d.%m.%Y %H:%M:%S"


class Entity(ABC):
    """Общий предок всех сущностей: имя, сравнение и вывод."""

    def __init__(self, name):
        self.name = name

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        value = str(value).strip()
        if value == "":
            raise ValueError("Название не может быть пустым")
        self._name = value

    def __eq__(self, other):
        return type(self) is type(other) and self.name.lower() == other.name.lower()

    def __lt__(self, other):
        return self.name.lower() < other.name.lower()

    def __str__(self):
        return self.info()

    @abstractmethod
    def info(self):
        """Короткое описание объекта для вывода."""


class Product(Entity):
    """Товар в списке покупок."""

    def __init__(self, name, quantity, price, bought=False):
        super().__init__(name)
        self.quantity = quantity
        self.price = price
        self.bought = bought

    @property
    def quantity(self):
        return self._quantity

    @quantity.setter
    def quantity(self, value):
        value = int(value)
        if value < 1:
            raise ValueError("Количество должно быть не меньше 1")
        self._quantity = value

    @property
    def price(self):
        return self._price

    @price.setter
    def price(self, value):
        value = float(value)
        if value < 0:
            raise ValueError("Цена не может быть отрицательной")
        self._price = value

    @property
    def bought(self):
        return self._bought

    @bought.setter
    def bought(self, value):
        self._bought = bool(value)

    def cost(self):
        return self.quantity * self.price

    def info(self):
        return f"{self.name}: {self.quantity} шт. × {self.price:.2f} ₽ = {self.cost():.2f} ₽"

    def __repr__(self):
        return f"Product({self.name!r}, {self.quantity}, {self.price}, {self.bought})"

    @staticmethod
    def total_cost(products):
        return sum(product.cost() for product in products)

    @staticmethod
    def create_start_list():
        data = [
            ("Молоко", 2, 89.90),
            ("Хлеб", 1, 45.00),
            ("Яйца", 1, 110.00),
            ("Сыр", 1, 320.00),
            ("Масло", 1, 180.00),
            ("Рис", 1, 95.00),
            ("Яблоки", 2, 120.00),
            ("Чай", 1, 150.00),
            ("Сахар", 1, 75.00),
            ("Курица", 1, 280.00),
        ]
        return [Product(name, quantity, price) for name, quantity, price in data]


class Session(Entity):
    """Сеанс работы с программой. Логин хранится в имени сущности (name)."""

    def __init__(self, login):
        super().__init__(login)
        self.time_in = datetime.now()
        self.time_out = None

    @property
    def login(self):
        return self.name

    @login.setter
    def login(self, value):
        self.name = value

    @property
    def time_in(self):
        return self._time_in

    @time_in.setter
    def time_in(self, value):
        self._time_in = value

    @property
    def time_out(self):
        return self._time_out

    @time_out.setter
    def time_out(self, value):
        self._time_out = value

    def finish(self):
        self.time_out = datetime.now()

    def info(self):
        return f"{self.name}: {self.time_in.strftime(DATE_FORMAT)}"

    def __repr__(self):
        return f"Session({self.name!r}, {self.time_in!r}, {self.time_out!r})"

    def save(self, path):
        write_header = not os.path.exists(path)
        with open(path, "a", encoding="utf-8") as file:
            if write_header:
                file.write(Session.make_border())
                file.write(Session.make_row("login", "time_in", "time_out"))
                file.write(Session.make_border())
            time_in = self.time_in.strftime(DATE_FORMAT)
            time_out = self.time_out.strftime(DATE_FORMAT)
            file.write(Session.make_row(self.login, time_in, time_out))
            file.write(Session.make_border())

    @staticmethod
    def make_border():
        # ширина ячейки + по одному пробелу слева и справа
        return "+" + "-" * (15 + 2) + "+" + "-" * (19 + 2) + "+" + "-" * (19 + 2) + "+\n"

    @staticmethod
    def make_row(login, time_in, time_out):
        return f"| {login:<15} | {time_in:<19} | {time_out:<19} |\n"


class KeyValueMap:
    """Собственное отображение «ключ → значение» на списке пар (ключ, значение)."""

    def __init__(self):
        self._entries = []

    @property
    def entries(self):
        return list(self._entries)

    @entries.setter
    def entries(self, pairs):
        new_entries = []
        for pair in pairs:
            if not isinstance(pair, tuple) or len(pair) != 2:
                raise ValueError("Каждый элемент должен быть парой (ключ, значение)")
            if pair[0] in [key for key, value in new_entries]:
                raise ValueError("Ключи не должны повторяться")
            new_entries.append(pair)
        self._entries = new_entries

    def key_list(self):
        return [key for key, value in self._entries]

    def put(self, key, value):
        keys = self.key_list()
        if key in keys:
            self._entries[keys.index(key)] = (key, value)
        else:
            self._entries.append((key, value))

    def find(self, key):
        keys = self.key_list()
        if key in keys:
            return self._entries[keys.index(key)][1]
        return None

    def delete(self, key):
        self._entries.pop(self.key_list().index(key))

    def __contains__(self, key):
        return key in self.key_list()

    def __iter__(self):
        return iter([value for key, value in self._entries])
