import os, pathlib, sys
current_dir = os.getcwd()
dir_to_add = pathlib.Path(current_dir).parent.as_posix()
sys.path.append(dir_to_add)
sys.path.append(f'{current_dir}/pages')
sys.path.append(f'{current_dir}/bots')
sys.path.append(f'{current_dir}/wordpresser')
sys.path.append(f'{dir_to_add}/app')
from nicegui import ui
from pages import homepage, scrapepage, wppage

def header(self):
    ui.colors(primary='#00712D', info='#179BAE')
    with ui.header(elevated=True):
        with ui.row().classes('w-full grid lg:grid-cols-6 grid-cols-1'):
            with ui.element('div').classes('lg:col-start-2 lg:col-span-4 flex justify-between'):
                with ui.link(target='/').classes('no-underline text-white'):
                    ui.label("🎯 The STF pipeline pulse").classes('font-serif text-h5 max-lg:text-center')
                with ui.link(target='/scraper').classes('md:no-underline text-white max-md:hidden'):
                    ui.label("🤖 Scraper").classes('font-serif text-h5 text-end')
                with ui.link(target='/wp_uploader').classes('md:no-underline text-white max-md:hidden'):
                    ui.label("⬆️ WP Uploader").classes('font-serif text-h5 text-end')
                #small screen
                with ui.link(target='/scraper').classes('text-white md:hidden'):
                    with ui.icon("smart_toy", size='lg'):
                        ui.tooltip('Scraper').classes('font-serif text-h5')
                with ui.link(target='/wp_uploader').classes('text-white md:hidden'):
                    with ui.icon("upload", size='lg'):
                        ui.tooltip('Wp Uploader').classes('font-serif text-h6')
                self.spinner = ui.spinner(size='lg', type='ball').props('color="white"')
                self.spinner.visible = False 

@ui.page('/')
def home_p():
    home_page = homepage.HomePage()
    header(home_page)
    home_page.main()
    
@ui.page('/scraper')
def scrape_p():
    scrape_page = scrapepage.ScraperPage()
    header(scrape_page)
    scrape_page.main()

@ui.page('/wp_uploader')
def wordpress_p():
    wp_page = wppage.Wp()
    header(wp_page)
    wp_page.main()
    
ui.run(
    host='0.0.0.0',
    port=2100,
    title='The STF pipeline pulse',
    favicon='🎯',
    reconnect_timeout=10,
    storage_secret='my_app'
)