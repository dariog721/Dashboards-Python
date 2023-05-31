import dash 
from dash import dcc
import dash_bootstrap_components as dbc
from dash import html
import plotly.graph_objs as go 
import plotly.express as px
from dash.dependencies import Input, Output
import geopandas as gpd
import pycountry
import pandas as pd
import json 
from app import app


#app = dash.Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.LUX],
#             meta_tags=[{'name': 'viewport',
# 
#
#                         'content': 'width=device-width, initial-scale=1.0'}]
#             )
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
    return df_map

def avg(df_map,index1,index2=None):
    if index2 is not None :
        suicides_100mean=df_map.pivot_table(['population','suicides_no'],
        index=[index1,index2],aggfunc={'population':'sum','suicides_no':'sum'}).reset_index()
        suicides_100mean['population/100kreal'] = suicides_100mean.apply(lambda x: (x['suicides_no'] / x['population']*100000),
        axis=1)    
        return suicides_100mean    
    else: 
        suicides_100mean=df_map.pivot_table(['population','suicides_no'],
        index=[index1],aggfunc={'population':'sum','suicides_no':'sum'}).reset_index()
        suicides_100mean['population/100kreal'] = suicides_100mean.apply(lambda x: (x['suicides_no'] / x['population']*100000),
        axis=1)    
        return suicides_100mean

def filtsex1(df_map,col1,filt1):
    df_map_s = df_map[(df_map[col1] == filt1)]
    df_map1= mean(df_map_s,'year')
    return  df_map1
    
df = cleaning(df_suicide)
df_map = geocoding(df)
suicides_100mean = avg(df_map,'country','iso_a3')

fig = go.Figure(data=
    go.Choropleth(
    locations=suicides_100mean['iso_a3'],
    z=suicides_100mean['population/100kreal'],
    text=suicides_100mean['country'],
    colorscale='YlOrRd',
    autocolorscale=False,
    marker_line_color='white',
    marker_line_width=0.5,
    colorbar=dict(
        title='Suicides/100k pop',
        title_font=dict(color='black'),
        tickfont=dict(color='black'),
        thickness = 10,
        len = 0.5 )
))

fig.update_layout(
    #title_text='Suicidios por cada 100k personas por país',
    title_font_color = "black",
    title_x=0,
    geo=dict(
        showframe=False,
        showcoastlines=True,
        projection_type='equirectangular'
    ) ,height =800,
    #width =100%,
    paper_bgcolor="white"
)

#Layout
maps_layout = html.Div([
                html.H1('Suicidios Mundiales',
                style = {'textAlign':'center',
                    'color': colors['text']
                    
                }),
            
                html.H2('Por país',
                style = {'textAlign':'center',
                    'color': colors['text']
                    
                }),              
            
                html.Div([
                dcc.Graph(id='map',
                            figure = fig)], 
                            style={'width':'100','float':'center'
                            
                }),                                       
                html.Div([
                        dcc.Graph(id = 'tendencia'
                        )],
                        style = {'width':'100%','display':'inline-block'
               
                }) ,                    
                html.Div([
                        dcc.Graph(id = 'sex1')],
                        style = {'width':'33%','display':'inline-block'
                }),

                html.Div([
                        dcc.Graph(id = 'age1')],
                        style = {'width':'33%','display':'inline-block'
                }),

                html.Div([
                        dcc.Graph(id = 'generation1')],
                        style = {'width':'33%','display':'inline-block'
                }),
                html.Div([
                html.Pre(id='hover-data', style={'paddingTop':35}) 
                ], style={'width':'25%'}),
                    
              
            
                ], style={'backgroundColor': colors['background']})


@app.callback(                                                                                                              
    Output('tendencia', 'figure'),
    [Input('map', 'clickData')]) 
def callback_json1(clickData):
    v_index = clickData['points'][0]["text"]
    df = avg(df_map,'year','country')
    df = df[df['country'] == v_index ] 
 
    return {
        'data':[go.Scatter(x=df['year'],y=df['population/100kreal'],mode='lines',name=f'{v_index}',line=dict(color="#8B0000"))],

        'layout' : go.Layout(
            title=f'Evolucion del suicidio en {v_index}',
            xaxis=dict(title='Años'),
            yaxis=dict(title='Suicidios cada 100k personas')
            )}

@app.callback(
    Output('sex1', 'figure'),
    [Input('map', 'clickData')]) 
def get_graph22(clickData):
    v_index = clickData['points'][0]["text"]
    df_map1 = df_map[(df_map['country'] == v_index )]
    df_map1 = avg(df_map1,'sex')
    return px.pie(
        df_map1,values=df_map1['population/100kreal'],names=df_map1['sex'],
        title=f'Suicidios por genero en {v_index}'
        )
@app.callback(
    Output('age1', 'figure'),
    [Input('map', 'clickData')]) 
def get_graph32(clickData):
    v_index = clickData['points'][0]["text"]
    df_map1 = df_map[(df_map['country'] == v_index )]
    df_map1 = avg(df_map1,'age')

    return px.pie(
        df_map1,values=df_map1['population/100kreal'],names=df_map1['age'],
        title=f'Suicidios por edad en {v_index} '
        )

@app.callback(
    Output('generation1', 'figure'),
    [Input('map', 'clickData')]) 
def get_graph42(clickData):
    v_index = clickData['points'][0]["text"]
    df_map1 = df_map[(df_map['country'] == v_index )]
    df_map1 = avg(df_map1,'generation')
    return px.pie(
        df_map1,values=df_map1['population/100kreal'],names=df_map1['generation'],
        title=f'Suicidios por generacion en {v_index}'
        )




# if __name__ == '__main__':
#     app.run_server()