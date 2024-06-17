import datetime
from jinja2 import Environment, FileSystemLoader, Template
import pandas as pd
import sqlite3
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import ssl
# from queries import provincial_irs, district_irs
import pdfkit
from random import getrandbits, randint
import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
# print(ROOT_DIR)


smtp_port = 587
smtp_server = "smtp.gmail.com"
gmail = "smeornmecz@gmail.com"
google_app_pass = "enup eadp cdxi aruw"
simple_email_context = ssl.create_default_context()

mail_to = ["mashkaponde@gmail.com","rkaponde@gmail.com", "reuben.kaponde@msi-inc.com"]

date = datetime.date.today()
current_year = datetime.datetime.now().year

con = sqlite3.connect("db/irs.db")

def make_report(con):
    # Load the data into a DataFrame
    provincial_df = pd.read_sql_query("select * from provincial_progress", con)
    # district_df = pd.read_sql_query("SELECT * from district_progress", con)
    # Load the district_irs.csv file into a DataFrame
    # district_df_csv = pd.read_csv('data/district_irs.csv')
    district_df_csv = pd.read_sql_query("select * from district_progress", con)

    # Convert the DataFrame to a dictionary
    provincial_data = {}
    for _, row in district_df_csv.iterrows():
        province = row['province']
        if province not in provincial_data:
            provincial_data[province] = []
        provincial_data[province].append(row.to_dict())

    # Ensure the dataframe is not empty and convert it to a dictionary
    if not provincial_df.empty:
        national_data = provincial_df.to_dict(orient='index')
    else:
        raise ValueError("Provincial DataFrame is empty!")

    sender_email = "smeornmecz@gmail.com"


    def format_with_commas(value):
        try:
            return "{:,}".format(value)
        except ValueError:
            return value

    data = {
            "subject": f"{current_year} IRS PROGRESS UPDATE",
            "greeting": f"Dear Yeah!",
            "sender_name": "NMEC SMEOR TEAM",
            'data': national_data,
            'provincial_data':provincial_data,
        }



    # Load the Jinja2 template
    env = Environment(loader=FileSystemLoader('templates'))
    env.filters['format_with_commas'] = format_with_commas

    template = env.get_template('email_temp2.html')

    # Render the template
    html_content = template.render(data)


    # # TEST WRITING TO PDF.

    # write the html to file
    with open(f"reports/report_{date}.html", 'wb') as file_:
        file_.write(html_content.encode("utf-8"))

    report_html = f"reports/report_{date}.html"

    #Define path to wkhtmltopdf.exe
    wkhtmltopdf_path = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
    wkhtmltopdf_config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)
    pdfkit.from_file(report_html, output_path=f"reports/report_{date}.pdf", configuration = wkhtmltopdf_config)



make_report(con)






