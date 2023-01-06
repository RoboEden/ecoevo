function capitalize(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}

function toOption(array) {
    let options = [];
    for (const item of array) {
        options.push({
            "label": capitalize(item),
            "value": item.toLowerCase(),
            "title": "secondary action"
        });
    }
    return options;
}
var all_item_list = [
    "gold",
    "hazelnut",
    "coral",
    "sand",
    "pineapple",
    "peanut",
    "stone",
    "pumpkin",
];
var player_list = ["gold_digger",
    "hazelnut_farmer",
    "coral_collector",
    "sand_picker",
    "pineapple_farmer",
    "peanut_farmer",
    "stone_picker",
    "pumpkin_farmer",];

var all_item_data = {
    'gold':
    {
        'id': 1,
        'supply': 0,
        'refresh_time': 1000000,
        'collect_time': 9,
        'capacity': 1,
        'harvest_num': 100,
        'reserve_num': 5000,
        'consume_num': 0,
        'expiry': 0,
        'disposable': false,
    },
    'hazelnut':
    {
        'id': 2,
        'supply': 1,
        'refresh_time': 15,
        'collect_time': 9,
        'capacity': 1,
        'harvest_num': 100,
        'reserve_num': 100,
        'consume_num': 100,
        'expiry': 0,
        'disposable': true,
    },
    'coral':
    {
        'id': 3,
        'supply': 0,
        'refresh_time': 1000000,
        'collect_time': 9,
        'capacity': 100,
        'harvest_num': 1,
        'reserve_num': 50,
        'consume_num': 0,
        'expiry': 0,
        'disposable': false,
    },
    'sand':
    {
        'id': 4,
        'supply': 0,
        'refresh_time': 1000000,
        'collect_time': 3,
        'capacity': 1,
        'harvest_num': 100,
        'reserve_num': 15000,
        'consume_num': 0,
        'expiry': 0,
        'disposable': false,
    },
    'pineapple':
    {
        'id': 5,
        'supply': 100,
        'refresh_time': 15,
        'collect_time': 9,
        'capacity': 100,
        'harvest_num': 1,
        'reserve_num': 1,
        'consume_num': 1,
        'expiry': 0,
        'disposable': true,
    },
    'peanut':
    {
        'id': 6,
        'supply': 1,
        'refresh_time': 5,
        'collect_time': 3,
        'capacity': 1,
        'harvest_num': 100,
        'reserve_num': 100,
        'consume_num': 100,
        'expiry': 0,
        'disposable': true,
    },
    'stone':
    {
        'id': 7,
        'supply': 0,
        'refresh_time': 1000000,
        'collect_time': 3,
        'capacity': 100,
        'harvest_num': 1,
        'reserve_num': 150,
        'consume_num': 0,
        'expiry': 0,
        'disposable': false,
    },
    'pumpkin':
    {
        'id': 8,
        'supply': 100,
        'refresh_time': 5,
        'collect_time': 3,
        'capacity': 100,
        'harvest_num': 1,
        'reserve_num': 1,
        'consume_num': 1,
        'expiry': 0,
        'disposable': true,
    },
}

window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside: {
        actionBinding: function (primaryAction) {
            if (primaryAction === "idle" || primaryAction === "collect") {
                return [[], undefined];
            }
            else if (primaryAction === "move") {
                let options = toOption(["up", "down", "left", "right"]);
                return [options, options[0].value];
            }
            else if (primaryAction === "consume") {
                let options = toOption(all_item_list);
                return [options, options[0].value];
            }
        },
        updateSelectedIds: function (selectedData) {
            if (selectedData == undefined) {
                return JSON.stringify([]);
            }
            else if ("points" in selectedData) {
                let selected_ids = [];
                for (const points of Object.values(selectedData.points)) {
                    if (player_list.includes(points["customdata"][0])) {
                        selected_ids.push(points["customdata"][1]);
                    }
                }
                return JSON.stringify(selected_ids);
            }
            else { return window.dash_clientside.no_update; }
        },
        displaySelectedActions: function (json_selected_ids, json_ctrl_next_actions) {
            const selected_ids = JSON.parse(json_selected_ids);
            if (selected_ids.length === 0) {
                return window.dash_clientside.no_update;
            }
            let buy_offer, main_action, primary_action, secondary_action, sell_offer;
            let ctrl_next_actions = JSON.parse(json_ctrl_next_actions);
            let data_table = [];

            for (const id of selected_ids) {
                let _action = ctrl_next_actions[id];
                [main_action, sell_offer, buy_offer] = _action;
                [primary_action, secondary_action] = main_action;
                data_table.push({
                    "id": id,
                    "primary action": primary_action,
                    "secondary action": secondary_action,
                    "sell offer": sell_offer,
                    "buy offer": buy_offer,
                });
            }
            return data_table;
        },
        displaySelectedPlayer: function (json_selected_ids, json_env_output_data) {
            const selected_ids = JSON.parse(json_selected_ids);
            if (selected_ids.length === 0) {
                return window.dash_clientside.no_update;
            }
            const ctx = document.getElementById('myChart');
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: ['Red', 'Blue', 'Yellow', 'Green', 'Purple', 'Orange'],
                    datasets: [{
                        label: '# of Votes',
                        data: [12, 19, 3, 5, 2, 3],
                        borderWidth: 1
                    }]
                },
                options: {
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });


            const env_output_data = JSON.parse(json_env_output_data);
            const id = selected_ids[0];
            const json_player = env_output_data.players[id];
            if (json_player !== undefined) {
                const player = JSON.parse(json_player)
                document.getElementById("basic-player-persona").innerText = player.persona;
                document.getElementById("basic-player-id").innerText = player.id;
                document.getElementById("basic-player-pos").innerText = player.pos;
                document.getElementById("basic-player-health").innerText = player.health;
                document.getElementById("basic-player-collect-remain").innerText = String(player.collect_remain);
                document.getElementById("basic-player-trade-result").innerText = player.trade_result;
                document.getElementById("radar-provider").innerText = '';
                document.getElementById("obs-provider").innerText = '';
                document.getElementById("reward-provider").innerText = env_output_data.rewards[id];
                document.getElementById("info-provider").innerText = env_output_data.info[id];
                var output = [];
                for (const item_name of all_item_list) {
                    let num = player.backpack[item_name]['num'];
                    let capacity = all_item_data[item_name]['capacity'];
                    output.push(num * capacity);
                    output.push(num);
                    output.push(capacity);
                }
                for (const item_name of all_item_list) {
                    let num = player.stomach[item_name]['num'];
                    let capacity = all_item_data[item_name]['capacity'];
                    output.push(num * capacity);
                    output.push(num);
                    output.push(capacity);
                }
                return output;
            }
        },
        controlActions: function (
            write_n_clicks, //Input
            clear_n_clicks,//Input
            json_raw_next_actions,//Input
            json_selected_ids,//State
            primary_action,//State
            secondary_action,//State
            json_written_actions,//State
        ) {
            const triggered_id = window.dash_clientside.callback_context.triggered[0].prop_id.split(".")[0];
            if (triggered_id === "clear-button-state") {
                return [json_raw_next_actions, JSON.stringify({})];
            }
            else {
                const raw_next_actions = JSON.parse(json_raw_next_actions);
                let written_actions = (json_written_actions !== undefined) ? JSON.parse(json_written_actions) : {};
                if (triggered_id === "write-button-state") {
                    const selected_ids = JSON.parse(json_selected_ids);
                    for (const id of selected_ids) {
                        written_actions[id] = [[primary_action,
                            secondary_action], undefined, undefined];
                    }
                }
                let ctrl_next_actions = Object.assign(raw_next_actions, written_actions);
                return [JSON.stringify(ctrl_next_actions), JSON.stringify(written_actions)];
            }
        },
    }
});