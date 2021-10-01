#!/usr/bin/env python
# coding: utf-8


import numpy as np
import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import plotly.graph_objs as go
import plotly.express as px
from plotly.subplots import make_subplots
import base64
import io
import urllib

app = dash.Dash(__name__)
server = app.server

census_master = pd.read_csv('master_data.csv')
census_master['zip'] = census_master['zip'].astype(str)
census_master['zip'] = census_master['zip'].apply(lambda x: '{0:0>5}'.format(x))



vals = list(census_master.columns)



def gen_census_data(df):
    df = df.rename(columns = {'Zip.Code': 'zip'})
    df['zip'] = df['zip'].astype(str)
    df['zip'] = df['zip'].apply(lambda x: '{0:0>5}'.format(x))
    export = pd.merge(df, census_master, how= 'left', on='zip')
    
    return export


def parse_contents(contents, filename):
    
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
           
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
           
            df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    return df


def aggregate_health_unemp(df):
    
    df['white_unemp'] = df['unemp_white_m'] + df['unemp_white_f']
    df['black_unemp'] = df['unemp_black_m'] + df['unemp_black_f']
    df['asian_unemp'] = df['unemp_asian_m'] + df['unemp_asian_f']
    df['native_unemp'] = df['unemp_native_m'] + df['unemp_native_f']
    df['pacif_unemp'] = df['unemp_pacif_m'] + df['unemp_pacif_f']
    df['other_unemp'] = df['unemp_other_m'] + df['unemp_other_f']
    
    df['white_hs_dip'] = df['hs_dip_white_m'] + df['hs_dip_white_f']
    df['black_hs_dip'] = df['hs_dip_black_m'] + df['hs_dip_black_f']
    df['asian_hs_dip'] = df['hs_dip_asian_m'] + df['hs_dip_asian_f']
    df['native_hs_dip'] = df['hs_dip_native_m'] + df['hs_dip_native_f']
    df['pacif_hs_dip'] = df['hs_dip_pacif_m'] + df['hs_dip_pacif_f']
    df['other_hs_dip'] = df['hs_dip_pacif_m'] + df['hs_dip_pacif_f']
    
    export = df.drop([
        'hs_dip_white_m',
        'hs_dip_white_f',
        'hs_dip_black_m',
        'hs_dip_black_f',
        'hs_dip_native_m',
        'hs_dip_native_f',
        'hs_dip_asian_m',
        'hs_dip_asian_f',
        'hs_dip_pacif_m',
        'hs_dip_pacif_f',
        'hs_dip_pacif_m',
        'hs_dip_pacif_f',
        'unemp_white_m',
        'unemp_white_f',
        'unemp_black_m',
        'unemp_black_f',
        'unemp_native_m',
        'unemp_native_f',
        'unemp_asian_m',
        'unemp_asian_f',
        'unemp_pacif_m',
        'unemp_pacif_f',
        'unemp_other_m',
        'unemp_other_f'
    ],
    axis = 1
    )
    
    return export


def summary_stat_by_state(dff, var):
    
    """
    Generates sample summary statistics for a given demeographic category across all represented races
    per state
    
    Input:
        dff - a pandas dataframe
        var - a string representing a demographic category (Population, Income, Health)
        
    Ouput:
        A pandas dataframe illustrating summary statistics per state 
    """
    dff = aggregate_health_unemp(dff)
    
    id_zip = dff[['ID', 'zip', 'STATE']]
    
    if var == 'Population':
        pop_df = dff.filter(like = 'pop')
        pop_df = pop_df.drop(['tot_pop_all'], axis = 1).copy()
        population_merge = pd.concat([id_zip, pop_df], axis = 1)
        population = population_merge.drop(['ID', 'zip'], axis = 1).groupby(['STATE']).mean().reset_index()
        stats = population.drop('STATE', axis = 1)
        population['mean'] = stats.mean(axis = 1)
        population['std'] = stats.std(axis = 1)
        population['max_race'] = stats.idxmax(axis = 1)
        population['max'] = stats.max(axis = 1)
        population['min_race'] = stats.idxmin(axis = 1)
        population['min'] = stats.min(axis = 1)
        population['range'] = population['max'] - population['min']
        d_pop = {
            'tot_pop_asian': 'asian', 
            'tot_pop_black': 'black', 
            'tot_pop_white': 'white',
            'tot_pop_native' : 'native',
            'tot_pop_pacif' : 'pacif',
            'tot_pop_other' : 'other'
        }
        population['max_race'] = population['max_race'].map(d_pop)
        population['min_race'] = population['min_race'].map(d_pop)
        
        return population.round(2)
        
    elif var == 'Income':
        income_df = dff.filter(like = 'med_fam_inc')
        income_df = income_df.drop(['med_fam_inc_all'], axis = 1).copy()
        income_merge = pd.concat([id_zip, income_df], axis = 1)
        income = income_merge.drop(['ID', 'zip'], axis = 1).groupby(['STATE']).mean().reset_index()
        stats = income.drop('STATE', axis = 1)
        income['mean'] = stats.mean(axis = 1)
        income['std'] = stats.std(axis = 1)
        income['max_race'] = stats.idxmax(axis = 1)
        income['max'] = stats.max(axis = 1)
        income['min_race'] = stats.idxmin(axis = 1)
        income['min'] = stats.min(axis = 1)
        income['range'] = income['max'] - income['min']
        d_inc = {
            'med_fam_inc_white' : 'white',
            'med_fam_inc_black' : 'black',
            'med_fam_inc_asian' : 'asian',
            'med_fam_inc_native' : 'native',
            'med_fam_inc_pacif' : 'pacif',
            'med_fam_inc_other' : 'other'
        }
        income['max_race'] = income['max_race'].map(d_inc)
        income['min_race'] = income['min_race'].map(d_inc)
        
        return income.round(2)
    
    elif var == 'Health':
        health_df = dff.filter(like = 'health')
        health_df = health_df.drop(['health_ins_all'], axis = 1).copy()
        health_merge = pd.concat([id_zip, health_df], axis = 1)
        health = health_merge.drop(['ID', 'zip'], axis = 1).groupby(['STATE']).mean().reset_index()
        stats = health.drop('STATE', axis = 1)
        health['mean'] = stats.mean(axis = 1)
        health['std'] = stats.std(axis = 1)
        health['max_race'] = stats.idxmax(axis = 1)
        health['max'] = stats.max(axis = 1)
        health['min_race'] = stats.idxmin(axis = 1)
        health['min'] = stats.min(axis = 1)
        health['range'] = health['max'] - health['min']
        d_health = {
            'health_ins_white' : 'white',
            'health_ins_black' : 'black',
            'health_ins_asian' : 'asian',
            'health_ins_native' : 'native',
            'health_ins_pacif' : 'pacif',
            'health_ins_other' : 'other'
        }
        health['max_race'] = health['max_race'].map(d_health)
        health['min_race'] = health['min_race'].map(d_health)
        
        return health.round(2)
    
    elif var == 'Unemployment':
        unemp_df = dff.filter(like = 'unemp')
        unemp_df = unemp_df.drop(['unemp_all_m', 'unemp_all_f'], axis = 1).copy()        
        unemp_merge = pd.concat([id_zip, unemp_df], axis = 1)
        unemp = unemp_merge.drop(['ID', 'zip'], axis = 1).groupby(['STATE']).mean().reset_index()
        stats = unemp.drop('STATE', axis = 1)
        unemp['mean'] = stats.mean(axis = 1)
        unemp['std'] = stats.std(axis = 1)
        unemp['max_race'] = stats.idxmax(axis = 1)
        unemp['max'] = stats.max(axis = 1)
        unemp['min_race'] = stats.idxmin(axis = 1)
        unemp['min'] = stats.min(axis = 1)
        unemp['range'] = unemp['max'] - unemp['min']
        d_unemp = {
            'white_unemp' : 'white',
            'black_unemp' : 'black',
            'asian_unemp' : 'asian',
            'native_unemp' : 'native',
            'pacif_unemp' : 'pacif',
            'other_unemp' : 'other'
        }
        unemp['max_race'] = unemp['max_race'].map(d_unemp)
        unemp['min_race'] = unemp['min_race'].map(d_unemp)
        
        return unemp.round(2)
    
    elif var == 'Education':
        hs_dip_df = dff.filter(like = 'hs_dip')
        hs_dip_df = hs_dip_df.drop(['hs_dip_all_m', 'hs_dip_all_f'], axis = 1).copy()  
        hs_dip_merge = pd.concat([id_zip, hs_dip_df], axis = 1)
        hs_dip = hs_dip_merge.drop(['ID', 'zip'], axis = 1).groupby(['STATE']).mean().reset_index()
        stats = hs_dip.drop('STATE', axis = 1)
        hs_dip['mean'] = stats.mean(axis = 1)
        hs_dip['std'] = stats.std(axis = 1)
        hs_dip['max_race'] = stats.idxmax(axis = 1)
        hs_dip['max'] = stats.max(axis = 1)
        hs_dip['min_race'] = stats.idxmin(axis = 1)
        hs_dip['min'] = stats.min(axis = 1)
        hs_dip['range'] = hs_dip['max'] - hs_dip['min']
        d_hs_dip = {
            'white_hs_dip' : 'white',
            'black_hs_dip' : 'black',
            'asian_hs_dip' : 'asian',
            'native_hs_dip' : 'native',
            'pacif_hs_dip' : 'pacif',
            'other_hs_dip' : 'other'
        }
        hs_dip['max_race'] = hs_dip['max_race'].map(d_hs_dip)
        hs_dip['min_race'] = hs_dip['min_race'].map(d_hs_dip)
        
        return hs_dip.round(2)
    
    else:
        print('error')

        
def summary_stat_per_sample(dff, var):
    
    """
    Generates sample summary statistics for a given demeographic category across all represented races
    per sample
    
    Input:
        dff - a pandas dataframe
        var - a string representing a demographic category (Population, Income, Health)
        
    Ouput:
        A pandas dataframe illustrating summary statistics per sample
    """
    
    dff = aggregate_health_unemp(dff)
    
    id_zip = dff[['ID', 'zip', 'STATE']]
    
    if var == 'Population':
        pop_df = dff.filter(like = 'pop')
        population = pop_df.drop(['tot_pop_all'], axis = 1).copy()
        population['mean'] = pop_df.mean(axis = 1)
        population['std'] = pop_df.std(axis = 1)
        population['max_race'] = pop_df.idxmax(axis = 1)
        population['max'] = pop_df.max(axis = 1)
        population['min_race'] = pop_df.idxmin(axis = 1)
        population['min'] = pop_df.min(axis = 1)
        population['range'] = population['max'] - population['min']
        d_pop = {
            'tot_pop_asian': 'asian', 
            'tot_pop_black': 'black', 
            'tot_pop_white': 'white',
            'tot_pop_native' : 'native',
            'tot_pop_pacif' : 'pacif',
            'tot_pop_other' : 'other'
        }
        population['max_race'] = population['max_race'].map(d_pop)
        population['min_race'] = population['min_race'].map(d_pop)
        pop_merge = pd.concat([id_zip, population], axis = 1)
        
        return pop_merge.round(2)
    
    elif var == 'Income':
        income_df = dff.filter(like = 'med_fam_inc')
        income = income_df.drop(['med_fam_inc_all'], axis = 1).copy()
        income['mean'] = income_df.mean(axis = 1)
        income['std'] = income_df.std(axis = 1)
        income['max_race'] = income_df.idxmax(axis = 1)
        income['max'] = income_df.max(axis = 1)
        income['min_race'] = income_df.idxmin(axis = 1)
        income['min'] = income_df.min(axis = 1)
        income['range'] = income['max'] - income['min']
        d_inc = {
            'med_fam_inc_white' : 'white',
            'med_fam_inc_black' : 'black',
            'med_fam_inc_asian' : 'asian',
            'med_fam_inc_native' : 'native',
            'med_fam_inc_pacif' : 'pacif',
            'med_fam_inc_other' : 'other'
        }
        income['max_race'] = income['max_race'].map(d_inc)
        income['min_race'] = income['min_race'].map(d_inc)
        inc_merge = pd.concat([id_zip, income], axis = 1)
        
        return inc_merge.round(2)
    
    elif var == 'Health':
        health_df = dff.filter(like = 'health')
        health = health_df.drop(['health_ins_all'], axis = 1).copy()
        health['mean'] = health_df.mean(axis = 1)
        health['std'] = health_df.std(axis = 1)
        health['max_race'] = health_df.idxmax(axis = 1)
        health['max'] = health_df.max(axis = 1)
        health['min_race'] = health_df.idxmin(axis = 1)
        health['min'] = health_df.min(axis = 1)
        health['range'] = health['max'] - health['min']
        d_health = {
            'health_ins_white' : 'white',
            'health_ins_black' : 'black',
            'health_ins_asian' : 'asian',
            'health_ins_native' : 'native',
            'health_ins_pacif' : 'pacif',
            'health_ins_other' : 'other'
        }
        health['max_race'] = health['max_race'].map(d_health)
        health['min_race'] = health['min_race'].map(d_health)
        health_merge = pd.concat([id_zip, health], axis = 1)   
        
        return health_merge.round(2)
    
    elif var == 'Unemployment':
        unemp_df = dff.filter(like = 'unemp')
        unemp = unemp_df.drop(['unemp_all_m', 'unemp_all_f'], axis = 1).copy()
        unemp['mean'] = unemp_df.mean(axis = 1)
        unemp['std'] = unemp_df.std(axis = 1)
        unemp['max_race'] = unemp_df.idxmax(axis = 1)
        unemp['max'] = unemp_df.max(axis = 1)
        unemp['min_race'] = unemp_df.idxmin(axis = 1)
        unemp['min'] = unemp_df.min(axis = 1)
        unemp['range'] = unemp['max'] - unemp['min']
        d_unemp = {
            'white_unemp' : 'white',
            'black_unemp' : 'black',
            'asian_unemp' : 'asian',
            'native_unemp' : 'native',
            'pacif_unemp' : 'pacif',
            'other_unemp' : 'other'
        }
        unemp['max_race'] = unemp['max_race'].map(d_unemp)
        unemp['min_race'] = unemp['min_race'].map(d_unemp)
        unemp_merge = pd.concat([id_zip, unemp], axis = 1)   
        
        return unemp_merge.round(2)
    
    elif var == 'Education':
        hs_dip_df = dff.filter(like = 'hs_dip')
        hs_dip = hs_dip_df.drop(['hs_dip_all_m', 'hs_dip_all_f'], axis = 1).copy()
        hs_dip['mean'] = hs_dip_df.mean(axis = 1)
        hs_dip['std'] = hs_dip_df.std(axis = 1)
        hs_dip['max_race'] = hs_dip_df.idxmax(axis = 1)
        hs_dip['max'] = hs_dip_df.max(axis = 1)
        hs_dip['min_race'] = hs_dip_df.idxmin(axis = 1)
        hs_dip['min'] = hs_dip_df.min(axis = 1)
        hs_dip['range'] = hs_dip['max'] - hs_dip['min']
        d_hs_dip = {
            'white_hs_dip' : 'white',
            'black_hs_dip' : 'black',
            'asian_hs_dip' : 'asian',
            'native_hs_dip' : 'native',
            'pacif_hs_dip' : 'pacif',
            'other_hs_dip' : 'other'
        }
        hs_dip['max_race'] = hs_dip['max_race'].map(d_hs_dip)
        hs_dip['min_race'] = hs_dip['min_race'].map(d_hs_dip)
        hs_dip_merge = pd.concat([id_zip, hs_dip], axis = 1)   
        
        return hs_dip_merge.round(2)
    
    else:
        print("input error")
        
def summary_stat_by_state_nr(dff):
    frame = dff[['STATE', 'gini_index', 'explicit_black_racial_bias', 'explicit_white_racial_bias','implicit_black_white_racial_bias']]
    snr = frame.groupby(['STATE']).mean().reset_index()
    
    return snr


# In[6]:


app.layout = html.Div(
    [
        html.Div(
            [
                html.Div(
                    [
                        html.Img(
                            src=app.get_asset_url("CDSCLogo_KY3.png"),
                            id="logo",
                            style={
                                "height": "100%",
                                "width": "100%",
                                "align" : "center"
                            },
                        )
                    ],
                    className="two columns",
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.H3(
                                    "Racial Inequalities Database",
                                    style={"margin-bottom": "0px"},
                                ),
                                html.H5(
                                    "Conceptual Devlopment and Social Cognition Lab", style={"margin-top": "0px"}
                                ),
                            ]
                        )
                    ],
                    className="eight column",
                    id="title",
                ),
                html.Div(
                    [
                        html.A(
                            html.Button("website", id="website-button"),
                            href="http://kidconcepts.org/",
                        )
                    ],
                    className="two columns",
                    id="button",
                ),
            ],
            id="header",
            className="row flex-display",
            style={"margin-bottom": "25px"},
        ),
        
        html.Div(
            [
                html.H6(
                    'Instructions'
                ),
                
                html.Ol(
                    id='instructions',
                    children = [
                        html.Li('Deidentify your data before uploading'),
                        html.Li('Ensure there is a column titled "zip" that identifies the zipcode of participants in your data'),
                        html.Li('Upload your data using the "Drag and Drop or Select Files" button below'),
                        html.Li('Be patient with it... it will take some time to load (especially for larger files and if multiple people are on it at the same time)'),
                        html.Li('formatting and aesthetics for the website are still in development. We recommend downlading the data and viewing it seperatley')
                    ]
                ),
            ],
            id='pre-amble',
            className="pretty_container",
        ),
        
        html.Div(
            [
                dcc.Upload(
                    id='upload-data',
                    children=html.Div([
                        'Drag and Drop or ',
                        html.A('Select Files')
                    ]),
                    style={
                        'width': '100%',
                        'height': '60px',
                        'lineHeight': '60px',
                        'borderWidth': '1px',
                        'borderStyle': 'dashed',
                        'borderRadius': '5px',
                        'textAlign': 'center',
                        'margin': '10px'
                    },
                ),
                
                html.P(
                    id = 'prompt',
                    children = 'Waiting for upload',
                    style = {
                        'padding': 5,
                        'font-weight': 'bold',
                        'textAlign': 'center',
                    }
                ),
                
            ],
            id='upload-container',
            style={"margin-bottom": "25px"},
        ),
        
       html.Div(
           [
                dash_table.DataTable(
                    id = 'master_table',
                    columns = [{'name': i, 'id': i, 'selectable': True, 'hideable': True} for i in vals],
                    data = [],
                    filter_action = 'native',
                    sort_action = 'native',
                    sort_mode = 'single',
                    column_selectable = 'multi',
                    row_selectable = 'multi',
                    selected_columns = [],
                    selected_rows = [],
                    page_action = 'native',
                    page_size = 100,
                    style_table={"height": "600px", 'overflowY': 'auto'},
                    fixed_rows={'headers': True},
                    style_cell={'minWidth': 100, 'width': 100, 'maxWidth': 100},
                    style_data_conditional=[
                    {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': 'rgb(248, 248, 248)'
                    }
                    ],
                    style_header={
                    'backgroundColor': 'rgb(230, 230, 230)',
                    'fontWeight': 'bold'
                    },
                ),
               
               html.Br(),
               
               html.A(
                    'Download Merged Data',
                    id='download-merge-link',
                    download="merged_data.csv",
                    href="",
                    target="_blank"
                ),

                html.Br(),

                html.A(
                    'Download Raw Data',
                    id='download-raw-link',
                    download="raw_data.csv",
                    href="",
                    target="_blank"
                ),
                 
           ],
           id='data-table-holder',
           className="pretty_container",
       ),
    
    html.Br(),
    
    html.Div(
        [
            dcc.Dropdown(
                id = 'select_category',
                options = [
                    {'label' : 'Median Family Income', 'value' : 'Income'},
                    {'label' : 'Total Population', 'value' : 'Population'},
                    {'label' : 'Proportion of Residents with Health Insurance Coverage', 'value' : 'Health'}, 
                    {'label' : 'High School Graduation Rate', 'value' : 'Education'},
                    {'label' : 'Rate of Unemployment', 'value' : 'Unemployment'},
                ],
                placeholder = 'Select Category',
                value = 'Income',
                style = {
                    'height' : '20px'
                }
            ),
            
            html.Br(),
            
            html.Hr(),
            
            html.H3(
                'Variable Distribution for all Zip codes by Race'
            ),
            
            html.Div(
                [
                    html.Div(
                        id = 'summary_by_sample',
                        className = 'mini_container five columns',
                        children = [],
                    ),
                    
                    html.Br(),
                    
                    dcc.Graph(
                        id = 'sum_stat',
                        className = 'mini_container seven columns',
                        figure ={}
                    ),
                ],
                id='per-sample',
                className='row flex-display'
            ),
            
            html.Br(),
            
            html.Hr(),
            
            html.H3(
                'Variable Average per State by Race'
            ),
            
            html.Div(
                [
                    html.Div(
                        id = 'summary_by_state',
                        className = 'mini_container five columns',
                        children = [],
                    ),
                    
                    html.Br(),
                    
                    html.Div(
                        [
                            dcc.Dropdown(
                                id = 'select_cloro',
                                options = [
                                    {'label' : 'white', 'value' : 'white'},
                                    {'label' : 'black', 'value' : 'black'}, 
                                    {'label' : 'asian', 'value' : 'asian'},
                                    {'label' : 'native', 'value' : 'native'},
                                    {'label' : 'pacif', 'value' : 'pacif'},
                                    {'label' : 'other', 'value' : 'other'},
                                ],
                                placeholder = 'Select Category',
                                value = 'white',
                                style = {
                                    'height' : '20px'
                                }
                            ),
                            
                            html.Hr(),
                            
                            dcc.Graph(
                                id = 'us_map',
                                figure ={}
                            ),
                        ],
                        id = 'us-graph-holder',
                        className = 'mini_container seven columns',
                    ),
                    
                ],
                id='per-state',
                className='row flex-display'
            ),
            
            html.Hr(),
            
            html.H3(
                'Variable Average per State, no racial breakdown'
            ),
            
            html.Div(
                [
                    html.Div(
                        id = 'summary_by_state_nr',
                        className = 'mini_container five columns',
                        children = [],
                    ),
                    
                    html.Br(),
                    
                    html.Div(
                        [
                            dcc.Dropdown(
                                id = 'select_cloro_nr',
                                options = [
                                    {'label' : 'Gini Index', 'value' : 'gini_index'},
                                    {'label' : 'Explicit Feelings of Warmth Towards White People', 'value' : 'twhite_0to10'},
                                    {'label' : 'Explicit Feelings of Warmth Towards Black People', 'value' : 'tblack_0to10'},
                                    {'label' : 'Implicit Black-White Racial Bias', 'value' : 'D_biep.White_Good_all'},
                                ],
                                placeholder = 'Select Category',
                                value = 'gini_index',
                                style = {
                                    'height' : '20px'
                                }
                            ),
                            
                            html.Hr(),
                            
                            dcc.Graph(
                                id = 'us_map_nr',
                                figure ={}
                            ),
                        ],
                        id = 'us-graph-holder-nr',
                        className = 'mini_container seven columns',
                    ),
                    
                ],
                id='per-state-nr',
                className='row flex-display'
            ),
            
        ],
        id='stat-analysis',
        className="pretty_container",
    ),
      
    html.Div(
        [
            html.Div(
                id='storage', 
                style={'display': 'none'},
                children = []
            ),

            html.Div(
                id='census', 
                style={'display': 'none'},
                children = census_master.to_json(date_format='iso', orient='split')
            ),  
        ],
        id='hidden-storage'
    ),
        
    ],
    id='main-container'
)


# In[7]:


@app.callback(
    [
        Output('storage', 'children'),
        Output('prompt', 'children'),
    ], 
    [
        Input('upload-data', 'contents')  
    ],
    [
        State('upload-data','filename')
    ]
)

def clean_data(contents, filename):
    if contents is None:
        raise PreventUpdate
    else:
        raw = parse_contents(contents, filename)
        
        try:
            df = gen_census_data(raw)
            store = df.to_json(date_format='iso', orient='split')
            prompt = 'load sucessful'
            return store, prompt
        except Exception as e:
            prompt = 'unsuccessful load'
            return dash.no_update, prompt


# In[8]:


@app.callback(
    [
        Output(component_id = 'master_table', component_property = 'columns'),
        Output(component_id = 'master_table', component_property = 'data'),
    ],
    [
        Input(component_id = 'storage', component_property = 'children')
    ]
)

def create_master_table(storage):
    if not storage:
        raise PreventUpdate
    else:
        df = pd.read_json(storage, orient='split')
        columns = [{'name': i, 'id': i, 'selectable': True, 'hideable': True} 
                   for i in df.columns]
        data = df.to_dict('records')
        
    return columns, data


# In[9]:


@app.callback(
    Output(component_id = 'download-merge-link', component_property = 'href'),
    [
        Input(component_id = 'storage', component_property = 'children')
    ]
)

def export_to_csv(storage):
    df = pd.read_json(storage, orient='split')
    csv_string = df.to_csv(index=False, encoding='utf-8')
    csv_string = "data:text/csv;charset=utf-8,%EF%BB%BF" + urllib.parse.quote(csv_string)
    
    return csv_string   


# In[10]:


@app.callback(
    Output(component_id = 'download-raw-link', component_property = 'href'),
    [
        Input(component_id = 'census', component_property = 'children')
    ]
)

def export_to_csv(census):
    df = pd.read_json(census, orient='split')
    csv_string = df.to_csv(index=False, encoding='utf-8')
    csv_string = "data:text/csv;charset=utf-8,%EF%BB%BF" + urllib.parse.quote(csv_string)
    
    return csv_string 


# In[11]:


@app.callback(
    [
        Output(component_id = 'summary_by_sample', component_property = 'children'),
        Output(component_id = 'summary_by_state', component_property = 'children'),
        Output(component_id = 'summary_by_state_nr', component_property = 'children'),
        
    ],
    [
        Input(component_id = 'master_table', component_property = 'derived_virtual_data'),
        Input(component_id = 'select_category', component_property = 'value')
    ]
)

def update_dash_tables(all_row_data, category):
    if not all_row_data:
        raise PreventUpdate
    else:
        dff = pd.DataFrame(all_row_data)

        summary_by_sample = summary_stat_per_sample(dff, category)
        summary_by_state = summary_stat_by_state(dff, category)
        summary_by_state_nr = summary_stat_by_state_nr(dff)

        table_1 = dash_table.DataTable(
            columns = [{'name': i, 'id': i, 'selectable': True, 'hideable': True} 
                       for i in summary_by_sample.columns],
            data = summary_by_sample.to_dict('records'),
            filter_action = 'native',
            sort_action = 'native',
            sort_mode = 'single',
            column_selectable = 'multi',
            row_selectable = 'multi',
            selected_columns = [],
            selected_rows = [],
            page_action = 'native',
            page_size = 100,
            style_table={'height': '800px', 'maxHeight': '800px', 'overflowY': 'auto'},
            fixed_rows={'headers': True},
            style_cell={'minWidth': 100, 'width': 100, 'maxWidth': 100},
            style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': 'rgb(248, 248, 248)'
            }
                ],
            style_header={
                'backgroundColor': 'rgb(230, 230, 230)',
                'fontWeight': 'bold'
                }
        )

        table_2 = dash_table.DataTable(
            columns = [{'name': i, 'id': i, 'selectable': True, 'hideable': True} 
                       for i in summary_by_state.columns],
            data = summary_by_state.to_dict('records'),
            filter_action = 'native',
            sort_action = 'native',
            sort_mode = 'single',
            column_selectable = 'multi',
            row_selectable = 'multi',
            selected_columns = [],
            selected_rows = [],
            page_action = 'native',
            page_size = 100,
            style_table={'height': '500px', 'overflowY': 'auto'},
            fixed_rows={'headers': True},
            style_cell={'minWidth': 100, 'width': 100, 'maxWidth': 100},
            style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': 'rgb(248, 248, 248)'
            }
                ],
            style_header={
                'backgroundColor': 'rgb(230, 230, 230)',
                'fontWeight': 'bold'
                }
        )
        
        table_3 = dash_table.DataTable(
            columns = [{'name': i, 'id': i, 'selectable': True, 'hideable': True} 
                       for i in summary_by_state_nr.columns],
            data = summary_by_state_nr.to_dict('records'),
            filter_action = 'native',
            sort_action = 'native',
            sort_mode = 'single',
            column_selectable = 'multi',
            row_selectable = 'multi',
            selected_columns = [],
            selected_rows = [],
            page_action = 'native',
            page_size = 100,
            style_table={'height': '500px', 'overflowY': 'auto'},
            fixed_rows={'headers': True},
            style_cell={'minWidth': 100, 'width': 100, 'maxWidth': 100},
            style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': 'rgb(248, 248, 248)'
            }
                ],
            style_header={
                'backgroundColor': 'rgb(230, 230, 230)',
                'fontWeight': 'bold'
                }
        ) 
    

        return table_1, table_2, table_3


# In[12]:


@app.callback(
    Output(component_id = 'sum_stat', component_property = 'figure'),
    [
        Input(component_id = 'master_table', component_property = 'derived_virtual_data'),
        Input(component_id = 'select_category', component_property = 'value')
    ]
)


def update_hist(all_row_data, category):
    if not all_row_data :
        raise PreventUpdate
    else:
    
        dff = pd.DataFrame(all_row_data)
        dff = aggregate_health_unemp(dff)
        fig = make_subplots(rows=3, cols=2, subplot_titles=("White", "Black", 'Asian', "Native", "Pacif", "Other"))

        if category == 'Income':

            fig.add_trace(go.Histogram(x = dff['med_fam_inc_white'], nbinsx=50, name = 'white'),row=1, col=1)
            fig.add_trace(go.Histogram(x = dff['med_fam_inc_black'], nbinsx=50, name = 'black'),row=1, col=2)
            fig.add_trace(go.Histogram(x = dff['med_fam_inc_asian'], nbinsx=50, name = 'asian'),row=2, col=1)
            fig.add_trace(go.Histogram(x = dff['med_fam_inc_native'], nbinsx=50, name = 'native'),row=2, col=2)
            fig.add_trace(go.Histogram(x = dff['med_fam_inc_pacif'], nbinsx=50, name = 'pacific'),row=3, col=1)
            fig.add_trace(go.Histogram(x = dff['med_fam_inc_other'], nbinsx=50, name = 'other'),row=3, col=2)
            fig.update_layout(title_text="Income", showlegend=False, height=1000)

        elif category == 'Population':

            fig.add_trace(go.Histogram(x = dff['tot_pop_white'], nbinsx=50, name = 'white'),row=1, col=1)
            fig.add_trace(go.Histogram(x = dff['tot_pop_black'], nbinsx=50, name = 'black'),row=1, col=2)
            fig.add_trace(go.Histogram(x = dff['tot_pop_asian'], nbinsx=50, name = 'asian'),row=2, col=1)
            fig.add_trace(go.Histogram(x = dff['tot_pop_native'], nbinsx=50, name = 'native'),row=2, col=2)
            fig.add_trace(go.Histogram(x = dff['tot_pop_pacif'], nbinsx=50, name = 'pacific'),row=3, col=1)
            fig.add_trace(go.Histogram(x = dff['tot_pop_other'], nbinsx=50, name = 'other'),row=3, col=2)
            fig.update_layout(title_text="Population", showlegend=False, height=1000)

        elif category == 'Health':

            fig.add_trace(go.Histogram(x = dff['health_ins_white'], nbinsx=50, name = 'white'),row=1, col=1)
            fig.add_trace(go.Histogram(x = dff['health_ins_black'], nbinsx=50, name = 'black'),row=1, col=2)
            fig.add_trace(go.Histogram(x = dff['health_ins_asian'], nbinsx=50, name = 'asian'),row=2, col=1)
            fig.add_trace(go.Histogram(x = dff['health_ins_native'], nbinsx=50, name = 'native'),row=2, col=2)
            fig.add_trace(go.Histogram(x = dff['health_ins_pacif'], nbinsx=50, name = 'pacific'),row=3, col=1)
            fig.add_trace(go.Histogram(x = dff['health_ins_other'], nbinsx=50, name = 'other'),row=3, col=2)
            fig.update_layout(title_text="Health", showlegend=False, height=1000)

        elif category == 'Education':

            fig.add_trace(go.Histogram(x = dff['white_hs_dip'], nbinsx=50, name = 'white'),row=1, col=1)
            fig.add_trace(go.Histogram(x = dff['black_hs_dip'], nbinsx=50, name = 'black'),row=1, col=2)
            fig.add_trace(go.Histogram(x = dff['asian_hs_dip'], nbinsx=50, name = 'asian'),row=2, col=1)
            fig.add_trace(go.Histogram(x = dff['native_hs_dip'], nbinsx=50, name = 'native'),row=2, col=2)
            fig.add_trace(go.Histogram(x = dff['pacif_hs_dip'], nbinsx=50, name = 'pacific'),row=3, col=1)
            fig.add_trace(go.Histogram(x = dff['other_hs_dip'], nbinsx=50, name = 'other'),row=3, col=2)
            fig.update_layout(title_text="Education", showlegend=False, height=1000)

        elif category == 'Unemployment':

            fig.add_trace(go.Histogram(x = dff['white_unemp'], nbinsx=50, name = 'white'),row=1, col=1)
            fig.add_trace(go.Histogram(x = dff['black_unemp'], nbinsx=50, name = 'black'),row=1, col=2)
            fig.add_trace(go.Histogram(x = dff['asian_unemp'], nbinsx=50, name = 'asian'),row=2, col=1)
            fig.add_trace(go.Histogram(x = dff['native_unemp'], nbinsx=50, name = 'native'),row=2, col=2)
            fig.add_trace(go.Histogram(x = dff['pacif_unemp'], nbinsx=50, name = 'pacific'),row=3, col=1)
            fig.add_trace(go.Histogram(x = dff['other_unemp'], nbinsx=50, name = 'other'),row=3, col=2)
            fig.update_layout(title_text="Unemployment", showlegend=False, height=1000)
            
        return fig


# In[13]:


@app.callback(
    Output(component_id = 'us_map', component_property = 'figure'),
    [
        Input(component_id = 'master_table', component_property = 'derived_virtual_data'),
        Input(component_id = 'select_category', component_property = 'value'),
        Input(component_id = 'select_cloro', component_property = 'value'),
    ]
)

def update_cloro(all_row_data, category, race):
    if all_row_data is None:
        raise PreventUpdate
    else:
        try:
            dff = pd.DataFrame(all_row_data)
            stat_by_state = summary_stat_by_state(dff, category)
            fig = px.choropleth(stat_by_state, 
                                locations="STATE", 
                                color=stat_by_state.filter(like=race).columns.tolist()[0], 
                                hover_name="STATE", scope = 'usa', 
                                locationmode = 'USA-states', 
                                labels = {stat_by_state.filter(like='white').columns.tolist()[0]: 'white',
                                          stat_by_state.filter(like='black').columns.tolist()[0]: 'black',
                                          stat_by_state.filter(like='asian').columns.tolist()[0]: 'asian',
                                          stat_by_state.filter(like='native').columns.tolist()[0]: 'native',
                                          stat_by_state.filter(like='pacif').columns.tolist()[0]: 'pacif',
                                          stat_by_state.filter(like='other').columns.tolist()[0]: 'other'
                                         })  

            return fig
        except KeyError:
            raise PreventUpdate


# In[14]:


@app.callback(
    Output(component_id = 'us_map_nr', component_property = 'figure'),
    [
        Input(component_id = 'master_table', component_property = 'derived_virtual_data'),
        Input(component_id = 'select_cloro_nr', component_property = 'value'),
    ]
)

def update_cloro_nr(all_row_data, category):
    if all_row_data is None:
        raise PreventUpdate
    else:
        try:
            dff = pd.DataFrame(all_row_data)
            stat_by_state = summary_stat_by_state_nr(dff)
            fig = px.choropleth(
                stat_by_state,
                locations="STATE", 
                color=category, 
                hover_name="STATE", 
                scope = 'usa', 
                locationmode = 'USA-states', 
                labels = {
                    'gini_index':'Gini Index',
                    'tblack_0to10': 'Warm-To-Black',
                    'twhite_0to10': 'Warm-To-White',
                    'D_biep.White_Good_all': 'Bias',
                }
            )
                    
            return fig
        except KeyError:
            raise PreventUpdate



if __name__ == '__main__':
    app.run_server(debug=True)





