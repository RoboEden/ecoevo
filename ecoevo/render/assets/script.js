function capitalize(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}

function toOption(array) {
    var options = [];
    for (var i = 0; i < array.length; i++) {
        options.push({
            'label': capitalize(array[i]),
            'value': array[i].toLowerCase(),
            'title': 'secondary action'
        });
    }
    return options;
}

window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside: {
        actionBinding: function (primaryAction) {
            if (primaryAction === "idle" || primaryAction === "collect") {
                let options = toOption(['none'])
                return [options, options[0].value];
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
        selectedPlayerActions: function (jsonified_selected_ids, jsonified_ctrl_next_actions) {
            var buy_offer, main_action, primary_action, secondary_action, sell_offer;

            if (jsonified_selected_ids === undefined || jsonified_ctrl_next_actions === undefined) {
                return [];
            }
            console.log(jsonified_selected_ids)

            var selected_ids = JSON.parse(jsonified_selected_ids);
            var ctrl_next_actions = JSON.parse(jsonified_ctrl_next_actions);
            var data_table = [];

            for (var i = 0; i < selected_ids.length; i += 1) {
                var id = selected_ids[i];
                var _action = ctrl_next_actions[id];
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
        }
    }
});