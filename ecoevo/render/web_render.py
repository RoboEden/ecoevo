import streamlit as st
import plotly.graph_objects as go

from typing import Dict
from ecoevo.maps import Tile
from ecoevo.entities.types import *
from streamlit.delta_generator import DeltaGenerator

class WebRender:

    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.gridcolor = 'rgb(28,28,28)'
        self.player_to_emoji = {
            'gold_digger': '🤑',
            'hazelnut_farmer': '🥴',
            'coral_collector': '😎',
            'sand_picker': '🤪',
            'pineapple_farmer': '🥳',
            'peanut_farmer': '😋',
            'stone_picker': '🤓',
            'pumpkin_farmer': '🤠',
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
        self.fig = go.Figure(
            go.Heatmap(
                z=[[1.0] * self.width for _ in range(self.height)],
                zmax=1,
                xgap=2,
                ygap=2,
                showscale=False,
                colorscale=[[0.0, self.gridcolor], [1.0, self.gridcolor]],
                hoverinfo="skip",
            ))


        self.fig.add_trace(
            go.Scatter(name='item_trace',
                # x=[pos[0] for pos in poses],
                # y=[pos[1] - 0.1 for pos in poses],
                showlegend=False,
                mode='text',
                # text=item_emoji,
                textfont_size=20,
                textposition="middle center",
                # customdata=info,
                hovertemplate=
                "%{customdata[0]}<br>Num: %{customdata[1]}<extra></extra>"))

        self.fig.add_trace(
            go.Scatter(name='player_trace',
                    #    x=[pos[0] for pos in poses],
                    #    y=[pos[1] + 0.1 for pos in poses],
                       showlegend=False,
                       mode='text',
                    #    text=player_emoji,
                       textfont_size=18,
                       textposition="middle center",
                    #    customdata=info,
                       hovertemplate="""%{customdata[0]}<br>
Id: %{customdata[1]}<br>
Health: %{customdata[2]}<br>
Pos: %{customdata[3]}<br>
<extra></extra>"""))

        self.fig.update_layout(
            autosize=False,
            width=800,
            height=800,
            margin=dict(l=10, r=10, b=10, t=10, pad=0),
            paper_bgcolor="#fdfcce",
            hoverlabel=dict(bgcolor="black",
                            font_size=16,
                            font_family="Rockwell"),
        )
        self.fig.update_xaxes(visible=False)
        self.fig.update_yaxes(visible=False)

    def render(self, map: Dict[PosType, Tile], ph:DeltaGenerator):
        self.update_item_trace(map)
        self.update_player_trace(map)
        ph.plotly_chart(self.fig)

    def update_item_trace(self, map: Dict[PosType, Tile]):
        poses = []
        item_emoji = []
        info = []
        for pos, tile in map.items():
            if tile.item is not None:
                poses.append(list(pos))
                item_emoji.append(self.item_to_emoji[tile.item.name])
                info.append([
                    tile.item.name,
                    tile.item.num,
                ])        
        self.fig.update_traces(x=[pos[0] for pos in poses],
                                y=[pos[1] + 0.1 for pos in poses],
                                text=item_emoji,
                                customdata=info,
                  selector=dict(type="scatter",name="item_trace"))

    def update_player_trace(self, map: Dict[PosType, Tile]):
        poses = []
        player_emoji = []
        info = []
        for pos, tile in map.items():
            if tile.player is not None:
                poses.append(list(pos))
                player_emoji.append(self.player_to_emoji[tile.player.persona])
                info.append([
                    tile.player.persona,
                    tile.player.id,
                    tile.player.health,
                    tile.player.pos,
                    tile.player.collect_remain,
                ])

        self.fig.update_traces(x=[pos[0] for pos in poses],
                                y=[pos[1] + 0.1 for pos in poses],
                                text=player_emoji,
                                customdata=info,
                  selector=dict(type="scatter",name="player_trace"))