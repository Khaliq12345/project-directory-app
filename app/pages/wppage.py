from nicegui import ui, app
from io import BytesIO
from wordpresser import bot
from threading import Thread
import config

class Wp:
    def __init__(self):
        self.is_bulk = False
        self.end_date = None
        self.content = None
        self.logs = 'No logs'
        self.api_value = None
    
    def check_api(self):
        app.storage.user['logged_in'] = self.api_value
        print(app.storage.user)
        ui.navigate.reload()
    
    def engine(self, func):
        try:
            self.logs = '<h5>Getting the categories</h5>'
            categories = bot.get_categories()
            self.logs += '<h5>Parsing Documents</h5>'
            all_posts = func(self.end_date, self.content)
            self.logs += f'<h5>Sending to wordpress {len(all_posts)} posts</h5>'
            for idx, post in enumerate(all_posts):
                self.logs += f'<h5>Article {idx + 1}</h5>'
                bot.send_to_wordpress(post, categories)
        except Exception as e:
            self.send_notif(e, 'negative')
        #return all_posts
    
    def handle_upload(self, e):
        content = BytesIO(e.content.read())
        self.content = content
        #doc = Document(content)
        # print(doc)
        #print(len(doc.paragraphs))

    def start_upload_engine(self):
        try:
            self.spinner.visible = True
            self.log_expander.value = True
            if self.is_bulk:
                if self.end_date == None:
                    self.send_notif('You must select an end date if bulk uploading', n_type='info')
                else:
                    self.engine(eval('bot.bulk_parse_document'))
            else:
                self.engine(eval('bot.parse_document'))
        except Exception as e:
            self.send_notif(e, n_type='error')
        finally:
            self.spinner.visible = False
    
    def start_upload(self):
        if self.content == None:
            self.send_notif('Document is empty', n_type='info')
        else:
            task = Thread(target=self.start_upload_engine)
            task.start()

    def send_notif(self, msg, n_type):
        with self.body:
            ui.notification(
            message=msg, 
            type=n_type,
            multi_line=True,
            timeout=5,
            close_button=True,
            position='top'
        )
    
    def main(self):
        ui.query('body').style('background-color: #F1DEC6;')
        self.body = ui.query('body').element
        with ui.column().classes('xl:grid xl:grid-cols-4 w-full'):
            with ui.column(align_items='center').classes('xl:col-start-2 xl:col-span-2 w-full justify-center'):
                ui.label('WORDPRESS UPLOADER').classes('flex text-h5 text-bold')
                with ui.expansion('Instructions').props('header-class="text-center"').classes('w-full'):
                    ui.label('''
                    Upload only a docx file and check the "Is Bulk Upload" button if you are uploading more than a day worth of article.
                    You must input a start date for bulk upload and optional for single upload. If you add a start date for single upload, 
                    the publish date on wordpress will be the date you input and not the current date.
                    ''').props('multi-line').classes('text-center w-full')
        
        with ui.column().classes('xl:grid xl:grid-cols-4 w-full'):
            with ui.row().classes('xl:col-start-2 xl:col-span-2 w-full'):
                with ui.element('div').classes('w-full flex justify-center') as self.api_ui:
                    ui.input('API KEY', password=True, password_toggle_button=True)\
                    .classes('w-full mb-2').bind_value(self, 'api_value')
                    ui.button('Login').on_click(self.check_api)
                
                if app.storage.user.get('logged_in'):
                    if app.storage.user.get('logged_in') == config.api_key:
                        self.api_ui.visible = False
                        ui.upload(
                        label='UPLOAD YOUR DOCX FILE(s)', auto_upload=True,
                        on_upload=self.handle_upload).classes('w-full').props('accept=".docx" flat')
                        with ui.row(align_items='center').classes('w-full justify-around'):
                            ui.checkbox('Is Bulk Upload').bind_value(self, 'is_bulk')
                            ui.input('End Date').props('type="date" stack-label clearable').bind_value(self, 'end_date')
                            ui.button('Start Upload').props('unelevated').on_click(self.start_upload)
                        with ui.row().classes('w-full'):
                            with ui.expansion('Uploading Logs', icon='info')\
                            .classes('w-full bg-cyan-600 header-class="text-h5 text-center w-full"') as self.log_expander:
                                with ui.scroll_area().classes('w-full h-40 border'):
                                    ui.html('No logs').bind_content(self, 'logs')
                    else:
                        self.send_notif('Wrong API KEY', n_type='negative')