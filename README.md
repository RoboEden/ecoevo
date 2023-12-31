# Economy-Evolution

Economy Evolution Environment for Currency Emergence Research
## Change log
See [CHANGES.md](./CHANGES.md) for details.

## Development
Make sure `pip` is the latest version.
```
pip install --upgrade setuptools
pip install --upgrade build
pip install -e .
```
## Custom Webapp
Install nodejs
```bash
curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash - &&\
sudo apt-get install -y nodejs
```
Install dependencies
```bash
npm install
```
Start dev 
```bash
npm run dev
```
Build 
```bash
npm run build
```

## Packaging
1. Data files should be included via the  `MANIFEST.in` file.
2. Build package.
```
python -m build
```

## Install
```
pip install dist/ecoevo-0.1.0-py3-none-any.whl
```
## Usage example
```python
from ecoevo import EcoEvo

env = EcoEvo(render_mode=False)
obs, info = env.reset()
done = False
while not done:
    actions = your_policy(obs, info)
    obs, rewards, done, info = env.step(actions)
```
You can change game setting such as `total_step` (the game durateion) and  `personae` (the num of players withhold each persona) in [`config.py`](ecoevo/config.py).

Note that for now change `MapConfig` is not effective.

## Render

To render, set `render_mode` to `True`. Default is `False`

Run the same code above and open the web app from your browser on `http://127.0.0.1:8050/`

>**_Under render mode:_**
>- Method `reset` is blocked till the web app is open in the browser.
>- Method `step` is blocked till step button is clicked.

## Items
First of all, here is a list of all avaliable `item_name`
| `item_name`   |
| :------------ |
| '`gold`'      |
| '`hazelnut`'  |
| '`coral`'     |
| '`sand`'      |
| '`pineapple`' |
| '`peanut`'    |
| '`stone`'     |
| '`pumpkin`'   |

See [item.yaml](ecoevo/entities/items.yaml) for a complete property of each item.

## Input
The game core takes a list of actions of `ActionType` as input after reset. See [types.py](ecoevo/entities/types.py) for more details.

As show below ActionType has three parts: **main action**, **sell offer** and **buy offer**.

Every step one player can execute ***only one*** **main action** and a pair of **sell offer** & **buy offer**.

The action for a single player is shown below
```python
ActionType = Tuple[MainActionType, OfferType, OfferType]
```
Note that "sell offer" stands *before* "buy offer" in the ternary tuple, following a comercial philosophy "You give before you get." by Napoleon Hill.
- **main action**

    It consists of a *primary action* and a *secondary action*. Its type `MainActionType` is defined as `Tuple[str, Optional[str]]`.   See the table below for valid strings in each condition.

    | primary action | secondary action                            |
    | -------------- | ------------------------------------------- |
    | `'move'`       | `'idle'`/`'up'`/`'down'`/`'right'`/`'left'` |
    | '`consume`'    | One of the string in `item_name`            |
    | '`collect`'    | `None`                                      |

- **sell offer** & **buy offer**

    | offer type | item                             | num          |
    | :--------- | :------------------------------- | :----------- |
    | sell offer | One of the string in `item_name` | negative int |
    | buy offer  | One of the string in `item_name` | positive int |

    If any one of the offer is `None`, the game core will skip both offers of this agent.

### Input Examples
```python
    actions = [
        (('consume', 'peanut'), ('gold', -5),('peanut', 20)),
        (('move', 'right'), None, None),
        (('move', 'up'), ('sand', -5), ('gold', 10)),
        ...
        (('move', 'left'), ('gold', -10), ('sand', 5)),
        (('consume', 'coral'), None, None),
        (('collect', None), None, None),
    ]
```

## Output
The gamecore outputs `obs`, `rewards`, `done`, `info` when step. See details below.

- `obs`: `Dict[IdType, Dict[PosType, Tile]]`

  Its key is a player's id and value is the local vision of this player. Vision radius is 7 and can be changed in [`config.py`](ecoevo/config.py).

  The local vision is also a dict with `(x, y)` coordinates as its key and   `Tile` object as its value.

  A tile contains either an item or a player, or both, at its position.

  If neither an item nor a player exists at this position, then it cannot be found in the local vision.

- `rewards`: `Dict[IdType, float]`

  Contains rewards for each players. See [reward.py](/ecoevo/reward.py) for implementation details.
- `done`: `bool`

  Returns to `True` if the current game is over.
- `info`: `Dict[IdType, dict]`

  Returns info of each player.
### Output Examples
- `obs`
    ```Python
    {
        0: {
            (0, 0): Tile(
                item=None,
                player=<ecoevo.entities.player.Player object at 0x7fa1dca04f50>
            ),
            ...
            (12, 7): Tile(item=Item(name='peanut', num=10000), player=None)
        },
        1: {
            (0, 1): Tile(
                item=None,
                player=<ecoevo.entities.player.Player object at 0x7fa1dca19c90>
            ),
            ...
            (9, 5): Tile(item=Item(name='coral', num=10000), player=None)
        },
        ...
    }
    ```
- `rewards`
    ```python
    {
        0: 0.0,
        1: 0.0,
        2: 0.0,
        3: 0.0,
        ...
        126: 0.0,
        127: 0.0
    }
    ```
- `done`
    ```python
    False
    ```
- `info`
    ```python
    {
        0: {
            'persona': 'gold_digger',
            'preference': {'gold': 1.0, 'hazelnut': 1.0, 'coral': 1.0, 'sand': 1.0, 'pineapple': 1.0, 'peanut': 1.0, 'stone': 1.0, 'pumpkin': 1.0},
            'ability': {'gold': 3.0, 'hazelnut': 9.0, 'coral': 9.0, 'sand': 3.0, 'pineapple': 9.0, 'peanut': 3.0, 'stone': 3.0, 'pumpkin': 3.0},
            'backpack': {
                'gold': Item(name='gold', num=0),
                'hazelnut': Item(name='hazelnut', num=0),
                'coral': Item(name='coral', num=0),
                'sand': Item(name='sand', num=0),
                'pineapple': Item(name='pineapple', num=0),
                'peanut': Item(name='peanut', num=0),
                'stone': Item(name='stone', num=0),
                'pumpkin': Item(name='pumpkin', num=0)
            },
            'stomach': {
                'gold': Item(name='gold', num=0),
                'hazelnut': Item(name='hazelnut', num=0),
                'coral': Item(name='coral', num=0),
                'sand': Item(name='sand', num=0),
                'pineapple': Item(name='pineapple', num=0),
                'peanut': Item(name='peanut', num=0),
                'stone': Item(name='stone', num=0),
                'pumpkin': Item(name='pumpkin', num=0)
            },
            'pos': (14, 29),
            'id': 0,
            'health': 100,
            'collect_remain': None,
            'last_action': None,
            'trade_result': 'Illegal'
        },
        ...
    }
    ```

## FAQ
- Can agent execute more than 1 action per step?
- Max visual distance?
- Max trade distance?
- What's the maximum bag volume?
- Where is the player itself in its local vision
- Why the local vision do not use absolute coordinate?
- What is collect remain?
- Where to see the trade result?
- How to get all item & player info from an EcoEvo object?
