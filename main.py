import getpass
from pathlib import Path

import flet as ft

from models import Session
from ui import ShoppingApp

REPORT_FILE = Path(__file__).parent / "report.txt"

if __name__ == "__main__":
    session = Session(getpass.getuser())
    try:
        ft.run(ShoppingApp.open_window)
    finally:
        session.finish()
        session.save(REPORT_FILE)
