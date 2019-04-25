import flask
from flask import Flask, render_template, url_for, flash, redirect
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import dash_table
import pandas as pd
from SqlConnect import getData

print(dcc.__version__) # 0.6.0 or above is required

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# hard-code query in getData().  Fix this
df = getData()
column_names_list = list(df.columns.values)
column_names_count = len(column_names_list)
server = flask.Flask(__name__)

# Flask portion: entry point and all html pages.
@server.route('/')
def index():
    return render_template('home.html')



# Dash portion: serve up the tables and charts
app = dash.Dash(__name__,server=server,
                external_stylesheets=external_stylesheets,
                routes_pathname_prefix='/dash/')

app.layout = html.Div([

    dash_table.DataTable(
        id='skynet-datatable',

        columns=[
            {"name": i, "id": i, "deletable": False} for i in df.columns],

        data=df.to_dict("rows"),
        editable=True,
        filtering=False,
        sorting=True,
        sorting_type="multi",
        row_selectable="multi",
        row_deletable=True,
        selected_rows=[],
        pagination_mode="fe",
        pagination_settings={
            "displayed_pages": 1,
            "current_page": 0,
            "page_size": 35,
        },
        navigation="page",

        n_fixed_rows=1,
        # style_table={'overflowX': 'scroll'},
        style_table={'backgroundColor': 'rgb(50, 50, 50)'},

        style_cell_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': 'rgb(248, 248, 248)',
                'if': {'row_index': 'even'},
                'backgroundColor': 'rgb(148, 148, 148)'

            }],
        style_cell={
            'backgroundColor': 'rgb(50, 50, 50)',
            'color': 'white',
            # 'minWidth': '0px', 'maxWidth': '40px',
            'whiteSpace': 'normal',
            'textOverflow': 'ellipsis',
            'textAlign': 'left'
        },
        style_header={
            'backgroundColor': 'black',
            'fontWeight': 'bold'
        },
    ),

    html.Div(id='datatable-interactivity-container')
])
@app.callback(
    Output('datatable-interactivity-container', "children"),
    [Input('skynet-datatable', "derived_virtual_data"),
     Input('skynet-datatable', "derived_virtual_selected_rows")])
def update_graph(rows, derived_virtual_selected_rows):
    # When the table is first rendered, `derived_virtual_data` and
    # `derived_virtual_selected_rows` will be `None`. This is due to an
    # idiosyncracy in Dash (unsupplied properties are always None and Dash
    # calls the dependent callbacks when the component is first rendered).
    # So, if `rows` is `None`, then the component was just rendered
    # and its value will be the same as the component's dataframe.
    # Instead of setting `None` in here, you could also set
    # `derived_virtual_data=df.to_rows('dict')` when you initialize
    # the component.
    if derived_virtual_selected_rows is None:
        derived_virtual_selected_rows = []

    if rows is None:
        dff = df
    else:
        dff = pd.DataFrame(rows)

    colors = []
    for i in range(len(dff)):
        if i in derived_virtual_selected_rows:
            colors.append("#7FDBFF")
        else:
            colors.append("#0074D9")

    return html.Div(
        [
            dcc.Graph(
                id=column,
                figure={
                    "data": [
                        {
                            "x": dff["AI count"],
                            # check if column exists - user may have deleted it
                            # If `column.deletable=False`, then you don't
                            # need to do this check.
                            "y": dff[column] if column in dff else [],
                            "type": "bar",
                            "marker": {"color": colors},
                        }
                    ],
                    "layout": {
                        "xaxis": {"automargin": True},
                        "yaxis": {"automargin": True},
                        "height": 250,
                        "margin": {"t": 10, "l": 10, "r": 10},
                    },
                },
            )

            for column in column_names_list
            # for column in ["AI count","AI","G2S Enabled","SAS Enabled","Push Number","Date of Test","Theme"]
        ]
    )

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')