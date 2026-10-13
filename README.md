# Shopping List

Учебный проект по ООП на Python и Flet — список покупок.

Можно добавить товар с количеством и ценой, отметить купленные товары, удалить товар и увидеть общую стоимость и стоимость купленного. При запуске в списке 10 стартовых товаров.

При закрытии окна в файл `report.txt` дописывается строка таблицы с полями `login`, `time_in`, `time_out`.

## Требования

- Python 3.12
- Flet 1.0.4 (десктопный режим)
- При первом запуске Flet скачивает клиент окна, поэтому нужен интернет.

## Установка

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Запуск

```bash
python main.py
```

Закрывайте окно крестиком — после этого записывается отчёт.

## Тесты

```bash
python -m unittest discover -v
```

## Файлы

- `models.py` — классы `Entity`, `Product`, `Session`, `KeyValueMap`
- `ui.py` — десять компонентов интерфейса и окно `ShoppingApp`
- `main.py` — запуск приложения и запись отчёта
- `tests/test_requirements.py` — тесты
