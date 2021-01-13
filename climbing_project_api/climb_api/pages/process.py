import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app

column1 = dbc.Col(
    [
       dcc.Markdown(
            """
        
            ## Process

            - Baseline predictions : mean absolute error 80 MegaWatts

                - Baseline predictions were determined to be the mean power output of each plant by type. Under this, the mean absolute error was around 80MW.

            - XGBoost regressor mean absolute error within 2 MegaWatts but it overfits

                - Initial predictions came from an XGBoosting regressor, under which the mean absolute error was less than 2 MW. This seemed promising, but the model may have overfit because several inputs like "number of generators" or "year" did not seem to change the predictions very much.

            - Ridge Regression provided a nice middleground. Mean absolute error: 20 MW 

                - I switched instead to a linear model, Ridge Regression. I was experimenting with Lasso regression as well but it tends to remove very low contributing factors entirely, making for a less interesting user experience. Under The final model, a mean absolute error of junst under 20 MW was achieved. Beating the baseline for sure, but not as accurate as I'd like.

            A big thank you for [Richmond Macaspac](https://github.com/macr) for helping with javascript specific "hacks" to make this work and generally providing great debugging support.
            """
        ),

    ],
)

layout = dbc.Row([column1])

