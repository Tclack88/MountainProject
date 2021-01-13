import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_daq as daq
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
from textwrap import dedent as d
import visdcc
import plotly.graph_objs as go
from joblib import load
import numpy as np
import json

from app import app

# import data
energy_codes = pd.read_csv('assets/energy_codes.csv')
data = pd.read_csv('assets/power_plants_human_readable.csv')
model = load('assets/ridge_regression_model.joblib')


# set invisible grid for lat/lon selection (us counties)
def clean_coordinates(latlon):
  latlon = latlon[:-1]
  if latlon[0] == '+':
    return float(latlon[1:])
  elif latlon[0] == '–':
    return -1*float(latlon[1:])

county_url = "https://en.wikipedia.org/wiki/User:Michael_J/County_table"
counties = pd.read_html(county_url)[0]
counties.Latitude = counties.Latitude.apply(clean_coordinates)
counties.Longitude = counties.Longitude.apply(clean_coordinates)


# Main plot
color_map = dict(zip(energy_codes['Energy Source Description'],energy_codes.color))
hover_name = 'plant_type'
hover_data = ['prime_mover','total_power']

customdata=counties['Sort [1]']

data2 = [go.Scattermapbox(lat=[0], lon=[0], mode='markers', marker=dict(size=8))]

mapbox_access_token = 'pk.eyJ1IjoiZXRwaW5hcmQiLCJhIjoiY2luMHIzdHE0MGFxNXVubTRxczZ2YmUxaCJ9.hwWZful0U2CQxit4ItNsiQ'
layout = go.Layout(hovermode='closest', width=1000,height=800,mapbox=dict(bearing=0,
    center=dict(lat=38.8484, lon=-98.921),
    pitch=0,zoom=3.2,accesstoken=mapbox_access_token,style = 'stamen-watercolor'))
fig = dict(data=data2, layout=layout)

# original map creation
#fig = px.scatter_mapbox(data_frame = counties,lat = 'Latitude',lon = 'Longitude',zoom=3.2,opacity=0)#,customdata='Sort [1]')
#fig.update_layout(mapbox_style = "stamen-watercolor",showlegend=False, width = 1000, height = 600)#,paper_bgcolor = 'papayawhip')


# Dropdown selection
plant_type_list = sorted(list(data.plant_type.unique()))

energy_sources_list = [ list(data[data['plant_type'] == plant_type].energy_source.unique()) for plant_type in plant_type_list]

plant_type__energy_dict = dict(zip(plant_type_list,energy_sources_list))



### Layouts
column1 = dbc.Col([
        
    dcc.Markdown(
            """
            ## Predictions
            """
            ),
        
        
    html.Label('Select plant type'),
   

    dcc.Dropdown(
        id = 'plant-type-dropdown',
        options = [{'label':plant_type,'value':plant_type} for plant_type in plant_type_list],
        placeholder = 'Select plant Type...'
        ),

    html.Br(),
        
    dcc.Dropdown(
        id = 'energy-source-dropdown',
        placeholder = 'Select energy source...'),
    
    html.Br(),

    dcc.Dropdown(
        id = 'prime-mover-dropdown',
        placeholder = 'Select prime mover...'),

    html.Hr(),
    html.Label('Set number of generators and year built',style={'display':'inline-block'} ),
    dcc.Slider(id='number-generators-slider',
        min = 1,
        max = 200,
        step = 1,
        value = 10,
        marks = {'10':'10','50':'50','100':'100','200':'200'}),
    html.Br(),
    html.P('10',id='number-generators-selected'),

    html.Br(),

    html.P('Year',style={'display':'inline-block'}),
    daq.NumericInput(id='year-built',
        value = 2020,
        min = 1880,
        max = 2025,
        style={'display':'inline-block'}),


    html.Hr(),

    html.Label('Set location:',style={'display':'inline-block'} ),

    html.H5('LongLat:   ',id='lnglat-display'),

    html.Br(),
    html.Hr(),

    html.Label('This plant\'s predicted power:',style={'display':'inline-block'} ),
    html.H5('Power (MegaWatts)',id='power-display'),

    ],md=4
)


live_lat_lon_style = {'textAlign':'right'}

column2 = dbc.Col(
    [
        dcc.Graph(id='graph',figure=fig),
        visdcc.Run_js(id = 'javascript'),

        html.H5('lat,long',id='live-lat-lon',style =live_lat_lon_style ),
        visdcc.Run_js(id = 'javascript2')
    ],md=8
)
 


layout = dbc.Row([column1, column2])




@app.callback(
        Output('energy-source-dropdown','options'),
        [Input('plant-type-dropdown','value')])
def update_energy_source_dropdown(option):
    return [{'label': source,'value':source} for source in plant_type__energy_dict[option]]

@app.callback(
        Output('prime-mover-dropdown','options'),
        [Input('plant-type-dropdown','value'),Input('energy-source-dropdown','value')])
def update_prime_mover_dropdown(plant,energy):
    #gp = data.groupby(['plant_type','energy_source']).prime_mover
    #choice_list = list(gp.groups.keys())
    prime_mover_list = list(data[(data.plant_type == plant) & (data.energy_source == energy)].prime_mover.unique())
    return [{'label':pm, 'value':pm} for pm in prime_mover_list]


# Part of an old solution
# @app.callback(
#     Output('relayout-data', 'children'),
#     [Input('basic-interactions', 'relayoutData')])
# def display_relayout_data(clickData):
#     return json.dumps(clickData, indent=2)

# @app.callback(
#          Output('relayout-data','children'),
#          [Input('plot','relayoutData')])
# def visualize(figure):
#     string =  str(figure['layout'].update(dict(mapbox = dict(center = dict (lat = relayoutData['mapbox.center']['Latitude'], lon = relayoutData['mapbox.center']['Longitude'] ), zoom = relayoutData["mapbox.zoom"]))))
#     string = 'newstring'
#     print(string)
#     return string
 

# @app.callback(
#     dash.dependencies.Output('display-lat-lon', 'children'),
#     [dash.dependencies.Input('map', 'hoverData')])
# def update_text(hoverData):
#     s = counties[counties['Sort [1]'] == hoverData['points'][0]['customdata']]
#     return html.P(f'lat: {s.iloc[0]["Latitude"]},\tlon: {s.iloc[0]["Longitude"]}')

@app.callback(
        Output('number-generators-selected','children'),
        [Input('number-generators-slider','value')])
def change_generator_number(value):
    return value


@app.callback(
    Output('javascript', 'run'),
    [Input('graph', 'id')])
def getlnglat(x):
    if x:
        return(
        '''
            let map1 = document.getElementById('graph')
            let map = map1._fullLayout.mapbox._subplot.map
            map.on('click', function(e) {
            let lngLat = e.lngLat
            setProps({'event': {lon: lngLat.lng.toFixed(3), lat: lngLat.lat.toFixed(3)}})
            })
        
        ''')
    return ""


@app.callback(
    Output('lnglat-display', 'children'),
    [Input('javascript', 'event')])
def showlnglat(event):
    if event:
        return f'Lon:{event["lon"]} Lat:{event["lat"]} '
    return 'Get location by hovering over the map'




@app.callback(
    Output('javascript2', 'run'),
    [Input('graph', 'id')])
def getlnglat(x):
    if x:
        return(
        '''
            let map1 = document.getElementById('graph')
            let map = map1._fullLayout.mapbox._subplot.map
            map.on('mousemove', function(e) {
            let lngLat = e.lngLat
            setProps({'event': {lon: lngLat.lng.toFixed(3), lat: lngLat.lat.toFixed(3)}})
            })

        ''')
    return ""


@app.callback(
    Output('live-lat-lon', 'children'),
    [Input('javascript2', 'event')])
def showlnglat(event):
    if event:
        return f'Lon:{event["lon"]} Lat:{event["lat"]} '
    return 'Select location by clicking on the map'







@app.callback(
        Output('power-display','children'),
        [Input('plant-type-dropdown','value'),
            Input('energy-source-dropdown','value'),
            Input('prime-mover-dropdown','value'),
            Input('year-built','value'),
            Input('lnglat-display','children'),
            Input('number-generators-selected','children')
        ])
def display_power(pt,es,pm,year,coords,n):
    coords = coords.split()
    lat = float(coords[1][4:])
    lon = float(coords[0][4:])
    sample = [[pt,es,pm,int(year),float(lat),float(lon),int(n)]]
    sample2 = [pt,es,pm,str(year),lat,lon,str(n)]
    cols = data.columns.drop(['total_power','power_encoded'])
    predict_df = pd.DataFrame(sample,columns = cols)
    prediction =  np.expm1(model.predict(predict_df)[0])
    return f'{prediction:,.2f} MW'



@app.callback(
        Output('graph','figure'),
        [Input('javascript','event'),
            Input('energy-source-dropdown','value')])
def update_pointer(event,en_src):
    data = [go.Scattermapbox(lat=[38.8484], lon=[-98.921],
        mode='markers', marker=dict(size=8))]
    if event:
        color = color_map[en_src]
        data = [go.Scattermapbox(lat=[event["lat"]], lon=[event["lon"]],
        mode='markers', marker=dict(size=20,color=color), text = [en_src])]

    layout = go.Layout(hovermode='closest', width=1000,height=800,mapbox=dict(bearing=0,
    center=dict(lat=38.8484, lon=-98.921),
    pitch=0,zoom=3.2,accesstoken=mapbox_access_token,style = 'stamen-watercolor'))
    
    fig = dict(data=data, layout=layout)
    return fig

