from sqlalchemy import create_engine
import pandas as pd
import plotly.express as px  # (version 4.7.0 or higher)
import plotly.graph_objects as go
from dash import dash_table, Dash, dcc, html, Input, Output  # pip install dash (version 2.0.0 or higher)
from datetime import datetime

app = Dash(__name__)

# -- Import and clean data (importing csv into pandas)

def load_data():
    # Connection setup   
    # Database URL  
    DATABASE_URL = "postgresql://postgresql_finance_user:Xda6CRIftQmupM1vnXit1fnbKIfcfLhc@dpg-cp1p0hud3nmc73b8v0qg-a.ohio-postgres.render.com:5432/postgresql_finance"
    #creating an SQLAlchemy engine
    engine = create_engine(DATABASE_URL)
    
    #load transactions
    transactions_query = "SELECT * FROM Transactions;"
    transactions_df = pd.read_sql(transactions_query, engine, parse_dates=['date'])

    #load monthly budgets
    monthly_budgets_query = "SELECT * FROM MonthlyBudgets;"
    monthly_budgets_df = pd.read_sql(monthly_budgets_query, engine)

    #load categorical budgets
    categorical_budgets_query = "SELECT * FROM CategoricalBudgets;"
    categorical_budgets_df = pd.read_sql(categorical_budgets_query, engine)

    engine.dispose()  # Close the connection safely

    return transactions_df, monthly_budgets_df, categorical_budgets_df

# Using the function
transactions_df, monthly_budgets_df, categorical_budgets_df = load_data()
print(transactions_df[:5])
print(monthly_budgets_df[:5])
print(categorical_budgets_df[:5])

# ------------------------------------------------------------------------------
# App layout

app.layout = html.Div([
    html.Link(
        href='https://fonts.googleapis.com/css2?family=Lexend:wght@100..900&display=swap',
        rel='stylesheet'
    ),
    html.Div([
        html.H1("MyFINANCE DASHBOARD", className = 'header'),
        html.Div([
            html.H4("Select Year and Month: "),
            dcc.Dropdown(
                id="slct_year",
                options=[
                    {'label': str(year), 'value': year} for year in range(2000, datetime.now().year + 1)
                ],
                multi=False,
                value=datetime.now().year-1,  # Default to current year
            className='dropdownYear'),
            
            dcc.Dropdown(id="slct_month",
                options=[
                {"label": "January", "value": 1},
                {"label": "Febuary", "value": 2},
                {"label": "March", "value": 3},
                {"label": "April", "value": 4},
                {"label": "May", "value": 5},
                {"label": "June", "value": 6},
                {"label": "July", "value": 7},
                {"label": "August", "value": 8},
                {"label": "September", "value": 9},
                {"label": "October", "value": 10},
                {"label": "November", "value": 11},
                {"label": "December", "value": 12}],    
                multi=False,
                value=1,
                className='dropdownMonth'),
        ], className='selectYearandMonth'),
        
        html.Div([
            html.Button('INPUT SPENDINGS', id='input_spendings'),
            html.Button('VIEW DASHBOARD', id='view_dashboard')
        ], className= 'button'),

        html.Div([
            html.Div([
                html.Div([
                    # html.H3("Financial Overview", className = 'dataTitle'),
                    html.H3("Net Balance", className='dataTitle'),
                    html.Div([
                        html.P(id='net-balance-output'),
                    ], className='outputBox'),
                    html.H3("Status", className='dataTitle'),
                    html.Div([
                        html.P(id='status-output'),
                    ], className='outputBox')
                ], className= 'financial-overview'),

                html.Div([
                    html.H3("Expense Cateogrization", className='dataTitle'),
                    dcc.Graph(id='expense_categorization_graph', figure={}),
                ], className= 'expense-categorization')
            ], className= 'section3'),

            html.Div([
                html.Div([
                    html.Div([
                        html.H3("Daily Spending Trend", className='dataTitle'),
                        dcc.Graph(id='daily_spending_trend_graph', figure={}),
                    ], className= 'daily-spending-trend'),

                    html.Div([
                        html.H3("Budget vs. Actual Spending Per Category", className='dataTitle'),
                        dcc.Graph(id='budget_vs_actual_spending_graph', figure={}),
                    ], className= 'budget-vs-actual-spending'),

                ], className= 'section4'),
                html.Div([
                    html.H3("Recent Transactions", className = 'dataTitle'),
                    dash_table.DataTable(
                        id='transactions_table',
                        columns=[{"name": i, "id": i} for i in transactions_df.columns],
                        data=transactions_df.to_dict('records'),
                        style_table={
                            'height': '300px',
                            'overflowY': 'auto'
                        },
                        style_cell={
                            'textAlign': 'left',
                            'color': 'white',
                            'backgroundColor': '#151a28',
                            'border': 'none'
                        },
                        style_header={
                            'backgroundColor': '#222222',
                            'fontWeight': 'bold'
                        }
                    )
                ], className= 'section5'), 
            ], className= 'dataContainer2')

        ], className= 'dataContainer') #it contains all the data
    ], className= 'dashboard')
], className= 'background')


# ------------------------------------------------------------------------------
# Connect the Plotly graphs with Dash Components
@app.callback(
    [
        Output('net-balance-output', 'children'), 
        Output('status-output', 'children'),
        Output('expense_categorization_graph', 'figure'), 
        Output('daily_spending_trend_graph', 'figure'),
        Output('budget_vs_actual_spending_graph', 'figure')
    ],
    [
        Input('slct_year', 'value'),
        Input('slct_month', 'value')
    ]
)

def update_graph(selected_year, selected_month):

    # Filter the DataFrame to the selected month
    filtered_df = transactions_df[(transactions_df['date'].dt.year == selected_year) &
                                  (transactions_df['date'].dt.month == selected_month)]

    total_spent = filtered_df['amount'].sum()

    monthly_budgets_df['budgetmonth'] = pd.to_datetime(monthly_budgets_df['budgetmonth'])

    monthly_budget = monthly_budgets_df[
        (monthly_budgets_df['budgetmonth'].dt.year == selected_year) &
        (monthly_budgets_df['budgetmonth'].dt.month == selected_month)
    ]['totalbudget'].iloc[0]

    net_balance = monthly_budget - total_spent
    net_balance_output = format_net_balance(net_balance)
    net_balance_output = html.Span(net_balance_output, className='netBalanceOutput')
    
    status_text, color = determine_status(monthly_budget, total_spent, selected_year, selected_month)
    status_output = html.Span(status_text, style={'color': color}, className='statusOutput')

    expense_categorization_fig = update_expense_categorization_graph(filtered_df)
    daily_spending_trend_fig = update_daily_spending_trend_graph(filtered_df, monthly_budgets_df, selected_year, selected_month)
    budget_vs_actual_spending_fig = update_budget_vs_actual_spending_graph(filtered_df, categorical_budgets_df)

    return net_balance_output, status_output, expense_categorization_fig, daily_spending_trend_fig, budget_vs_actual_spending_fig


def calculated_daily_budget(monthly_budget, year, month):
    days_in_month = pd.Period(f'{year}-{month}').days_in_month
    return monthly_budget/days_in_month



def format_net_balance(net_balance, ):
    print("Net Balance:", net_balance)  # Debugging statement
    if net_balance < 0:
        formatted_balance = f"({-net_balance})"
    else:
        formatted_balance = str(net_balance)
    print("Formatted Balance:", formatted_balance)  # Debugging statement
    return formatted_balance


def determine_status(monthly_budget, total_spent, selected_year, selected_month):
    
    status_colors = {
        "PERFECT": "green",
        "GOOD": "blue",
        "OKAY": "yellow",
        "POOR": "orange",
        "HORRIBLE": "red"
    }

    daily_budget = calculated_daily_budget(monthly_budget, selected_year, selected_month)
    today = pd.Timestamp.today()
    if selected_year == today.year and selected_month == today.month:
        days_so_far = today.day
    else:
        days_so_far = pd.Period(f'{selected_year}-{selected_month}').days_in_month

    average_daily_spending = total_spent / days_so_far
    spent_percentage = (average_daily_spending/daily_budget) * 100

    status_key = "HORRIBLE"  # Default to the worst case
    if spent_percentage < 60:
        status_key = "PERFECT"
    elif 60 <= spent_percentage < 80:
        status_key = "GOOD"
    elif 80 <= spent_percentage < 90:
        status_key = "OKAY"
    elif 90 <= spent_percentage < 100:
        status_key = "POOR"

    return status_key, status_colors[status_key]


def update_expense_categorization_graph(filtered_df):
    fig = px.pie(
        filtered_df, 
        values='amount', 
        names='categoryname', 
        color='categoryname',
        hole=0.3
    )

    fig.update_traces(
        # textinfo='percent',  # Show both percentage and label
        insidetextorientation='radial',  # Better orientation for text inside
        textfont=dict(
            color='#eeeee4',
            size=13
        )
    )

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=0, b=0),
        height=300,
        legend=dict(
            font=dict(
                color="#eeeee4",
                size=10
            )
        )
    )

    return fig

def update_daily_spending_trend_graph(filtered_df, monthly_budgets_df, selected_year, selected_month):
    
    # Ensure 'budgetmonth' is a datetime object
    monthly_budgets_df['budgetmonth'] = pd.to_datetime(monthly_budgets_df['budgetmonth'])

    # Extract the monthly budget for the selected year and month
    monthly_budget = monthly_budgets_df[
        (monthly_budgets_df['budgetmonth'].dt.year == selected_year) &
        (monthly_budgets_df['budgetmonth'].dt.month == selected_month)
    ]['totalbudget'].iloc[0]  # Get the first item

    # Sum daily spending and calculate cumulative total
    daily_spending = filtered_df.groupby(filtered_df['date'].dt.day)['amount'].sum().cumsum().reset_index()
    daily_spending.columns = ['Day', 'Cumulative Spending']

    # Prepare a DataFrame for plotting the constant budget line
    max_day = daily_spending['Day'].max()
    budget_line = pd.DataFrame({
        'Day': [1, max_day],
        'Total Budget': [monthly_budget, monthly_budget]
    })

    # Add a column to classify spending relative to budget
    daily_spending['Status'] = daily_spending['Cumulative Spending'].apply(
        lambda x: 'Under' if x <= monthly_budget else 'Over'
    )

    fig = px.line(
        daily_spending,
        x='Day',
        y='Cumulative Spending',
        labels={
            'Cumulative Spending': 'cumulative spending ($)',
            'Day': 'day of the month'
        },
        color='Status',
        color_discrete_map={'Under': 'green', 'Over': 'red'},
        markers=True,
        # color_discrete_sequence=["#92154f"],  # Blue for Budget, Red for Actual Spending
    )

    fig.update_traces(
        line=dict(width=3)
    )  # Set the line width to 4 pixels


    #add budget line to function
     # Add budget line to the same figure
    fig.add_scatter(x=budget_line['Day'], y=budget_line['Total Budget'], mode='lines', name='Total Budget', line=dict(color='red', dash='dash'))

    # Customize the plot
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),  # Left, Right, Top, Bottom margins in pixels

        xaxis_tickangle=0,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(
            tickmode='array',
            tickvals=list(range(1, max_day + 1, 1)),  # Tick every day
            tickfont=dict(
                size=9,
                color="#eeeee4"
            ),
            title_font=dict(
                color="#eeeee4"),
            showgrid=False
        ),
        yaxis=dict(
            title_font=dict(color="#eeeee4"),
            tickfont=dict(color="#eeeee4"),
            showgrid=True,
            gridcolor='lightblue'
        ),
        legend=dict(
            title='',
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='center',
            x=0.5,
            font=dict(
                color="#eeeee4",
                size=12
            )
        )
    )

    return fig

def update_budget_vs_actual_spending_graph(filtered_df, categorical_budgets_df):
    
    # Merge actual spending data with budgets data
    actual_spending = filtered_df.groupby('categoryname')['amount'].sum().reset_index()
    budget_data = categorical_budgets_df[['categoryname', 'categorybudget']].groupby('categoryname').sum().reset_index() 
    
    # Merging the actual spending with the budgets
    summary_df = pd.merge(budget_data, actual_spending, on='categoryname', how='left')
    summary_df.fillna(0, inplace=True)  # Replace NaN with 0 for categories with no spending

    summary_df.rename(columns={'categorybudget': 'Budget', 'amount': 'Spent'}, inplace=True)

    # Create the bar chart for Budget vs Actual Spending
    fig = px.bar(
        summary_df, 
        x='categoryname', 
        y=['Budget', 'Spent'],
        labels={
            'categoryname': 'category types',
            'value': 'amount ($)', #represented with 2 different y-values, so is labeled as 'value'
            'variable': '' #represented with 2 different y-values, so is labeled as 'value'
        },
        barmode='group',
        color_discrete_sequence=["#92154f", "#f19500"]  # Blue for Budget, Red for Actual Spending

    )
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        # showlegend=False,
        xaxis_tickangle=45,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',

        legend = dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            font=dict(
                color="#eeeee4",
                size=12
            )
        ),
        xaxis=dict(
            title_font=dict(color="#eeeee4"),  # Color for the X-axis title
            tickfont=dict(
                color="#eeeee4",
                size=10
                ),  # Color for the X-axis ticks
            showgrid=True,  # Determines whether or not grid lines are drawn
            gridcolor='rgba(0,0,0,0)'  # Color of grid lines
        ),
        yaxis=dict(
            title_font=dict(color="#eeeee4"),  # Color for the Y-axis title
            tickfont=dict(color="#eeeee4"),  # Color for the Y-axis ticks
            showgrid=True,  # Determines whether or not grid lines are drawn
            gridcolor='lightblue'  # Color of grid lines
        )
    )
                 
    return fig

# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True)