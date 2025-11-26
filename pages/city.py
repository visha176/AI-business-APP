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





# ================== SAMPLE FILE (UNCHANGED) ==================
def create_sample_file():
    # Creating a sample DataFrame with the required headers
    sample_data = {
        'DESIGN': ['Design1', 'Design2'],
        'STORE_NAME': ['Store1', 'Store2'],
        '1st Rcv Date': [datetime(2023, 1, 1), datetime(2023, 2, 1)],
        'UPC/Barcode/SKU': [1223456, 345678],
        'Shop Rcv Qty': [100, 150],
        'Disp. Qty': [10, 20],
        'O.H Qty': [90, 130],
        'Sold Qty': [50, 80],
        'Color': ['Red', 'Blue'],
        'Size': ['Small', 'Medium'],
        'Volume': ['Casual', 'Fancy'],
        'product_type': ['Lawn', 'Chiffon'],
        'City': ['Lahore', 'Multan']  # Changed Zone to City
    }
    sample_df = pd.DataFrame(sample_data)

    # Converting DataFrame to an Excel file in memory
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        sample_df.to_excel(writer, index=False, sheet_name='Sample Data')
    processed_data = output.getvalue()
    return processed_data




# ================== PROCESSING LOGIC (UNCHANGED) ==================
def adjust_date(df, threshold_date):
    def adjust_single_date(date):
        threshold_timestamp = pd.Timestamp(threshold_date)
        if date <= threshold_timestamp:
            return threshold_timestamp
        else:
            return date
    df['1st Rcv Date'] = pd.to_datetime(df['1st Rcv Date'])
    df['Adjusted 1st Rcv Date'] = df['1st Rcv Date'].apply(adjust_single_date)
    return df

def aggregate_data(df, threshold_date):
    df = adjust_date(df, threshold_date)
    return df.groupby(['City', 'UPC/Barcode/SKU', 'STORE_NAME', 'DESIGN',
                       'Adjusted 1st Rcv Date', 'Volume', 'product_type', 'Size', 'Color']).agg({
        'Shop Rcv Qty': 'sum',
        'Disp. Qty': 'sum',
        'O.H Qty': 'sum',
        'Sold Qty': 'sum'
    }).reset_index()

def calculate_sell_through(desired_df):
    sell_through = (desired_df['Sold Qty'] /
                    (desired_df['Shop Rcv Qty'] - desired_df['Disp. Qty']) * 100)
    sell_through = sell_through.replace([np.inf, -np.inf, np.nan], 0)
    desired_df['shop Sell Through'] = sell_through.astype(int)
    return desired_df

def calculate_days(df):
    current_date = datetime.now()
    df['Shop Days'] = (current_date - df['Adjusted 1st Rcv Date']).dt.days
    return df

def calculate_design_sell_through(df):
    df['Net Receiving'] = df['Shop Rcv Qty'] - df['Disp. Qty']
    design_totals = df.groupby(['UPC/Barcode/SKU', 'City']).agg(
        {'Sold Qty': 'sum', 'Net Receiving': 'sum'}).reset_index()
    design_totals['design Sell Through'] = (
        design_totals['Sold Qty'] / design_totals['Net Receiving'] * 100)
    design_totals['design Sell Through'] = design_totals['design Sell Through'].replace(
        [np.inf, -np.inf, np.nan], 0).astype(int)
    return design_totals

def merge_data(desired_df, design_totals):
    return pd.merge(desired_df,
                    design_totals[['UPC/Barcode/SKU', 'City', 'design Sell Through']],
                    on=['UPC/Barcode/SKU', 'City'],
                    how='left')

def apply_status_condition(desired_df):
    desired_df['Status'] = 'Low'
    desired_df.loc[desired_df['shop Sell Through'] > desired_df['design Sell Through'], 'Status'] = 'High'
    return desired_df

def process_data(desired_df):
    article_days = desired_df.groupby(['UPC/Barcode/SKU', 'City'])['Shop Days'].max().reset_index()
    merged_df = pd.merge(desired_df, article_days,
                         on=['UPC/Barcode/SKU', 'City'],
                         how='left',
                         suffixes=('', '_max_days'))
    merged_df_grouped = merged_df.groupby(['UPC/Barcode/SKU', 'City']).agg({
        'O.H Qty': 'sum',
        'Sold Qty': 'sum',
        'Shop Days': 'max'
    }).reset_index()
    result_df = merged_df_grouped[['UPC/Barcode/SKU', 'City', 'Shop Days']].rename(
        columns={'Shop Days': 'Date Difference'})
    return result_df

def process_and_calculate_cover(df, article_days):
    merged_df = pd.merge(df, article_days,
                         on=['UPC/Barcode/SKU', 'City'],
                         how='left',
                         suffixes=('', '_max_days'))
    merged_df_grouped = merged_df.groupby(['UPC/Barcode/SKU', 'City']).agg({
        'O.H Qty': 'sum',
        'Sold Qty': 'sum',
        'Shop Days': 'max'
    }).reset_index()
    result_df = merged_df_grouped[['UPC/Barcode/SKU', 'City', 'Shop Days']].rename(
        columns={'Shop Days': 'Date Difference'})
    merged_df_grouped = pd.merge(merged_df_grouped, result_df,
                                 on=['UPC/Barcode/SKU', 'City'],
                                 how='left')
    merged_df_grouped['Targeted Cover'] = merged_df_grouped['O.H Qty'] / (
        merged_df_grouped['Sold Qty'] / merged_df_grouped['Date Difference'])
    return merged_df_grouped

def merge_with_desired_cover(desired_df, merged_df_grouped):
    desired_df = pd.merge(desired_df,
                          merged_df_grouped[['UPC/Barcode/SKU', 'City', 'Targeted Cover']],
                          on=['UPC/Barcode/SKU', 'City'],
                          how='left')
    desired_df['Targeted Cover'] = desired_df['Targeted Cover'].fillna(0).replace(
        [np.inf, -np.inf], 0).astype(int)
    return desired_df

def calculate_article_days(df):
    df['Adjusted 1st Rcv Date'] = pd.to_datetime(df['Adjusted 1st Rcv Date'], errors='coerce')
    df = df.dropna(subset=['Adjusted 1st Rcv Date'])
    today = pd.Timestamp.now().normalize()
    df['Max Design Days'] = (today - df['Adjusted 1st Rcv Date']).dt.days
    article_days = df.groupby(['UPC/Barcode/SKU', 'City'])['Max Design Days'].max().reset_index()
    return article_days

def calculate_required_cover(desired_df):
    desired_df['Transfer in/out'] = desired_df['Targeted Cover'] * (
        desired_df['Sold Qty'] / desired_df['Shop Days']) - desired_df['O.H Qty']
    desired_df['Transfer in/out'] = desired_df['Transfer in/out'].replace(
        [np.inf, -np.inf, np.nan], 0).astype(int)
    return desired_df

def merge_desired_with_article_days(desired_df, article_days):
    desired_df = pd.merge(desired_df, article_days,
                          on=['UPC/Barcode/SKU', 'City'],
                          how='left')
    return desired_df

def filter_data(desired_df, sell_through_threshold, days_threshold):
    filtered_df = desired_df[
        (desired_df['design Sell Through'] > sell_through_threshold) &
        (desired_df['Max Design Days'] > days_threshold)
    ]
    return filtered_df

def process_transfer_details(filtered_df):
    sending_stores = filtered_df[filtered_df['Transfer in/out'] < 0]
    receiving_stores = filtered_df[filtered_df['Transfer in/out'] > 0]
    transfer_details = []

    for sending_index, sending_row in sending_stores.iterrows():
        matches = receiving_stores[
            (receiving_stores['City'] == sending_row['City']) &  # Ensure same City
            (receiving_stores['UPC/Barcode/SKU'] == sending_row['UPC/Barcode/SKU']) &
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
                'City': sending_row['City'],
                'UPC/Barcode/SKU': sending_row['UPC/Barcode/SKU'],
                'From Store': sending_row['STORE_NAME'],
                'To Store': receiving_row['STORE_NAME'],
                'DESIGN': sending_row['DESIGN'],
                'Size': sending_row['Size'],
                'Color': sending_row['Color'],
                'Volume': sending_row['Volume'],
                'product_type': sending_row['product_type'],
                'Quantity Transferred': transfer_qty
            })
            total_qty_to_transfer -= transfer_qty
            if total_qty_to_transfer <= 0:
                break

    return pd.DataFrame(transfer_details)

def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Transfer Details')
    return output.getvalue()


# ================== UI & FLOW ==================
def show_city():
        
    # ================== PAGE NAVIGATION DROPDOWN ==================
    page_choice = st.selectbox(
        "🔀 Go to Page:",
        ("City", "Regional", "Network"),
        key="page_selector_city"
    )

    if page_choice == "Regional":
        st.switch_page("pages/regional.py")
    elif page_choice == "Network":
        st.switch_page("pages/network.py")

    st.session_state["current_page"] = "City"

    # ================== PAGE STYLING ==================
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
                font-size: inherit;
                font-family: inherit;
                color: inherit;
                width: 100%;
                cursor: pointer;
                background-color: rgb(27 26 26);
                border: 1px solid rgba(49, 51, 63, 0.2);
            }
            h1 {
                font-family: "Source Sans Pro", sans-serif;
                font-weight: 700;
                color: rgb(244 245 253);
                padding: 1.25rem 0px 1rem;
            }
        </style>
    """, unsafe_allow_html=True)

    # ================== PAGE CONTENT ==================
    st.title("City 🌆")

    sample_file = create_sample_file()
    st.download_button(
        label="Download Sample Excel File",
        data=sample_file,
        file_name="sample_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # 🔹 Filters -----------------
       # 🔹 Filters row
    filter_defs = [
        ("Volume", "Volume"),
        ("product_type", "product_type"),
        ("Seasons", "Seasons"),
        ("City", "City"),
        ("Years", "Years"),  # 👈 NEW: filter by Years column
    ]

    filters = {}
    cols = st.columns(len(filter_defs))

    for i, (label, db_col) in enumerate(filter_defs):
        options = get_unique_values(db_col)
        selected_option = cols[i].selectbox(f"Select {label}", options=options, index=0)
        filters[label] = None if selected_option == "All" else selected_option

    threshold_date = st.date_input("Season Launch Date", min_value=datetime(2020, 1, 1), value=datetime.now())
    sell_through_threshold = st.number_input("Enter Sell-Through Threshold (%)", min_value=0, max_value=100, value=60)
    days_threshold = st.number_input("Enter Minimum Age", min_value=0, max_value=100, value=30)

    # ▶ PROCESSING
    if st.button("Process Data"):
        with st.spinner("Processing data, please wait..."):
            data = load_data_from_db(
                Volume_filter=filters["Volume"],
                product_type_filter=filters["product_type"],
                season_filter=filters["Seasons"],
                city_filter=filters["City"],
                Years_filter=filters["Years"],
            )

            if data.empty:
                st.warning("No data found for selected filters.")
            else:
                adjusted_data = adjust_date(data, threshold_date)
                aggregated_data = aggregate_data(adjusted_data, threshold_date)
                sell_through_data = calculate_sell_through(aggregated_data)
                days_data = calculate_days(sell_through_data)
                design_sell_through_data = calculate_design_sell_through(days_data)
                merged_data = merge_data(days_data, design_sell_through_data)
                status_data = apply_status_condition(merged_data)
                processed_data = process_data(status_data)
                cover_data = process_and_calculate_cover(status_data, processed_data)
                cover_merged_data = merge_with_desired_cover(status_data, cover_data)
                article_days = calculate_article_days(cover_merged_data)
                final_data = merge_desired_with_article_days(
                    calculate_required_cover(cover_merged_data), article_days
                )
                filtered_data = filter_data(final_data, sell_through_threshold, days_threshold)
                transfer_details = process_transfer_details(filtered_data)

                st.session_state.filtered_data = filtered_data
                st.session_state.transfer_details = transfer_details

                st.dataframe(filtered_data)

    if "filtered_data" in st.session_state:
        st.download_button(
            label="Download Processed Data",
            data=to_excel(st.session_state.filtered_data),
            file_name="processed_city.xlsx"
        )
        st.download_button(
            label="Download Transfer Details",
            data=to_excel(st.session_state.transfer_details),
            file_name="transfer_details_city.xlsx"
        )

if __name__ == "__main__":
    show_city()


