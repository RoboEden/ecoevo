import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

from typing import Dict
from ecoevo.maps import Tile
from ecoevo.entities.types import *


class WebRender:

    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.player_to_emoji = {
            'gold_digger': ':angry_face:',
            'hazelnut_farmer': ':angry_face_with_horns:',
            'coral_collector': ':anguished_face:',
            'sand_picker': ':anxious_face_with_sweat:',
            'pineapple_farmer': ':astonished_face:',
            'peanut_farmer': ':beaming_face_with_smiling_eyes:',
            'stone_picker': ':cat_face:',
            'pumpkin_farmer': ':bear_face:',
        }

        self.item_to_emoji = {
            'gold': '🪙',
            'hazelnut': '🌰',
            'coral': '🪸',
            'sand': '🏖️',
            'pineapple': '🍍',
            'peanut': '🥜',
            'stone': '🪨',
            'pumpkin': '🎃',
        }
        self.fig = go.Figure()
        self.fig.update_layout(
            autosize=False,
            width=800,
            height=800,
            margin=dict(l=10, r=10, b=10, t=10, pad=4),
            paper_bgcolor="#B68E55",
        )

        self.colorscale = [[0.0, 'rgb(12,12,12)']]

    def render(self, map: Dict[PosType, Tile]):
        color = [[.0] * self.width for _ in range(self.height)]
        emoji = [[''] * self.width for _ in range(self.height)]
        name = [[''] * self.width for _ in range(self.height)]
        num = [[''] * self.width for _ in range(self.height)]
        for pos, tile in map.items():
            x, y = pos
            if tile.item is not None:
                emoji[x][y] = self.item_to_emoji[tile.item.name]
                name[x][y] = tile.item.name
                num[x][y] = tile.item.num

        self.fig.add_trace(go.Heatmap(z=color, ))
        #  title='Periodic Table')
        self.fig.update_traces(
            xgap=2,
            ygap=2,
            showscale=False,
            colorscale=self.colorscale,
            text=emoji,
            texttemplate="%{text}",
            textfont_size=20,
            customdata=np.moveaxis([name, num], 0, -1),
            hovertemplate=
            "%{customdata[0]}<br>Num: %{customdata[1]:.2f}<extra></extra>",
        )
        self.fig.update_xaxes(visible=False)
        self.fig.update_yaxes(visible=False)
        st.plotly_chart(self.fig)