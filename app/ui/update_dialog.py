from typing import Awaitable, Callable, cast
from types import SimpleNamespace

from pydantic import AnyHttpUrl, ValidationError
from nicegui import ui

from app.schemas.url import UrlMapUpdateRequest

from app.ui.dialog import Dialog, DialogError

class EditLinkDialog(Dialog):
    """
    Dialog for adding new mapping between url and short link
    """
    def __init__(self, async_callback:Callable[[SimpleNamespace], Awaitable[DialogError|None]]|None = None) -> None:
        super().__init__(async_callback=async_callback)
        self.title = "Edit Link"
        self.action_title = "Save"
        self.url_value = ""
        self.link_value=""

    def set_values(self, url:str, link:str):
        self.url_value = url
        self.link_value = link

    def setup(self, form):
        # cannot edit link only url
        form.link_input = ui.input(label='Short Link', value=self.link_value).classes('w-20').props('readonly outlined')
        form.url_input = ui.input(label='URL', value=self.url_value).classes('w-100')

    def reset(self, form):
        form.url_input.value = ''
        form.link_input.value = ''

    async def validate(self, form) -> bool:
        # ensure all fields are filled in
        form.url_input.props(remove='error :error-message')
        if not form.url_input.value:
            self.notify_warning('Please fill out url field')
            return False
        # validate our fields
        try:
            validated_data = UrlMapUpdateRequest(
                url=cast(AnyHttpUrl, form.url_input.value)
            )
            del validated_data
            return True
        except ValidationError as e:
            # Loop through Pydantic's structural error format
            for error in e.errors():
                field_name = error['loc'][0]
                error_msg = error['msg']
                
                # Highlight the correct field in NiceGUI
                if field_name == 'url':
                    form.url_input.props(f'error error-message="{error_msg}"')
            return False


