from types import SimpleNamespace
from typing import Awaitable, Callable
from nicegui import ui

from app.ui.dialog import Dialog, DialogError

class DeleteLinkDialog(Dialog):
    """
    Dialog for adding new mapping between url and short link
    """
    def __init__(self, async_callback:Callable[[SimpleNamespace], Awaitable[DialogError|None]]|None = None) -> None:
        super().__init__(async_callback=async_callback)
        self.title = "Delete Link"
        self.action_title = "Delete"
        self.url_value = ""
        self.link_value=""

    def set_values(self, url:str, link:str):
        self.url_value = url
        self.link_value = link

    def setup(self, form):
        ui.label(text="Confirm deletion of the following link:")
        form.link_input = ui.input(label='Short Link', value=self.link_value).classes('w-20').props('readonly outlined')
        form.url_input = ui.input(label='URL', value=self.url_value).classes('w-100').props('readonly outlined')

    def reset(self, form):
        form.url_input.value = ''
        form.link_input.value = ''

    async def validate(self, form) -> bool:
        return True # nothing to validate


