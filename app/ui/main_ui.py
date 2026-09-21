from nicegui import APIRouter, ui
from app.dependencies import repo
from app.ui.new_dialog import create_new_dialog
async def load_data(hostname):
    rows = await repo.list_all()
    print(rows)
    for r in rows:
         r["link_url"]=hostname+r["link"]
    return rows
     

async def main_page():
    hostname =  str(ui.context.client.request.base_url)
    columns = [
        {"name": "link", "label": "link", "field": "link"},
        {"name": "url", "label": "URL", "field": "url"},
        {"name": "created", "label": "created", "field": "created"},
    ]

    # Load initial data from the database
    initial_rows = await load_data(hostname=hostname)
    # Create the table element
    table = ui.table(columns=columns, rows=initial_rows, row_key='id').classes('w-full items-stretch')
    #rows_per_page = 2
    # table._props["pagination"] = {"rowsPerPage": rows_per_page, "page": 1}
    with table.add_slot('body-cell-link'):
        with table.cell('link'):
            ui.link().props(':innerHTML=props.value :href=props.row.link_url')
    async def refresh_data():
            table.rows = await load_data(hostname=hostname)
            ui.notify('Data refreshed!')
    async def new_data(link_input, url_input):
        # try:
        print("add ", link_input, url_input)
        await repo.add_new_url_and_link(link=link_input, url=url_input)
        table.rows = await load_data(hostname=hostname)
        ui.notify(f'{link_input} created')

    with ui.header().classes('bg-blue-500 text-white p-4 items-center'):
        ui.label('Url Shortener').classes('text-h6')
        ui.space()
        ui.button(icon="sync", on_click=refresh_data).classes('q-mt-md').props('flat dense color=white')
        ui.button(icon="settings", on_click=lambda: ui.navigate.to('../docs')).classes('q-mt-md').props('flat dense color=white')
    new_dialog = await create_new_dialog(new_data)
    ui.button('Add', on_click=new_dialog.open).props('fab icon=add').classes('fixed bottom-4 right-4')





