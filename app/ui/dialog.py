from abc import ABC, abstractmethod
from types import SimpleNamespace
from typing import Awaitable, Callable


from nicegui import ui

class DialogError:
    """
    utility class to pass error
    we use this instead of string to allow future expansion of what info to be returned from callback
    """
    def __init__(self, message:str) -> None:
        self.message = message


class Dialog(ABC):
    def __init__(self, async_callback:Callable[[SimpleNamespace], Awaitable[DialogError|None]]|None = None) -> None:
        self.title = "Dialog"
        self.cancel_title="Cancel"
        self.action_title="Ok"
        self.form = SimpleNamespace()
        self.async_callback = async_callback
    @abstractmethod
    def setup(self, form):
        """
        Setup dialog fields here
        """
    @abstractmethod
    def reset(self, form):
        """
        reset dialogs fields
        """
    @abstractmethod
    async def validate(self, form) -> bool:
        """
        validate form 
        return False if validation failed
        """
    async def action(self, form)->bool:
        """
        """
        result = None
        if self.async_callback:
            result=await self.async_callback(form)
        if result:
            self.notify_warning(result.message)
            return False
        return True # close dialog

    def show(self) -> None:
        """
        show dialog
        """
        print("SHOW")
        with ui.dialog() as dialog, ui.card().classes('w-120'):
            ui.label(self.title).classes('text-lg font-bold')
            self.setup(self.form)
            async def handle_action():
                if await self.validate(self.form) and await self.action(self.form):
                    self.reset(self.form)
                    dialog.close()
            with ui.row().classes('justify-end w-full'):
                ui.button(self.cancel_title, on_click=dialog.close).props('flat')
                ui.button(self.action_title, on_click=handle_action)
            dialog.open()


    def notify_warning(self, warning):
        """
        notify warning
        """    
        ui.notify(warning, type='warning')