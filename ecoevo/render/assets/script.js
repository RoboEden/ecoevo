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


window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside: {
        actionBinding: function (primaryAction, json_all_item_data) {
            const all_items = Object.keys(JSON.parse(json_all_item_data));
            if (primaryAction === "idle" || primaryAction === "collect") {
                return [[], undefined];
            }
            else if (primaryAction === "move") {
                let options = toOption(["up", "down", "left", "right"]);
                return [options, options[0].value];
            }
            else if (primaryAction === "consume") {
                let options = toOption(all_items);
                return [options, options[0].value];
            }
        },
        updateSelectedIds: function (selectedData, json_all_persona) {
            if (selectedData == undefined) {
                return JSON.stringify([]);
            }
            else if ("points" in selectedData) {
                const all_persona = Object.keys(JSON.parse(json_all_persona));
                let selected_ids = [];
                for (const points of Object.values(selectedData.points)) {
                    if (all_persona.includes(points["customdata"][0])) {
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
                    "sell offer": String(sell_offer),
                    "buy offer": String(buy_offer),
                });
            }
            return data_table;
        },
        displaySelectedPlayer: function (json_selected_ids, json_env_output_data, json_all_item_data, json_all_persona) {
            const selected_ids = JSON.parse(json_selected_ids);
            const ALL_ITEM_DATA = JSON.parse(json_all_item_data);
            const all_items = Object.keys(ALL_ITEM_DATA)
            const ALL_PERSONA_DATA = JSON.parse(json_all_persona);
            if (selected_ids.length === 0) {
                return window.dash_clientside.no_update;
            }
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
                const ctx = document.getElementById("radar-chart");
                let chart = Chart.getChart(ctx);
                if (chart === undefined) {
                    new Chart(ctx, {
                        type: 'radar',
                        data: {
                            labels: all_items,
                            datasets: [{
                                label: 'Preference',
                                data: new Array(all_items.length).fill(0),
                                fill: true,
                                backgroundColor: 'rgba(255, 99, 132, 0.2)',
                                borderColor: 'rgb(255, 99, 132)',
                                pointBackgroundColor: 'rgb(255, 99, 132)',
                                pointBorderColor: '#fff',
                                pointHoverBackgroundColor: '#fff',
                                pointHoverBorderColor: 'rgb(255, 99, 132)',
                                order: 1
                            }, {
                                label: 'Ability',
                                data: new Array(all_items.length).fill(0),
                                fill: true,
                                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                                borderColor: 'rgb(54, 162, 235)',
                                pointBackgroundColor: 'rgb(54, 162, 235)',
                                pointBorderColor: '#fff',
                                pointHoverBackgroundColor: '#fff',
                                pointHoverBorderColor: 'rgb(54, 162, 235)',
                                order: 2
                            }]
                        },
                        options: {
                            elements: {
                                line: {
                                    borderWidth: 3
                                }
                            }
                        },
                    });
                }
                else {
                    chart.data.labels = Object.keys(ALL_PERSONA_DATA[player.persona].preference);
                    chart.data.datasets[0].data = Object.values(ALL_PERSONA_DATA[player.persona].preference);
                    chart.data.datasets[1].data = Object.values(ALL_PERSONA_DATA[player.persona].ability);
                    chart.update()
                }
                document.getElementById("reward-provider").innerText = env_output_data.rewards[id];
                document.getElementById("info-provider").innerText = env_output_data.info[id];

                return env_output_data.rewards[id];
            }
        },
        controlActions: function (
            write_n_clicks, //Input
            clear_n_clicks,//Input
            json_raw_next_actions,//Input
            json_selected_ids,//State
            json_written_actions,//State
            primary_action,//State
            secondary_action,//State
            sell_item,//State
            sell_num,//State
            buy_item,//State
            buy_num,//State
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
                    let sell_offer = sell_item !== 'None' ? [sell_item, -sell_num] : undefined;
                    let buy_offer = buy_item !== 'None' ? [buy_item, buy_num] : undefined;
                    for (const id of selected_ids) {
                        written_actions[id] = [[primary_action,
                            secondary_action], sell_offer, buy_offer];
                    }
                }
                let ctrl_next_actions = Object.assign(raw_next_actions, written_actions);
                return [JSON.stringify(ctrl_next_actions), JSON.stringify(written_actions)];
            }
        },
    }
});