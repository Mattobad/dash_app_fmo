import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.express as px

# from jupyter_dash import JupyterDash
import dash_bootstrap_components as dbc
import dash_table
import dash_table.FormatTemplate as FormatTemplate

# df = px.data.gapminder()
# all_continents = df.continent.unique()
import pandas as pd
from datetime import datetime as dt
#internal imports
from app import app

import os
# logger
import logging


# set the logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# for showing the logs to console
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

# adding the stream handler
logger.addHandler(stream_handler)


# utility functions
def load_data(path,file_name):

    file_path =os.path.join(path,file_name)
    return pd.read_csv(file_path)


'''
Loading files
'''
data_path = "data/"
# property info
df_property = load_data(data_path,"property_info_main.csv")
# df_property.drop('Portfolio_Manager_Property_ID',axis=1,inplace=True)
df_property.rename(columns={'Gross Floor Area':'GFA(Sq.ft)'},inplace=True)

# building data
building_df = load_data(data_path,"building_avg_info.csv")

rename_cols = ['Property_Name', 'Property_type', 'GFA',
       'YearBuilt', 'Unit_of_Measure', 'Cost', 'Consumption',
       'Consumption_per_Sqft']

# rename the cols
building_df.columns = rename_cols

# FMO monthly data 
monthly_fmo_df = load_data(data_path,"open_data_with_property_categories.csv")

#######################################################################################################
"""
TAB COMPONENT
"""
#######################################################################################################

app_tabs = html.Div([
    # dbc -> dash wrapper for bootstrap components
    dbc.Tabs([
        
        # dbc.Tab(label="HRM FMO", tab_id ="tab-hrm", labelClassName="text-success font-weight-bold",
        #         activeLabelClassName="text-danger"),
        dbc.Tab(label="HRM Property Type", tab_id ="tab_property_type", labelClassName="text-success font-weight-bold",
                activeLabelClassName="text-danger"),
        dbc.Tab(label="HRM Property", tab_id ="tab_property", labelClassName="text-success font-weight-bold",
                activeLabelClassName="text-danger"),
        
        
    ],
    id='tabs',
    active_tab = "tab-mentions",
    ),
], className='mt-3'
)


#######################################################################################################
"""
MAIN LAYOUT
"""
#######################################################################################################
main_layout = html.Div([
    # header row
     dbc.Row(
        dbc.Col(html.H1("FMO Dashboard",
                        className='text-center text-primary mb-4'),
                width=12)
    ),

    html.Hr(),
    dbc.Row(dbc.Col(app_tabs, width=12),className='mb-3'),
    html.Div(id='content', children=[]),
    
    # Another graph to show energy efficiency of the building on card view

        ]
        )

#######################################################################################################
"""
MOCKUP COMPONENT & VARIABLES
"""
#######################################################################################################

PAGE_SIZE = 10

mockup_layout = html.Div([

    html.H5('Overall Average Energy consumption data table'),
    html.Hr(),
    html.Div(id="dtable"),
    html.Br(),

#     dbc.Row([
#         dbc.Col([
#                 dcc.Dropdown(id='dpdn_aggregate', multi=False, value= 'Year',
#                          options=[{'label':x, 'value':x}
#                                   for x in ['Year','Month']]
# #                                   for x in sorted(df['Symbols'].unique())],
#                          ),
#             ],
#                 xs=12, sm=12, md=12, lg=5, xl=5
#             )
#     ]),

    html.Br(),
    html.H6(id='sub-title'),
    html.Hr(),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody(
                    id='c-cost'
                    # html.P("Text-1",className='card-text')
                )
            ])
        ]),
        dbc.Col([
            dbc.Card([
                dbc.CardBody(
                    id='c-usage'
                    # html.P("Text-2",className='card-text')
                )
            ])
        ]),
        dbc.Col([
            dbc.Card([
                dbc.CardBody(
                    id = 'c-cost-sq'
                    # html.P("Text-3",className='card-text')
                )
            ])
        ]),
        
    ]),

    # spaces
    html.Br(),

    html.Div(id='line_graph'),
    html.Div(id='line_graph1')
])

#######################################################################################################
"""
MAIN CALLBACKS
"""
#######################################################################################################
#main callback for the Tabs
@app.callback(
    Output("content",'children'),
    [Input('tabs','active_tab')]
)
def switch_tab(tab_chosen):
    # if tab_chosen == "tab-hrm":
    #     return hrm_layout #html.P("HRM")
    if tab_chosen == "tab_property":
        return mockup_layout #html.P("Daily time series for the energy consumption")
    
    elif tab_chosen == "tab_property_type":
        return html.P("HRM Property Type")#nilm_layout
    
    return html.P("Please select one the tabs to display the content")



#######################################################################################################
"""
MOCKUP CALLBACKS
"""
#######################################################################################################

cols_selected = ['Property Name',
                         #'Portfolio_Manager_Property_ID',
                         'Year Built',
                         'Property_type',
                         'GFA(Sq.ft)']
# data table
@app.callback(
    Output('dtable','children'),
    [Input('dtable','value')])
def update_data_table(value):


    dtable = dash_table.DataTable(
        id='datatable-paging',
        columns=[{"name": i, "id": i} for i in df_property[cols_selected].columns
        ],
        # data=building_df.to_dict('records'),
        filter_action='native',

        # style_table={
        #     'height': 200,
        # },
        style_data={
            'width': '100px', 'minWidth': '100px', 'maxWidth': '200px',
            'overflow': 'hidden',
            'textOverflow': 'ellipsis',
        },

        #adding color highlight
        style_data_conditional= [
            {
                'if' :{
                    'filter_query': '{{GFA(Sq.ft)}} = {}'.format(i),
                    'column_id': 'GFA(Sq.ft)'
                },
                'backgroundColor': 'tomato',
                'color': 'white'
            } for i in [df_property['GFA(Sq.ft)'].min(),
                                    df_property['GFA(Sq.ft)'].max()]
        ],

        # tooltip_data=[
        #     {
        #         column: {'value': str(value), 'type': 'markdown'}
        #         for column, value in row.items() if column in ['Property_Name','Property_type']
        #     } for row in data
        # ],
        # tooltip_duration=None,

        sort_action='custom',
        sort_mode='single',
        sort_by=[],
        row_selectable='single',
        selected_columns=[],
        selected_rows=[],
        page_action="native",
        page_current= 0,
        page_size= PAGE_SIZE,
        #hidden_columns = ['geometry'],
    )

    return dtable


# table sorting
@app.callback(
    Output('datatable-paging', 'data'),
    [Input('datatable-paging', 'sort_by')])
def update_table(sort_by):

    # work
    df = df_property[cols_selected]
    if len(sort_by):
        dff = df.sort_values(
            sort_by[0]['column_id'],
            ascending=sort_by[0]['direction'] == 'asc',
            inplace=False
        )
    else:
        # No sort is applied
        dff = df

    return dff.to_dict('records')


"""
Update building information
"""
# card views
@app.callback(
    # Output('bar_content','children'),
    Output('c-cost','children'),
    Output('c-usage','children'),
    Output('c-cost-sq','children'),
    Output('sub-title','children'),
    [Input('datatable-paging', "derived_virtual_data"),
    Input('datatable-paging', "derived_virtual_selected_rows")])
def upate_card_views(rows, derived_v_rows):

    if derived_v_rows is None: # nothing is selected
        return 
    elif rows is None:
        dff=[['1']]  # nothing to select

    else:
        try:
            dff = pd.DataFrame(rows)
            logger.info(f'selected rows={derived_v_rows}')
            logger.info(f'DataFrame columns={dff.columns}')
            logger.info(f'{dff}')
            logger.info(f"Number of units = {dff['Property Name'].nunique()}")
            logger.info(f"{dff['Property_type'].value_counts()}")
            # extract the info from the selected row
            building_name = dff['Property Name'][derived_v_rows].values[0]
            built_year = dff['Year Built'][derived_v_rows].values[0]
            property_type = dff['Property_type'][derived_v_rows].values[0]
            logger.info(f'Selected building name = {building_name} & year={built_year} & {property_type}')
            
            ## Card views
            current_year = dt.now().year
            oldest = dff.loc[dff['Property_type'] == property_type,'Year Built'].min()
            newest = dff.loc[dff['Property_type'] == property_type,'Year Built'].max()
            bool_mask_old = (dff['Property_type'] == property_type) & (dff['Year Built'] == oldest)
            bool_mask_new = (dff['Property_type'] == property_type) & (dff['Year Built'] == newest)

            old_builiding = dff.loc[bool_mask_old,'Property Name'].iloc[0]
            new_building = dff.loc[bool_mask_new,'Property Name'].iloc[0]
            building_number = dff.loc[dff['Property_type'] == property_type,'Property Name'].nunique()
            # card dummy values
            card_1 = html.P(f'Building "{building_name}" age = {current_year - built_year}')

            card_2 = html.P(f'Oldest Building "{old_builiding}" age = {current_year - oldest}')
            card_3 = html.P(f'Newest Building "{new_building}" age = {current_year - newest}')

            title_header = f'Building name = "{building_name}" from property type = "{property_type}({building_number} units)"'

            return card_1,card_2,card_3,title_header

        except:
            logger.exception('Error!!!: card view')


# line graph for KWHr
@app.callback(
    Output('line_graph','children'),
    # Output('line_graph1','children'),
    [Input('datatable-paging', "derived_virtual_data"),
    Input('datatable-paging', "derived_virtual_selected_rows")])
def upate_mock_bar(rows, derived_v_rows):

    if derived_v_rows is None: # nothing is selected
        return 
    elif rows is None:
        dff=[['1']]  # nothing to select

    else:

        try:
            
            dff = pd.DataFrame(rows)
            logger.info(f'DataFrame columns={dff.columns}')
            # extract the info from the selected row
            building_name = dff['Property Name'][derived_v_rows].values[0]

            built_year = dff['Year Built'][derived_v_rows].values[0]
            property_type = dff['Property_type'][derived_v_rows].values[0]

            building_id = df_property.loc[df_property['Property Name'] == building_name,
                                                    'Portfolio_Manager_Property_ID'].iloc[0]

            yearly_df = monthly_fmo_df.groupby(['Portfolio_Manager_Property_ID','Portfolio_Manager_Property_Name',
                                                'Property_type',
                                                'Unit_of_Measure','Year']).agg({'Consumption':'mean',
                                                                            'Cost':'mean'})

            yearly_df = yearly_df.add_prefix('Yearly_avg_').reset_index().round(2)

            logger.info(f'DataFrame columns = {yearly_df.columns}')
            logger.info(f'{yearly_df.head()}')
           

            # building name from the monthly consumption dataset
            building_name1 = yearly_df.loc[yearly_df['Portfolio_Manager_Property_ID'] == building_id,
                                                                'Portfolio_Manager_Property_Name'].iloc[0]

            logger.info(f'Building Id = {building_id} with name = {building_name1}')
            bool_mask = (yearly_df['Property_type'] == property_type) & \
                                                (yearly_df['Unit_of_Measure'] == 'kWh (kilowatt-hours)')


            

            df1 = yearly_df.loc[bool_mask]

            df1['Year'] = df1['Year'].astype('str')

            title = f'Yearly average renewable enegery(kWh (kilowatt-hours)) by `{property_type}` property category'
            fig = px.line(df1, x='Year',y='Yearly_avg_Consumption',color='Portfolio_Manager_Property_Name',
                                    color_discrete_sequence=['#95a5a6'],##57606f,#c8d6e5
                                    color_discrete_map ={str(building_name1):"#54a0ff"})
            fig.update_layout(plot_bgcolor="#f1f2f6",showlegend=False,title=title)

            if property_type in ['Indoor Arena','Police Station']:
                return dcc.Graph(figure=fig), None

            # bool mask for energy consumption fuel
            bool_mask_fuel = (yearly_df['Property_type'] == property_type) & \
                                                (yearly_df['Unit_of_Measure'] != 'kWh (kilowatt-hours)')


            title1 = f'Yearly average non-renewable enegery(L (Litres)) by `{property_type}` property category'
            df2 = yearly_df.loc[bool_mask_fuel]
            df2['Year'] = df2['Year'].astype('str')
            fig1 = px.line(df2, x='Year',y='Yearly_avg_Consumption',color='Portfolio_Manager_Property_Name',
                                    color_discrete_sequence=['#95a5a6'],##57606f,#c8d6e5
                                    color_discrete_map ={str(building_name1):"#54a0ff"})
            fig1.update_layout(plot_bgcolor="#f1f2f6",showlegend=False,title=title1)
            # text anotation
            # fig.update_traces(texttemplate='%{text:.2s}', textposition='outside')
            # fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')

            return dcc.Graph(figure=fig),dcc.Graph(figure=fig1)
             
        except:
            logger.exception('Error!!!: line graph')

# # line graph for fuels
# @app.callback(
#     # Output('line_graph','children'),
#     Output('line_graph1','children'),
#     [Input('datatable-paging', "derived_virtual_data"),
#     Input('datatable-paging', "derived_virtual_selected_rows")])
# def upate_mock_bar(rows, derived_v_rows):

#     if derived_v_rows is None: # nothing is selected
#         return 
#     elif rows is None:
#         dff=[['1']]  # nothing to select

#     else:

#         try:
            
#             print('HEllo')
#         except:
#             logger.exception('Error!!!: line graph')