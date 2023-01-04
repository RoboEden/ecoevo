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
        }
    }
});