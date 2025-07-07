# Muscarelle Museum Collection Diversity Dashboard

A comprehensive dashboard for visualizing diversity in the Muscarelle Museum's permanent collection, focusing on artist gender and cultural heritage representation.

## Features

- **Summary KPIs**: Gender distribution, cultural heritage breakdown, acquisition trends  
- **Interactive Visualizations**: Bar charts, pie charts, time series, heat maps  
- **Advanced Filters**: Date ranges, departments, demographics  
- **Export Capabilities**: CSV downloads and summary statistics  
- **Real-time Updates**: Dynamic filtering and cross-chart interactions  

## Live Demo

🔗 **[View Live Dashboard](https://your-deployed-url-here.streamlit.app)**

## Local Development

### Prerequisites

- Python 3.7+
- pip or conda

### Installation

1. Clone the repository:

   ```bash
   git clone git@github.com:maroufpaul/deai_muscaralle.git
   cd deai_muscaralle
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the dashboard:

   ```bash
   streamlit run museum_dashboard.py
   ```

## Data Sources

This dashboard uses enriched museum collection data with artist information sourced from:

- **Wikidata** – Gender and biographical information  
- **VIAF** – Artist authority records  
- **Getty ULAN** – Art-specific biographical data  

## Technical Stack

- **Frontend**: Streamlit  
- **Data Processing**: Pandas, NumPy  
- **Visualizations**: Plotly  
- **Deployment**: Streamlit Community Cloud  

## Project Structure

```
deai_muscaralle/
├── museum_dashboard.py        # Main dashboard application
├── data_enrichment.py         # Data enrichment pipeline
├── requirements.txt           # Python dependencies
├── .streamlit/
│   └── config.toml            # Streamlit configuration
├── README.md                  # Project README
└── data/                      # Sample data files
    └── sample_collection.csv
```

## Contributing

This project was developed as part of a graduate computer science internship at the musuem to support curatorial planning, grant reporting, and strategic DEAI initiatives.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For questions about this dashboard or the underlying data enrichment process, please contact:

- **Developer**: Marouf Paul  
- **Email**: maroofpaul1@gmail.com  
- **Institution**: will decide soon....

## Acknowledgments

- 
- 
- 
