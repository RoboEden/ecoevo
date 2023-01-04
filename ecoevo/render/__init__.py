try:
    import dash_bootstrap_components
    from dash import dcc, html, dash_table, ctx, exceptions
    from dash import Dash, Output, Input, State, ClientsideFunction
    from plotly import graph_objects
    from rich import print
    from ecoevo.render.app import WebApp
except ImportError:
    raise ImportError("Try pip install ecoevo[render]!")