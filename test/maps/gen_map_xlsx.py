import openpyxl, pathlib
import numpy as np
import json

W, H = 32, 32
INPUT_XLSX = pathlib.Path(__file__).parents[0].joinpath('map.xlsx')
OUTPUT_JSON = pathlib.Path(__file__).parents[2].joinpath('ecoevo/data/xlsx.json')

def load_data(file) -> np.ndarray:
    wb = openpyxl.load_workbook(file)
    ws = wb.worksheets[0]

    data = -np.ones((W, H), dtype=int)

    for j, row in enumerate(ws.values):
        for i, cell in enumerate(row):
            if i < W and j < H and isinstance(cell, str):
                data[i, H-1-j] = 'ABCDEFGH'.index(cell)
    return data

def print_data(data: np.ndarray):
    ch = ["🪙 ", "🌰", "🪸 ", "🏖️ ", "🍍", "🥜", "🪨 ", "🎃", "⬛"]
    s = ""
    for j in reversed(range(H)):
        for i in range(W):
            icon = ch[data[i, j]]
            s += icon
        s += '\n'
    print(s)
  
def data_to_json(data: np.ndarray) -> str:
    names = ["gold", "hazelnut", "coral", "sand", "pineapple", "peanut", "stone", "pumpkin", "empty"]
    tiles = []
    for i in range(W):
        row = []
        for j in range(H):
            row.append(names[data[i, j]])
        tiles.append(row)
    dic = dict(
      width=W,
      height=H,
      tiles=tiles,
    )
    return json.dumps(dic)
    

if __name__ == '__main__':
    data = load_data(INPUT_XLSX)
    print_data(data)
    jstr = data_to_json(data)
    with open(OUTPUT_JSON, 'w') as f:
        f.write(jstr)
    