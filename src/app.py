from dash import Dash, dcc, html, dash_table
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
from datetime import datetime
import pandas as pd
import numpy as np

# Load data from CSV files
real_2d = np.loadtxt('real2d.csv', delimiter=',')
pred_2d = np.loadtxt('pred2d.csv', delimiter=',')
HP_TIME_BINS = pd.read_csv('HP_TIME_BINS.csv', header=None).iloc[:, 0].tolist()

# Load the features data
FEATURES = pd.read_csv('features.csv', parse_dates=['Date'])

app = Dash(__name__)
server = app.server

app.layout = html.Div([
    html.H1("Data Visualization and Value Retrieval"),
    dcc.RadioItems(
        id='data-type-radio',
        options=[
            {'label': 'Real Data', 'value': 'real'},
            {'label': 'Predicted Data', 'value': 'pred'}
        ],
        value='pred',
        style={'marginBottom': 20}
    ),
    html.Div([
        html.Label('Date:'),
        dcc.DatePickerSingle(
            id='date-input',
            date=FEATURES['Date'].dt.strftime('%Y-%m-%d').iloc[0],
            style={'marginRight': '10px'}
        ),
        
        html.Label('Heater profile time:'),
        dcc.Input(id='hp-time-bin', type='number', value=0, style={'marginRight': '10px'}),
        
        html.Button('Submit', id='submit-val', n_clicks=0)
    ], style={'marginBottom': 20}),
    
    html.Div(id='output-value'),
    
    dcc.Graph(id='3d-plot', style={'width': '100%', 'height': '800px'})
])

@app.callback(
    Output('3d-plot', 'figure'),
    Input('data-type-radio', 'value')
)
def update_graph(selected_data_type):
    z_data = real_2d if selected_data_type == 'real' else pred_2d
    # Prepare custom hover text
    text = [[f'Date: {FEATURES["Date"].iloc[i].strftime("%Y-%m-%d")}<br>HP Time Bin: {HP_TIME_BINS[j]}<br>Value: {z_data[j][i]:.2f}'
             for i in range(len(FEATURES['Date']))] for j in range(len(HP_TIME_BINS))]

    # Create the surface plot with custom hover text
    fig = go.Figure(data=[go.Surface(z=z_data, x=FEATURES['Date'], y=HP_TIME_BINS, colorscale='Viridis', text=text, hoverinfo='x+y+z+text')])

    fig.update_layout(title=f'{selected_data_type.capitalize()} Data Visualization', autosize=True,
                      scene=dict(
                          xaxis=dict(title='Date'),  # Label for the x-axis
                          yaxis=dict(title='Time of heater profile'),  # Label for the y-axis
                          zaxis=dict(title='Magnetic Field Value in nT'),  # Label for the z-axis
                          camera=dict(eye=dict(x=1.5, y=1.5, z=1.5))))
    return fig

@app.callback(
    Output('output-value', 'children'),
    Input('submit-val', 'n_clicks'),
    State('data-type-radio', 'value'),
    State('date-input', 'date'),
    State('hp-time-bin', 'value')
)
def display_value(n_clicks, data_type, date_str, hp_time_bin):
    if n_clicks > 0:
        data = real_2d if data_type == 'real' else pred_2d
        date = datetime.strptime(date_str, '%Y-%m-%d')
        # Find the index of the date in the 'FEATURES' DataFrame
        date_idx = FEATURES[FEATURES['Date'] == date].index.tolist()
        if date_idx and 0 <= hp_time_bin < data.shape[0]:
            date_idx = date_idx[0]  # Get the first matching index
            value = data[hp_time_bin, date_idx]
            return f'Value for {date_str} at Time of heater profile {hp_time_bin}: {value}'
        else:
            return 'Date or HP Time Bin is out of bounds'
    return ''

if __name__ == '__main__':
    app.run_server(debug=False, port=8062)
