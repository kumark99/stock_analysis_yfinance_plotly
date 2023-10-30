import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go

# Initialize the Dash app
app = dash.Dash(__name__)

# Define external CSS for dark theme
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# Add external stylesheets to the app
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# Define the app layout
app.layout = html.Div([
    html.H1("Stock Data Analysis", style={'textAlign': 'center', 'color': 'black'}),
    
    # Input field for the stock symbol with debounce
    dcc.Input(id='stock-symbol', type='text', value='AAPL', debounce=True, style={'textAlign': 'center'}),
    
    # Button to trigger data retrieval
    html.Button('Fetch Data', id='fetch-button', style={'textAlign': 'center'}),

    # Historical candlestick chart
    dcc.Graph(id='candlestick-chart'),
    
    # Table to display results
    html.Table(id='results-table', children=[
        html.Tr([html.Th("Metric", style={'textAlign': 'center', 'color': 'black'}), html.Th("Value", style={'textAlign': 'center', 'color': 'black'})], style={'backgroundColor': 'rgb(35, 35, 35)'}),
    ], style={'textAlign': 'center', 'color': 'black'})
])

# Callback to update the table with stock data
@app.callback(
    [Output('results-table', 'children'), Output('candlestick-chart', 'figure')],
    Input('fetch-button', 'n_clicks'),
    Input('stock-symbol', 'n_submit'),  # Added input for Enter key press
    State('stock-symbol', 'value')  # Added state for input value
)
def update_table(n_clicks, n_submit, stock_symbol):
    if n_clicks is None and n_submit is None:
        return [html.Tr([html.Th("Metric", style={'textAlign': 'center', 'color': 'black'}), html.Th("Value", style={'textAlign': 'center', 'color': 'black'})], style={'backgroundColor': 'rgb(35, 35, 35)'})]

    try:
        # Create a Ticker object for the stock symbol
        stock = yf.Ticker(stock_symbol)

        # Fetch historical data for the past 1 year until the current date
        end_date = datetime.today().strftime('%Y-%m-%d')
        start_date = (datetime.today() - timedelta(days=365)).strftime('%Y-%m-%d')
        data = stock.history(period="1y", start=start_date, end=end_date)

        # Ensure date indices are in datetime format
        data.index = pd.to_datetime(data.index)

        # Calculate the returns for 1 week, 1 month, 3 months, 6 months, and 1 year
        current_date = data.index[-1]
        one_week_ago = current_date - timedelta(weeks=1)
        one_month_ago = current_date - timedelta(weeks=4)
        three_months_ago = current_date - timedelta(weeks=12)
        six_months_ago = current_date - timedelta(weeks=24)
        one_year_ago = current_date - timedelta(weeks=52)

        returns = {
            "1 Week": (data["Close"][current_date] / data["Close"][one_week_ago] - 1) * 100,
            "1 Month": (data["Close"][current_date] / data["Close"][one_month_ago] - 1) * 100,
            "3 Months": (data["Close"][current_date] / data["Close"][three_months_ago] - 1) * 100,
            "6 Months": (data["Close"][current_date] / data["Close"][six_months_ago] - 1) * 100,
            "1 Year": (data["Close"][current_date] / data["Close"][one_year_ago] - 1) * 100,
        }

        # Fetch stock's fundamentals data
        pe_ratio = stock.info["trailingPE"]
        beta_value = stock.info["beta"]

        # Convert high and low columns to numeric and find max and min
        high_52_weeks = pd.to_numeric(data["High"]).max()
        low_52_weeks = pd.to_numeric(data["Low"]).min()

        # Calculate how far the current price is from 52-week high and low
        current_price = data["Close"][current_date]
        percent_from_high = ((current_price - high_52_weeks) / high_52_weeks) * 100
        percent_from_low = ((current_price - low_52_weeks) / low_52_weeks) * 100

        # Create a table of results
        table_rows = [
            html.Tr([html.Td("1 Week Return", style={'color': 'black'}), 
                    html.Td("1 Month Return", style={'color': 'black'}),
                    html.Td("3 Months Return", style={'color': 'black'}),
                    html.Td("6 Months Return", style={'color': 'black'}),
                    html.Td("1 Year  Return", style={'color': 'black'}),
                    html.Td("52-Week High", style={'color': 'black'}),
                    html.Td("52-Week Low", style={'color': 'black'}),
                    html.Td("P/E Ratio", style={'color': 'black'}),
                    html.Td("Beta Value", style={'color': 'black'}),
                    html.Td("Percent(%) from High", style={'color': 'black'}),
                    html.Td("Percent(%) from Low", style={'color': 'black'})
                    ]),
                 html.Tr([html.Td(f"{returns['1 Week']:.2f}%", style={'color': 'white', 'backgroundColor': 'green' if returns['1 Week'] > 25 else ('orange' if returns['1 Week'] > 0 else 'red')}),
                    html.Td(f"{returns['1 Month']:.2f}%", style={'color': 'white', 'backgroundColor': 'green' if returns['1 Month'] > 25 else ('orange' if returns['1 Month'] > 0 else 'red')}),
                    html.Td(f"{returns['3 Months']:.2f}%", style={'color': 'white', 'backgroundColor': 'green' if returns['3 Months'] > 25 else ('orange' if returns['3 Months'] > 0 else 'red')}),
                    html.Td(f"{returns['6 Months']:.2f}%", style={'color': 'white', 'backgroundColor': 'green' if returns['6 Months'] > 25 else ('orange' if returns['6 Months'] > 0 else 'red')}),
                    html.Td(f"{returns['1 Year']:.2f}%", style={'color': 'white', 'backgroundColor': 'green' if returns['1 Year'] > 25 else ('orange' if returns['1 Year'] > 0 else 'red')}),
                    html.Td(f"{high_52_weeks:.2f}", style={'color': 'black'}),
                    html.Td(f"{low_52_weeks:.2f}", style={'color': 'black'}),
                    html.Td(f"{pe_ratio:.2f}", style={'color': 'black'}),
                    html.Td(f"{beta_value:.2f}", style={'color': 'black'}),
                    html.Td(f"{percent_from_high:.2f}", style={'color': 'white', 'backgroundColor': 'green' if percent_from_high > 25 else ('orange' if percent_from_high > 0 else 'red')}),
                    html.Td(f"{percent_from_low:.2f}", style={'color': 'white', 'backgroundColor': 'green' if percent_from_low > 25 else ('orange' if percent_from_low > 0 else 'red')})
                   ])

            ]
        
         # Create the candlestick chart
        candlestick_chart = go.Figure(data=[go.Candlestick(x=data.index,
                                                           open=data['Open'],
                                                           high=data['High'],
                                                           low=data['Low'],
                                                           close=data['Close'])])
        candlestick_chart.update_layout(title=f'{stock_symbol} Historical Candlestick Chart',
                                        xaxis_title='Date',
                                        yaxis_title='Price',
                                        xaxis_rangeslider_visible=True)

        return table_rows, candlestick_chart

        #return table_rows

    except Exception as e:
        return [html.Tr([html.Td("An error occurred", style={'color': 'black'}), html.Td(str(e), style={'color': 'black'})])]

if __name__ == '__main__':
    app.run_server(debug=True)
