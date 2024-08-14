from nicegui import ui
from static import *
from sqlalchemy import create_engine, select, and_
import pandas as pd
import app_model
from threading import Thread
import pandas as pd
import config

def make_the_special_query(values, column):
    queries = []
    for x in values:
        new_q = f"(app_model.Project.{column}.ilike('%{x}%'))"
        queries.append(new_q)
    query = '|'.join(queries)
    return query

def date_filter_checker(filter_values, date_str):
    if filter_values.get(date_str) and len(filter_values.get(date_str)) > 0:
        return True
    else:
        return False

def make_date_query(filter_values):
    match [date_filter_checker(filter_values, 'date_from'), date_filter_checker(filter_values, 'date_to')]:
        case [True, True]:
            q = and_(
                app_model.Project.date >= filter_values['date_from'],
                app_model.Project.date <= filter_values['date_to'],
            )
            return q
        case [True, False]:
            q = and_(
                app_model.Project.date >= filter_values['date_from'],
            )
            return q    
        case [False, True]:
            q = and_(
                app_model.Project.date <= filter_values['date_to'],
            )
            return q
        case [False, False]:
            return False

def set_value(self, value, key):
    self.filter_values[key] = value

def dataloader_engine(self, stmt):
    self.spinner.visible = True
    self.total_data = get_total_data_count(self, stmt)
    stmt = stmt.limit(10).offset(10*self.pagination_num)
    with self.engine.connect() as con:
        self.dataframe = pd.read_sql(stmt, con=con)
        self.listing_ui()
        self.spinner.visible = False
    self.pagination_ui.refresh()

def dataloader(self, stmt):
    task = Thread(target=dataloader_engine, args=(self, stmt))
    task.start()
    
def get_total_data_count(self, stmt):
    with self.engine.connect() as con:
        df = pd.read_sql(stmt, con=con)
        return round(len(df)/10)


class HomePage:
    def __init__(self):
        self.filter_values = {}
        self.engine = create_engine(config.connection_string)
        self.dataframe = pd.DataFrame()
        self.pagination_num = 0
        self.total_data = None
        self.filtered_data = []
        self.stmt = select(app_model.Project)
        
    def clear_filters(self):
        self.pagination_num = 0
        self.filter_ui.refresh()
        self.stmt = select(app_model.Project)
        self.dataframe = dataloader(self, self.stmt)
        
    def start_filtering(self):
        print('Filtering')
        print(self.filter_values)
        self.pagination_num = 0
        self.expansion.value = False
        self.stmt = select(app_model.Project)
        for x in self.filter_values:
            if len(self.filter_values[x]) > 0:
                match x:
                    case 'country':
                        query = make_the_special_query(self.filter_values[x], 'countries')
                        self.stmt = self.stmt.where(eval(query))
                    case 'status':
                        query = make_the_special_query(self.filter_values[x], 'status')
                        self.stmt = self.stmt.where(eval(query))
                    case 'sector':
                        query = make_the_special_query(self.filter_values[x], 'sectors')
                        self.stmt = self.stmt.where(eval(query))
                    case 'directory':
                        self.stmt = self.stmt.where(app_model.Project.directory.in_(self.filter_values[x]))
                    case 'date_from':
                        date_query = make_date_query(self.filter_values)
                        if date_query != False:
                            self.stmt = self.stmt.where(date_query)
                    case 'date_to':
                        date_query = make_date_query(self.filter_values)
                        if date_query != False:
                            self.stmt = self.stmt.where(date_query)
        dataloader(self, self.stmt)

    def get_next_data(self, num):
        self.pagination_num = num
        dataloader(self, self.stmt)

    @ui.refreshable
    def pagination_ui(self):        
        self.pagination_box.clear()
        with self.pagination_box:
            ui.pagination(0, self.total_data, direction_links=True, value=self.pagination_num)\
                .classes('flex w-full justify-center').on_value_change(
                lambda e: self.get_next_data(e.value)
            ).props('boundary-links :max-pages="5"')

    @ui.refreshable
    def filter_ui(self):
        with ui.expansion('Filters').classes('w-full')\
        .props('header-class="text-bold text-black text-center text-h5"') as self.expansion:
            with ui.element('div').classes('w-full flex flex-col space-y-3 lg:justify-center'):
                for filter_name in filter_names:
                    if filter_name == 'directory':
                        ui.select(options=directories, label=filter_name.title(), multiple=True)\
                        .props('hide-dropdown-icon use-chips behavior="dialog"')\
                            .on_value_change(
                            lambda e, key=filter_name: set_value(self, e.value, key)
                        )
                    elif filter_name == 'date':
                        with ui.row().classes('w-full grid grid-cols-2'):
                            ui.input("From").props('stack-label outlined type="date"').classes('w-full').\
                                on_value_change(
                                    lambda e: set_value(self, e.value, 'date_from')
                                )
                            ui.input("To").props('stack-label outlined type="date"').classes('w-full').\
                                on_value_change(
                                    lambda e: set_value(self, e.value, 'date_to')
                                )
                    else:
                        ui.select(options=[], label=filter_name.title(), multiple=True, new_value_mode='add-unique')\
                        .props('hide-dropdown-icon use-input use-chips')\
                            .on_value_change(
                            lambda e, key=filter_name: set_value(self, e.value, key)
                        )
                with ui.button_group().props('unelevated').classes('w-full'):
                    ui.button('Search').on_click(
                        self.start_filtering
                    ).classes('w-full')
                    ui.button('Clear').on_click(
                        self.clear_filters
                    ).classes('w-full')
        
    def listing_ui(self):
        self.listing_box.clear()
        with self.listing_box:
            with ui.element('div').classes('w-full lg:col-start-2 lg:col-span-4 space-y-3 mt-5'):
                ui.label(f'Project Listings').classes('text-5 flex w-full justify-center')
                ui.separator()
                for idx, row in self.dataframe.iterrows():
                    with ui.card().classes('bg-transparent').props('flat bordered'):
                        with ui.card_section():
                            with ui.link(target=row['project_url'], new_tab=True):
                                ui.label(row['title']).classes('text-h6')
                            ui.label(f"Country - {row['countries']}").classes('text-h8 font-mono')
                            ui.label(f"Sectors - {row['sectors']}").classes('text-h8 font-mono')
                            ui.label(f"Status - {row['status']}").classes('text-h8 font-mono')
                            ui.label(f"Directory - {row['directory']}").classes('text-h8 font-mono')
                            ui.label(f"Date - {row['date']}").classes('text-h8 font-mono')
                            
                    #ui.separator()
            
    def main(self):
        ui.query('body').style('background-color: #bfc2c7;')
        self.body = ui.query('body').element
        self.filter_ui()
        self.listing_box = ui.row().classes('w-full h-full grid lg:grid-cols-6 grid-cols-1 bg-white')
        self.pagination_box = ui.element('div').classes('flex w-full justify-center')
        self.stmt = select(app_model.Project)
        dataloader(self, self.stmt)
        self.pagination_ui()

        