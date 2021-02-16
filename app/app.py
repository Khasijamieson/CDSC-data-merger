#!/usr/bin/env python
# coding: utf-8

import numpy as np
import pandas as pd
from datetime import datetime 
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

census_master = pd.read_csv('data/master.csv')
census_master['zip'] = census_master['zip'].astype(str)
census_master['zip'] = census_master['zip'].apply(lambda x: '{0:0>5}'.format(x))

col_names = {
    'B01001_001E' : 'total_population',
    'B01001H_001E' : 'tot_white_pop',
    'B01001I_001E' : 'tot_hisp_pop',
    'B01001B_001E' : 'tot_black_pop',
    'B01001C_001E' : 'tot_native_pop',
    'B01001D_001E' : 'tot_asian_pop',
    'B01001E_001E' : 'tot_pacif_pop',
    'B01001F_001E' : 'tot_other_pop',
    'B19113H_001E' : 'med_fam_inc_white',
    'B19113I_001E' : 'med_fam_inc_hisp',
    'B19113B_001E' : 'med_fam_inc_black',
    'B19113C_001E' : 'med_fam_inc_native',
    'B19113D_001E' : 'med_fam_inc_asian' ,
    'B19113E_001E' : 'med_fam_inc_pacif',
    'B19113F_001E' : 'med_fam_inc_other',
    'C27001H_001E' : 'health_ins_white',
    'C27001I_001E' : 'health_ins_hisp',
    'C27001B_001E' : 'health_ins_black',
    'C27001C_001E' : 'health_ins_native',
    'C27001D_001E' : 'health_ins_asian',
    'C27001E_001E' : 'health_ins_pacif',
    'C27001F_001E' : 'health_ins_other',
    'C15002H_003E' : 'm_white_no_hs_dip',
    'C15002H_008E' : 'f_white_no_hs_dip',
    'C15002I_003E' : 'm_hisp_no_hs_dip',
    'C15002I_008E' : 'f_hisp_no_hs_dip',
    'C15002B_003E' : 'm_black_no_hs_dip',
    'C15002B_008E' : 'f_black_no_hs_dip',
    'C15002C_003E' : 'm_native_no_hs_dip',
    'C15002C_008E' : 'f_native_no_hs_dip',
    'C15002D_003E' : 'm_asian_no_hs_dip',
    'C15002D_008E' : 'f_asian_no_hs_dip',
    'C15002E_003E' : 'm_pacif_no_hs_dip',
    'C15002E_008E' : 'f_pacif_no_hs_dip',
    'C15002F_003E' : 'm_other_no_hs_dip',
    'C15002F_008E' : 'f_other_no_hs_dip',
    'C23002H_008E' : 'm_white_unemp',
    'C23002H_021E' : 'f_white_unemp',
    'C23002I_008E' : 'm_hisp_unemp',
    'C23002I_021E' : 'f_hisp_unemp',
    'C23002B_008E' : 'm_black_unemp',
    'C23002B_021E' : 'f_black_unemp',
    'C23002C_008E' : 'm_native_unemp',
    'C23002C_021E' : 'f_native_unemp',
    'C23002D_008E' : 'm_asian_unemp',
    'C23002D_021E' : 'f_asian_unemp',
    'C23002E_008E' : 'm_pacif_unemp',
    'C23002E_021E' : 'f_pacif_unemp',
    'C23002F_008E' : 'm_other_unemp',
    'C23002F_021E' : 'f_other_unemp',
}

var = list(col_names.keys())


# In[4]:


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
    
    df['white_unemp'] = df['m_white_unemp'] + df['f_white_unemp']
    df['hisp_unemp'] = df['m_hisp_unemp'] + df['f_hisp_unemp']
    df['black_unemp'] = df['m_black_unemp'] + df['f_black_unemp']
    df['asian_unemp'] = df['m_asian_unemp'] + df['f_asian_unemp']
    df['native_unemp'] = df['m_native_unemp'] + df['f_native_unemp']
    df['pacif_unemp'] = df['m_pacif_unemp'] + df['f_pacif_unemp']
    df['other_unemp'] = df['m_other_unemp'] + df['f_other_unemp']
    
    df['white_no_hs_dip'] = df['m_white_no_hs_dip'] + df['f_white_no_hs_dip']
    df['hisp_no_hs_dip'] = df['m_hisp_no_hs_dip'] + df['f_hisp_no_hs_dip']
    df['black_no_hs_dip'] = df['m_black_no_hs_dip'] + df['f_black_no_hs_dip']
    df['asian_no_hs_dip'] = df['m_asian_no_hs_dip'] + df['f_asian_no_hs_dip']
    df['native_no_hs_dip'] = df['m_native_no_hs_dip'] + df['f_native_no_hs_dip']
    df['pacif_no_hs_dip'] = df['m_pacif_no_hs_dip'] + df['f_pacif_no_hs_dip']
    df['other_no_hs_dip'] = df['m_other_no_hs_dip'] + df['f_other_no_hs_dip']
    
    export = df.drop([
        'm_white_no_hs_dip',
        'f_white_no_hs_dip',
        'm_hisp_no_hs_dip',
        'f_hisp_no_hs_dip',
        'm_black_no_hs_dip',
        'f_black_no_hs_dip',
        'm_native_no_hs_dip',
        'f_native_no_hs_dip',
        'm_asian_no_hs_dip',
        'f_asian_no_hs_dip',
        'm_pacif_no_hs_dip',
        'f_pacif_no_hs_dip',
        'm_other_no_hs_dip',
        'f_other_no_hs_dip',
        'm_white_unemp',
        'f_white_unemp',
        'm_hisp_unemp',
        'f_hisp_unemp',
        'm_black_unemp',
        'f_black_unemp',
        'm_native_unemp',
        'f_native_unemp',
        'm_asian_unemp',
        'f_asian_unemp',
        'm_pacif_unemp',
        'f_pacif_unemp',
        'm_other_unemp',
        'f_other_unemp'
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
        pop_df = dff.filter(like = 'tot_')
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
            'tot_asian_pop': 'asian', 
            'tot_black_pop': 'black', 
            'tot_hisp_pop': 'hispanic', 
            'tot_white_pop': 'white',
            'tot_native_pop' : 'native',
            'tot_pacif_pop' : 'pacif',
            'tot_other_pop' : 'other'
        }
        population['max_race'] = population['max_race'].map(d_pop)
        population['min_race'] = population['min_race'].map(d_pop)
        
        return population.round(2)
        
    elif var == 'Income':
        income_df = dff.filter(like = 'inc')
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
            'med_fam_inc_hisp' : 'hisp',
            'med_fam_inc_native' : 'native',
            'med_fam_inc_pacif' : 'pacif',
            'med_fam_inc_other' : 'other'
        }
        income['max_race'] = income['max_race'].map(d_inc)
        income['min_race'] = income['min_race'].map(d_inc)
        
        return income.round(2)
    
    elif var == 'Health':
        health_df = dff.filter(like = 'health')
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
            'health_ins_hisp' : 'hisp',
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
            'hisp_unemp' : 'hisp',
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
            'white_no_hs_dip' : 'white',
            'hisp_no_hs_dip' : 'hisp',
            'black_no_hs_dip' : 'black',
            'asian_no_hs_dip' : 'asian',
            'native_no_hs_dip' : 'native',
            'pacif_no_hs_dip' : 'pacif',
            'other_no_hs_dip' : 'other'
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
        pop_df = dff.filter(like = 'tot_')
        population = pop_df.copy()
        population['mean'] = pop_df.mean(axis = 1)
        population['std'] = pop_df.std(axis = 1)
        population['max_race'] = pop_df.idxmax(axis = 1)
        population['max'] = pop_df.max(axis = 1)
        population['min_race'] = pop_df.idxmin(axis = 1)
        population['min'] = pop_df.min(axis = 1)
        population['range'] = population['max'] - population['min']
        d_pop = {
            'tot_asian_pop': 'asian', 
            'tot_black_pop': 'black', 
            'tot_hisp_pop': 'hispanic', 
            'tot_white_pop': 'white',
            'tot_native_pop' : 'native',
            'tot_pacif_pop' : 'pacif',
            'tot_other_pop' : 'other'
        }
        population['max_race'] = population['max_race'].map(d_pop)
        population['min_race'] = population['min_race'].map(d_pop)
        pop_merge = pd.concat([id_zip, population], axis = 1)
        
        return pop_merge.round(2)
    
    elif var == 'Income':
        income_df = dff.filter(like = 'inc')
        income = income_df.copy()
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
            'med_fam_inc_hisp' : 'hisp',
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
        health = health_df.copy()
        health['mean'] = health_df.mean(axis = 1)
        health['std'] = health_df.std(axis = 1)
        health['max_race'] = health_df.idxmax(axis = 1)
        health['max'] = health_df.max(axis = 1)
        health['min_race'] = health_df.idxmin(axis = 1)
        health['min'] = health_df.min(axis = 1)
        health['range'] = health['max'] - health['min']
        d_health = {
            'health_ins_white' : 'white',
            'health_ins_hisp' : 'hisp',
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
        unemp = unemp_df.copy()
        unemp['mean'] = unemp_df.mean(axis = 1)
        unemp['std'] = unemp_df.std(axis = 1)
        unemp['max_race'] = unemp_df.idxmax(axis = 1)
        unemp['max'] = unemp_df.max(axis = 1)
        unemp['min_race'] = unemp_df.idxmin(axis = 1)
        unemp['min'] = unemp_df.min(axis = 1)
        unemp['range'] = unemp['max'] - unemp['min']
        d_unemp = {
            'white_unemp' : 'white',
            'hisp_unemp' : 'hisp',
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
        hs_dip = hs_dip_df.copy()
        hs_dip['mean'] = hs_dip_df.mean(axis = 1)
        hs_dip['std'] = hs_dip_df.std(axis = 1)
        hs_dip['max_race'] = hs_dip_df.idxmax(axis = 1)
        hs_dip['max'] = hs_dip_df.max(axis = 1)
        hs_dip['min_race'] = hs_dip_df.idxmin(axis = 1)
        hs_dip['min'] = hs_dip_df.min(axis = 1)
        hs_dip['range'] = hs_dip['max'] - hs_dip['min']
        d_hs_dip = {
            'white_no_hs_dip' : 'white',
            'hisp_no_hs_dip' : 'hisp',
            'black_no_hs_dip' : 'black',
            'asian_no_hs_dip' : 'asian',
            'native_no_hs_dip' : 'native',
            'pacif_no_hs_dip' : 'pacif',
            'other_no_hs_dip' : 'other'
        }
        hs_dip['max_race'] = hs_dip['max_race'].map(d_hs_dip)
        hs_dip['min_race'] = hs_dip['min_race'].map(d_hs_dip)
        hs_dip_merge = pd.concat([id_zip, hs_dip], axis = 1)   
        
        return hs_dip_merge.round(2)
    
    else:
        print("input error")


app.layout = html.Div([

    html.H2(
        children = 'Conceptual Development and Social Cognition Lab',
        style = {
               'textAlign': 'center',
        }    
    ),
    
    html.Div(
        children = 'Census Data Aggregator',
        style = {
            'textAlign': 'center',
            'padding': 10,
        }
    ),
    
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
    
    dash_table.DataTable(
        id = 'master_table',
        columns = [{'name': i, 'id': i, 'selectable': True, 'hideable': True} for i in var],
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
        ),
    
    html.Br(),
    html.Br(),
    
    html.A(
        'Download Data',
        id='download-link',
        download="merged_data.csv",
        href="",
        target="_blank"
    ),
    
    html.Br(),
    html.Br(),
    
    dcc.Dropdown(
        id = 'select_category',
        options = [
            {'label' : 'Income', 'value' : 'Income'},
            {'label' : 'Population', 'value' : 'Population'},
            {'label' : 'Health', 'value' : 'Health'}, 
            {'label' : 'Education', 'value' : 'Education'},
            {'label' : 'Unemployment', 'value' : 'Unemployment'},
        ],
        placeholder = 'Select Category',
        value = 'Income',
        style = {'width': '40%'}
    ),
    
    html.Br(),
    html.Br(),
    
    
    html.Div(
        id = 'summary_by_sample',
        children = [],
    ),
    
    html.Br(),
    
    html.Div(
        id = 'summary_by_state',
        children = [],
    ),
    
    html.Br(),
    html.Br(),
    
    dcc.Graph(
        id = 'sum_stat',
        figure ={}
    ),
    
    html.Br(),
    html.Br(),
    
    dcc.Dropdown(
        id = 'select_cloro',
        options = [
            {'label' : 'white', 'value' : 'white'},
            {'label' : 'black', 'value' : 'black'}, 
            {'label' : 'asian', 'value' : 'asian'},
            {'label' : 'hisp', 'value' : 'hisp'},
            {'label' : 'native', 'value' : 'native'},
            {'label' : 'pacif', 'value' : 'pacif'},
            {'label' : 'other', 'value' : 'other'},
        ],
        placeholder = 'Select Category',
        value = 'white',
        style = {'width': '40%'}
    ),    
    
    dcc.Graph(
        id = 'us_map',
        figure ={}
    ),
    
    
    html.Br(),
    
    html.Div(
        id='storage', 
        style={'display': 'none'},
        children = []
    ),

    html.Br(),
    html.Br(),
])


@app.callback(
    Output('storage', 'children'), 
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
        df = gen_census_data(raw)

        return df.to_json(date_format='iso', orient='split')



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


# In[12]:


@app.callback(
    Output(component_id = 'download-link', component_property = 'href'),
    [
        Input(component_id = 'storage', component_property = 'children')
    ]
)

def export_to_csv(storage):
    df = pd.read_json(storage, orient='split')
    csv_string = df.to_csv(index=False, encoding='utf-8')
    csv_string = "data:text/csv;charset=utf-8,%EF%BB%BF" + urllib.parse.quote(csv_string)
    
    return csv_string
    


@app.callback(
    [
        Output(component_id = 'summary_by_sample', component_property = 'children'),
        Output(component_id = 'summary_by_state', component_property = 'children')
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

        return table_1, table_2


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
        fig = make_subplots(rows=2, cols=4)

        if category == 'Income':

            fig.add_trace(go.Histogram(x = dff['med_fam_inc_white'], nbinsx=50, name = 'white'),row=1, col=1)
            fig.add_trace(go.Histogram(x = dff['med_fam_inc_black'], nbinsx=50, name = 'black'),row=1, col=2)
            fig.add_trace(go.Histogram(x = dff['med_fam_inc_asian'], nbinsx=50, name = 'asian'),row=1, col=3)
            fig.add_trace(go.Histogram(x = dff['med_fam_inc_hisp'], nbinsx=50, name = 'hispanic'),row=1, col=4)
            fig.add_trace(go.Histogram(x = dff['med_fam_inc_native'], nbinsx=50, name = 'native'),row=2, col=1)
            fig.add_trace(go.Histogram(x = dff['med_fam_inc_pacif'], nbinsx=50, name = 'pacific'),row=2, col=2)
            fig.add_trace(go.Histogram(x = dff['med_fam_inc_other'], nbinsx=50, name = 'other'),row=2, col=3)
            fig.update_layout(title_text="Income", height=700)

        elif category == 'Population':

            fig.add_trace(go.Histogram(x = dff['tot_white_pop'], nbinsx=50, name = 'white'),row=1, col=1)
            fig.add_trace(go.Histogram(x = dff['tot_black_pop'], nbinsx=50, name = 'black'),row=1, col=2)
            fig.add_trace(go.Histogram(x = dff['tot_asian_pop'], nbinsx=50, name = 'asian'),row=1, col=3)
            fig.add_trace(go.Histogram(x = dff['tot_hisp_pop'], nbinsx=50, name = 'hispanic'),row=1, col=4)
            fig.add_trace(go.Histogram(x = dff['tot_native_pop'], nbinsx=50, name = 'native'),row=2, col=1)
            fig.add_trace(go.Histogram(x = dff['tot_pacif_pop'], nbinsx=50, name = 'pacific'),row=2, col=2)
            fig.add_trace(go.Histogram(x = dff['tot_other_pop'], nbinsx=50, name = 'other'),row=2, col=3)
            fig.update_layout(title_text="Population", height=700)

        elif category == 'Health':

            fig.add_trace(go.Histogram(x = dff['health_ins_white'], nbinsx=50, name = 'white'),row=1, col=1)
            fig.add_trace(go.Histogram(x = dff['health_ins_black'], nbinsx=50, name = 'black'),row=1, col=2)
            fig.add_trace(go.Histogram(x = dff['health_ins_asian'], nbinsx=50, name = 'asian'),row=1, col=3)
            fig.add_trace(go.Histogram(x = dff['health_ins_hisp'], nbinsx=50, name = 'hispanic'),row=1, col=4)
            fig.add_trace(go.Histogram(x = dff['health_ins_native'], nbinsx=50, name = 'native'),row=2, col=1)
            fig.add_trace(go.Histogram(x = dff['health_ins_pacif'], nbinsx=50, name = 'pacific'),row=2, col=2)
            fig.add_trace(go.Histogram(x = dff['health_ins_other'], nbinsx=50, name = 'other'),row=2, col=3)
            fig.update_layout(title_text="Health", height=700)

        elif category == 'Education':

            fig.add_trace(go.Histogram(x = dff['white_no_hs_dip'], nbinsx=50, name = 'white'),row=1, col=1)
            fig.add_trace(go.Histogram(x = dff['black_no_hs_dip'], nbinsx=50, name = 'black'),row=1, col=2)
            fig.add_trace(go.Histogram(x = dff['asian_no_hs_dip'], nbinsx=50, name = 'asian'),row=1, col=3)
            fig.add_trace(go.Histogram(x = dff['hisp_no_hs_dip'], nbinsx=50, name = 'hispanic'),row=1, col=4)
            fig.add_trace(go.Histogram(x = dff['native_no_hs_dip'], nbinsx=50, name = 'native'),row=2, col=1)
            fig.add_trace(go.Histogram(x = dff['pacif_no_hs_dip'], nbinsx=50, name = 'pacific'),row=2, col=2)
            fig.add_trace(go.Histogram(x = dff['other_no_hs_dip'], nbinsx=50, name = 'other'),row=2, col=3)
            fig.update_layout(title_text="Education", height=700)

        elif category == 'Unemployment':

            fig.add_trace(go.Histogram(x = dff['white_unemp'], nbinsx=50, name = 'white'),row=1, col=1)
            fig.add_trace(go.Histogram(x = dff['black_unemp'], nbinsx=50, name = 'black'),row=1, col=2)
            fig.add_trace(go.Histogram(x = dff['asian_unemp'], nbinsx=50, name = 'asian'),row=1, col=3)
            fig.add_trace(go.Histogram(x = dff['hisp_unemp'], nbinsx=50, name = 'hispanic'),row=1, col=4)
            fig.add_trace(go.Histogram(x = dff['native_unemp'], nbinsx=50, name = 'native'),row=2, col=1)
            fig.add_trace(go.Histogram(x = dff['pacif_unemp'], nbinsx=50, name = 'pacific'),row=2, col=2)
            fig.add_trace(go.Histogram(x = dff['other_unemp'], nbinsx=50, name = 'other'),row=2, col=3)
            fig.update_layout(title_text="Unemployment", height=700)

        return fig


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
                                          stat_by_state.filter(like='hisp').columns.tolist()[0]: 'hisp',
                                          stat_by_state.filter(like='native').columns.tolist()[0]: 'native',
                                          stat_by_state.filter(like='pacif').columns.tolist()[0]: 'pacif',
                                          stat_by_state.filter(like='other').columns.tolist()[0]: 'other'
                                         })  

            return fig
        except KeyError:
            raise PreventUpdate


if __name__ == '__main__':
    app.run_server(debug = True)

