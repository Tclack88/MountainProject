import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_daq as daq
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import plotly.express as px
import pandas as pd
#from textwrap import dedent as d
import visdcc
import plotly.graph_objs as go
import numpy as np
import json
import networkx as nx
from app import app
# import data
from assets.pyramid_class import *

### Layouts
column1 = dbc.Col([
        
    dcc.Markdown(
            """
            ## Make Your Pyramid
            """
            ),
         
         
    html.Label('Insert URL from Mountain Project'),
    
 
    html.Br(),

    dcc.Input(
        id = 'ticks-url',
        placeholder = 'ex: "mountainproject.com/user/1234567/first-last/tick-export"',
        size = '50',
        ),
    
    html.Br(),

    dcc.Checklist(
        id='style',
        options=[
            {'label':'sport', 'value':'sport'},
            {'label':'trad', 'value':'trad'}
            ],
        value=['sport','trad'],
        style={'display':'inline-block'}),

    html.Br(),

    html.Div(
        [dcc.Dropdown(
            id = 'location-dropdown-1',
            placeholder = 'Narrow down location')
        ], style={'display':'none'}, id='location-1-div',
    ),

    html.Br(),

    html.Div(
        [dcc.Dropdown(
            id = 'location-dropdown-2',
            placeholder = 'Narrow down location')
        ], style={'display':'none'}, id='location-2-div',
    ),

    html.Br(),

     html.Div(
        [dcc.Dropdown(
            id = 'location-dropdown-3',
            placeholder = 'Narrow down location')
        ], style={'display':'none'}, id='location-3-div',
    ),

    html.Br(),

    html.Div(
        [dcc.Dropdown(
            id = 'location-dropdown-4',
            placeholder = 'Narrow down location')
        ], style={'display':'none'}, id='location-4-div',
    ),

    html.Br(),

    html.Div(
        [dcc.Dropdown(
            id = 'location-dropdown-5',
            placeholder = 'Narrow down location')
        ], style={'display':'none'}, id='location-5-div',
    ),


    html.Br(),
    #html.Button(id='submit', n_clicks=0, children='Make Pyramid!',color='primary')
    dbc.Button('Make Pyramid', color='primary', id='submit', type='submit', n_clicks=0)
    ])
 
# placeholder Triangle Figure"
fig = go.Figure(go.Scatter(x=[0,1,2,0], y=[0,2,0,0], fill="toself"))
fig.update_layout(title_text="No Info Yet")

column2 = dbc.Col(
        [
            #html.Img(src=app.get_asset_url('placeholder.png'))
            dcc.Graph(
                id='pyramid',
                figure=fig)
            ]
        )
layout = dbc.Row([column1,column2])

@app.callback(
        Output('pyramid','figure'),
        [Input('submit','n_clicks'), # I think button click is fixed
         State('ticks-url', 'value'),
         State('style','value'),
         State('location-dropdown-1','value'),
         State('location-dropdown-2','value'),
         State('location-dropdown-3','value'),
         State('location-dropdown-4','value')])

def make_pyramid(n_clicks,url,style,
        location1=None,location2=None,location3=None,location4=None):
    if url is None:
        raise PreventUpdate
    else:
        location_choices = []
        if location1:
            location_choices.append(location1)
        if location2:
            location_choices.append(location2)
        if location3:
            location_choices.append(location3)
        if location4:
            location_choices.append(location4)
        print(location_choices)
        document = str(url)
        P = Pyramid(document,location_choices)
        fig = P.show_pyramids(style)
        return fig

# Populate dropdowns

# LOCATION 1
@app.callback(
        Output(component_id='location-1-div', component_property='style'),
        [Input('ticks-url', 'value')])
def show_location1(url):
    #print(P.climber)
    if url is None:
        raise PreventUpdate
    else:
        document = str(url)
        location_list = pd.read_csv(document).Location.unique()
        if any(location_list):
            return {'display':'inline'}
        else:
            return {'display':'none'}

@app.callback(
        Output('location-dropdown-1','options'),
        [Input('submit','n_clicks'), # I think button click is fixed
         State('ticks-url', 'value')])
def update_location_dropdown1(n_clicks, url):
    if url is None:
        raise PreventUpdate
    else:
        document = str(url)
        #global LOCATION_LIST # make accessible by other dropdowns
        location_list = pd.read_csv(document).Location.unique()
        top = []
        edge_list = []
        node_list = []
        for l in location_list:
            sub_list = l.split(' > ')
            first_item = sub_list[0]
            if not first_item in top:
                top.append(first_item)
            for i in range(0, len(sub_list)):
                if not sub_list[i] in node_list:
                    node_list.append(sub_list[i])
                if i == len(sub_list)-1:
                    break

                pair = '>'.join([sub_list[i],sub_list[i+1]])
                if not pair in edge_list:
                    edge_list.append(pair)
        # make global graphs object with all this
        global G # G is graph object that contains all areas + sub-areas
        G = nx.DiGraph()
        for node in node_list:
            G.add_node(node)
        for edge in edge_list:
            source, child = edge.split('>')
            G.add_edge(source,child)
        return [{'label': choice,'value':choice} for choice in top]


# LOCATION 2
@app.callback(
        Output(component_id='location-2-div', component_property='style'),
        [Input('location-dropdown-1', 'value')])
def show_location2(location1):
    if location1:
        return {'display':'inline'}
    else:
        return {'display':'none'}

@app.callback(
        Output('location-dropdown-2','options'),
        [Input('location-dropdown-1','value')])
def update_location_dropdown2(location1):
    if location1 is None:
        raise PreventUpdate
    else:
        options = G.successors(location1)
        return [{'label': option,'value':option} for option in options]

# LOCATION 3
@app.callback(
        Output(component_id='location-3-div', component_property='style'),
        [Input('location-dropdown-2', 'value')])
def show_location3(location2):
    if location2:
        return {'display':'inline'}
    else:
        return {'display':'none'}

@app.callback(
        Output('location-dropdown-3','options'),
        [Input('location-dropdown-2','value')])
def update_location_dropdown3(location2):
    if location2 is None:
        raise PreventUpdate
    else:
        options = G.successors(location2)
        return [{'label': option,'value':option} for option in options]

# LOCATION 4
@app.callback(
        Output(component_id='location-4-div', component_property='style'),
        [Input('location-dropdown-3', 'value')])
def show_location4(location3):
    if location3:
        return {'display':'inline'}
    else:
        return {'display':'none'}

@app.callback(
        Output('location-dropdown-4','options'),
        [Input('location-dropdown-3','value')])
def update_location_dropdown4(location3):
    if location3 is None:
        raise PreventUpdate
    else:
        options = G.successors(location3)
        return [{'label': option,'value':option} for option in options]
