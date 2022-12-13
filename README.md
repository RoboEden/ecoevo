# Economy-Evolution

Economy Evolution Environment for Currency Emergence Research
## Install
Clone the repo, `cd` into the folder and run
```
pip install -e .
```
## Usage example
```python
from ecoevo import EcoEvo

env = EcoEvo()
obs, infos = env.reset()
done = False
while not done:
    actions = my_policy(obs, infos) # your policy goes here
    obs, reward, done, infos = env.step(actions)
```
You can change game setting such as `total_step` (the game durateion) and  `personae` (the num of players withhold each persona) in [`ecoevo.config`](ecoevo/config.py). 

Note that for now change `MapSize` is not effective.

## Items
First of all, here is a list of all avaliable `item_name`
| `item_name`  |               |
| ------------ | ------------- |
| '`gold`'     | '`pineapple`' |
| '`hazelnut`' | '`peanut`'    |
| '`coral`'    | '`stone`'     |
| '`sand`'     | '`pumpkin`'   |
See [item.yaml](ecoevo/entities/items.yaml) for a complete property of each item. 

## Input
The game core takes a list of actions of `ActionType` as input after reset. See [types.py](ecoevo/entities/types.py) for more details.

As show below ActionType has three parts: **main action**, **sell offer** and **buy offer**.

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
    | ---------- | -------------------------------- | ------------ |
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
The gamecore outputs


## Render
WIP