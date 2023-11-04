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
df = df.groupby('PSTATABB', as_index=False)['PLNGENAN'].sum()
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

    dcc.Graph(id='my_bee_map', figure={})

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
    dff = dff[dff["PSTATABB"] == option_slctd]

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

    fig = px.scatter_geo(dff,
                     locationmode='USA-states', 
                     locations="iso_alpha",
                     color="continent", # which column to use to set the color of markers
                     hover_name="country", # column added to hover information
                     size="pop", # size of markers
                     projection="natural earth")

    return container, fig
# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True)

