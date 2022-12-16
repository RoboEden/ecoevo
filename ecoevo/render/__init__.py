
try:
    from dash import Dash, html,dcc, Output, Input
    from rich import print
    from plotly import graph_objects as go
    import dash_bootstrap_components as dbc
except ImportError:
    raise ImportError("Try pip install ecoevo[render]!")