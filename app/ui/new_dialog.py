from typing import cast

from pydantic import AnyHttpUrl, ValidationError
from nicegui import ui
from app.schemas.url import UrlMapCreateRequest

async def create_new_dialog(save_row_callback=None):
    with ui.dialog() as dialog, ui.card().classes('w-80'):
        ui.label('Add New Link').classes('text-lg font-bold')

        # Input fields to capture user data
        url_input = ui.input(label='URL')
        link_input = ui.input(label='Short Link')

        with ui.row().classes('justify-end w-full'):
            ui.button('Cancel', on_click=dialog.close).props('flat')

            # Save button triggers row insertion
            async def save_row():
                link_input.props(remove='error :error-message')
                url_input.props(remove='error :error-message')
                if link_input.value and url_input.value:
                    try:
                        validated_data = UrlMapCreateRequest(
                            url=cast(AnyHttpUrl, url_input.value),
                            link=cast(str, link_input.value),
                        )
                        del validated_data

                        # Add a new dictionary structure matching your columns
                        if save_row_callback:
                            print("has callback")
                            await save_row_callback(link_input.value, url_input.value)
                        # Clear fields and close the modal
                        link_input.value = ''
                        url_input.value = ''
                        dialog.close()
                    except ValidationError as e:
                        # Loop through Pydantic's structural error format
                        for error in e.errors():
                            field_name = error['loc'][0]
                            error_msg = error['msg']
                            
                            # Highlight the correct field in NiceGUI
                            if field_name == 'link':
                                link_input.props(f'error error-message="{error_msg}"')
                            elif field_name == 'url':
                                url_input.props(f'error error-message="{error_msg}"')
                else:
                    ui.notify('Please fill out all fields', type='warning')

            ui.button('Save', on_click=save_row)
        return dialog