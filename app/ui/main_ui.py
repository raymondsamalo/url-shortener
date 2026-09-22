from nicegui import ui
from sqlalchemy import exc
from app.dependencies import repo
from app.ui.dialog import DialogError
from app.ui.new_dialog import NewLinkDialog
from app.ui.update_dialog import EditLinkDialog
from app.util.logger import get_module_logger
logger = get_module_logger(__name__)
async def load_data(hostname):
    rows = await repo.list_all()
    print(rows)
    for r in rows:
         r["link_url"]=hostname+r["link"]
    return rows
     

async def main_page():
    hostname =  str(ui.context.client.request.base_url)
    columns = [
        {"name": "link", "label": "Link", "field": "link", 'align':'left'},
        {"name": "url", "label": "URL", "field": "url", 'align':'left'},
        {"name": "created", "label": "Created", "field": "created", 'align':'right'},
        {'name': 'actions', 'label': 'Actions', 'align': 'center'},
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
    async def new_data(form)->DialogError|None:
        link_input = form.link_input.value
        url_input  = form.url_input.value
        try:
            await repo.add_new_url_and_link(link=link_input, url=url_input)
            table.rows = await load_data(hostname=hostname)
            ui.notify(f'{link_input} created')
        except exc.IntegrityError as e:
            logger.exception(e)
            return DialogError("Link already existed")
        except exc.OperationalError as e:
            logger.exception(e)
            return DialogError("Database error, please retry")
        except exc.SQLAlchemyError as e:
            logger.exception(e)
            return DialogError("Unknown Database error, please retry")

    async def edit_data(form)->DialogError|None:
        link_input = form.link_input.value
        url_input  = form.url_input.value
        try:
            await repo.update_url_for_link(link=link_input, url=url_input)
            table.rows = await load_data(hostname=hostname)
            ui.notify(f'{link_input} updated')
        except exc.IntegrityError as e:
            logger.exception(e)
            return DialogError("Link already existed")
        except exc.OperationalError as e:
            logger.exception(e)
            return DialogError("Database error, please retry")
        except exc.SQLAlchemyError as e:
            logger.exception(e)
            return DialogError("Unknown Database error, please retry")


    def handle_delete(link: str):
        """Filters out the target row by its unique name and refreshes the table."""
        ui.notify(f'Deleted {link}')

    def open_edit_dialog(link: str, url:str):
        ui.notify(f'Edit {link} -> {url}')
        edit_dialog = EditLinkDialog(edit_data)
        edit_dialog.set_previous_value(link=link, url=url)
        edit_dialog.show() 

    with table.add_slot('body-cell-actions'):
        with table.cell('actions'):
            # ui.row keeps the buttons neatly aligned next to each other
            with ui.row().classes('items-center justify-center no-wrap gap-2'):
                
                # Edit Button
                ui.button(icon='edit').props('flat dense color=primary').on(
                    'click',
                    js_handler='() => emit(props.row.link,props.row.url)',
                    handler=lambda e: open_edit_dialog(e.args[0], e.args[1])
                )
                
                # Delete Button
                ui.button(icon='delete').props('flat dense color=negative').on(
                    'click',
                    js_handler='() => emit(props.row.link)',
                    handler=lambda e: handle_delete(e.args)
                )



    with ui.header().classes('bg-blue-500 text-white p-4 items-center'):
        ui.label('Url Shortener').classes('text-h6')
        ui.space()
        ui.button(icon="sync", on_click=refresh_data).classes('q-mt-md').props('flat dense color=white')
        ui.button(icon="settings", on_click=lambda: ui.navigate.to('../docs')).classes('q-mt-md').props('flat dense color=white')


    new_dialog = NewLinkDialog(new_data) 
    ui.button('Add', on_click=new_dialog.show).props('fab icon=add').classes('fixed bottom-4 right-4')





