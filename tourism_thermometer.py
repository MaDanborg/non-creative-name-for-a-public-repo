import dash
from dash import Dash, html, dcc, dash_table, callback
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go

df_climate = pd.read_csv('climate_all_Sara.csv')
df_climate.dropna(inplace = True)

df_iso = pd.read_csv('iso_codes.csv')
df_iso.dropna(inplace = True)

result = pd.merge(df_climate, df_iso, how = "outer", on="country")

filter = result['country'].isin(['Uruguay', 'Angola', 'Spain', 'Thailand', 'Sweden', 'France', 'Canada', 'Mexico', 'Australia', 'Russia', 'India', 
                                'Saudi Arabia', 'China', 'Brazil', 'Greeland', 'Senegal', 'Kenya', 'Malawi', 'Barbados', 'Japan', 'Sri Lanka'])
df_countries = result[filter]

df_countries.columns = ['city', 'country', 'date', 'lat', 'lon', 'region', 'avg_max_temp', 'avg_min_temp', 'avg_temp', 'alpha-3', 'continent']

df_countries['date'] = pd.to_datetime(df_countries['date'])
df_countries.sort_values('date', ascending=True, inplace=True)
df_countries['day'] = df_countries['date'].dt.day
df_countries['month'] = df_countries['date'].dt.month
df_countries['year'] = df_countries['date'].dt.year

df_countries['avg_month'] = df_countries.groupby(['country', 'city', 'month'])['avg_temp'].transform('mean')
df = df_countries
df['month'].replace(to_replace = [1,2,3,4,5,6,7,8,9], value = ['jan','feb','mar','apr','may','jun','jul','aug','sep'], inplace = True)

fig3 = px.scatter_geo(df, 
                        lat='lat', lon='lon', 
                        hover_name='city', size=df['avg_max_temp'].abs(),
                        center={'lat': 40.4, 'lon': -3.68}, 
                        text='city',
                        animation_frame = 'month',
                        color='avg_max_temp',
                        color_continuous_scale=px.colors.sequential.Redor,
                        projection = 'eckert4',
                        fitbounds = 'locations',
                        labels = {'avg_max_temp':'avg maximum temp'},
                        #title = 'average maximum temperature accross the globe - monthly',
                        width = 1000,
                        height = 650
                    )
df_Spain = df[df['country'] == 'Spain']
df_Spain.sort_values(by = 'date', ascending=True, inplace=False)

mask = df_Spain['month'] == 10
mask2 = df_Spain['month'] == 11
mask3 = df_Spain['year'] == 2023
df_Spain = df_Spain[~mask & ~mask2 & mask3]
df_Spain['month'].replace(to_replace = [1,2,3,4,5,6,7,8,9], value = ['jan','feb','mar','apr','may','jun','jul','aug','sep'], inplace = True)
df_Spain

fig4 = px.bar(df_Spain, 
             x='date', 
             y='avg_temp',  
             color='avg_temp',
             color_continuous_scale=px.colors.sequential.Redor,
            # animation_frame = 'month',
             labels = {'date':'month', 'avg_temp':'avg daily temp'},
             height=250
      )

fig4.update_layout({
'plot_bgcolor': 'rgba(0, 0, 0, 0)',
'paper_bgcolor': 'rgba(0, 0, 0, 0)',
})

df_Spain_provinces = pd.read_csv('tourists_spain_per_province_202401222012.csv')
df_Spain_provinces = df_Spain_provinces[df_Spain_provinces['province'].isin(['Barcelona', 'Madrid', 'Málaga'])]
mask = df_Spain_provinces['month'] == 10
mask2 = df_Spain_provinces['month'] == 11
df_Spain_provinces = df_Spain_provinces[~mask & ~mask2]
df_Spain_provinces['month'].replace(to_replace = [1,2,3,4,5,6,7,8,9], value = ['jan','feb','mar','apr','may','jun','jul','aug','sep'], inplace = True)

fig5 = px.bar(df_Spain_provinces, 
             x='month', 
             y='total_tourists',  
             color = 'province',
             color_discrete_map = {'Barcelona': '#c5165c', 'Madrid': 'LightCoral', 'Málaga': 'LightPink'},
             barmode = 'group',
             text_auto ='.2s',
             labels = {'month':'month', 'total_tourists':'total inbound tourists'},
             height=250
      )

fig5.update_layout({
'plot_bgcolor': 'rgba(0, 0, 0, 0)',
'paper_bgcolor': 'rgba(0, 0, 0, 0)',
})

df_Spain2 = df_Spain[['city', 'month', 'year', 'avg_month']]
df_Spain2['avg_month'] = df_Spain2['avg_month'].round()
df_Spain2 = df_Spain2[df_Spain2['year'] == 2023]
df_Spain2.drop_duplicates(subset=None, keep='first', inplace=True, ignore_index=True)

graph3 = dcc.Graph(figure=fig3, style = {'margin-left': 250})
graph4 = dcc.Graph(figure=fig4)
graph5 = dcc.Graph(figure=fig5)
app = dash.Dash(external_stylesheets=[dbc.themes.JOURNAL])
server = app.server

months = df_Spain['month'].unique().tolist() 
province = df_Spain_provinces['province'].unique().tolist()

radio = dcc.RadioItems(['Barcelona', 'Madrid', 'Málaga'], value = province, inline = True, style = {'paddingLeft': '30px', 'fontSize':14, 'textAlign':'center'})

dropdown = dcc.Dropdown(['jan','feb','mar','apr','may','jun','jul','aug','sep']
                        , value=['jan','feb','mar','apr','may','jun','jul','aug','sep'] 
                        , clearable=True
                        , multi=True
                        , placeholder="select a month"
                        , style = {'padding': 5, 'margin-top': 40, "backgroundColor": "white", "color": "slate", 'margin-left': 25}
                       )

app.layout = html.Div([html.H1("tourism thermometer"
                               , style={'textAlign': 'left'
                                         , 'margin-top': 50
                                         , 'margin-left': 25
                                         , 'fontSize': 50
                                         }),
                       html.Div(" a visualization of how tourism and temperatures walk hand in hand"
                               , style={'textAlign': 'left'
                                         , 'margin-left': 25
                                         , 'fontSize': 14
                                         ,'backgroundColor': 'DarkSalmon'
                                         , 'color': 'white'
                                         , 'width': '420px'
                                         , 'border-radius': '5px'
                                         }),
                       html.Br(),
                       html.Br(),
                       html.Div([html.Div("through the course of the 12 months of the year, temperatures change naturally and sometimes quite drastically. have a look at the average daily maximum temperatures across the globe from september 2022 through august 2023." 
                                , style={'textAlign': 'justify', 'backgroundColor': 'indianred', 'color': 'white', 
                                         'width': '1450px', 'border-radius': '15px', 'margin_top' : 40,
                                         'padding': 25, 
                                         'fontSize': 17,
                                         'fontWeight' : 'bold',
                                         'margin-left': 25}), graph3]),
                       html.Div("source: www.weatherapi.com", style = {'textAlign': 'right', 'fontSize': 12.5, 'color': 'slate', 'margin-right':50}),
                       html.Br(),
                       html.Br(),
                       html.Br(),
                       html.Div([html.Div("now try and play around with the charts below. check how, by selecting different months, the average daily temperature changes - and so does the number of international tourists in spanish provinces." 
                                , style={'textAlign': 'justify', 'backgroundColor': 'indianred', 'color': 'white', 'border-radius': '15px', 
                                         'width': '1450px', 
                                         'padding': 25, 
                                         'fontSize': 17,
                                         'fontWeight' : 'bold',
                                         'margin-left': 25}), dropdown, graph4,
                                         html.Div("source: www.weatherapi.com", style = {'textAlign': 'right', 'fontSize': 12.5, 'color': 'slate', 'margin-right':50}),
                                         html.Br(),
                                         html.Br(),
                                         radio, graph5,
                                         html.Div("source: ine.es", style = {'textAlign': 'right', 'fontSize': 12.5, 'color': 'slate', 'margin-right':50}),
                                        html.Br(),
                                        html.Br(),
                                        html.Div("here's some food for thought for you now: is the warmest month the one that attracts more tourists? if you're looking for comfortable temperatures and less tourists to share spaces with, when would you go to málaga?" 
                                         , style={'textAlign': 'justify', 'backgroundColor': 'indianred', 'color': 'white', 'border-radius': '15px', 
                                         'width': '1450px', 
                                         'padding': 25, 
                                         'fontSize': 17,
                                         'fontWeight' : 'bold',
                                         'margin-left': 25}),
                                        html.Br(),
                                        html.Br(),
                                        html.Br(),
                                        html.Div("dashboard app by marília borges", style={'textAlign':'center', 'fontSize':12.5, 'color':'slate'}),
                                        html.Div("data analysis and strategic market research", style={'textAlign':'center', 'fontSize':10, 'color':'slate'}),
                                        html.Div("berlin, january 2024", style={'textAlign':'center', 'fontSize':10, 'color':'slate'}),
                                        html.Br(),
                                        html.Br()        ])
                      ])
                  
@app.callback(
    [Output(graph4, "figure"), 
    Output(graph5, "figure", allow_duplicate=True)],
    Input(dropdown, "value"),
    prevent_initial_call='initial_duplicate'
)

def update_bar_chart(months):
    mask = df_Spain['month'].isin(months)
    mask2 = df_Spain_provinces['month'].isin(months)
    fig4 = px.bar(df_Spain[mask], 
             x='date', 
             y='avg_temp',  
             color='avg_temp',
             color_continuous_scale=px.colors.sequential.Redor,
             labels = {'date':'month', 'avg_temp':'avg daily temp'},
             height=250)
    fig4.update_layout({
'plot_bgcolor': 'rgba(0, 0, 0, 0)',
'paper_bgcolor': 'rgba(0, 0, 0, 0)'})
    fig5 = px.bar(df_Spain_provinces[mask2], 
             x='month', 
             y='total_tourists',  
             color = 'province',
             color_discrete_map = {'Barcelona': '#c5165c', 'Madrid': 'LightCoral', 'Málaga': 'LightPink'},
             barmode = 'group',
             text_auto ='.2s',
             labels = {'month':'month', 'total_tourists':'total inbound tourists'},
             height = 250)
    fig5.update_layout({
'plot_bgcolor': 'rgba(0, 0, 0, 0)',
'paper_bgcolor': 'rgba(0, 0, 0, 0)'})

    return fig4, fig5

@app.callback(
    Output(graph5, "figure"),
    Input(radio, "value")
     )

def update_province(input):
    mask3 = df_Spain_provinces['province'] == input
    fig5 = px.bar(df_Spain_provinces[mask3], 
             x='month', 
             y='total_tourists',  
             color = 'province',
             color_discrete_map = {'Barcelona': '#c5165c', 'Madrid': 'LightCoral', 'Málaga': 'LightPink'},
             barmode = 'group',
             text_auto ='.2s',
             labels = {'month':'month', 'total_tourists':'total inbound tourists'},
             height = 250)
    fig5.update_layout({
'plot_bgcolor': 'rgba(0, 0, 0, 0)',
'paper_bgcolor': 'rgba(0, 0, 0, 0)'})

    return fig5

if __name__ == '__main__':
     app.run_server(port = 9070)