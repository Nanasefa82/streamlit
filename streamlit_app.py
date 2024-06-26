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


st.write("### (2) Multiselect for Sub-Categories based on Selected Category")

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

# Group Order Date by Year
unique_years = grouped_sales['Year'].unique()
plt.xticks(unique_years, [str(year) for year in unique_years])

plt.tight_layout()  # Adjust layout to make room for the rotated x-axis labels

# Show the plot in Streamlit
st.pyplot(plt)

st.write("### (4) Metrics for Sales, Profit and Overall Profit Margin ")

# Initialize session_state variables if they do not exist
if 'total_sales' not in st.session_state:
    st.session_state.total_sales = 0
if 'total_profit' not in st.session_state:
    st.session_state.total_profit = 0
if 'overall_profit_margin' not in st.session_state:
    st.session_state.overall_profit_margin = 0

if not selected_sub_categories:
    st.write("Please select at least one sub-category to display detailed metrics.")
else:
    # Metrics calculations for the selected sub-categories
    st.session_state.total_sales = filtered_df['Sales'].sum()
    st.session_state.total_profit = filtered_df['Profit'].sum()
    
    if st.session_state.total_sales > 0:  # To avoid division by zero
        st.session_state.overall_profit_margin = (st.session_state.total_profit / st.session_state.total_sales) * 100
    else:
        st.session_state.overall_profit_margin = 0

# Displaying metrics
col1, col2, col3 = st.columns(3)
col1.metric("Total Sales", f"${st.session_state.total_sales:,.2f}")
col2.metric("Total Profit", f"${st.session_state.total_profit:,.2f}")
col3.metric("Overall Profit Margin (%)", f"{st.session_state.overall_profit_margin:,.2f}%")

st.write("### (5) Calculating overall average profit margin for comparison using delta option (all products across all categories)")

# Calculate the overall average profit margin
total_sales_overall = df['Sales'].sum()
total_profit_overall = df['Profit'].sum()
if total_sales_overall > 0:
    overall_average_profit_margin = (total_profit_overall / total_sales_overall) * 100
else:
    overall_average_profit_margin = 0

# Calculate the delta for the profit margin
profit_margin_delta = st.session_state.overall_profit_margin - overall_average_profit_margin

# Display the overall average profit margin for comparison (all products across all categories)
st.metric("Overall Average Profit Margin Compared to All Categories (%)", 
          f"{overall_average_profit_margin:,.2f}%", 
          delta=f"{profit_margin_delta:,.2f}%")