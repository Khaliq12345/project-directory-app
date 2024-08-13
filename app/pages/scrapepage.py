from nicegui import ui
from threading import Thread
from static import *
from bots import run as runner

#[adb, afd, caf, eib, iadb, ifad, mapafrica, opec, worldbank]


class ScraperPage():
    def __init__(self):
        self.num = 0
        self.to_scrape = []
    
    def script_engine(self):
        self.num = 0
        try:
            all_projects = []
            self.spinner.visible = True
            self.progress_ui.visible = True
            inc = 1/len(self.to_scrape)
            for i in self.to_scrape:
                runner.start_scripts([script_dict[i]], all_projects)
                self.num += inc
            runner.save_data(all_projects)
            self.spinner.visible = False
        except Exception as e:
            self.spinner.visible = False
            with self.notif_box:
                ui.notification(
                    message=f'Error: {e}', position='top',
                    type='negative', timeout=5, close_button=True
                )

    def start_script(self):
        Thread(target=self.script_engine).start()
    
    def main(self):
        with ui.column(align_items='center').classes('w-full justify-center'):
            ui.label('DIRECTORY SCRAPER')\
            .classes('flex text-h5 text-bold')
        ui.select(label='Choose the directory you want to update', options=directories, multiple=True)\
        .classes('w-full justify-center').props('use-chips').bind_value(self, 'to_scrape')
        with ui.row().classes('w-full justify-center'):
            ui.button("Start").props('unelevated').on_click(
                self.start_script
            )
            self.spinner = ui.spinner(size='md', type='tail')
            self.spinner.visible = False
        
        self.notif_box = ui.element('div')
        self.progress_ui = ui.linear_progress().bind_value(self, 'num').props('stripe rounded')
        self.progress_ui.visible = False