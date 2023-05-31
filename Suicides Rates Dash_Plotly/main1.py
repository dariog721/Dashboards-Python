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
from app import app
import dash_bootstrap_components as dbc
# app = dash.Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.LUX],
#                 meta_tags=[{'name': 'viewport',
#                             'content': 'width=device-width, initial-scale=1.0'}]
#                 )

colors = {
    "background" : "#FFFFFF",
    "text" : '#111111'
}  

#Datos 

df_suicide=pd.read_csv(r'D:\CODIGOS\Github\SUICIDES_RATES\Dash\master.csv')

def cleaning(df):
    df.drop(columns=['HDI for year','country-year'],inplace=True)
    df['country'].replace("Republic of Korea", "Korea, Republic of", inplace = True)
    df['country'].replace('Czech Republic', "Czechia", inplace = True)
    df['country'].replace('Macau', 'Macao', inplace = True)
    df['country'].replace('Saint Vincent and Grenadines', "Saint Vincent and the Grenadines", inplace = True)
    df_clean= (df)
    return df_clean
def geocoding(df):
    countries = {}
    for country in pycountry.countries:
        countries[country.name] = country.alpha_3
    world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
    cities = gpd.read_file(gpd.datasets.get_path('naturalearth_cities'))
    df_keys = pd.DataFrame(list(countries.items()), columns=['country', 'iso_a3'])
    df_suicide = df.merge(df_keys,how='inner',on='country')
    df_map = df_suicide.merge(world,how='inner',on='iso_a3')
    df_map = df_map[df_map['year'] != 2016]
    return df_map
def mean(df_map,index):  
    df_comp = df_map.pivot_table(['population','suicides_no'],
    index=[index],aggfunc={'population':'sum','suicides_no':'sum'}).reset_index()
    df_comp['population/100kreal'] = df_comp.apply(lambda x: ((x['suicides_no'] / x['population']) *100000),
    axis=1)    
    return df_comp
def filtsex1(df_map,col1,filt1):
    df_map_s = df_map[(df_map[col1] == filt1)]
    df_map1= mean(df_map_s,'year')
    return  df_map1

df = cleaning(df_suicide)
df_map = geocoding(df)

#Layout
mains = html.Div([
                        html.H2('Suicidios Mundiales',
                        style = {'textAlign':'center',
                            'color': colors['text']
                            
                        }),
                    
                        html.Div('Comportamiento del suicidio',
                        style = {'textAlign':'center',
                            'color': colors['text']
                            
                        }),          
                        html.Div( 
                                [dcc.RangeSlider(id = 'slider_main',
                                min=df_map['year'].min(),
                                max=df_map['year'].max(),
                                marks={str(i) : i for i in df_map['year'].unique()},
                                value=[df_map['year'].min(),df_map['year'].max()]
                            ),
                        ],style={'width':'100%','display':'inline-block'
                        }),
                    
                        html.Div([
                                dcc.Graph(id = 'timeline_main')],
                                style = {'width':'100%','display':'inline-block'
                        }),
                        html.Div([
                                dcc.Graph(id = 'timelinegender_main')],
                                style = {'width':'48%','display':'inline-block'
                        }),     
   
                        html.Div([
                                dcc.Graph(id = 'timelinegenderage_main')],
                                style = {'width':'48%','display':'inline-block'
                        }),

                        html.Div([
                                dcc.Graph(id = 'sex_main')],
                                style = {'width':'33%','display':'inline-block'
                        }),

                        html.Div([
                                dcc.Graph(id = 'age_main')],
                                style = {'width':'33%','display':'inline-block'
                        }),

                        html.Div([
                                dcc.Graph(id = 'generation_main')],
                                style = {'width':'33%','display':'inline-block'
                        })
                    
                        ], style={'backgroundColor': colors['background']} )
@app.callback(
    Output('timeline_main', 'figure'),
    [Input('slider_main', 'value')]) 
def get_graph_time(filt):
    df_comp1 = mean(df_map,'year')
    print(filt[0])
    df_comp1 = df_comp1[(df_comp1['year'] >= filt[0]) &( df_comp1['year'] <= filt[1])]

    return {
        'data' : [
            go.Scatter(
            x=df_comp1['year'],
            y=df_comp1['population/100kreal'],
            mode='lines'
            )],

        'layout' : go.Layout(
            title='Evolucion del suicidio de 1985-2015',
            xaxis=dict(title='Años'),
            yaxis=dict(title='data')
            )}

@app.callback(
    Output('timelinegender_main', 'figure'),
    [Input('slider_main', 'value')]) 
def get_graph_l1(filt):

    df_map_m = filtsex1(df_map,'sex','male') 
    df_map_f = filtsex1(df_map,'sex','female') 

    df_map_f = df_map_f[(df_map_f['year'] >= filt[0]) &( df_map_f['year'] <= filt[1])]
    df_map_m = df_map_m[(df_map_m['year'] >= filt[0]) &( df_map_m['year'] <= filt[1])]

    trace0 = go.Scatter(x=df_map_m['year'],y=df_map_m['population/100kreal'],mode='lines',name='Male')
    trace1 = go.Scatter(x=df_map_f['year'],y=df_map_f['population/100kreal'],mode='lines',name='Female')
    
    data = [trace0,trace1]
    return {
        'data' :data,

        'layout' : go.Layout(
            title='Evolucion del suicidio por genero',
            xaxis=dict(title='Años'),
            yaxis=dict(title='data')
            )}

@app.callback(
    Output('timelinegenderage_main', 'figure'),
    [Input('slider_main', 'value')]) 
def get_graph__Sl(filt):
    df_map_1 = filtsex1(df_map,'age','15-24 years') 
    df_comp1 = df_map_1[(df_map_1['year'] >= filt[0]) &( df_map_1['year'] <= filt[1])]
  
    df_map_2 = filtsex1(df_map,'age','35-54 years')
    df_comp2 = df_map_2[(df_map_2['year'] >= filt[0]) &(df_map_2['year'] <= filt[1])]

    df_map_3 = filtsex1(df_map,'age','75+ years')
    df_comp3 = df_map_3[(df_map_3['year'] >= filt[0]) &( df_map_3['year'] <= filt[1])]

    df_map_4 = filtsex1(df_map,'age','25-34 years')
    df_comp4 = df_map_4[(df_map_4['year'] >= filt[0]) &( df_map_4['year'] <= filt[1])]

    trace0 = go.Scatter(x=df_comp1['year'],y=df_comp1['population/100kreal'],mode='lines',name='15-24 years')
    trace1 = go.Scatter(x=df_comp2['year'],y=df_comp2['population/100kreal'],mode='lines',name='35-54 years')
    trace2 = go.Scatter(x=df_comp3['year'],y=df_comp3['population/100kreal'],mode='lines',name='75+ years')
    trace3 = go.Scatter(x=df_comp4['year'],y=df_comp4['population/100kreal'],mode='lines',name='25-34 years')
    data = [trace0,trace1,trace2,trace3]
    
    return {
        'data' :data,

        'layout' : go.Layout(
            title='Evolucion del suicidio por edad',
            xaxis=dict(title='Años'),
            yaxis=dict(title='data')
            )}


@app.callback(
    Output('sex_main', 'figure'),
    [Input('slider_main', 'value')]) 
def get_graph_sex(filt):
    df_map1 = df_map[(df_map['year'] >= filt[0] )&(df_map['year'] <= filt[1])]
    df_map1 = mean(df_map1,'sex')
    return px.pie(
        df_map1,values=df_map1['population/100kreal'],names=df_map1['sex'],
        title=f'Suicidios por genero {filt[0]} a {filt[1]}'
        )
@app.callback(
    Output('age_main', 'figure'),
    [Input('slider_main', 'value')]) 
def get_graph2_age(filt):
    df_map1 = df_map[(df_map['year'] >= filt[0] )&(df_map['year'] <= filt[1])]
    df_map1 = mean(df_map1,'age')

    return px.pie(
        df_map1,values=df_map1['population/100kreal'],names=df_map1['age'],
        title=f'Suicidios por edad {filt[0]} a {filt[1]}'
        )

@app.callback(
    Output('generation_main', 'figure'),
    [Input('slider_main', 'value')]) 
def get_graph_gen(filt):
    df_map1 = df_map[(df_map['year'] >= filt[0] )&(df_map['year'] <= filt[1])]
    df_map1 = mean(df_map1,'generation')

    return px.pie(
        df_map1,values=df_map1['population/100kreal'],names=df_map1['generation'],
        title=f'Suicidios por generacion {filt[0]} a {filt[1]}'
        )
# if __name__ == '__main__':
#     app.run_server()