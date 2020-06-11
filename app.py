import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from analyzis import mapa, cumulative, growth



app = dash.Dash(__name__)
server = app.server


app.layout = html.Div(children = [
    html.H1('Coronavirus Analysis and Visualization'),
    html.H2('Map animation'),
    dcc.Graph(
        id='map',
        figure=mapa,
        className = 'testowo'
    ),
    html.H2('Cumulative sick curve'), 
    dcc.Graph(
        id='cumulative',
        figure=cumulative
    ),
    html.H2('Daily increase curve'),
    dcc.Graph(
        id='growth',
        figure=growth
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)
