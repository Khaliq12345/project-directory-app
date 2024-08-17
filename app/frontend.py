from nicegui import ui
from fastapi import FastAPI
from pages import homepage, scrapepage

def header(self):
    ui.colors(primary='#00712D', info='#4158A6')
    with ui.header(elevated=True):
        with ui.row().classes('w-full grid lg:grid-cols-6 grid-cols-1'):
            with ui.element('div').classes('lg:col-start-2 lg:col-span-4 flex justify-between'):
                with ui.link(target='/').classes('no-underline text-white'):
                    ui.label("🎯 The STF pipeline pulse").classes('font-serif text-h5 max-lg:text-center')
                with ui.link(target='/scraper').classes('no-underline text-white'):
                    ui.label("🤖 Scraper").classes('font-serif text-h5 text-end')
                self.spinner = ui.spinner(size='lg', type='ball').props('color="white"')
                self.spinner.visible = False

def init(fastapi_app: FastAPI) -> None:
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
        
    ui.run_with(
        fastapi_app,
        title='The STF pipeline pulse',
        favicon='🎯',
        reconnect_timeout=10
    )