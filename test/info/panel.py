import os, json, rich
from typing import Dict, List

from ecoevo.entities.items import ALL_ITEM_DATA
from ecoevo.entities.player import ALL_PERSONAE

ITEM=list(ALL_ITEM_DATA.keys())
PERSONAE=list(ALL_PERSONAE.keys())

def panels_dict() -> Dict[str, List[str]]:
    return {
        title: [
            '{}_{}_price-cur'.format(title, item) if item != title else 0
            for item in ITEM 
        ]
        for title in ITEM
    }

# def panels_dict() -> Dict[str, List[str]]:
#     return {
#         title: [
#             '{}_collect_match_ratio-cur'.format(persona)
#             for persona in PERSONAE
#         ]
#         for title in ['Persona collect match ratio']
#     }
    
def metric_int(id, num):
    return {
        "field": str(num),
        "id": id,
        "meta": {},
        "settings": {
            "script": str(num)
        },
        "type": "bucket_script",
        "pipelineVariables": []
    }

def metric_field(id, field):
    return {
        "field": field,
        "id": id,
        "meta": {},
        "settings": {},
        "type": "avg",
    }

def gen_panel(title, fields):
    with open(os.path.join(os.path.dirname(__file__), 'template.json')) as f:
        data = json.load(f)
    data['title'] = title
    for i, field in enumerate(fields):
        id = i + 1
        if isinstance(field, int):
            metric = metric_int(id, field)
        else:
            metric = metric_field(id, field)
        data['targets'][0]['metrics'].append(metric)
    return json.dumps(data)

def gen_panels(title_fields_dict: Dict[str, List[str]]):
    l = []
    for title, fields in title_fields_dict.items():
        l.append(gen_panel(title, fields))
    return '\n'.join(l)

if __name__ == '__main__':
    with open(os.path.join(os.path.dirname(__file__), 'panel.json'), 'w') as f:
        f.write(gen_panels(panels_dict()))
