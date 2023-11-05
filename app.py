import pandas as pd
import plotly.express as px

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

app= dash.Dash(__name__)

#------------------------------------------------------------------------------

columns_to_read = ['SEQPLT','YEAR',	'PSTATABB','PNAME',	'ORISPL','FIPSST','LAT', 'LON',	'PLNGENAN']
df = pd.read_csv("eGRID2021_data_plnt.csv", usecols= columns_to_read)


# Analyze data
# print(df['YEAR'].unique())
print(df['PSTATABB'].unique())
df['PLNGENAN'] = pd.to_numeric(df['PLNGENAN'].str.replace(',', ''), errors='coerce')
df = df.dropna(subset=['PLNGENAN'])
df['PLNGENANFLTRD'] = df['PLNGENAN'].apply(lambda x: max(0, x))
# df = df.groupby('PSTATABB', as_index=False)['PLNGENAN'].sum()
# df.reset_index(inplace=True)
print(df[:5])

#------------------------------------------------------------------------------------

# App layout
app.layout = html.Div([

    html.H1("Web Application Dashboards with Dash", style={'text-align': 'center'}),

    dcc.Dropdown(id='statelist',
                    options=[{'label': val, 'value': val} for val in df['PSTATABB'].unique()],
                    value=df['PSTATABB'].unique()[0],  # Set the default selected value
                    style= {'width': "40%"}
                 ),

    html.Div(id='output_container', children=[]),
    html.Br(),

    dcc.Graph(id='my_bee_map', figure={}, style={'width': '100%', 'height': '90vh'})

])

#--------------------------------------------------------------------------
# Connect the Plotly graphs with Dash Components
@app.callback(
    [Output(component_id='output_container', component_property='children'),
     Output(component_id='my_bee_map', component_property='figure')],
    [Input(component_id='statelist', component_property='value')]
)
def update_graph(option_slctd):
    print(option_slctd)
    print(type(option_slctd))

    container = "The state chosen by user was: {}".format(option_slctd)

    dff = df.copy()
    # dff = dff[dff["PSTATABB"] == option_slctd]

    # Plotly Express
    # fig = px.choropleth(
    #     data_frame=dff,
    #     locationmode='USA-states',
    #     locations='PSTATABB',
    #     scope="usa",
    #     color='PLNGENAN',
    #     hover_data=['PSTATABB', 'PLNGENAN'],
    #     color_continuous_scale=px.colors.sequential.YlOrRd,
    #     labels={'Pct of Colonies Impacted': '% of Bee Colonies'},
    #     template='plotly_dark'
    # )

    fig = px.scatter_mapbox(dff, 
                        lat='LAT', 
                        lon='LON', 
                        hover_data=['PLNGENAN'],
                        color='PSTATABB', 
                        size='PLNGENANFLTRD', 
                        zoom=3, 
                        center=dict(lat=37.7749 , lon=-96.7885),
                        mapbox_style='open-street-map')
    
#     fig = px.scatter_geo(
#     df,
#     locationmode='USA-states',
#     lat='LAT',
#     lon='LON',
#     color='PSTATABB', 
#     size='PLNGENANFLTRD',
#     projection = 'albers usa'
# )
#     fig.update_geos(
#     scope="usa",  # Focus on the United States
#     center=dict(lat=37.0902, lon=-95.7129),  # Set the center of the map to include Alaska
#     projection_scale=2  # Adjust the zoom level as needed
# )
    # fig.update_layout(
    # geo=dict(
    #     showcoastlines=True,
    #     coastlinecolor="Black",
    #     showland=True,
    #     landcolor="rgb(0, 229, 229)",
    #     showframe=False
    # )
# )

    return container, fig
# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True)

