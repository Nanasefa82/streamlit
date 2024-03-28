import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import math
import plotly.express as px
import seaborn as sns 

st.title("Data App Assignment")

st.write("### Input Data and Examples")
df = pd.read_csv("Superstore_Sales_utf8.csv", parse_dates=True)
st.dataframe(df)

# This bar chart will not have solid bars--but lines--because the detail data is being graphed independently
st.bar_chart(df, x="Category", y="Sales")

# Now let's do the same graph where we do the aggregation first in Pandas... (this results in a chart with solid bars)
st.dataframe(df.groupby("Category").sum())
# Using as_index=False here preserves the Category as a column.  If we exclude that, Category would become the datafram index and we would need to use x=None to tell bar_chart to use the index
st.bar_chart(df.groupby("Category", as_index=False).sum(), x="Category", y="Sales", color="#04f")

# Aggregating by time
# Here we ensure Order_Date is in datetime format, then set is as an index to our dataframe
df["Order_Date"] = pd.to_datetime(df["Order_Date"])
df.set_index('Order_Date', inplace=True)
# Here the Grouper is using our newly set index to group by Month ('M')
sales_by_month = df.filter(items=['Sales']).groupby(pd.Grouper(freq='M')).sum()

st.dataframe(sales_by_month)

# Here the grouped months are the index and automatically used for the x axis
st.line_chart(sales_by_month, y="Sales")


st.write("### (1) Dropdown for Categories")

unique_categories = df['Category'].unique()
unique_categories = sorted(unique_categories)
Category = st.selectbox('Select a Category', unique_categories)

st.write("### (2) Multiselect for Sub-Categories based on Selected Cateogry")


filtered_df = df[df['Category'] == Category].reset_index()  # Resetting index to use 'Order_Date' in plotting
unique_sub_categories = sorted(filtered_df['Sub_Category'].unique())
selected_sub_categories = st.multiselect('Select a Sub Category:', options=unique_sub_categories)

st.write("### (3) Line Chart of Aggregated Sales for Sub-Categories Across Years")


if not selected_sub_categories:
    st.write("Please select at least one sub-category to display the sales chart.")
else:
    filtered_df = filtered_df[filtered_df['Sub_Category'].isin(selected_sub_categories)]

# Ensure Order_Date is in datetime format
filtered_df['Order_Date'] = pd.to_datetime(filtered_df['Order_Date'])

# Create a 'Year' column for grouping
filtered_df['Year'] = filtered_df['Order_Date'].dt.year

# Group by 'Year' and 'Sub_Category', then sum the Sales
grouped_sales = filtered_df.groupby(['Year', 'Sub_Category'])['Sales'].sum().reset_index()

plt.figure(figsize=(10, 6))
plot = sns.lineplot(data=grouped_sales, x='Year', y='Sales', hue='Sub_Category', marker='o')
plt.title('Sales Over Time by Year for Selected Sub-Categories')
plt.xlabel('Year')
plt.ylabel('Total Sales')

# Setting x-tick labels: Directly use the unique 'Year' values from your DataFrame
# This assumes 'Year' in your DataFrame is already in the correct integer format
unique_years = grouped_sales['Year'].unique()
plt.xticks(unique_years, [str(year) for year in unique_years], rotation=45)

plt.tight_layout()  # Adjust layout to make room for the rotated x-axis labels

# Show the plot in Streamlit
st.pyplot(plt)

st.write("### (4) Metrics for Sales, Profit and Overall Profit Margin ")

if not selected_sub_categories:
    st.write("Please select at least one sub-category to display metrics.")
else:
    # Metrics calculations for the selected sub-categories
    total_sales = filtered_df['Sales'].sum()
    total_profit = filtered_df['Profit'].sum()
    if total_sales > 0:  # To avoid division by zero
        overall_profit_margin = (total_profit / total_sales) * 100
    else:
        overall_profit_margin = 0

   
    # Displaying metrics
        
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Sales", f"${total_sales:,.2f}")
    col2.metric("Total Profit", f"${total_profit:,.2f}")
    col3.metric("Overall Profit Margin (%)", f"${total_profit:,.2f}")

st.write("### (5) use the delta option Calculating overall average profit margin for comparison (all products across all categories)")

total_sales = filtered_df['Sales'].sum()
total_profit = filtered_df['Profit'].sum()
overall_profit_margin = (total_profit / total_sales) * 100
overall_total_sales = df['Sales'].sum()
overall_total_profit = df['Profit'].sum()
if overall_total_sales > 0:
        overall_average_profit_margin = (overall_total_profit / overall_total_sales) * 100
else:
        overall_average_profit_margin = 0


profit_margin_delta = overall_profit_margin - overall_average_profit_margin
st.metric("Overall Profit Margin (%)", f"{overall_profit_margin:.2f}%", delta=f"{profit_margin_delta:.2f}%")