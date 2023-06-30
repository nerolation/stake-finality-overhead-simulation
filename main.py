import dash
from dash import dcc, html  # Updated import statement
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import numpy as np

# Variables
total_eth_supply = 2**27
participation_rate_of_total_percent = 10  # 10%
messeges_per_valiator_for_finality = 2
target_traffic_per_sec = 5000


def get_number_of_validators(min_stake, participation):
    return int(
        total_eth_supply / min_stake * (participation_rate_of_total_percent / 100)
    )


def get_traffic_per_sec(
    nr_of_validators, finality_in_sec, messeges_per_valiator_for_finality
):
    return int(nr_of_validators * messeges_per_valiator_for_finality / finality_in_sec)


def get_required_finality_time(
    nr_of_validators,
    messeges_per_valiator_for_finality,
    messages_per_second=target_traffic_per_sec,
):
    return (
        int(nr_of_validators * messeges_per_valiator_for_finality) / messages_per_second
    )


def seconds_to_slots(s):
    return s // 12


min_stake_values = np.linspace(1, 100, 100)

nr_of_validators = [get_number_of_validators(i, 100) for i in min_stake_values]
finality_values = [
    seconds_to_slots(get_required_finality_time(i, 2)) for i in nr_of_validators
]

figure = go.Figure()
figure.add_trace(
    go.Scatter(
        x=min_stake_values,
        y=finality_values,
        mode="lines",
        name="Finality Time",
        hovertemplate="<b>Min Stake</b>: %{x:.2f} ETH<br>"
        + "<b>Finality Time</b>: %{y:.2f} slots<br>"
        + "<extra></extra>",
    )
)

figure.update_layout(
    title=f"Impact of Min Stake on Finality Time<br>(Overhead per Second = {target_traffic_per_sec} messages)",
    xaxis_title="Min Stake in ETH",
    yaxis_title="Finality Time in Slots",
    width=500,
    height=450,
    autosize=True,
    margin=dict(l=20, r=20, t=70, b=20),
    title_font=dict(size=16),  # Modify the font size here.
    title_x=0.5,
)


app = dash.Dash(__name__)

app.layout = html.Div(
    [
        html.Div(
            [
                dcc.Slider(
                    id="min-stake-slider",
                    min=1,
                    max=100,
                    value=32,
                    marks={
                        i: "Min Stake (ETH)".format(i) if i == 1 else str(i)
                        for i in range(1, 101, 20)
                    },
                    step=1,
                ),
                html.Div(
                    id="min-stake-output",
                    style={
                        "display": "flex",
                        "justifyContent": "center",
                        "alignItems": "center",
                        "width": "100%",
                        "height": "100%",
                        "paddingBottom": 20,
                    },
                ),  # label for slider
                dcc.Slider(
                    id="finality-in-sec-slider",
                    min=1,
                    max=1000,
                    value=12 * 32 * 2,
                    marks={
                        i: "Finality in Sec".format(i) if i == 1 else str(i)
                        for i in range(1, 1001, 200)
                    },
                    step=1,
                ),
                html.Div(
                    id="finality-in-sec-output",
                    style={
                        "display": "flex",
                        "justifyContent": "center",
                        "alignItems": "center",
                        "width": "100%",
                        "height": "100%",
                        "paddingBottom": 20,
                    },
                ),  # label for slider
                html.Div(
                    id="traffic-per-sec-output",
                    style={
                        "display": "flex",
                        "justifyContent": "center",
                        "alignItems": "center",
                        "width": "100%",
                        "height": "100%",
                        "paddingBottom": 20,
                    },
                ),  # label for traffic_per_sec
            ],
            style={"padding": 20},
        ),  # Adds padding around the sliders
        html.Div(
            [dcc.Graph(id="graph-output", figure=figure)],
            style={
                "display": "flex",
                "justifyContent": "center",
                "alignItems": "center",
                "width": "100%",
                "height": "100%",
            },
        ),
        html.Div(
            [
                html.P(
                    f"Participation Rate of ETH staked vs. Total ETH available (%): {participation_rate_of_total_percent}"
                )
            ],
            style={
                "display": "flex",
                "justifyContent": "center",
                "alignItems": "center",
                "width": "100%",
                "height": "100%",
            },
        ),  # Adds padding around the text
        html.Div(
            [
                html.P(
                    f"Messages (Traffic) Per Validator for Finality: {messeges_per_valiator_for_finality}"
                )
            ],
            style={
                "display": "flex",
                "justifyContent": "center",
                "alignItems": "center",
                "width": "100%",
                "height": "100%",
            },
        ),
    ]
)


@app.callback(
    [
        Output("min-stake-output", "children"),
        Output("finality-in-sec-output", "children"),
        Output("traffic-per-sec-output", "children"),
    ],
    [Input("min-stake-slider", "value"), Input("finality-in-sec-slider", "value")],
)
def update_output(min_stake, finality_in_sec):
    nr_of_validators = get_number_of_validators(min_stake, 100)
    traffic_per_sec = get_traffic_per_sec(nr_of_validators, finality_in_sec, 2)
    return (
        f"Min Stake: {min_stake}",
        f"Finality in Sec: {finality_in_sec}",
        f"Overhead per Second: {traffic_per_sec} messages",
    )


if __name__ == "__main__":
    app.run_server(debug=True)
