function capitalize(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}

function toOption(array) {
    let options = [];
    for (const item of Object.values(array)) {
        options.push({
            'label': capitalize(item),
            'value': item.toLowerCase(),
            'title': 'secondary action'
        });
    }
    return options;
}

window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside: {
        actionBinding: function (primaryAction) {
            if (primaryAction === "idle" || primaryAction === "collect") {
                return [[], undefined];
            }
            else if (primaryAction === "move") {
                let options = toOption(['up', 'down', 'left', 'right'])
                return [options, options[0].value];
            }
            else if (primaryAction === "consume") {
                let options = toOption([
                    'gold',
                    'hazelnut',
                    'coral',
                    'sand',
                    'pineapple',
                    'peanut',
                    'stone',
                    'pumpkin',
                ])
                return [options, options[0].value];
            }
        },
        selectedPlayerActions: function (json_selected_ids, json_ctrl_next_actions) {
            let buy_offer, main_action, primary_action, secondary_action, sell_offer;
            if (json_selected_ids === undefined) {
                throw window.dash_clientside.PreventUpdate;
            }
            let selected_ids = JSON.parse(json_selected_ids);
            let ctrl_next_actions = JSON.parse(json_ctrl_next_actions);
            let data_table = [];

            for (const id of Object.values(selected_ids)) {
                let _action = ctrl_next_actions[id];
                [main_action, sell_offer, buy_offer] = _action;
                [primary_action, secondary_action] = main_action;
                data_table.push({
                    "id": id,
                    "primary action": primary_action,
                    "secondary action": secondary_action,
                    "sell offer": sell_offer,
                    "buy offer": buy_offer
                });
            }
            return data_table;
        },
        updateSelectedIds: function (selectedData) {
            if (selectedData === undefined || !('points' in selectedData)) {
                throw window.dash_clientside.PreventUpdate;
            }
            const player_list = ['gold_digger',
                'hazelnut_farmer',
                'coral_collector',
                'sand_picker',
                'pineapple_farmer',
                'peanut_farmer',
                'stone_picker',
                'pumpkin_farmer',];
            let selected_ids = [];
            for (const points of Object.values(selectedData.points)) {
                if (player_list.includes(points['customdata'][0])) {
                    selected_ids.push(points['customdata'][1]);
                }
            }
            return JSON.stringify(selected_ids);
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
            if (triggered_id === 'clear-button-state') {
                return [json_raw_next_actions, JSON.stringify({})]
            }
            else {
                const raw_next_actions = JSON.parse(json_raw_next_actions);
                let written_actions = (json_written_actions !== undefined) ? JSON.parse(json_written_actions) : {};
                if (triggered_id === 'write-button-state' && json_selected_ids !== undefined) {
                    const selected_ids = JSON.parse(json_selected_ids);
                    for (const id of Object.values(selected_ids)) {
                        written_actions[id] = [[primary_action,
                            secondary_action], undefined, undefined]
                    }
                }
                let ctrl_next_actions = Object.assign(raw_next_actions, written_actions);
                return [JSON.stringify(ctrl_next_actions), JSON.stringify(written_actions)]
            }
        }
    }
});