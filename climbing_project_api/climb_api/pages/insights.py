import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from app import app

# Import data
data = pd.read_csv("assets/power_plants_human_readable.csv")
energy_codes = pd.read_csv("assets/energy_codes.csv")

# setup and create figure 1
color_map = dict(zip(energy_codes['Energy Source Description'],energy_codes.color))
# energy_source_net_power = data.groupby('energy_source').total_power.sum().sort_values(ascending=False).reset_index()
# subgroup = energy_source_net_power
# fig = px.bar(subgroup[:15], x= 'total_power', y='energy_source',orientation = 'h',
#              color = 'energy_source', color_discrete_map = color_map,
#              title = 'Natural gas provides as much power to the U.S. <br>      as the next 6 leading energy sources')
# fig.update_traces(marker_line_color='#000000', marker_line_width=1.5, showlegend=False)
# 
# # create figure 2
# energy_source_net_power2 = data[data.year_built < 1980].groupby('energy_source').total_power.sum().sort_values(ascending=False).reset_index()
# subgroup2 = energy_source_net_power2
# 
# fig2 = px.bar(subgroup2[:15], x= 'total_power', y='energy_source',orientation = 'h',
#              color = 'energy_source', color_discrete_map = color_map,
#              title = 'Current power plants in the 1980s (retired plants not included)')
# fig2.update_traces(marker_line_color='#000000', marker_line_width=1.5, showlegend=False)
# 
# # create figure 3
# energy_source_net_power3 = data[data.year_built < 1960].groupby('energy_source').total_power.sum().sort_values(ascending=False).reset_index()
# subgroup3 = energy_source_net_power3
# 
# fig3 = px.bar(subgroup3[:15], x= 'total_power', y='energy_source',orientation = 'h',
#              color = 'energy_source', color_discrete_map = color_map,
#              title = 'Current power plants in the 1960s (retired plants not included)')
# fig3.update_traces(marker_line_color='#000000', marker_line_width=1.5, showlegend=False)

energy_source_net_power = data.groupby('energy_source').total_power.sum().sort_values(ascending=False).reset_index()

subgroup = energy_source_net_power[:14]
x = subgroup.total_power
y = subgroup.energy_source
fig = go.Figure(go.Bar(
            x=x,
            y=y,
            orientation='h',
            marker_color=subgroup.energy_source.map(color_map))
            )
fig.update_traces(marker_line_color='#000000', marker_line_width=1.5, showlegend=False)



column1 = dbc.Col(
    [
        dcc.Markdown(
            """
            ## Insights


            - Hydroelectric power is old and still going strong

            Hydroelectric power both as an immediate source and as pumped to heights forenergy storage (blue - pumping energy for reversible) is among the oldest sources of energy, many of the original plants built in the early 18th century are still active today.

            - A hope for Nuclear?

            It's a shame that very few nuclear plants have been built since the 80s
            s (only 5 and one since the turn of the century) as they have the biggest power density. Despite this, as of 2019 it's the second leading source of raw power.

            - Renewable energy is on the rise! 

            As technologies such as wind, solar, geothermal and even biomass catch up to displace coal (black) and petroleum products (purple), there's hope for a carbon free future.


            """

        ),
    ],
    md=4,
)


column2 = dbc.Col(
    [
        dcc.Graph(id='bar-chart',figure=fig),
        #dcc.Graph(id='graph2',figure=fig2),
        #dcc.Graph(id='graph3',figure=fig3)

        dcc.Slider(id='year-slider',
            min=1900,
            max = 2020,
            step = 1,
            value = 2020,
            marks = {str(yr) : str(yr) for yr in range(1900,2030,10)}),
        html.Br(),
        html.Br(),
        html.Label('year:',style={'display':'inline-block'}),
        html.Label('-------',style={'display':'inline-block','color':'white'}),
        html.P('2019',id='selected-year',style={'display':'inline-block'})
    ]
)

layout = dbc.Row([column1, column2])

@app.callback(
        Output('bar-chart','figure'),
        [Input('year-slider','value')])
def update_plot(year):
    current_data = data[data.year_built <= year]
    energy_source_net_power = current_data.groupby('energy_source').total_power.sum().sort_values(ascending=False).reset_index()

    subgroup = energy_source_net_power[:14]
    x = subgroup.total_power
    y = subgroup.energy_source
    fig = go.Figure(go.Bar(
        x=x,
        y=y,
        orientation='h',
        marker_color=subgroup.energy_source.map(color_map)))
    fig.update_traces(marker_line_color='#000000', marker_line_width=1.5, showlegend=False)
    return fig

@app.callback(
        Output('selected-year','children'),
        [Input('year-slider','value')])
def update_year(year):
    return year
