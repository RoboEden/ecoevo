import math
from typing import Dict, List, Tuple
from ecoevo.entities import Tile, Player
from ecoevo.render import graph_objects as go
from ecoevo.types import PosType, IdType, OfferType


class GameScreen:

    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.gridcolor = 'rgb(28,28,28)'
        self.trade_line_width = 0.2
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
        self.init_figure()

    def init_figure(self):
        self.fig = go.Figure(
            go.Heatmap(z=[[1.0] * self.width for _ in range(self.height)],
                       zmax=1,
                       xgap=2,
                       ygap=2,
                       showscale=False,
                       colorscale=[[0.0, self.gridcolor], [1.0, self.gridcolor]],
                       hoverinfo="skip"), )

        self.fig.add_trace(
            go.Scatter(name='item-trace',
                       showlegend=False,
                       mode='text',
                       textfont_size=20,
                       textposition="middle center",
                       textfont_color="rgba(0,0,0,0.7)",
                       hovertemplate="%{customdata[0]}<br>Num: %{customdata[1]}<extra></extra>",
                       selected_textfont_color='rgba(0,0,0,0.5)',
                       unselected_textfont_color='rgba(0,0,0,0.5)'), )

        self.fig.add_trace(
            go.Scatter(name='player-trace',
                       showlegend=False,
                       mode='text',
                       textfont_size=18,
                       textposition="middle center",
                       hovertemplate="""%{customdata[0]}<br>Id: %{customdata[1]}<extra></extra>"""))

        self.fig.update_layout(
            clickmode='event+select',
            dragmode='lasso',
            modebar_remove=['pan', 'zoom', 'zoomin', 'zoomout', 'resetscale', 'autoscale'],
            autosize=False,
            width=800,
            height=800,
            margin=dict(l=5, r=5, b=5, t=5, pad=0),
            paper_bgcolor="#fdfcce",
            plot_bgcolor="#373c38",
            hoverlabel=dict(bgcolor="black", font_size=16, font_family="Rockwell"),
        )
        self.fig.update_xaxes(visible=False)
        self.fig.update_yaxes(visible=False)

    def update(self, map: Dict[PosType, Tile], dict_flow: Dict[Tuple[IdType, IdType], OfferType],
               players: List[Player]):
        self.update_item_trace(map)
        self.update_player_trace(map)
        self.update_trade_trace(dict_flow, players)

    def update_item_trace(self, map: Dict[PosType, Tile]):
        poses = []
        item_emoji = []
        customdata = []
        for pos, tile in map.items():
            if tile.item is not None:
                poses.append(list(pos))
                item_emoji.append(self.item_to_emoji[tile.item.name])
                customdata.append([
                    tile.item.name,
                    tile.item.num,
                ])
        self.fig.update_traces(x=[pos[0] for pos in poses],
                               y=[pos[1] - 0.1 for pos in poses],
                               text=item_emoji,
                               customdata=customdata,
                               selector=dict(type="scatter", name="item-trace"))

    def update_player_trace(self, map: Dict[PosType, Tile]):
        poses = []
        player_emoji = []
        customdata = []
        for pos, tile in map.items():
            if tile.player is not None:
                poses.append(list(pos))
                player_emoji.append(self.player_to_emoji[tile.player.persona])
                customdata.append([
                    tile.player.persona,
                    tile.player.id,
                ])

        self.fig.update_traces(x=[pos[0] for pos in poses],
                               y=[pos[1] + 0.1 for pos in poses],
                               text=player_emoji,
                               customdata=customdata,
                               selector=dict(type="scatter", name="player-trace"))

    def update_trade_trace(self, dict_flow: Dict[Tuple[IdType, IdType], OfferType], players: List[Player]):
        self.fig.data = self.fig.data[0:3]
        visited = []
        for (id_foo, id_bar), offer_foo in dict_flow.items():
            if (id_foo, id_bar) in visited:
                continue
            x = [players[id_foo].pos[0], players[id_bar].pos[0]]
            y = [players[id_foo].pos[1], players[id_bar].pos[1]]
            item_foo, num_foo = offer_foo
            item_bar, num_bar = dict_flow[(id_bar, id_foo)]
            visited.append((id_foo, id_bar))
            visited.append((id_bar, id_foo))
            if x[0] == x[1]:
                line_width = self.trade_line_width
                x_left = [_x + line_width / 2 for _x in x]
                x_right = [_x - line_width / 2 for _x in x]
                xs = x_left + x_right[::-1]
                ys = y + y[::-1]
            else:
                line_width = self.trade_line_width / math.cos(math.atan((y[0] - y[1]) / (x[0] - x[1])))
                y_upper = [_y + line_width / 2 for _y in y]
                y_lower = [_y - line_width / 2 for _y in y]

                xs = x + x[::-1]
                ys = y_upper + y_lower[::-1]

            self.fig.add_trace(
                go.Scatter(
                    x=xs,
                    y=ys,
                    fill='toself',
                    fillcolor='rgba(255,255,255,0.5)',
                    line_color='rgba(255,255,255,0)',
                    hoveron='fills',
                    showlegend=False,
                    name=
                    f"""【player {id_foo}】 {item_bar} +{num_bar}, {item_foo} -{num_foo} <br>【player {id_bar}】 {item_foo} +{num_foo}, {item_bar} -{num_bar} """,
                ))
