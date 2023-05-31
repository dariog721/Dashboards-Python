import dash_bootstrap_components as dbc
import dash 
from dash import dcc
from dash import html
import plotly.graph_objs as go 
import plotly.express as px
from dash.dependencies import Input, Output
import geopandas as gpd
import pycountry
import pandas as pd
import json     
from maps import maps_layout
from main1 import mains
from app import app 

app_tabs = html.Div([
    html.H2('Selecciona la pestaña'),
    dcc.Tabs(id="tabsp", value='tab-2', children=[
        dcc.Tab(label='Suicidios por país', id='tab-1'),
        dcc.Tab(label='Suicidios mundiales', id='tab-2'),
    ]),
    html.Div(id='tabs-content')
])


app.layout = dbc.Container([
    dbc.Row(dbc.Col(html.H1("Dashboard Suicidios Mundiales",
                            style={"textAlign": "center"}), width=12)),
    html.Hr(),
    dbc.Row(dbc.Col(app_tabs, width=12), className="mb-3"),
    html.Div(id='content', children=[])

])

@app.callback(Output('content', 'children'),
              Input('tabsp', 'value'))
def render_content(tab):
    if tab == 'tab-1':    
        return maps_layout
    elif tab == 'tab-2':
        return mains

        
if __name__=='__main__':
    app.run_server()