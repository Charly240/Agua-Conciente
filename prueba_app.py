import flet as ft
from app import mostrar_app


def main(page: ft.Page):
    page.title = "Agua Consciente"
    page.bgcolor = ft.Colors.GREY_50
    page.padding = 0
    page.scroll = ft.ScrollMode.AUTO

    mostrar_app(page, "Usuario de prueba")


ft.app(target=main)