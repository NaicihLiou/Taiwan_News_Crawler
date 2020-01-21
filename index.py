import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from app import App_no_option, App_with_option, generate_plot, App_positions, App_neutrality, App_positions_neutrality
from homepage import Homepage

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.UNITED])
app.config.suppress_callback_exceptions = True
app.layout = html.Div([
    dcc.Location(id = 'url', refresh = False), # monitors the url
    html.Div(id = 'page-content')
])

@app.callback(
    Output(component_id='page-content', component_property='children'), # Output(updated_component_id , updated_component_parameter)
    [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/report-overview': return App_no_option('overview') 
    elif pathname == '/report-position':return App_positions() #App_with_option('position')
    elif pathname == '/report-neutrality':return App_neutrality() #App_no_option('neutrality')
    elif pathname == '/report-position_neutrality':return App_positions_neutrality() #App_with_option('position_neutrality')
    elif pathname == '/about-us': return Homepage()
    else: return Homepage()

@app.callback(
    Output('output_with_option', 'children'),
    [Input('pop_radio_items', 'value'), Input('url', 'pathname')]
)
def update_graph(plot_media, pathname):
    if pathname == '/report-position': 
        graph = generate_plot(fig_num='position', time_type='week', plot_media=plot_media)
    elif pathname == '/report-neutrality':
        graph = generate_plot(fig_num='neutrality', time_type='week', plot_media=plot_media)
    else:    # pathname == '/report-position_neutrality'
        graph = generate_plot(fig_num='position_neutrality', time_type='week', plot_media=plot_media)
    return dcc.Graph(figure=graph)

if __name__ == '__main__':
    app.run_server(debug=True)



"""
# run dash in vitual environment
pip3 install virtualenv
pip3 install virtualenvwrapper
mkdir ~/.virtualenvs

virtualenv -p python3 envtest
source envtest/bin/activate
git clone https://github.com/OpenEIT/OpenEIT.git
pip3 install -r ./OpenEIT/requirements.txt
pip3 install dash dash_bootstrap_components plotly pandas colorlover matplotlib Image # reinstall packages
"""

"""
# OSError: [Errno 48] Address already in use
# Already have a process bound to the default port (8000). locate the other process
sudo lsof -i:8050
kill -9 <pid>
"""



