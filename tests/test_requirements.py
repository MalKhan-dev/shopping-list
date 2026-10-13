import ast
import os
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

import flet as ft

from models import DATE_FORMAT, Entity, KeyValueMap, Product, Session
from ui import (AddButton, BoughtCheckbox, DeleteButton, InputRow, NameField, PriceField,
                ProductRow, QuantityField, ShoppingApp, TitleText, TotalText)

PROJECT = Path(__file__).resolve().parent.parent

COMPONENTS = [
    (TitleText, ft.Text),
    (NameField, ft.TextField),
    (QuantityField, ft.TextField),
    (PriceField, ft.TextField),
    (AddButton, ft.Button),
    (InputRow, ft.Row),
    (BoughtCheckbox, ft.Checkbox),
    (DeleteButton, ft.IconButton),
    (ProductRow, ft.Row),
    (TotalText, ft.Text),
]


class FakeEvent:
    """Заменяет событие Flet: обработчикам нужен только e.control."""

    def __init__(self, control):
        self.control = control


class RequirementsTest(unittest.TestCase):

    def test_abstract_entity(self):
        with self.assertRaises(TypeError):
            Entity("Без типа")
        self.assertIsInstance(Product("Хлеб", 1, 45), Entity)
        self.assertIsInstance(Session("user"), Entity)

    def test_getters_and_setters(self):
        product = Product("Хлеб", 1, 45)
        product.quantity = "3"
        product.price = "45.5"
        product.bought = True
        self.assertEqual(product.quantity, 3)
        self.assertEqual(product.price, 45.5)
        self.assertTrue(product.bought)
        for bad_value in ("0", "abc"):
            with self.assertRaises(ValueError):
                product.quantity = bad_value
        with self.assertRaises(ValueError):
            product.price = "-1"
        with self.assertRaises(ValueError):
            product.name = "   "
        session = Session("anna")
        session.login = "boris"
        self.assertEqual((session.login, session.name), ("boris", "boris"))
        with self.assertRaises(ValueError):
            session.login = ""

    def test_app_properties(self):
        app = ShoppingApp()
        for name in ("products", "name_field", "quantity_field", "price_field",
                     "add_button", "product_list", "total_text"):
            self.assertIsInstance(getattr(ShoppingApp, name), property)
            self.assertIs(getattr(app, name), getattr(app, "_" + name))
        new_products = KeyValueMap()
        app.products = new_products
        self.assertIs(app._products, new_products)

    def test_comparison(self):
        self.assertEqual(Product("Молоко", 1, 90), Product("молоко", 2, 80))
        self.assertNotEqual(Product("Молоко", 1, 90), Product("Хлеб", 1, 90))
        self.assertTrue(Product("Хлеб", 1, 45) > Product("Молоко", 1, 90))
        names = [product.name for product in sorted(Product.create_start_list())]
        self.assertEqual(names, ["Курица", "Масло", "Молоко", "Рис", "Сахар",
                                 "Сыр", "Хлеб", "Чай", "Яблоки", "Яйца"])

    def test_str_and_repr(self):
        product = Product("Чай", 2, 100)
        self.assertEqual(str(product), "Чай: 2 шт. × 100.00 ₽ = 200.00 ₽")
        self.assertEqual(repr(product), "Product('Чай', 2, 100.0, False)")

    def test_key_value_map(self):
        products = KeyValueMap()
        products.put("a", 1)
        products.put("b", 2)
        products.put("a", 3)
        self.assertIn("a", products)
        self.assertEqual(products.find("a"), 3)
        self.assertIsNone(products.find("x"))
        products.delete("b")
        self.assertNotIn("b", products)
        self.assertEqual(list(products), [3])

        entries = products.entries
        self.assertEqual(entries, [("a", 3)])
        entries.append(("c", 4))
        self.assertNotIn("c", products)
        products.entries = [("x", 1), ("y", 2)]
        self.assertEqual(list(products), [1, 2])
        for bad_entries in ([("x",)], ["x"], [("x", 1), ("x", 2)]):
            with self.assertRaises(ValueError):
                products.entries = bad_entries
        self.assertEqual(products.entries, [("x", 1), ("y", 2)])

    def test_start_list_and_total(self):
        products = Product.create_start_list()
        self.assertEqual(len(products), 10)
        self.assertAlmostEqual(Product.total_cost(products), 1674.80)

    def test_report_table(self):
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "report.txt")
            for login in ("anna", "boris"):
                session = Session(login)
                session.finish()
                session.save(path)
            lines = Path(path).read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(lines), 7)
        borders = [[i for i, char in enumerate(line) if char in "+|"] for line in lines]
        self.assertEqual(borders, [borders[0]] * len(lines))
        self.assertEqual([len(line) for line in lines], [len(lines[0])] * len(lines))
        header = "| login           | time_in             | time_out            |"
        self.assertEqual(lines.count(header), 1)
        rows = [line for line in lines if line.startswith("|") and line != header]
        self.assertEqual(len(rows), 2)
        for row in rows:
            cells = [cell.strip() for cell in row.strip("|").split("|")]
            datetime.strptime(cells[1], DATE_FORMAT)
            datetime.strptime(cells[2], DATE_FORMAT)

    def test_no_dict_in_code(self):
        files = list(PROJECT.glob("*.py")) + list(PROJECT.glob("tests/*.py"))
        for path in files:
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                self.assertNotIsInstance(node, (ast.Dict, ast.DictComp), path.name)
                if isinstance(node, ast.Name):
                    self.assertNotEqual(node.id, "dict", path.name)
                if isinstance(node, ast.arguments):
                    self.assertIsNone(node.kwarg, path.name)
                if isinstance(node, ast.keyword):
                    self.assertIsNotNone(node.arg, path.name)

    def test_own_components(self):
        used = set(self.collect_types(ShoppingApp()))
        self.assertEqual(len(set(COMPONENTS)), 10)
        for component_class, flet_class in COMPONENTS:
            self.assertTrue(issubclass(component_class, flet_class))
            self.assertEqual(component_class.__init__.__qualname__,
                             component_class.__name__ + ".__init__")
            self.assertIn(component_class, used)

    def test_app_start_state(self):
        app = ShoppingApp()
        self.assertEqual(len(app.product_list.controls), 10)
        self.assertEqual(app.total_text.value, "Итого: 1674.80 ₽, куплено на: 0.00 ₽")

    def test_add_product(self):
        app = self.make_app()
        app.name_field.value = " Кофе "
        app.quantity_field.value = "2"
        app.price_field.value = "300.5"
        app.add_product(None)
        product = app.products.find("кофе")
        self.assertEqual((product.name, product.quantity, product.price), ("Кофе", 2, 300.5))
        self.assertEqual(len(app.product_list.controls), 11)
        names = [self.row_product(row).name for row in app.product_list.controls]
        self.assertEqual(names, sorted(names))
        self.assertEqual(app.total_text.value, "Итого: 2275.80 ₽, куплено на: 0.00 ₽")
        fields = (app.name_field.value, app.quantity_field.value, app.price_field.value)
        self.assertEqual(fields, ("", "1", ""))

    def test_add_product_errors(self):
        cases = [
            ("  ", "1", "10", "name_field", "Введите название"),
            ("молоко", "1", "10", "name_field", "Такой товар уже есть"),
            ("Кофе", "0", "10", "quantity_field", "Целое ≥ 1"),
            ("Кофе", "1", "", "price_field", "Число ≥ 0"),
            ("Кофе", "1", "-5", "price_field", "Число ≥ 0"),
        ]
        for name, quantity, price, field_name, message in cases:
            app = self.make_app()
            app.name_field.value = name
            app.quantity_field.value = quantity
            app.price_field.value = price
            app.add_product(None)
            self.assertEqual(getattr(app, field_name).error, message)
            self.assertEqual(len(app.product_list.controls), 10)
            self.assertEqual(app.name_field.value, name)

    def test_toggle_and_delete_product(self):
        app = self.make_app()
        checkbox = self.find_row(app, "Молоко").controls[0].content
        checkbox.value = True
        app.toggle_product(FakeEvent(checkbox))
        self.assertTrue(app.products.find("молоко").bought)
        self.assertTrue(self.find_row(app, "Молоко").controls[0].content.value)
        self.assertEqual(app.total_text.value, "Итого: 1674.80 ₽, куплено на: 179.80 ₽")

        delete_button = self.find_row(app, "Молоко").controls[-1]
        app.delete_product(FakeEvent(delete_button))
        self.assertNotIn("молоко", app.products)
        self.assertEqual(len(app.product_list.controls), 9)
        self.assertEqual(app.total_text.value, "Итого: 1495.00 ₽, куплено на: 0.00 ₽")

    def make_app(self):
        app = ShoppingApp()
        app.update = lambda: None  # без окна update() недоступен
        return app

    def row_product(self, row):
        return row.controls[0].content.data

    def find_row(self, app, name):
        for row in app.product_list.controls:
            if self.row_product(row).name == name:
                return row
        return None

    def collect_types(self, control):
        types = [type(control)]
        children = list(getattr(control, "controls", None) or [])
        if isinstance(getattr(control, "content", None), ft.Control):
            children.append(control.content)
        for child in children:
            types += self.collect_types(child)
        return types


if __name__ == "__main__":
    unittest.main()
