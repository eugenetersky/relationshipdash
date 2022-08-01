import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import json
import streamlit as st

from bokeh.plotting import figure
from bokeh.plotting import figure, output_file, show
from bokeh.io import output_file, show
from bokeh.models import ColumnDataSource, FactorRange
from bokeh.palettes import GnBu3, OrRd3

sql_freq = '''
        SELECT SUBSTR('JanFebMarAprMayJunJulAugSepOctNovDec', 1 + 3*STRFTIME('%m', t.date), -3) AS month,
            COUNT(t.from_id) AS num
        FROM messages AS t
        WHERE t.from_id IS NOT NULL AND t.date >= '2022-01-01'
        GROUP BY STRFTIME('%m', t.date)
        ORDER BY STRFTIME('%m', t.date)
'''

sql_overall = '''
        SELECT count(*) as c, t.name as n
        FROM messages AS t
        WHERE t.date >= '2022-01-01' 
            AND t.from_id IS NOT NULL
        GROUP by 2
'''

sql_average_per_day = '''
        SELECT SUBSTR('JanFebMarAprMayJunJulAugSepOctNovDec', 1 + 3*STRFTIME('%m', t.date), -3) AS month,
            COUNT(t.name) / 
                STRFTIME(
                    '%d', 
                DATE(
                t.date,
        'start of month',
        '+1 month',
        '-1 day'
        )) AS avg_per_day
        FROM messages AS t
        WHERE t.from_id IS NOT NULL AND t.date >= '2022-01-01'
        GROUP BY STRFTIME('%m', t.date)
'''

sql_week = '''
        SELECT SUBSTR('SunMonTueWedThuFriSatSun', 4 + 3*STRFTIME('%w', t.date), -3) AS day_of_week, COUNT(*) AS count
        FROM messages AS t
        WHERE t.from_id IS NOT NULL AND t.date >= '2022-01-01'
        GROUP BY STRFTIME('%w', t.date)
'''

sql_per_month = '''
        SELECT t.name AS name, SUBSTR('JanFebMarAprMayJunJulAugSepOctNovDec', 1 + 3*STRFTIME('%m', t.date), -3) AS month,
                COUNT(t.name) AS num
        FROM messages AS t
        WHERE t.from_id IS NOT NULL AND t.date >= '2022-01-01'
        GROUP BY t.name, STRFTIME('%m', t.date)
        ORDER BY STRFTIME('%m', t.date)
'''

def select(sql):
  return pd.read_sql(sql, con)

st.title('Relationship Dashboard 2022')

st.markdown('''
[How to download Telegram chat history](https://www.techmesto.com/backup-or-export-telegram-chats/)

Note: this app will only analyze chat history starting from 1st of January 2022
''')

uploaded_file = st.file_uploader("Upload your chat log (JSON-format only)", type='json')
if uploaded_file is not None:
     #dataframe = pd.read_csv(uploaded_file)
     data = json.loads(uploaded_file.read())
     messages = pd.json_normalize(data, record_path =['messages'])
     messages = messages.drop(columns = ['text', 'id'])
     messages = messages.rename(columns={"from": "name"})
     con = sqlite3.connect("db")
     messages.to_sql("messages", con, index=False, if_exists="replace")
     #frequency per month
     freq = select(sql_freq)
     num = freq['num']
     months = freq['month']
     p = figure(x_range=months, height=350, title="Overall trend", toolbar_location=None, tools="")
     #p.vbar(x=months, top=num, width=0.9)
     p.line(x=months, y=num, legend_label="number of messages", color="blue", line_width=2)
     p.legend.location = "top_left"
     p.xgrid.grid_line_color = None
     p.y_range.start = 0
     st.bokeh_chart(p)
     #number of messages
     mdata = select(sql_overall)
     names = mdata['n']
     counts = mdata['c']
     p = figure(x_range=names, height=350, title="Number of messages", toolbar_location=None, tools="")
     p.vbar(x=names, top=counts, width=0.9)
     p.xgrid.grid_line_color = None
     p.y_range.start = 0
     st.bokeh_chart(p)
     #average per day per month
     average_per_day = select(sql_average_per_day)
     avg = average_per_day['avg_per_day']
     months = average_per_day['month']
     p = figure(x_range=months, height=350, title="Average number of messages per day per month", toolbar_location=None, tools="")
     p.vbar(x=months, top=avg, width=0.9)
     p.xgrid.grid_line_color = None
     p.y_range.start = 0
     st.bokeh_chart(p)
     #average per weekday
     weekday = select(sql_week)
     wdays_count = weekday['count']
     wdays = weekday['day_of_week']
     p = figure(x_range=wdays, height=350, title="Number of messages per day of week", toolbar_location=None, tools="")
     p.vbar(x=wdays, top=wdays_count, width=0.9)
     p.xgrid.grid_line_color = None
     p.y_range.start = 0
     st.bokeh_chart(p)
