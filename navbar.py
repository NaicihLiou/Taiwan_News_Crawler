import dash_bootstrap_components as dbc

HOME_LOGO = "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fd/Academia_Sinica_Emblem.svg/1200px-Academia_Sinica_Emblem.svg.png"
"""
def Navbar():
    navbar = dbc.NavbarSimple(
        children=[
            dbc.NavItem(dbc.NavLink("Calendar", active=True, href="#", n_clicks=0)),
            dbc.NavItem(dbc.NavLink("Overview", href="/report-overview")),
            dbc.NavItem(dbc.NavLink("Positions", href="/report-position")),
            dbc.NavItem(dbc.NavLink("Neutrality", href="/report-neutrality")),
            dbc.NavItem(dbc.NavLink("Positions & Neutrality", href="/report-position_neutrality")),
        ],
        brand="Home", brand_href="/home", #brand_style =
        sticky="top",   # Stick the navbar as scrolling
        #color="dark", dark=True,
        color="#ffffff", light=True
    )
    return navbar
"""
import dash_html_components as html
def Navbar():
    navbar = dbc.Navbar(
        dbc.Container(
            [
                html.A(
                    # Use row and col to control vertical alignment of logo / brand
                    dbc.Row(
                        [dbc.Col(html.Img(src=HOME_LOGO, height="30px")),],
                        align="center", no_gutters=True,
                    ),
                    href="https://plot.ly",
                ),
                #dbc.Col(dbc.NavbarBrand("Home", href="/home"), sm=3, md=2),
                dbc.Col(dbc.NavItem(dbc.NavLink("報導量", href="/report-overview"))),
                dbc.Col(dbc.NavItem(dbc.NavLink("立場中立性", href="/report-position"))),
                dbc.Col(dbc.NavItem(dbc.NavLink("語氣客觀性", href="/report-neutrality"))),
                dbc.Col(dbc.NavItem(dbc.NavLink("總覽", href="/report-position_neutrality"))),
                dbc.Col(dbc.NavItem(dbc.NavLink("關於我們", href="/about-us"))),
            ]
        ),
        color="#ffffff", light=True,
        #color="dark", dark=True,
        className="ml-auto flex-nowrap mt-12 mt-md-12",
        #className="mb-12",
    )
    return  navbar
            
