import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import json
import streamlit as st

import altair as alt

from bokeh.plotting import figure

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
            ))
        AS avg_per_day
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

uploaded_file = st.file_uploader('Upload your chat log (JSON-format only)', type='json')
if (uploaded_file is not None):
     data = json.loads(uploaded_file.read())
     messages = pd.json_normalize(data, record_path =['messages'])
     messages = messages.drop(columns = ['text', 'id']) #messages are not analyzed
     messages = messages.rename(columns={'from': 'name'})
     con = sqlite3.connect('db')
     messages.to_sql('messages', con, index=False, if_exists='replace')
     #frequency per month
     freq = select(sql_freq)
     p = figure(x_range=freq['month'], height=350, title='Overall trend', toolbar_location=None, tools='')
     p.line(x=freq['month'], y=freq['num'], legend_label='number of messages', color='blue', line_width=2)
     p.legend.location = 'top_left'
     p.xgrid.grid_line_color = None
     p.y_range.start = 0
     st.bokeh_chart(p)
     #number of messages
     mdata = select(sql_overall)
     p = figure(x_range=mdata['n'], height=350, title='Number of messages', toolbar_location=None, tools='')
     p.vbar(x=mdata['n'], top=mdata['c'], width=0.9)
     p.xgrid.grid_line_color = None
     p.y_range.start = 0
     st.bokeh_chart(p)
     #average per day per month
     average_per_day = select(sql_average_per_day)
     p = figure(x_range=average_per_day['month'], height=350, title='Average number of messages per day per month',
            toolbar_location=None, tools='')
     p.vbar(x=average_per_day['month'], top=average_per_day['avg_per_day'], width=0.9)
     p.xgrid.grid_line_color = None
     p.y_range.start = 0
     st.bokeh_chart(p)
     #average per weekday
     weekday = select(sql_week)
     p = figure(x_range=weekday['day_of_week'], height=350, title='Number of messages per day of week', toolbar_location=None, tools='')
     p.vbar(x=weekday['day_of_week'], top=weekday['count'], width=0.9)
     p.xgrid.grid_line_color = None
     p.y_range.start = 0
     st.bokeh_chart(p)
     #average per weekday pie chart
     altchart = alt.Chart(weekday).mark_arc().encode(theta=alt.Theta(field='count',
                    type='quantitative'),
                    color=alt.Color(field='day_of_week',
                    type='nominal'),)
     st.altair_chart(altchart, use_container_width=True)
