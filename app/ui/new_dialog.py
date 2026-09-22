from typing import Awaitable, Callable, cast
from types import SimpleNamespace

from pydantic import AnyHttpUrl, ValidationError
from nicegui import ui
from app.schemas.url import UrlMapCreateRequest

from app.ui.dialog import Dialog, DialogError

class NewLinkDialog(Dialog):
    """
    Dialog for adding new mapping between url and short link
    """
    def __init__(self, async_callback:Callable[[SimpleNamespace], Awaitable[DialogError|None]]|None = None) -> None:
        super().__init__(async_callback=async_callback)
        self.title = "New Link"
        self.action_title = "Save"

    def setup(self, form):
        form.link_input = ui.input(label='Short Link').classes('w-100')
        form.url_input = ui.input(label='URL').classes('w-100')

    def reset(self, form):
        form.url_input.value = ''
        form.link_input.value = ''

    async def validate(self, form) -> bool:
        # ensure all fields are filled in
        form.link_input.props(remove='error :error-message')
        form.url_input.props(remove='error :error-message')
        if not form.link_input.value or not form.url_input.value:
            self.notify_warning('Please fill out all fields')
            return False
        # validate our fields
        try:
            validated_data = UrlMapCreateRequest(
                url=cast(AnyHttpUrl, form.url_input.value),
                link=cast(str, form.link_input.value),
            )
            del validated_data
            return True
        except ValidationError as e:
            # Loop through Pydantic's structural error format
            for error in e.errors():
                field_name = error['loc'][0]
                error_msg = error['msg']
                
                # Highlight the correct field in NiceGUI
                if field_name == 'link':
                    form.link_input.props(f'error error-message="{error_msg}"')
                elif field_name == 'url':
                    form.url_input.props(f'error error-message="{error_msg}"')
            return False


