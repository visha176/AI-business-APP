import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from io import BytesIO
import requests  # for calling Flask API

# 🔗 Flask+ngrok base URL from Streamlit secrets
API_URL = st.secrets.get("api_url")  # e.g. "https://abcd-xyz.ngrok-free.app"


def load_data_from_db(
    Volume_filter=None,
    product_type_filter=None,
    season_filter=None,
    Years_filter=None
):
    if "user_id" not in st.session_state:
        st.error("User ID not found. Please log in.")
        return pd.DataFrame()

    try:
        resp = requests.post(
            f"{API_URL}/store_data",
            json={
                "user_id": st.session_state["user_id"],
                "Volume": Volume_filter,
                "product_type": product_type_filter,
                "Season": season_filter,
                "Years": Years_filter,
            },
            timeout=30,
        )
        resp.raise_for_status()
        result = resp.json()

        if not result.get("success"):
            st.error(f"API error: {result.get('error', 'Unknown error')}")
            return pd.DataFrame()

        data = result.get("data", [])
        df = pd.DataFrame(data)

        # 🔹 Normalize column names
        df.columns = df.columns.str.strip()
        df.columns = df.columns.str.replace(" ", "_")

        # 🔹 Standardize 'first_rcv_date' naming if DB returns different spelling/case
        for col in df.columns:
            if col.lower() == "first_rcv_date":
                if col != "first_rcv_date":
                    df = df.rename(columns={col: "first_rcv_date"})
                break

        # 🔹 Convert key columns to correct numeric types
        numeric_cols = ["Sold_Qty", "Shop_Rcv_Qty", "Disp_Qty", "OH_Qty"]
        for c in numeric_cols:
            if c in df.columns:
                df[c] = pd.to_numeric(df[c], errors="coerce")

        # 🔹 Convert date column to datetime
        if "first_rcv_date" in df.columns:
            df["first_rcv_date"] = pd.to_datetime(df["first_rcv_date"], errors="coerce")

        return df

    except Exception as e:
        st.error(f"API Error while loading data: {e}")
        return pd.DataFrame()



def get_unique_values(column_name: str):
    """
    Call Flask /unique_values endpoint to get filter values.
    """
    if "user_id" not in st.session_state:
        st.error("User ID not found.")
        return ["All"]

    try:
        resp = requests.post(
            f"{API_URL}/unique_values",
            json={
                "user_id": st.session_state["user_id"],
                "column": column_name,
            },
            timeout=30,
        )
        resp.raise_for_status()
        result = resp.json()

        if not result.get("success"):
            st.error(f"API error (unique_values): {result.get('error', 'Unknown error')}")
            return ["All"]

        values = result.get("values", [])
        return ["All"] + values

    except Exception as e:
        st.error(f"API Error while loading values for {column_name}: {e}")
        return ["All"]




def create_sample_file():
    """Return an in-memory Excel sample file."""
    sample_data = {
        "DESIGN": ["Design1", "Design2"],
        "STORE_NAME": ["Store1", "Store2"],
        "first_rcv_date": [datetime(2023, 1, 1), datetime(2023, 2, 1)],
        "UPC_Barcode_SKU": [1223456, 345678],
        "Shop_Rcv_Qty": [100, 150],
        "Disp_Qty": [10, 20],
        "OH_Qty": [90, 130],
        "Sold_Qty": [50, 80],
        "Color": ["Red", "Blue"],
        "Size": ["Small", "Medium"],
        "Volume": ["Casual", "Fancy"],
        "product_type": ["Lawn", "Chiffon"],
    }
    df = pd.DataFrame(sample_data)

    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Sample Data")
    return output.getvalue()

   
def adjust_date(df, threshold_date):
    if 'first_rcv_date' in df.columns:
        df['first_rcv_date'] = pd.to_datetime(df['first_rcv_date'], errors='coerce')
    else:
        st.error("'first_rcv_date' column is missing.")
        return df

    threshold_timestamp = pd.Timestamp(threshold_date)
    df['Adjusted_first_Rcv_Date'] = df['first_rcv_date'].apply(
        lambda date: threshold_timestamp if pd.notnull(date) and date <= threshold_timestamp else date
    )
    
    return df

def aggregate_data(df, threshold_date):
    df = adjust_date(df, threshold_date)
    required_columns = ['UPC_Barcode_SKU', 'STORE_NAME', 'DESIGN', 'Adjusted_first_Rcv_Date', 'Volume', 'product_type', 'Size', 'Color']
    for col in required_columns:
        if col not in df.columns:
            st.error(f"Error: '{col}' column is missing in the data.")
            return df

    return df.groupby(required_columns).agg({
        'Shop_Rcv_Qty': 'sum',
        'Disp_Qty': 'sum',
        'OH_Qty': 'sum',
        'Sold_Qty': 'sum'
    }).reset_index()

def calculate_sell_through(df):
    if 'Shop_Rcv_Qty' not in df.columns or 'Disp_Qty' not in df.columns or 'Sold_Qty' not in df.columns:
        st.error("Error: Required columns for calculating sell-through are missing.")
        return df
    sell_through = (df['Sold_Qty'] / (df['Shop_Rcv_Qty'] - df['Disp_Qty']) * 100).replace([np.inf, -np.inf, np.nan], 0)
    df['shop Sell Through'] = sell_through.astype(int)
    
    return df

def calculate_days(df):
    if 'Adjusted_first_Rcv_Date' not in df.columns:
        st.error("Error: 'Adjusted_first_Rcv_Date' column is missing.")
        return df

    current_date = datetime.now()
    df['Shop Days'] = (current_date - df['Adjusted_first_Rcv_Date']).dt.days
    
    return df


def calculate_design_sell_through(df):
    if 'UPC_Barcode_SKU' not in df.columns:
        st.error("Error: 'UPC_Barcode_SKU' column is missing.")
        return df

    df['Net Receiving'] = df['Shop_Rcv_Qty'] - df['Disp_Qty']
    design_totals = df.groupby('UPC_Barcode_SKU').agg({'Sold_Qty': 'sum', 'Net Receiving': 'sum'}).reset_index()
    design_totals['design Sell Through'] = (design_totals['Sold_Qty'] / design_totals['Net Receiving'] * 100).replace([np.inf, -np.inf, np.nan], 0).astype(int)

    
    return design_totals

def merge_data(desired_df, design_totals):
    if 'UPC_Barcode_SKU' not in desired_df.columns or 'UPC_Barcode_SKU' not in design_totals.columns:
        st.error("Error: 'UPC_Barcode_SKU' column is missing in one of the DataFrames.")
        return desired_df

    if 'design Sell Through' not in design_totals.columns:
        st.error("Error: 'design Sell Through' column is missing in design_totals.")
        return desired_df

    merged_df = pd.merge(desired_df, design_totals[['UPC_Barcode_SKU', 'design Sell Through']], on='UPC_Barcode_SKU', how='left')
    
    return merged_df

def apply_status_condition(df):
    if 'shop Sell Through' not in df.columns or 'design Sell Through' not in df.columns:
        st.error("Error: 'shop Sell Through' or 'design Sell Through' column is missing.")
        return df

    df['Status'] = 'Low'
    df.loc[df['shop Sell Through'] >= df['design Sell Through'], 'Status'] = 'High'
    
    return df

def process_data(desired_df):#replacw with upc
    article_days = desired_df.groupby('UPC_Barcode_SKU')['Shop Days'].max().reset_index()
    merged_df = pd.merge(desired_df, article_days, on='UPC_Barcode_SKU', how='left', suffixes=('', '_max_days'))
    merged_df_grouped = merged_df.groupby('UPC_Barcode_SKU').agg({
        'OH_Qty': 'sum',
        'Sold_Qty': 'sum',
        'Shop Days': 'max'
    }).reset_index()
    result_df = merged_df_grouped[['UPC_Barcode_SKU', 'Shop Days']].rename(columns={'Shop Days': 'Date Difference'})
    return result_df

def process_and_calculate_cover(df, article_days):#replace design with upc 
    merged_df = pd.merge(df, article_days, on='UPC_Barcode_SKU', how='left', suffixes=('', '_max_days'))
    merged_df_grouped = merged_df.groupby('UPC_Barcode_SKU').agg({
        'OH_Qty': 'sum',
        'Sold_Qty': 'sum',
        'Shop Days': 'max'
    }).reset_index()
    result_df = merged_df_grouped[['UPC_Barcode_SKU', 'Shop Days']].rename(columns={'Shop Days': 'Date Difference'})
    merged_df_grouped = pd.merge(merged_df_grouped, result_df, on='UPC_Barcode_SKU', how='left')
    merged_df_grouped['Targeted Cover'] = merged_df_grouped['OH_Qty'] / (merged_df_grouped['Sold_Qty'] / merged_df_grouped['Date Difference'])
    return merged_df_grouped

def merge_with_desired_cover(desired_df, merged_df_grouped):
    desired_df = pd.merge(desired_df, merged_df_grouped[['UPC_Barcode_SKU', 'Targeted Cover']], on='UPC_Barcode_SKU', how='left')
    desired_df['Targeted Cover'] = desired_df['Targeted Cover'].fillna(0).replace([np.inf, -np.inf], 0).astype(int)
    return desired_df

def calculate_article_days(df):
    # Ensure 'Adjusted_first_Rcv_Date' exists and use the correct name
    df['Adjusted_first_Rcv_Date'] = pd.to_datetime(df['Adjusted_first_Rcv_Date'], errors='coerce')
    df = df.dropna(subset=['Adjusted_first_Rcv_Date'])  # Corrected column name here
    today = pd.Timestamp.now().normalize()
    df['Max Design Days'] = (today - df['Adjusted_first_Rcv_Date']).dt.days
    article_days = df.groupby('UPC_Barcode_SKU')['Max Design Days'].max().reset_index()
    return article_days



def calculate_required_cover(desired_df): # desired cover * Sold_Qty / days = required on hand when we minus current o.h= transfer in/out
    desired_df['Transfer in/out'] = desired_df['Targeted Cover'] * (desired_df['Sold_Qty'] / desired_df['Shop Days']) - desired_df['OH_Qty']
    desired_df['Transfer in/out'] = desired_df['Transfer in/out'].replace([np.inf, -np.inf, np.nan], 0).astype(int)
    return desired_df

def merge_desired_with_article_days(desired_df, article_days):
    desired_df = pd.merge(desired_df, article_days, on='UPC_Barcode_SKU', how='left')
    return desired_df

def filter_data(desired_df, sell_through_threshold, days_threshold):
    filtered_df = desired_df[(desired_df['design Sell Through'] > sell_through_threshold) & (desired_df['Max Design Days'] > days_threshold)]
    return filtered_df

def process_transfer_details(filtered_df):
    sending_stores = filtered_df[filtered_df['Transfer in/out'] < 0]
    receiving_stores = filtered_df[filtered_df['Transfer in/out'] > 0]
    transfer_details = []

    for sending_index, sending_row in sending_stores.iterrows():
        matches = receiving_stores[
            (receiving_stores['UPC_Barcode_SKU'] == sending_row['UPC_Barcode_SKU']) &
            (receiving_stores['STORE_NAME'] != sending_row['STORE_NAME']) &
            (receiving_stores['Transfer in/out'] > 0)
        ]

        if matches.empty:
            continue

        total_qty_to_transfer = abs(sending_row['Transfer in/out'])

        for receiving_index, receiving_row in matches.iterrows():
            transfer_qty = min(total_qty_to_transfer, receiving_row['Transfer in/out'])
            sending_stores.at[sending_index, 'Transfer in/out'] += transfer_qty
            receiving_stores.at[receiving_index, 'Transfer in/out'] -= transfer_qty
            transfer_details.append({
                'UPC_Barcode_SKU': sending_row['UPC_Barcode_SKU'],
                'From Store': sending_row['STORE_NAME'],
                'To Store': receiving_row['STORE_NAME'],
                'DESIGN': sending_row['DESIGN'],
                'Size': sending_row['Size'],
                'Color': sending_row['Color'],
                'Volume': sending_row['Volume'],
                'product_type': sending_row['product_type'],
                'Size': sending_row['Size'],
                'Quantity Transferred': transfer_qty
            })
            total_qty_to_transfer -= transfer_qty
            if total_qty_to_transfer <= 0:
                break

    transfer_df = pd.DataFrame(transfer_details)
    return transfer_df


def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    processed_data = output.getvalue()
    return processed_data
# Function to get unique values for filters
def get_unique_values(column_name: str):
    if 'user_id' not in st.session_state:
        st.error("User ID not found.")
        return ["All"]

    try:
        response = requests.post(
            f"{API_URL}/unique_values",
            json={"user_id": st.session_state["user_id"], "column": column_name},
            timeout=30
        )
        result = response.json()
        values = result.get("values", [])
        return ["All"] + values

    except Exception as e:
        st.error(f"Error loading values: {e}")
        return ["All"]


def show_Network():      

    # 🌐 Page Navigation Dropdown
    st.markdown(
        """
        <style>
            .page-dropdown {
                width: 200px;
                margin-bottom: 20px;
                font-size: 16px;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    page_choice = st.selectbox(
        "🔀 Go to Page:",
        ("Network", "City", "Regional"),
        key="page_selector"
    )

    if page_choice == "City":
       st.session_state["selected_page"] = "City"
       st.rerun()
    elif page_choice == "Regional":
       st.session_state["selected_page"] = "Regional"
       st.rerun()

    st.markdown("""
        <style>
                .stApp {
            background-image: url("https://images.unsplash.com/photo-1557683316-973673baf926?ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&q=80&w=1129");
            background-size: cover;
            color:white;
        }
       .st-emotion-cache-5qfegl {
    display: inline-flex;
    -webkit-box-align: center;
    align-items: center;
    -webkit-box-pack: center;
    justify-content: center;
    font-weight: 400;
    padding: 0.25rem 0.75rem;
    border-radius: 0.5rem;
    min-height: 2.5rem;
    margin: 0px;
    line-height: 1.6;
    text-transform: none;
    font-size: inherit;
    font-family: inherit;
    color: inherit;
    width: 100%;
    cursor: pointer;
    user-select: none;
    background-color: rgb(3 3 3);
    border: 1px solid rgba(49, 51, 63, 0.2);
}
                .st-emotion-cache-144mis {
  
    display: none;
}
                h1 {
    font-family: "Source Sans Pro", sans-serif;
    font-weight: 700;
    color: rgb(244 245 253);
    padding: 1.25rem 0px 1rem;
    margin: 0px;
    line-height: 1.2;
}
.st-emotion-cache-3qzj0x p {
    word-break: break-word;
    margin: 0px;
    color: white;
}
                .st-emotion-cache-1whx7iy p {
    /* word-break: break-word; */
    margin-bottom: 0px;
    font-size: 14px;
    color: white;
}

                }

        
                
        </style>
    """, unsafe_allow_html=True)
    st.title('Network🌐')

    # Download sample file
    sample_file = create_sample_file()
    st.download_button(
        label="Download Sample Excel File",
        data=sample_file,
        file_name='sample_data.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    
    # Define the columns we want to create filters for
    filter_columns = ["Volume", "product_type", "Season"]
    filters = {}
    cols = st.columns(len(filter_columns) + 1)  # +2 for the date inputs
# MULTISELECT FILTERS
    # MULTISELECT FILTERS
    for i, column in enumerate(filter_columns):
        options = get_unique_values(column)
        selected_options = cols[i].multiselect(f"Select {column}", options=options, key=f"{column}_filter")
        filters[column] = selected_options if selected_options else None

# YEAR FILTER (outside loop)
    year_options = get_unique_values("Years")
    selected_years = cols[len(filter_columns)].multiselect("Select Year(s)", options=year_options, key="year_filter")



    # Input fields for data processing
    threshold_date = st.date_input("Season Launch Date", min_value=datetime(2020, 1, 1), value=datetime.now())
    sell_through_threshold = st.number_input("Enter Sell-Through Threshold (%)", min_value=0, max_value=100, value=60)
    days_threshold = st.number_input("Enter Minimum Age", min_value=0, max_value=100, value=30)

    # Button to initiate data processing
    if st.button("Process Data"):
        with st.spinner('Processing data, please wait...'):
            # Load data with applied filters
            data = load_data_from_db(
            Volume_filter=filters["Volume"],
            product_type_filter=filters["product_type"],
            season_filter=filters["Season"],
            Years_filter=selected_years
     )

            # Step-by-step data processing
            adjusted_data = adjust_date(data, threshold_date)
            if 'Adjusted_first_Rcv_Date' not in adjusted_data.columns:
                st.error("Error: 'Adjusted_first_Rcv_Date' column is missing after adjustment.")
                return

            aggregated_data = aggregate_data(adjusted_data, threshold_date)
            sell_through_data = calculate_sell_through(aggregated_data)
            days_data = calculate_days(sell_through_data)
            design_sell_through_data = calculate_design_sell_through(days_data)
            merged_data = merge_data(days_data, design_sell_through_data)
            status_data = apply_status_condition(merged_data)
            
            # Additional processing steps
            processed_data = process_data(status_data)
            cover_data = process_and_calculate_cover(status_data, processed_data)
            cover_merged_data = merge_with_desired_cover(status_data, cover_data)
            article_days = calculate_article_days(cover_merged_data)
            required_cover_data = calculate_required_cover(cover_merged_data)
            final_data = merge_desired_with_article_days(required_cover_data, article_days)
            filtered_data = filter_data(final_data, sell_through_threshold, days_threshold)
            transfer_details = process_transfer_details(filtered_data)

            # Store results in session state
            st.session_state.filtered_data = filtered_data
            st.session_state.transfer_details = transfer_details

            

    # Download buttons for processed data
    if 'filtered_data' in st.session_state and 'transfer_details' in st.session_state:
        processed_data_excel = to_excel(st.session_state.filtered_data)
        transfer_data_excel = to_excel(st.session_state.transfer_details)

        st.download_button(
            label="Download Processed Data",
            data=processed_data_excel,
            file_name="processed_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        st.download_button(
            label="Download Transfer Details",
            data=transfer_data_excel,
            file_name="transfer_details.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )










