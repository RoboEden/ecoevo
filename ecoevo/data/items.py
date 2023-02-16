from ecoevo.config import EnvConfig, MapConfig

LIST_ITEM = ['gold', 'hazelnut', 'coral', 'sand', 'pineapple', 'peanut', 'stone', 'pumpkin']

# basic properties
ALL_ITEM_DATA = {
    'gold': {
        'disposable': False,
        'divisible': True,
        'luxury': True
    },
    'hazelnut': {
        'disposable': True,
        'divisible': True,
        'luxury': True
    },
    'coral': {
        'disposable': False,
        'divisible': False,
        'luxury': True
    },
    'sand': {
        'disposable': False,
        'divisible': True,
        'luxury': False
    },
    'pineapple': {
        'disposable': True,
        'divisible': False,
        'luxury': True
    },
    'peanut': {
        'disposable': True,
        'divisible': True,
        'luxury': False
    },
    'stone': {
        'disposable': False,
        'divisible': False,
        'luxury': False
    },
    'pumpkin': {
        'disposable': True,
        'divisible': False,
        'luxury': False
    },
}

# config
num_player = EnvConfig.num_person_type * len(LIST_ITEM)
num_block_resource = MapConfig.generate_num_block_resource

# params
capacity_large = 100
refresh_time_default = 20
big_m = 1e6
magnify_abundant = 10
collect_time_default = 1
avr_luxury_large = 1
margin_reserve = 0.25
reserve_luxury_large = round(num_player / num_block_resource * (1 + margin_reserve))

# other properties
for name, item in ALL_ITEM_DATA.items():
    # id
    item['id'] = LIST_ITEM.index(name) + 1

    # health supply
    item['supply'] = 0 if not item['disposable'] else 1 if item['divisible'] else capacity_large

    # refresh time
    item['refresh_time'] = refresh_time_default if item['disposable'] else round(big_m)

    # collect time
    item['collect_time'] = collect_time_default

    # capacity
    item['capacity'] = 1 if item['divisible'] else capacity_large

    # reserve amount
    reserve_num = reserve_luxury_large
    if not item['luxury']:
        reserve_num *= magnify_abundant
    if item['divisible']:
        reserve_num *= capacity_large
    item['reserve_num'] = reserve_num

    # harvest amount
    item['harvest_num'] = item['reserve_num'] if item['luxury'] else round(item['reserve_num'] / magnify_abundant)

    # consume amount
    item['consume_num'] = 0 if not item['disposable'] else 1 if not item['divisible'] else capacity_large

    # expiration time
    item['expiry'] = 0  # reserved property

if __name__ == '__main__':
    import rich
    rich.print(ALL_ITEM_DATA)
