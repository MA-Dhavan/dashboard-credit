import duckdb
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio


path = './german_credit_data/german.data'
df = duckdb.query(f"""
    SELECT *
    FROM read_csv_auto('{path}', delim=' ', header=False)
""").to_df()

cols = [
    "checking_status","duration","credit_history","purpose","credit_amount",
    "savings","employment","installment_rate","personal_status","other_debtors",
    "residence_since","property","age","other_installment","housing",
    "existing_credits","job","dependents","telephone","foreign_worker",
    "target"
]
df.columns = cols
df['target'] = df['target'].map({1:'Good', 2:'Bad'})
df['age_group'] = pd.cut(df['age'], bins=[19,30,40,50,60,70],
                         labels=['20-30','31-40','41-50','51-60','61-70'])

duckdb.register('loans', df)


def get_bad_rate(group_col):
    return duckdb.query(f"""
        SELECT {group_col},
               COUNT(*) AS total,
               SUM(CASE WHEN target='Bad' THEN 1 ELSE 0 END) AS bad_loans,
               ROUND(100.0*SUM(CASE WHEN target='Bad' THEN 1 ELSE 0 END)/COUNT(*),2) AS bad_rate
        FROM loans
        GROUP BY {group_col}
        ORDER BY bad_rate DESC
    """).to_df()

res_checking = get_bad_rate('checking_status')
res_credit_hist = get_bad_rate('credit_history')
res_purpose = get_bad_rate('purpose')
res_age = get_bad_rate('age_group')



fig = make_subplots(rows=2, cols=2,
                    subplot_titles=("Default Rate by Checking Status",
                                    "Default Rate by Credit History",
                                    "Default Rate by Loan Purpose",
                                    "Default Rate by Age Group"))

# Chart 1: checking_status

checking_status_map = {
    'A11': 'Balance < 0',
    'A12': '0 <= Balance < 200',
    'A13': 'Balance >= 200',
    'A14': 'No Checking Account'
}

df['checking_status'] = df['checking_status'].map(checking_status_map)

res_checking['checking_status'] = res_checking['checking_status'].map(checking_status_map)
fig.add_trace(go.Bar(x=res_checking['checking_status'],
                     y=res_checking['bad_rate'],
                     text=res_checking['bad_rate'],
                     texttemplate='%{text:.1f}%',
                     name='Checking Status'),
              row=1, col=1)

# Chart 2: credit_history

credit_history_map = {
    'A30': 'No credits taken',
    'A31': 'All credits at this bank paid back duly',
    'A32': 'Existing credits paid back duly till now',
    'A33': 'Delay in paying off in past',
    'A34': 'Critical account'
}
df['credit_history'] = df['credit_history'].map(credit_history_map)

res_credit_hist['credit_history'] = res_credit_hist['credit_history'].map(credit_history_map)
fig.add_trace(go.Bar(x=res_credit_hist['credit_history'],
                     y=res_credit_hist['bad_rate'],
                     text=res_credit_hist['bad_rate'],
                     texttemplate='%{text:.1f}%',
                     name='Credit History'),
              row=1, col=2)

# Chart 3: purpose

purpose_map = {
    'A40': 'Car (new)',
    'A41': 'Car (used)',
    'A42': 'Furniture/equipment',
    'A43': 'Radio/TV',
    'A44': 'Domestic appliances',
    'A45': 'Repairs',
    'A46': 'Education',
    'A48': 'Vacation',
    'A49': 'Retraining',
    'A410': 'Business'
}
df['purpose'] = df['purpose'].map(purpose_map)

res_purpose['purpose'] = res_purpose['purpose'].map(purpose_map)
fig.add_trace(go.Bar(x=res_purpose['purpose'],
                     y=res_purpose['bad_rate'],
                     text=res_purpose['bad_rate'],
                     texttemplate='%{text:.1f}%',
                     name='Purpose'),
              row=2, col=1)

# Chart 4: age_group
fig.add_trace(go.Bar(x=res_age['age_group'],
                     y=res_age['bad_rate'],
                     text=res_age['bad_rate'],
                     texttemplate='%{text:.1f}%',
                     name='Age Group'),
              row=2, col=2)

fig.update_layout(height=800, width=1200, title_text="Credit Performance Dashboard")
fig.show()


pio.write_html(fig, file='dashboard.html', auto_open=False, include_plotlyjs='cdn')
print("Dashboard saved as dashboard.html")

