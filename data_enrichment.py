import pandas as pd
import requests
import time
import json
from urllib.parse import quote
import logging
from typing import Dict, List, Optional, Tuple
import re

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ArtistEnrichmentPipeline:
    """
    A pipeline for enriching museum artist data with gender and heritage information
    from various linked open data sources.
    """
    
    def __init__(self, delay_seconds: float = 1.0):
        self.delay_seconds = delay_seconds
        self.wikidata_endpoint = "https://query.wikidata.org/sparql"
        self.viaf_endpoint = "http://viaf.org/viaf/search"
        
        # Gender mappings
        self.gender_mappings = {
            'Q6581097': 'Male',
            'Q6581072': 'Female',
            'Q48270': 'Non-Binary',
            'Q1097630': 'Non-Binary',  # Intersex
            'Q2449503': 'Non-Binary',  # Transgender
        }
        
        # Heritage region mappings (simplified)
        self.heritage_mappings = {
            # Europe
            'Q142': 'European',  # France
            'Q183': 'European',  # Germany
            'Q38': 'European',   # Italy
            'Q29': 'European',   # Spain
            'Q145': 'European',  # United Kingdom
            'Q34': 'European',   # Sweden
            'Q35': 'European',   # Denmark
            'Q55': 'European',   # Netherlands
            'Q40': 'European',   # Austria
            'Q39': 'European',   # Switzerland
            'Q36': 'European',   # Poland
            'Q37': 'European',   # Lithuania
            'Q33': 'European',   # Finland
            'Q20': 'European',   # Norway
            'Q159': 'European',  # Russia
            
            # North America
            'Q30': 'North American',    # United States
            'Q16': 'North American',    # Canada
            'Q96': 'North American',    # Mexico
            
            # Asia
            'Q148': 'East Asian',       # China
            'Q17': 'East Asian',        # Japan
            'Q884': 'East Asian',       # South Korea
            'Q668': 'South Asian',      # India
            'Q819': 'South Asian',      # Laos
            'Q334': 'Southeast Asian',  # Singapore
            'Q833': 'Southeast Asian',  # Malaysia
            'Q928': 'Southeast Asian',  # Philippines
            'Q252': 'Southeast Asian',  # Indonesia
            'Q869': 'Southeast Asian',  # Thailand
            'Q881': 'Southeast Asian',  # Vietnam
            'Q889': 'South Asian',      # Afghanistan
            'Q843': 'South Asian',      # Pakistan
            'Q902': 'South Asian',      # Bangladesh
            'Q424': 'Southeast Asian',  # Cambodia
            'Q819': 'Southeast Asian',  # Laos
            'Q836': 'Southeast Asian',  # Myanmar
            'Q878': 'Middle Eastern',   # United Arab Emirates
            'Q858': 'Middle Eastern',   # Syria
            'Q796': 'Middle Eastern',   # Iraq
            'Q794': 'Middle Eastern',   # Iran
            'Q801': 'Middle Eastern',   # Israel
            'Q822': 'Middle Eastern',   # Lebanon
            'Q199': 'European',         # 1
            
            # Africa
            'Q258': 'African',          # South Africa
            'Q1033': 'African',         # Nigeria
            'Q1028': 'African',         # Morocco
            'Q79': 'African',           # Egypt
            'Q1049': 'African',         # Sudan
            'Q1014': 'African',         # Libya
            'Q1029': 'African',         # Morocco
            'Q1050': 'African',         # Swaziland
            'Q1037': 'African',         # Rwanda
            'Q1036': 'African',         # Uganda
            'Q1019': 'African',         # Madagascar
            'Q1020': 'African',         # Malawi
            'Q1041': 'African',         # Senegal
            'Q1008': 'African',         # Ivory Coast
            'Q1032': 'African',         # Niger
            'Q1027': 'African',         # Mauritania
            'Q1042': 'African',         # Sierra Leone
            'Q1009': 'African',         # Cameroon
            'Q1007': 'African',         # Central African Republic
            'Q1006': 'African',         # Burkina Faso
            'Q1005': 'African',         # Burundi
            'Q1011': 'African',         # Cape Verde
            'Q1013': 'African',         # Djibouti
            'Q1017': 'African',         # Equatorial Guinea
            'Q1018': 'African',         # Eritrea
            'Q115': 'African',          # Ethiopia
            'Q1000': 'African',         # Gabon
            'Q1005': 'African',         # Gambia
            'Q117': 'African',          # Ghana
            'Q1007': 'African',         # Guinea
            'Q1008': 'African',         # Guinea-Bissau
            'Q1028': 'African',         # Kenya
            'Q1013': 'African',         # Lesotho
            'Q1014': 'African',         # Liberia
            'Q1016': 'African',         # Mali
            'Q1027': 'African',         # Mauritius
            'Q1020': 'African',         # Mozambique
            'Q1030': 'African',         # Namibia
            'Q1032': 'African',         # Republic of the Congo
            'Q1039': 'African',         # São Tomé and Príncipe
            'Q1044': 'African',         # Somalia
            'Q1045': 'African',         # South Sudan
            'Q1046': 'African',         # Tanzania
            'Q1007': 'African',         # Togo
            'Q1048': 'African',         # Tunisia
            'Q1049': 'African',         # Zambia
            'Q954': 'African',          # Zimbabwe
            
            # Latin America
            'Q414': 'Latin American',   # Argentina
            'Q155': 'Latin American',   # Brazil
            'Q298': 'Latin American',   # Chile
            'Q739': 'Latin American',   # Colombia
            'Q241': 'Latin American',   # Cuba
            'Q736': 'Latin American',   # Ecuador
            'Q804': 'Latin American',   # Panama
            'Q717': 'Latin American',   # Venezuela
            'Q750': 'Latin American',   # Bolivia
            'Q733': 'Latin American',   # Paraguay
            'Q77': 'Latin American',    # Uruguay
            'Q419': 'Latin American',   # Guatemala
            'Q774': 'Latin American',   # Honduras
            'Q792': 'Latin American',   # El Salvador
            'Q811': 'Latin American',   # Nicaragua
            'Q800': 'Latin American',   # Costa Rica
            'Q790': 'Latin American',   # Haiti
            'Q786': 'Latin American',   # Dominican Republic
            'Q766': 'Latin American',   # Jamaica
            'Q757': 'Latin American',   # Saint Vincent and the Grenadines
            'Q760': 'Latin American',   # Saint Lucia
            'Q769': 'Latin American',   # Grenada
            'Q784': 'Latin American',   # Dominica
            'Q781': 'Latin American',   # Antigua and Barbuda
            'Q778': 'Latin American',   # Bahamas
            'Q244': 'Latin American',   # Barbados
            'Q242': 'Latin American',   # Belize
            'Q734': 'Latin American',   # Guyana
            'Q730': 'Latin American',   # Suriname
            'Q18': 'Latin American',    # Trinidad and Tobago
        }
    
    def clean_artist_name(self, name: str) -> str:
        """Clean and standardize artist names"""
        if pd.isna(name):
            return ""
        
        # Remove extra whitespace
        name = re.sub(r'\s+', ' ', name.strip())
        
        # Handle "Last, First" format
        if ',' in name:
            parts = name.split(',')
            if len(parts) == 2:
                last, first = parts
                name = f"{first.strip()} {last.strip()}"
        
        # Remove common suffixes
        suffixes = ['Jr.', 'Sr.', 'III', 'II', 'IV']
        for suffix in suffixes:
            name = name.replace(suffix, '').strip()
        
        return name
    
    def query_wikidata(self, artist_name: str, birth_year: Optional[int] = None, 
                      death_year: Optional[int] = None) -> Optional[Dict]:
        """
        Query Wikidata for artist information including gender and nationality
        """
        try:
            # Clean the name for the query
            clean_name = self.clean_artist_name(artist_name)
            
            # Build SPARQL query
            query = f"""
            SELECT DISTINCT ?person ?personLabel ?gender ?genderLabel ?birthDate ?deathDate ?nationality ?nationalityLabel ?occupation ?occupationLabel
            WHERE {{
              ?person wdt:P31 wd:Q5 .  # Is a human
              ?person rdfs:label "{clean_name}"@en .
              
              OPTIONAL {{ ?person wdt:P21 ?gender . }}
              OPTIONAL {{ ?person wdt:P569 ?birthDate . }}
              OPTIONAL {{ ?person wdt:P570 ?deathDate . }}
              OPTIONAL {{ ?person wdt:P27 ?nationality . }}
              OPTIONAL {{ ?person wdt:P106 ?occupation . }}
              
              # Filter for artists/creators
              {{
                ?person wdt:P106 wd:Q1028181 .  # painter
              }} UNION {{
                ?person wdt:P106 wd:Q1281618 .  # sculptor
              }} UNION {{
                ?person wdt:P106 wd:Q33231 .    # photographer
              }} UNION {{
                ?person wdt:P106 wd:Q483501 .   # artist
              }} UNION {{
                ?person wdt:P106 wd:Q15296811 . # draughtsperson
              }}
              
              SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en" . }}
            }}
            """
            
            # Add birth/death year filters if available
            if birth_year:
                query = query.replace(
                    "SERVICE wikibase:label", 
                    f"FILTER(YEAR(?birthDate) = {birth_year} || !BOUND(?birthDate))\n      SERVICE wikibase:label"
                )
            
            if death_year:
                query = query.replace(
                    "SERVICE wikibase:label",
                    f"FILTER(YEAR(?deathDate) = {death_year} || !BOUND(?deathDate))\n      SERVICE wikibase:label"
                )
            
            # Execute query
            response = requests.get(
                self.wikidata_endpoint,
                params={'query': query, 'format': 'json'},
                headers={'User-Agent': 'MuseumDataEnrichment/1.0'}
            )
            
            if response.status_code == 200:
                data = response.json()
                results = data.get('results', {}).get('bindings', [])
                
                if results:
                    # Return the first result
                    result = results[0]
                    
                    # Extract gender
                    gender = 'Unknown'
                    if 'gender' in result:
                        gender_uri = result['gender']['value']
                        gender_id = gender_uri.split('/')[-1]
                        gender = self.gender_mappings.get(gender_id, 'Unknown')
                    
                    # Extract heritage/nationality
                    heritage = 'Unknown'
                    if 'nationality' in result:
                        nationality_uri = result['nationality']['value']
                        nationality_id = nationality_uri.split('/')[-1]
                        heritage = self.heritage_mappings.get(nationality_id, 'Unknown')
                    
                    return {
                        'wikidata_id': result['person']['value'].split('/')[-1],
                        'gender': gender,
                        'heritage': heritage,
                        'birth_date': result.get('birthDate', {}).get('value'),
                        'death_date': result.get('deathDate', {}).get('value'),
                        'nationality_label': result.get('nationalityLabel', {}).get('value'),
                        'confidence': 0.8  # High confidence for exact name match
                    }
                    
        except Exception as e:
            logger.error(f"Error querying Wikidata for {artist_name}: {str(e)}")
        
        return None
    
    def query_viaf(self, artist_name: str) -> Optional[Dict]:
        """
        Query VIAF (Virtual International Authority File)