import duckdb
import pandas as pd
import plotly.express as px
import plotly.io as pio

# Path to your file
path = './german_credit_data/german.data'


df = duckdb.query(f"""
    SELECT *
    FROM read_csv_auto('{path}', delim=' ', header=False)
""").to_df()

#print(df.head())

cols = [
    "checking_status","duration","credit_history","purpose","credit_amount",
    "savings","employment","installment_rate","personal_status","other_debtors",
    "residence_since","property","age","other_installment","housing",
    "existing_credits","job","dependents","telephone","foreign_worker",
    "target"
]
df.columns = cols
df['target'] = df['target'].map({1:'Good', 2:'Bad'})

print(df.head())
duckdb.register('loans', df)
res = duckdb.query("""
    SELECT checking_status,
           COUNT(*) AS total,
           SUM(CASE WHEN target='Bad' THEN 1 ELSE 0 END) AS bad_loans,
           ROUND(100.0*SUM(CASE WHEN target='Bad' THEN 1 ELSE 0 END)/COUNT(*),2) AS bad_rate
    FROM loans
    GROUP BY checking_status
    ORDER BY bad_rate DESC
""").to_df()
print(res)

fig = px.bar(res, x='checking_status', y='bad_rate',
             title='Default rate by checking account status',
             text='bad_rate')
fig.update_traces(texttemplate='%{text:.1f}%')
fig.show()

pio.write_html(fig, file='dashboard.html', auto_open=False,
               include_plotlyjs='cdn') 

