from supabase import create_client, Client
import pandas as pd
import streamlit as st
import plotly.express as px
import time

# Supabase credentials
API_URL = st.secrets["URL_SUPA"]
API_KEY = st.secrets["API_SUPA"]

# Create Supabase client
supabase: Client = create_client(API_URL, API_KEY)

# Function to fetch the last 200 rows of data from Supabase
def fetch_data():
    response = supabase.table('Main data').select('*').order('created_at', desc=True).limit(200).execute()
    data = response.data
    df = pd.DataFrame(data)
    
    if 'created_at' in df.columns:
        df['created_at'] = pd.to_datetime(df['created_at'])
    
    # Sort the DataFrame by created_at in ascending order to show oldest first
    df = df.sort_values(by='created_at', ascending=True).reset_index(drop=True)
    
    return df

# Streamlit page configuration
st.set_page_config(page_title="Arduino Sensor Data Dashboard", layout='wide', page_icon="📊")

# Apply custom styles to the dashboard
st.markdown(
    """
    <style>
        /* Style for the main title */
        .title {
            font-size: 36px;
            font-weight: bold;
            color: #4A4A4A;
            text-align: center;
            padding-bottom: 20px;
        }
        
        /* Button style */
        .stButton button {
            background-color: #F0F0F5;
            color: #333;
            border: 1px solid #D1D1E0;
            border-radius: 8px;
            padding: 8px 16px;
            font-size: 16px;
        }
        
        /* Button on hover */
        .stButton button:hover {
            background-color: #E0E0F5;
            color: #000;
        }

        /* Style the metrics */
        div[data-testid="metric-container"] {
            background-color: #F9F9F9;
            border: 1px solid #E0E0E0;
            padding: 16px;
            border-radius: 10px;
            color: #333;
            font-size: 18px;
        }

        /* Main background */
        body {
            background-color: #FBFBFB;
        }

        /* Section padding */
        .section {
            padding-top: 20px;
            padding-bottom: 20px;
        }
    </style>
    """, unsafe_allow_html=True
)

# Title and description
st.markdown("<h1 class='title'>Sensor Data Dashboard</h1>", unsafe_allow_html=True)
st.write("""
    This  dashboard visualizes real-time data collected from K5H sensors. 
    You can view live sensor data and toggle between different graph plots using the buttons below.
""")

# Initialize session state for button toggles
if 'show_rr' not in st.session_state:
    st.session_state['show_rr'] = False
if 'show_hr' not in st.session_state:
    st.session_state['show_hr'] = False
if 'show_distance' not in st.session_state:
    st.session_state['show_distance'] = False
if 'show_movement' not in st.session_state:
    st.session_state['show_movement'] = False
if 'show_magnitude' not in st.session_state:
    st.session_state['show_magnitude'] = False

# Fetch initial data
df = fetch_data()

# Placeholder for live data and graphs
placeholder = st.empty()

# Loop to update data and re-render graphs in real-time
while True:
    df = fetch_data()

    if not df.empty:
        most_recent = df.iloc[-1]  # Get the most recent row
        
        # Display the current sensor readings
        with placeholder.container():
            st.markdown("### Current Sensor Readings")
            metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
            
            with metrics_col1:
                st.metric("Respiratory Rate (bpm)", most_recent["Respiration Rate"])
                st.metric("Body Movement Indicator", most_recent["Body Movement Indicator"])
            
            with metrics_col2:
                st.metric("Heart Rate (bpm)", most_recent["Heart Rate"])
                st.metric("Movement Magnitude", most_recent["Relative Body Movement Magnitude"])
            
            with metrics_col3:
                st.metric("Distance (cm)", most_recent["Distance Between Target and Radar"])
                st.metric("Presence", most_recent["Presence Detection"])

            # Section for buttons
            st.markdown("<div class='section'></div>", unsafe_allow_html=True)
            st.markdown("### Toggle Graphs Below")
            button_col1, button_col2, button_col3, button_col4, button_col5 = st.columns(5)

            # Static unique keys by appending fixed suffixes to the keys
            with button_col1:
                if st.button("Respiratory Rate Plot", key="toggle_rr_1"):
                    st.session_state['show_rr'] = not st.session_state['show_rr']

            with button_col2:
                if st.button("Heart Rate Plot", key="toggle_hr_2"):
                    st.session_state['show_hr'] = not st.session_state['show_hr']

            with button_col3:
                if st.button("Distance Plot", key="toggle_distance_3"):
                    st.session_state['show_distance'] = not st.session_state['show_distance']

            with button_col4:
                if st.button("Body Movement Plot", key="toggle_movement_4"):
                    st.session_state['show_movement'] = not st.session_state['show_movement']

            with button_col5:
                if st.button("Movement Magnitude Plot", key="toggle_magnitude_5"):
                    st.session_state['show_magnitude'] = not st.session_state['show_magnitude']
            
            # Show or hide each plot based on the button toggle state
            if st.session_state['show_rr']:
                st.markdown('### Respiratory Rate Over Time')
                fig_rr = px.line(df, x='created_at', y='Respiration Rate', title='Respiratory Rate Over Time',
                                 labels={'created_at': 'Time', 'Respiration Rate': 'Respiratory Rate (bpm)'},
                                 markers=True, color_discrete_sequence=["#FF9999"])
                st.plotly_chart(fig_rr, use_container_width=True)

            if st.session_state['show_hr']:
                st.markdown('### Heart Rate Over Time')
                fig_hr = px.line(df, x='created_at', y='Heart Rate', title='Heart Rate Over Time',
                                 labels={'created_at': 'Time', 'Heart Rate': 'Heart Rate (bpm)'},
                                 markers=True, color_discrete_sequence=["#9999FF"])
                st.plotly_chart(fig_hr, use_container_width=True)

            if st.session_state['show_distance']:
                st.markdown('### Distance Between Target and Radar Over Time')
                fig_distance = px.line(df, x='created_at', y='Distance Between Target and Radar', title='Distance Over Time',
                                       labels={'created_at': 'Time', 'Distance Between Target and Radar': 'Distance (cm)'},
                                       markers=True, color_discrete_sequence=["#99FF99"])
                st.plotly_chart(fig_distance, use_container_width=True)

            if st.session_state['show_movement']:
                st.markdown('### Body Movement Indicator Over Time')
                fig_movement = px.line(df, x='created_at', y='Body Movement Indicator', title='Body Movement Indicator Over Time',
                                       labels={'created_at': 'Time', 'Body Movement Indicator': 'Movement Indicator'},
                                       markers=True, color_discrete_sequence=["#FFD699"])
                st.plotly_chart(fig_movement, use_container_width=True)

            if st.session_state['show_magnitude']:
                st.markdown('### Relative Body Movement Magnitude Over Time')
                fig_magnitude = px.line(df, x='created_at', y='Relative Body Movement Magnitude', title='Movement Magnitude Over Time',
                                        labels={'created_at': 'Time', 'Relative Body Movement Magnitude': 'Movement Magnitude'},
                                        markers=True, color_discrete_sequence=["#CC99FF"])
                st.plotly_chart(fig_magnitude, use_container_width=True)
    
    # Refresh data every 10 seconds
    time.sleep(2)
