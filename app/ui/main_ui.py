from nicegui import APIRouter, ui
from app.dependencies import repo

# Initialize the NiceGUI router
async def main_page():
    columns = [
        {"name": "link", "label": "link", "field": "link"},
        {"name": "url", "label": "URL", "field": "url"},
        {"name": "created", "label": "created", "field": "created"},
    ]
    rows_per_page = 2

    # Load initial data from the database
    initial_rows = await repo.list_all()

    # Create the table element
    table = ui.table(columns=columns, rows=initial_rows, row_key='id').classes('w-full items-stretch')
    table._props["pagination"] = {"rowsPerPage": rows_per_page, "page": 1}
    async def refresh_data():
            table.rows = await repo.list_all()
            ui.notify('Data refreshed!')
    with ui.header().classes('bg-blue-500 text-white p-4 items-center'):
        ui.label('Url Shortener').classes('text-h6')
        ui.space()
        ui.button(icon="sync", on_click=refresh_data).classes('q-mt-md').props('flat dense color=white')
        ui.button(icon="add", on_click=refresh_data).classes('q-mt-md').props('flat dense color=white')
        ui.button(icon="settings", on_click=lambda: ui.navigate.to('../docs')).classes('q-mt-md').props('flat dense color=white')





