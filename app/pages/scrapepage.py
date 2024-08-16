from nicegui import ui
from threading import Thread
from static import *
from bots import run as runner
import pandas as pd
from sqlalchemy import create_engine
import config
import smtplib
from dateparser import parse
from email.message import EmailMessage

#[adb, afd, caf, eib, iadb, ifad, mapafrica, opec, worldbank]


class ScraperPage():
    def __init__(self):
        self.num = 0
        self.to_scrape = []
        self.countries = []
        self.tdate_string = "None"
        self.new_data = pd.DataFrame()

    def send_email(self, message, from_email, to_email):
        msg_dict = EmailMessage()
        msg_dict['Subject'] = "NEW DEAL"
        msg_dict['From'] = from_email
        msg_dict['To'] = to_email
        msg_dict.set_content(message)
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()
        s.login(config.login_email, config.passwd)
        s.send_message(msg_dict)
        s.quit()

    def make_message(self, unique_df):
        msgs = []
        for idx, row in unique_df.iterrows():
            txt = f"\n\
            ------------------------------------------\n\n\
            Title: {row['title']}\n\
            Project Link: {row['project_url']}\n\
            Country: {row['countries']}\n"
            msgs.append(txt)
        return '\n '.join(msgs)
    
    def get_unique_data_based_on_countries(self, c_list: list[str], unique_df: pd.DataFrame):
        saved_index = []
        for x in c_list:
            idx = unique_df[unique_df['countries'].str.lower().str.contains(x.lower())].index
            [saved_index.append(x) for x in idx]

        return unique_df[unique_df.index.isin(saved_index)]
    
    def send_message(self):
        unique_df = self.new_data[self.new_data['date'] >= self.tdate]
        unique_df = unique_df[unique_df['date'] <= parse('now').strftime("%Y-%m-%d")]
        unique_df_c = self.get_unique_data_based_on_countries(self.countries, unique_df)
        if not unique_df_c.empty:
            msg = self.make_message(unique_df_c)
            self.send_email(msg, config.from_email, config.to_email)
            with self.notif_box:
                ui.notification(
                    message=f'EMAIL SENT', position='top',
                    type='info', timeout=5, close_button=True
                )
        else:
            with self.notif_box:
                ui.notification(
                    message=f'No new deals for the select countries', position='top',
                    type='info', timeout=5, close_button=True
                )
    
    def email_notif_handler(self):
        if self.tdate_string and len(self.countries) > 0:
            tdate = parse(self.tdate_string)
            if tdate:
                self.tdate = tdate.strftime("%Y-%m-%d")
                print("Sending message")
                self.send_message()
                print("EMAIL SENT!")
    
    def script_engine(self):
        self.num = 0
        try:
            all_projects = []
            self.spinner.visible = True
            self.progress_ui.visible = True
            inc = 1/len(self.to_scrape) if len(self.to_scrape) > 0 else 1
            for i in self.to_scrape:
                runner.start_scripts([script_dict[i]], all_projects)
                self.num += inc
            self.new_data = pd.DataFrame(all_projects)
            runner.save_data(self.new_data)
            self.email_notif_handler()
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
        ui.query('body').style('background-color: #F1DEC6;')
        with ui.column(align_items='center').classes('w-full justify-center'):
            ui.label('DIRECTORY SCRAPER')\
            .classes('flex text-h5 text-bold')
        ui.select(label='Choose the directory you want to update', options=directories, multiple=True)\
        .classes('w-full justify-center').props('use-chips stack-label').bind_value(self, 'to_scrape')
        
        with ui.row().classes('w-full grid grid-cols-3'):
            ui.select(label='Choose the countries for the email notification', options=[], multiple=True, new_value_mode='add-unique')\
            .classes('w-full justify-center col-span-2').props('hide-dropdown-icon use-input use-chips stack-label')\
            .bind_value(self, 'countries')
            
            ui.input("Date range").props('stack-label type="date"').classes('col-span-1').bind_value(self, 'tdate_string')
        
        with ui.row().classes('w-full justify-center'):
            ui.button("Start").props('unelevated').on_click(
                self.start_script
            )
            self.spinner = ui.spinner(size='md', type='tail')
            self.spinner.visible = False
        
        self.notif_box = ui.element('div')
        self.progress_ui = ui.linear_progress().bind_value(self, 'num').props('stripe rounded')
        self.progress_ui.visible = False