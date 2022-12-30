try:
    from dash import Dash, dash_table, dcc, html
    from dash import Output, Input, State
    from rich import print
    from plotly import graph_objects
    import dash_bootstrap_components
    from ecoevo.render.app import WebApp
except ImportError:
    raise ImportError("Try pip install ecoevo[render]!")