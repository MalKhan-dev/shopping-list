import flet as ft

from models import KeyValueMap, Product

NAME_WIDTH = 220
QUANTITY_WIDTH = 90
PRICE_WIDTH = 110
COST_WIDTH = 110


class TitleText(ft.Text):
    """Заголовок окна."""

    def __init__(self):
        super().__init__(value="Список покупок", size=24, weight=ft.FontWeight.BOLD)


class NameField(ft.TextField):
    """Поле названия: получает фокус при запуске, Enter добавляет товар."""

    def __init__(self, on_submit):
        super().__init__(label="Товар", width=NAME_WIDTH, autofocus=True, on_submit=on_submit)


class QuantityField(ft.TextField):
    """Поле количества: только цифры, по умолчанию 1."""

    def __init__(self):
        super().__init__(label="Кол-во", value="1", width=QUANTITY_WIDTH,
                         input_filter=ft.NumbersOnlyInputFilter())


class PriceField(ft.TextField):
    """Поле цены: число с точкой и не больше двух знаков после неё."""

    def __init__(self):
        super().__init__(label="Цена", width=PRICE_WIDTH,
                         input_filter=ft.InputFilter(regex_string=r"^[0-9]*\.?[0-9]{0,2}$"))


class AddButton(ft.Button):
    """Кнопка добавления товара."""

    def __init__(self, on_click):
        super().__init__(content="Добавить", icon=ft.Icons.ADD, on_click=on_click)


class InputRow(ft.Row):
    """Форма ввода: поля и кнопка в одну строку, выровнены по центру."""

    def __init__(self, name_field, quantity_field, price_field, add_button):
        super().__init__(controls=[name_field, quantity_field, price_field, add_button],
                         vertical_alignment=ft.CrossAxisAlignment.CENTER)


class BoughtCheckbox(ft.Checkbox):
    """Флажок «куплено» с названием товара. Товар хранится в data."""

    def __init__(self, product, on_change):
        super().__init__(label=product.name, value=product.bought,
                         data=product, on_change=on_change)


class DeleteButton(ft.IconButton):
    """Кнопка удаления товара. Товар хранится в data."""

    def __init__(self, product, on_click):
        super().__init__(icon=ft.Icons.DELETE_OUTLINE, tooltip="Удалить",
                         data=product, on_click=on_click)


class ProductRow(ft.Row):
    """Строка товара. Ширина ячеек совпадает с шириной полей формы."""

    def __init__(self, product, on_toggle, on_delete):
        super().__init__(
            controls=[
                # width у самого Checkbox масштабирует флажок, поэтому ширину задаёт Container
                ft.Container(content=BoughtCheckbox(product, on_toggle), width=NAME_WIDTH,
                             alignment=ft.Alignment.CENTER_LEFT),
                ft.Text(f"{product.quantity} шт.", width=QUANTITY_WIDTH),
                ft.Text(f"{product.price:.2f} ₽", width=PRICE_WIDTH),
                ft.Text(f"{product.cost():.2f} ₽", width=COST_WIDTH),
                DeleteButton(product, on_delete),
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )


class TotalText(ft.Text):
    """Итоговая строка: общая сумма и сумма купленного."""

    def __init__(self):
        super().__init__(size=16, weight=ft.FontWeight.BOLD)

    def show(self, total, bought_total):
        self.value = f"Итого: {total:.2f} ₽, куплено на: {bought_total:.2f} ₽"


class ShoppingApp(ft.Column):
    """Корневой компонент окна: хранит товары и собирает интерфейс."""

    def __init__(self):
        super().__init__(expand=True)
        self.products = KeyValueMap()
        for product in Product.create_start_list():
            self.products.put(product.name.lower(), product)

        self.name_field = NameField(on_submit=self.add_product)
        self.quantity_field = QuantityField()
        self.price_field = PriceField()
        self.add_button = AddButton(on_click=self.add_product)
        self.product_list = ft.ListView(expand=True)
        self.total_text = TotalText()
        self.controls = [
            TitleText(),
            InputRow(self.name_field, self.quantity_field, self.price_field, self.add_button),
            self.product_list,
            self.total_text,
        ]
        self.refresh()

    @property
    def products(self):
        return self._products

    @products.setter
    def products(self, value):
        self._products = value

    @property
    def name_field(self):
        return self._name_field

    @name_field.setter
    def name_field(self, value):
        self._name_field = value

    @property
    def quantity_field(self):
        return self._quantity_field

    @quantity_field.setter
    def quantity_field(self, value):
        self._quantity_field = value

    @property
    def price_field(self):
        return self._price_field

    @price_field.setter
    def price_field(self, value):
        self._price_field = value

    @property
    def add_button(self):
        return self._add_button

    @add_button.setter
    def add_button(self, value):
        self._add_button = value

    @property
    def product_list(self):
        return self._product_list

    @product_list.setter
    def product_list(self, value):
        self._product_list = value

    @property
    def total_text(self):
        return self._total_text

    @total_text.setter
    def total_text(self, value):
        self._total_text = value

    @staticmethod
    def open_window(page):
        page.title = "Shopping List"
        page.window.width = 720
        page.window.height = 700
        page.padding = 20
        page.add(ShoppingApp())

    def refresh(self):
        products = sorted(self.products)
        self.product_list.controls = [
            ProductRow(product, self.toggle_product, self.delete_product) for product in products
        ]
        bought = [product for product in products if product.bought]
        self.total_text.show(Product.total_cost(products), Product.total_cost(bought))

    def add_product(self, e):
        product = self.read_product()
        if product is not None:
            self.products.put(product.name.lower(), product)
            self.clear_form()
        self.refresh()
        self.update()

    def toggle_product(self, e):
        product = e.control.data
        product.bought = e.control.value
        self.refresh()
        self.update()

    def delete_product(self, e):
        product = e.control.data
        self.products.delete(product.name.lower())
        self.refresh()
        self.update()

    def read_product(self):
        """Создаёт товар из полей формы. При ошибке пишет её под полем и возвращает None."""
        self.name_field.error = None
        self.quantity_field.error = None
        self.price_field.error = None
        try:
            product = Product(self.name_field.value, 1, 0)
        except ValueError:
            self.name_field.error = "Введите название"
            return None
        if product.name.lower() in self.products:
            self.name_field.error = "Такой товар уже есть"
            return None
        try:
            product.quantity = self.quantity_field.value
        except ValueError:
            self.quantity_field.error = "Целое ≥ 1"
            return None
        try:
            product.price = self.price_field.value
        except ValueError:
            self.price_field.error = "Число ≥ 0"
            return None
        return product

    def clear_form(self):
        self.name_field.value = ""
        self.quantity_field.value = "1"
        self.price_field.value = ""
