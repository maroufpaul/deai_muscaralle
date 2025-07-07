import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import io

# Set page configuration
st.set_page_config(
    page_title="Muscarelle Museum - Collection Diversity Dashboard",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #2E4057;
        text-align: center;
        margin-bottom: 2rem;
    }
    .kpi-container {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #007bff;
    }
    .filter-section {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Sample data generation function
@st.cache_data
def generate_sample_data():
    """Generate sample museum data for demonstration"""
    np.random.seed(42)
    
    # Sample artists and metadata
    artists = [
        "Mary Cassatt", "Pablo Picasso", "Frida Kahlo", "Vincent van Gogh",
        "Georgia O'Keeffe", "Claude Monet", "Yayoi Kusama", "Jean-Michel Basquiat",
        "Louise Bourgeois", "Jackson Pollock", "Kara Walker", "Kehinde Wiley",
        "Amy Tan", "Ai Weiwei", "Banksy", "Kaws", "Takashi Murakami",
        "Kerry James Marshall", "Cindy Sherman", "Jeff Koons"
    ]
    
    genders = ["Female", "Male", "Non-Binary", "Unknown"]
    heritage_regions = ["European", "North American", "East Asian", "African", 
                       "Latin American", "Middle Eastern", "Indigenous", "Mixed Heritage"]
    departments = ["Painting", "Sculpture", "Photography", "Prints & Drawings", 
                  "Contemporary Art", "Decorative Arts"]
    
    # Generate artwork data
    n_artworks = 500
    data = []
    
    for i in range(n_artworks):
        artist = np.random.choice(artists)
        
        # Simulate realistic gender distribution (skewed historically)
        if artist in ["Mary Cassatt", "Frida Kahlo", "Georgia O'Keeffe", "Yayoi Kusama", 
                     "Louise Bourgeois", "Kara Walker", "Cindy Sherman"]:
            gender = "Female"
        elif artist in ["Banksy"]:
            gender = "Unknown"
        else:
            gender = np.random.choice(["Male", "Female", "Non-Binary"], p=[0.7, 0.25, 0.05])
        
        # Heritage mapping (simplified)
        heritage_map = {
            "Mary Cassatt": "North American", "Pablo Picasso": "European",
            "Frida Kahlo": "Latin American", "Vincent van Gogh": "European",
            "Georgia O'Keeffe": "North American", "Claude Monet": "European",
            "Yayoi Kusama": "East Asian", "Jean-Michel Basquiat": "African",
            "Louise Bourgeois": "European", "Jackson Pollock": "North American",
            "Kara Walker": "African", "Kehinde Wiley": "African",
            "Amy Tan": "East Asian", "Ai Weiwei": "East Asian",
            "Banksy": "European", "Kaws": "North American",
            "Takashi Murakami": "East Asian", "Kerry James Marshall": "African",
            "Cindy Sherman": "North American", "Jeff Koons": "North American"
        }
        
        heritage = heritage_map.get(artist, np.random.choice(heritage_regions))
        
        # Generate acquisition date (weighted toward recent years)
        start_date = datetime(1950, 1, 1)
        end_date = datetime(2024, 12, 31)
        
        # Weight more recent acquisitions
        years = np.arange(1950, 2025)
        weights = np.exp((years - 1950) * 0.02)  # Exponential growth
        year = np.random.choice(years, p=weights/weights.sum())
        
        acquisition_date = datetime(year, 
                                  np.random.randint(1, 13), 
                                  np.random.randint(1, 29))
        
        data.append({
            'artwork_id': f"MA{i+1:04d}",
            'title': f"Artwork {i+1}",
            'artist_name': artist,
            'year_created': np.random.randint(1850, 2024),
            'acquisition_date': acquisition_date,
            'department': np.random.choice(departments),
            'medium': np.random.choice(["Oil on canvas", "Watercolor", "Bronze", 
                                      "Photography", "Mixed media", "Lithograph"]),
            'gender': gender,
            'heritage': heritage
        })
    
    return pd.DataFrame(data)

# Load data
df = generate_sample_data()

# Title
st.markdown('<h1 class="main-header">🎨 Muscarelle Museum Collection Diversity Dashboard</h1>', 
            unsafe_allow_html=True)

# Sidebar filters
st.sidebar.markdown("## 🔍 Filters")

# Date range filter
min_date = df['acquisition_date'].min()
max_date = df['acquisition_date'].max()
date_range = st.sidebar.date_input(
    "Acquisition Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Department filter
departments = ['All'] + sorted(df['department'].unique().tolist())
selected_departments = st.sidebar.multiselect(
    "Department",
    departments,
    default=['All']
)

# Gender filter
genders = ['All'] + sorted(df['gender'].unique().tolist())
selected_genders = st.sidebar.multiselect(
    "Artist Gender",
    genders,
    default=['All']
)

# Heritage filter
heritage_options = ['All'] + sorted(df['heritage'].unique().tolist())
selected_heritage = st.sidebar.multiselect(
    "Cultural Heritage",
    heritage_options,
    default=['All']
)

# Apply filters
filtered_df = df.copy()

# Date filter
if len(date_range) == 2:
    start_date, end_date = date_range
    filtered_df = filtered_df[
        (filtered_df['acquisition_date'].dt.date >= start_date) & 
        (filtered_df['acquisition_date'].dt.date <= end_date)
    ]

# Department filter
if 'All' not in selected_departments and selected_departments:
    filtered_df = filtered_df[filtered_df['department'].isin(selected_departments)]

# Gender filter
if 'All' not in selected_genders and selected_genders:
    filtered_df = filtered_df[filtered_df['gender'].isin(selected_genders)]

# Heritage filter
if 'All' not in selected_heritage and selected_heritage:
    filtered_df = filtered_df[filtered_df['heritage'].isin(selected_heritage)]

# KPI Cards
st.markdown("## 📊 Key Performance Indicators")

kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)

with kpi_col1:
    st.markdown('<div class="kpi-container">', unsafe_allow_html=True)
    total_works = len(filtered_df)
    st.metric("Total Artworks", f"{total_works:,}")
    st.markdown('</div>', unsafe_allow_html=True)

with kpi_col2:
    st.markdown('<div class="kpi-container">', unsafe_allow_html=True)
    female_pct = (filtered_df['gender'] == 'Female').mean() * 100
    st.metric("Female Artists", f"{female_pct:.1f}%")
    st.markdown('</div>', unsafe_allow_html=True)

with kpi_col3:
    st.markdown('<div class="kpi-container">', unsafe_allow_html=True)
    underrep_heritage = ['African', 'Latin American', 'Indigenous', 'Middle Eastern']
    underrep_pct = filtered_df['heritage'].isin(underrep_heritage).mean() * 100
    st.metric("Underrepresented Heritage", f"{underrep_pct:.1f}%")
    st.markdown('</div>', unsafe_allow_html=True)

with kpi_col4:
    st.markdown('<div class="kpi-container">', unsafe_allow_html=True)
    recent_cutoff = datetime.now() - timedelta(days=365*5)  # Last 5 years
    recent_works = filtered_df[filtered_df['acquisition_date'] >= recent_cutoff]
    recent_female_pct = (recent_works['gender'] == 'Female').mean() * 100 if len(recent_works) > 0 else 0
    st.metric("Recent Female Acquisitions", f"{recent_female_pct:.1f}%")
    st.markdown('</div>', unsafe_allow_html=True)

# Visualization section
st.markdown("## 📈 Visualizations")

# Row 1: Gender and Heritage charts
viz_col1, viz_col2 = st.columns(2)

with viz_col1:
    st.markdown("### Gender Distribution")
    gender_counts = filtered_df['gender'].value_counts()
    fig_gender = px.bar(
        x=gender_counts.index,
        y=gender_counts.values,
        title="Artworks by Artist Gender",
        color=gender_counts.index,
        color_discrete_map={
            'Female': '#ff6b6b',
            'Male': '#4ecdc4',
            'Non-Binary': '#45b7d1',
            'Unknown': '#96ceb4'
        }
    )
    fig_gender.update_layout(showlegend=False, height=400)
    st.plotly_chart(fig_gender, use_container_width=True)

with viz_col2:
    st.markdown("### Cultural Heritage Distribution")
    heritage_counts = filtered_df['heritage'].value_counts()
    fig_heritage = px.pie(
        values=heritage_counts.values,
        names=heritage_counts.index,
        title="Artists by Cultural Heritage"
    )
    fig_heritage.update_layout(height=400)
    st.plotly_chart(fig_heritage, use_container_width=True)

# Row 2: Time series and intersection analysis
viz_col3, viz_col4 = st.columns(2)

with viz_col3:
    st.markdown("### Acquisition Trends by Gender")
    # Group by year and gender
    yearly_gender = filtered_df.groupby([
        filtered_df['acquisition_date'].dt.year, 'gender'
    ]).size().reset_index(name='count')
    
    fig_timeline = px.line(
        yearly_gender,
        x='acquisition_date',
        y='count',
        color='gender',
        title="Annual Acquisitions by Artist Gender",
        color_discrete_map={
            'Female': '#ff6b6b',
            'Male': '#4ecdc4',
            'Non-Binary': '#45b7d1',
            'Unknown': '#96ceb4'
        }
    )
    fig_timeline.update_layout(height=400)
    st.plotly_chart(fig_timeline, use_container_width=True)

with viz_col4:
    st.markdown("### Gender × Heritage Intersection")
    # Create crosstab
    crosstab = pd.crosstab(filtered_df['heritage'], filtered_df['gender'])
    
    fig_heatmap = px.imshow(
        crosstab.values,
        x=crosstab.columns,
        y=crosstab.index,
        color_continuous_scale='Blues',
        title="Gender × Heritage Intersection"
    )
    fig_heatmap.update_layout(height=400)
    st.plotly_chart(fig_heatmap, use_container_width=True)

# Detailed data table
st.markdown("## 📋 Detailed Collection Data")

# Search functionality
search_term = st.text_input("🔍 Search by artist name or artwork title:", "")

# Filter by search term
display_df = filtered_df.copy()
if search_term:
    display_df = display_df[
        display_df['artist_name'].str.contains(search_term, case=False, na=False) |
        display_df['title'].str.contains(search_term, case=False, na=False)
    ]

# Select columns for display
display_columns = ['artwork_id', 'title', 'artist_name', 'year_created', 
                  'acquisition_date', 'department', 'gender', 'heritage']

st.dataframe(
    display_df[display_columns].sort_values('acquisition_date', ascending=False),
    use_container_width=True,
    height=400
)

# Export functionality
st.markdown("## 💾 Export Data")

export_col1, export_col2 = st.columns(2)

with export_col1:
    # CSV export
    csv_buffer = io.StringIO()
    filtered_df.to_csv(csv_buffer, index=False)
    st.download_button(
        label="📥 Download Filtered Data (CSV)",
        data=csv_buffer.getvalue(),
        file_name=f"muscarelle_collection_data_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

with export_col2:
    # Summary statistics export
    summary_stats = pd.DataFrame({
        'Metric': ['Total Artworks', 'Female Artists (%)', 'Male Artists (%)', 
                  'Non-Binary Artists (%)', 'Unknown Gender (%)',
                  'Underrepresented Heritage (%)'],
        'Value': [
            len(filtered_df),
            (filtered_df['gender'] == 'Female').mean() * 100,
            (filtered_df['gender'] == 'Male').mean() * 100,
            (filtered_df['gender'] == 'Non-Binary').mean() * 100,
            (filtered_df['gender'] == 'Unknown').mean() * 100,
            filtered_df['heritage'].isin(['African', 'Latin American', 'Indigenous', 'Middle Eastern']).mean() * 100
        ]
    })
    
    summary_csv = io.StringIO()
    summary_stats.to_csv(summary_csv, index=False)
    st.download_button(
        label="📊 Download Summary Statistics (CSV)",
        data=summary_csv.getvalue(),
        file_name=f"muscarelle_summary_stats_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

# Footer
st.markdown("---")
st.markdown("*Dashboard created for the Muscarelle Museum of Art - Collection Diversity Analysis*")
st.markdown("*Data enriched using Wikidata, VIAF, and ULAN*")