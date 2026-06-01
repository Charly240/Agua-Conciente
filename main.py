import flet as ft
from login import mostrar_login


def main(page: ft.Page):
    page.title = "Agua Consciente"
    page.bgcolor = ft.Colors.BLUE_GREY_50
    page.padding = 0
    page.scroll = ft.ScrollMode.AUTO

    mostrar_login(page)


ft.app(target=main)