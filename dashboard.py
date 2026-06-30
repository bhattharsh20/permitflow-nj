import streamlit as st
import pandas as pd
from supabase import create_client

# Set up clean, wide-screen page layout
st.set_page_config(page_title="PermitFlow NJ - Deal Scout", layout="wide")

# 1. Configuration & Keys
SUPABASE_URL = st.secrets["https://skwrstisakfwcmxcvpxh.supabase.co"]
UPABASE_KEY = st.secrets["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNrd3JzdGlzYWtmd2NteGN2cHhoIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4MjgzMzI1OSwiZXhwIjoyMDk4NDA5MjU5fQ.3w6LL06XyG8qu8yh2zhtp9GtAdTNAV53r2Qz45mY2jg"]

@st.cache_resource
def init_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

# Fetch scored records from Supabase
def load_data():
    try:
        response = supabase.table("liquor_licenses").select("*").order("deal_score", desc=True).execute()
        return pd.DataFrame(response.data)
    except Exception as e:
        st.error(f"Error connecting to Supabase: {e}")
        return pd.DataFrame()

df = load_data()

# --- HEADER SECTION ---
st.title("🕵️‍♂️ PermitFlow NJ — Deal Scout Dashboard")
st.markdown("Real-time commercial intelligence tracking pocket and inactive liquor license acquisition targets.")
st.write("---")

if not df.empty:
    # --- METRIC CARDS ---
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Scouted Assets", len(df))
    with col2:
        high_value_count = len(df[df['deal_score'] >= 70]) if 'deal_score' in df.columns else 0
        st.metric("🔥 High-Value Target Deals", high_value_count)
    with col3:
        pocket_count = df['status_desc'].str.contains('Pocket', case=False, na=False).sum() if 'status_desc' in df.columns else 0
        st.metric("🚀 Highly Portable Pocket Licenses", pocket_count)

    st.write("###")

    # --- SIDEBAR FILTERS ---
    st.sidebar.header("Filter Leads")
    
    all_towns = sorted(df['municipality'].unique()) if 'municipality' in df.columns else []
    selected_towns = st.sidebar.multiselect("Select Municipalities", all_towns, default=all_towns)
    
    score_cutoff = st.sidebar.slider("Minimum Deal Score", 0, 100, 70)

    # Apply filters dynamically
    filtered_df = df.copy()
    if 'municipality' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['municipality'].isin(selected_towns)]
    if 'deal_score' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['deal_score'] >= score_cutoff]

    # --- MAIN INTERACTIVE LEAD TABLE ---
    st.subheader(f"Ranked Pipeline Opportunities ({len(filtered_df)} showing)")
    
    # Ensure columns exist before displaying to prevent errors
    expected_cols = ["deal_score", "municipality", "trade_name", "status_desc", "license_id", "agent_notes"]
    available_cols = [col for col in expected_cols if col in filtered_df.columns]
    
    display_df = filtered_df[available_cols]
    
    # Map raw columns to clean display headers
    rename_dict = {
        "deal_score": "Score",
        "municipality": "Township",
        "trade_name": "Entity / Operating Trade Name",
        "status_desc": "State Status",
        "license_id": "License Number",
        "agent_notes": "Scout Analysis Notes"
    }
    display_df = display_df.rename(columns={k: v for k, v in rename_dict.items() if k in available_cols})

    # Render dataframe cleanly with interactive styling
    if "Score" in display_df.columns:
        st.dataframe(
            display_df.style.background_gradient(subset=["Score"], cmap="YlOrRd"), 
            use_container_width=True,
            hide_index=True
        )
    else:
        st.dataframe(display_df, use_container_width=True, hide_index=True)

else:
    st.info("No data found. Ensure your database tables are populated by your scripts.")