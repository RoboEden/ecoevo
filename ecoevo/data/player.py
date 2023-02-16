from ecoevo.data.items import LIST_ITEM

LIST_PERSONAE = [
    'gold_digger', 'hazelnut_farmer', 'coral_collector', 'sand_picker', 'pineapple_farmer', 'peanut_farmer',
    'stone_picker', 'pumpkin_farmer'
]

ALL_PERSONAE = {
    personae: {
        'preference': {item: 1
                       for item in LIST_ITEM},
        'ability': {item: 1
                    for item in LIST_ITEM}
    }
    for personae in LIST_PERSONAE
}

if __name__ == '__main__':
    import rich
    rich.print(ALL_PERSONAE)
