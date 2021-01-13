import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import numpy as np
from app import app

"""
https://dash-bootstrap-components.opensource.faculty.ai/l/components/layout

Layout in Bootstrap is controlled using the grid system. The Bootstrap grid has 
twelve columns.

There are three main layout components in dash-bootstrap-components: Container, 
Row, and Col.

The layout of your app should be built as a series of rows of columns.

We set md=4 indicating that on a 'medium' sized or larger screen each column 
should take up a third of the width. Since we don't specify behaviour on 
smaller size screens Bootstrap will allow the rows to wrap so as not to squash 
the content.
"""

column1 = dbc.Col(
    [
        dcc.Markdown(
            """
        
            ## Climbing pyramid

            Learn about your progress, link your mountain project ticks

           """
        ),
        dcc.Link(dbc.Button('Try It Out!', color='primary'), href='/pyramid')
    ],
    md=4,
)


# energy_codes = pd.read_csv('assets/energy_codes.csv')
# data = pd.read_csv('assets/power_plants_human_readable.csv')
# 
# # map fuel colors to intuitive colors
# color_map = dict(zip(energy_codes['Energy Source Description'],energy_codes.color))
# # hover data
# hover_name = 'plant_type'
# hover_data = ['prime_mover','total_power']
# 
# title='The current U.S. power layout. Zoom around, find your local power plants!'
# 
# fig = px.scatter_mapbox(data_frame = data, lat = 'lat', lon = 'lon', size = 'total_power', color = 'energy_source',color_discrete_map = color_map,zoom=3.2,hover_data=hover_data,hover_name = hover_name,size_max = 25)
# 
# 
# fig.update_layout(mapbox_style = "stamen-watercolor",showlegend=False,title=title, width = 1000, height = 600)
# 

# column2 = dbc.Col(
#     [
#         dcc.Graph(figure=fig),
#         ],md=8
# )

#layout = dbc.Row([column1, column2])
layout = dbc.Row([column1])
