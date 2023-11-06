import pandas as pd
import plotly.express as px
import re

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

app= dash.Dash(__name__,)

#------------------------------------------------------------------------------

columns_to_read = ['Plant file sequence number','Data Year','Plant state abbreviation','Plant name',
                   'DOE/EIA ORIS plant or facility code','Plant FIPS state code','Plant latitude',
                     'Plant longitude','Plant annual net generation (MWh)']
df = pd.read_csv("eGRID2021_data_plnt.csv", usecols= columns_to_read)


# Analyze data
# print(df['YEAR'].unique())
print(df['Plant state abbreviation'].unique())
df['Plant annual net generation (MWh)'] = pd.to_numeric(df['Plant annual net generation (MWh)'].str.replace(',', ''), errors='coerce')
df = df.dropna(subset=['Plant annual net generation (MWh)'])
df['Plant annual net generation'] = df['Plant annual net generation (MWh)'].apply(lambda x: max(0, x))


options = [{'label': 'USA', 'value' : 'USA'}]
statelist = [{'label': val, 'value': val} for val in df['Plant state abbreviation'].unique()]
options.extend(statelist)

#------------------------------------------------------------------------------------

# App layout
app.layout = html.Div([
    
    dcc.Location(id = 'url'),
    html.H1("Power Plants in US", style={'text-align': 'center'}),
   
    html.P("Choose Region :  ", style={'display': 'inline-block', 'margin-left': '100px'}),
    dcc.Dropdown(id='statelist',
                    options=options,
                    value=options[0]['value'],  # Set the default selected value
                    style= {'width': "40%", 'display': 'inline-block', 'margin-left': '10px'}
                 ),
    # html.Br(),
    # html.P("Show top ", style={'display': 'inline-block'}),
    # dcc.Dropdown(id = 'dropnum',
    #     options=[],
    #     style={'display': 'inline-block', 'margin-left': '10px', 'margin-right': '10px'}
    # ),
    # html.P(" power plants", id='color-output', style={'display': 'inline-block', 'margin-left': '10px'}),
    
    html.Br(),

    dcc.Graph(id='plant_map', figure={}, style={'width': '100%', 'height': '90vh'}),

    html.Br(),

    dcc.Graph(id='bar_plot', figure={}, style={'width': '100%', 'height': '90vh'})

])

#--------------------------------------------------------------------------
# Connect the Plotly graphs with Dash Components
# @app.callback(
#     [Output(component_id='dropnum', component_property='options'),
#      Output(component_id='dropnum', component_property='value'),
#      Output(component_id='my_bee_map', component_property='figure')],
#     [Input(component_id='statelist', component_property='value'),
#      Input(component_id='dropnum', component_property='value'),]
# )
@app.callback(
    [Output(component_id='plant_map', component_property='figure'),
     Output(component_id='bar_plot', component_property='figure')],
    [Input(component_id='statelist', component_property='value'),
     Input(component_id='url', component_property='search')]
)
def update_graph(option_slctd, search_param):
   
    dff = df.copy()

    usnetgen = dff['Plant annual net generation (MWh)'].sum()
    df_state = dff.groupby('Plant state abbreviation', as_index=False)['Plant annual net generation (MWh)'].sum()
    df_state = df_state.rename(columns={'Plant annual net generation (MWh)': 'State annual net generation (MWh)'})

    total_plants = dff['DOE/EIA ORIS plant or facility code'].count()
    match = re.search(r'\?n=(\d+)', search_param)
    n = int(match.group(1)) if match else total_plants
    n = min(n,total_plants)
    value = min(n, total_plants)
    
    df_topn = dff.sort_values(by='Plant annual net generation (MWh)', ascending=False).head(value)
    merged_df = df_topn.merge(df_state, on='Plant state abbreviation', how='left')
    merged_df['Percent net generation by state(%)'] = merged_df['State annual net generation (MWh)'].apply(lambda x : (x/usnetgen)*100 )
    
    if option_slctd != 'USA':
        dff = dff[dff["Plant state abbreviation"] == option_slctd]
        centre_lat = dff['Plant latitude'].mean()
        centre_lon = dff['Plant longitude'].mean()
        zoom = 5
    else:
        centre_lat= 37.7749
        centre_lon= -96.7885
        zoom = 3

    # total_plants = dff['PNAME'].count()
    # options = [{'label': i+1, 'value': i+1} for i in range(total_plants)]
    # value = min(num_slctd, total_plants) if num_slctd is not None else total_plants
    # top_n_df = dff.sort_values(by='PLNGENAN', ascending=False).head(value)

    fig = px.scatter_mapbox(merged_df,
                        lat='Plant latitude', 
                        lon='Plant longitude', 
                        hover_name = 'Plant state abbreviation',
                        hover_data={'Plant latitude': False,
                                    'Plant annual net generation': False, 
                                    'Plant state abbreviation': False,
                                    'Plant name': True,
                                    'Plant annual net generation (MWh)': True,
                                    'State annual net generation (MWh)': True,
                                    'Percent net generation by state(%)':':.3f', 
                                    'Plant longitude': False},
                        color='Plant state abbreviation', 
                        size='Plant annual net generation', 
                        zoom= zoom, 
                        center=dict(lat=centre_lat , lon=centre_lon),
                        mapbox_style='open-street-map')
    
    bar = px.bar(df_topn, x='Plant file sequence number', y='Plant annual net generation',
                 hover_data=['Plant name', 'Plant annual net generation'],)
    bar.update_xaxes(type='category')
    
    return fig, bar
# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True)

