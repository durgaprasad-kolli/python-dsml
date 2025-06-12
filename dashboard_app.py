# Import necessary libraries
import streamlit as st
import pandas as pd
import plotly.express as px
import io

# --- 1. Data Loading and Preparation ---

# For demonstration, we'll create a dummy CSV content as a string.
# In a real application, you would load data from a file (st.file_uploader),
# a database (sqlite3, SQLAlchemy), or an API (requests).
@st.cache_data # Cache the data loading to improve performance on re-runs
def load_data():
    """
    Loads sample sales data for the dashboard.
    In a real application, this would fetch data from a database, API, or file.
    """
    data_csv = """
Date,Region,Category,Product,Sales,Units
2023-01-01,East,Electronics,Laptop,1200,1
2023-01-01,West,Clothing,T-Shirt,25,2
2023-01-02,East,Food,Milk,5,1
2023-01-02,Central,Electronics,Mouse,30,1
2023-01-03,West,Electronics,Keyboard,75,1
2023-01-03,East,Clothing,Jeans,60,1
2023-01-04,Central,Food,Bread,3,1
2023-01-04,East,Electronics,Monitor,300,1
2023-01-05,West,Food,Cheese,15,1
2023-01-05,Central,Clothing,Jacket,150,1
2023-01-06,East,Electronics,Laptop,1100,1
2023-01-06,West,Clothing,Socks,10,2
2023-01-07,Central,Food,Eggs,7,1
2023-01-07,East,Electronics,Webcam,40,1
2023-01-08,West,Electronics,Printer,200,1
2023-01-08,Central,Clothing,Dress,80,1
2023-01-09,East,Food,Yogurt,8,1
2023-01-09,West,Electronics,Headphones,90,1
2023-01-10,Central,Electronics,Speaker,60,1
2023-01-10,East,Clothing,Hat,20,1
"""
    # Use io.StringIO to treat the string as a file
    df = pd.read_csv(io.StringIO(data_csv))
    df['Date'] = pd.to_datetime(df['Date']) # Convert 'Date' column to datetime objects
    return df

df = load_data()

# --- 2. Streamlit App Layout and Widgets ---

# Set the page configuration (optional but good practice)
st.set_page_config(
    page_title="Dynamic Sales Dashboard",
    page_icon="📊",
    layout="wide" # Use wide layout for better visualization space
)

st.title("📊 Dynamic Sales Dashboard")

# Create a sidebar for filters
st.sidebar.header("Filter Data")

# Region filter
selected_regions = st.sidebar.multiselect(
    "Select Region(s)",
    options=df['Region'].unique(),
    default=df['Region'].unique() # Select all by default
)

# Category filter
selected_categories = st.sidebar.multiselect(
    "Select Category(s)",
    options=df['Category'].unique(),
    default=df['Category'].unique() # Select all by default
)

# Date range filter
min_date = df['Date'].min().date()
max_date = df['Date'].max().date()
date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Apply filters
if date_range: # Ensure date_range is not empty before unpacking
    start_date, end_date = date_range
    filtered_df = df[
        (df['Region'].isin(selected_regions)) &
        (df['Category'].isin(selected_categories)) &
        (df.Date.dt.date >= start_date) &
        (df.Date.dt.date <= end_date)
    ]
else:
    filtered_df = df # If no date range is selected, use the full dataframe


# Display a warning if the filtered DataFrame is empty
if filtered_df.empty:
    st.warning("No data available for the selected filters. Please adjust your selections.")
else:
    # --- 3. Display Raw Data ---
    st.subheader("Raw Data Preview")
    st.dataframe(filtered_df, use_container_width=True)

    # --- 4. Display Key Performance Indicators (KPIs) ---
    st.subheader("Key Performance Indicators")

    # Create columns for KPIs
    col1, col2, col3 = st.columns(3)

    with col1:
        total_sales = filtered_df['Sales'].sum()
        st.metric(label="Total Sales", value=f"${total_sales:,.2f}")

    with col2:
        avg_sales_per_unit = filtered_df['Sales'].sum() / filtered_df['Units'].sum()
        st.metric(label="Avg. Sales per Unit", value=f"${avg_sales_per_unit:,.2f}")

    with col3:
        total_units = filtered_df['Units'].sum()
        st.metric(label="Total Units Sold", value=f"{total_units:,}")

    # --- 5. Interactive Charts ---
    st.subheader("Interactive Sales Visualizations")

    # Create two columns for charts
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.write("### Sales by Category")
        # Aggregate data for bar chart
        sales_by_category = filtered_df.groupby('Category')['Sales'].sum().reset_index()
        fig_bar = px.bar(
            sales_by_category,
            x='Category',
            y='Sales',
            title='Total Sales by Product Category',
            labels={'Sales': 'Total Sales ($)', 'Category': 'Product Category'}
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with chart_col2:
        st.write("### Sales Distribution by Region")
        # Aggregate data for pie chart
        sales_by_region = filtered_df.groupby('Region')['Sales'].sum().reset_index()
        fig_pie = px.pie(
            sales_by_region,
            values='Sales',
            names='Region',
            title='Percentage of Sales by Region',
            hole=0.3 # Creates a donut chart
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    st.write("### Sales Trend Over Time")
    # Aggregate data for line chart (daily sales)
    sales_trend = filtered_df.groupby('Date')['Sales'].sum().reset_index()
    fig_line = px.line(
        sales_trend,
        x='Date',
        y='Sales',
        title='Daily Sales Trend',
        labels={'Sales': 'Total Sales ($)', 'Date': 'Date'},
        markers=True # Show markers on the line
    )
    st.plotly_chart(fig_line, use_container_width=True)

    st.write("### Product Sales Breakdown")
    # You can allow the user to select the X and Y axis for a more flexible chart
    x_axis_options = filtered_df.columns.tolist()
    # Filter out 'Date' and 'Sales' as primary Y-axis typically
    x_axis_options = [col for col in x_axis_options if col not in ['Sales', 'Date', 'Units']] 
    
    selected_x_axis = st.selectbox(
        "Select dimension for bar chart:",
        options=x_axis_options,
        index=x_axis_options.index('Product') if 'Product' in x_axis_options else 0 # Default to Product
    )

    if selected_x_axis:
        sales_by_dimension = filtered_df.groupby(selected_x_axis)['Sales'].sum().reset_index()
        fig_dynamic_bar = px.bar(
            sales_by_dimension,
            x=selected_x_axis,
            y='Sales',
            title=f'Total Sales by {selected_x_axis}',
            labels={'Sales': 'Total Sales ($)'}
        )
        st.plotly_chart(fig_dynamic_bar, use_container_width=True)