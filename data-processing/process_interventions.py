import pandas as pd
import json
from pathlib import Path

# Paths
raw_data_path = Path(__file__).parent / 'raw-data'
viz_datasets_path = Path(__file__).parent / 'viz-datasets'

# UCDP name -> Standard name for display and centroid lookup
ucdp_name_mapping = {
    'Russia (Soviet Union)': 'Russia',
    'DR Congo (Zaire)': 'DR Congo',
    'Cambodia (Kampuchea)': 'Cambodia',
    'Vietnam (North Vietnam)': 'Vietnam',
    'Yemen (North Yemen)': 'Yemen',
    'Zimbabwe (Rhodesia)': 'Zimbabwe',
    'Serbia (Yugoslavia)': 'Serbia',
    'Ivory Coast': 'Ivory Coast',
    'United States of America': 'USA',
    'United Kingdom': 'UK',
    'United Arab Emirates': 'UAE',
    'Bosnia-Herzegovina': 'Bosnia',
    'Central African Republic': 'CAR',
}

# Country centroids (lat, lon) - approximate centers
centroids = {
    'Afghanistan': [33.93, 67.71],
    'Albania': [41.15, 20.17],
    'Algeria': [28.03, 1.66],
    'Angola': [-12.5, 18.5],
    'Argentina': [-38.42, -63.62],
    'Armenia': [40.07, 45.04],
    'Australia': [-25.27, 133.78],
    'Austria': [47.52, 14.55],
    'Azerbaijan': [40.14, 47.58],
    'Bahrain': [26.07, 50.56],
    'Bangladesh': [23.68, 90.36],
    'Belgium': [50.50, 4.47],
    'Benin': [9.31, 2.32],
    'Bhutan': [27.51, 90.43],
    'Bolivia': [-16.29, -63.59],
    'Bosnia': [43.92, 17.68],
    'Botswana': [-22.33, 24.68],
    'Brazil': [-14.24, -51.93],
    'Burkina Faso': [12.24, -1.56],
    'Burundi': [-3.37, 29.92],
    'Cambodia': [12.57, 104.99],
    'Cameroon': [7.37, 12.35],
    'Canada': [56.13, -106.35],
    'CAR': [6.61, 20.94],
    'Chad': [15.45, 18.73],
    'China': [35.86, 104.20],
    'Colombia': [4.57, -74.30],
    'Congo': [-0.23, 15.83],
    'Czech Republic': [49.82, 15.47],
    'Denmark': [56.26, 9.50],
    'Djibouti': [11.83, 42.59],
    'DR Congo': [-4.04, 21.76],
    'Ecuador': [-1.83, -78.18],
    'Egypt': [26.82, 30.80],
    'El Salvador': [13.79, -88.90],
    'Eritrea': [15.18, 39.78],
    'Estonia': [58.60, 25.01],
    'Ethiopia': [9.15, 40.49],
    'Finland': [61.92, 25.75],
    'France': [46.23, 2.21],
    'Gabon': [-0.80, 11.61],
    'Gambia': [13.44, -15.31],
    'Germany': [51.17, 10.45],
    'Ghana': [7.95, -1.02],
    'Greece': [39.07, 21.82],
    'Guatemala': [15.78, -90.23],
    'Guinea': [9.95, -9.70],
    'Guinea-Bissau': [11.80, -15.18],
    'Haiti': [18.97, -72.29],
    'Hungary': [47.16, 19.50],
    'Indonesia': [-0.79, 113.92],
    'Iran': [32.43, 53.69],
    'Iraq': [33.22, 43.68],
    'Ireland': [53.14, -7.69],
    'Italy': [41.87, 12.57],
    'Ivory Coast': [7.54, -5.55],
    'Jordan': [30.59, 36.24],
    'Kazakhstan': [48.02, 66.92],
    'Kenya': [-0.02, 37.91],
    'Latvia': [56.88, 24.60],
    'Lesotho': [-29.61, 28.23],
    'Liberia': [6.43, -9.43],
    'Libya': [26.34, 17.23],
    'Lithuania': [55.17, 23.88],
    'Luxembourg': [49.82, 6.13],
    'Madagascar': [-18.77, 46.87],
    'Malawi': [-13.25, 34.30],
    'Malaysia': [4.21, 101.98],
    'Mali': [17.57, -4.00],
    'Mauritania': [21.01, -10.94],
    'Mexico': [23.63, -102.55],
    'Moldova': [47.41, 28.37],
    'Morocco': [31.79, -7.09],
    'Mozambique': [-18.67, 35.53],
    'Nepal': [28.39, 84.12],
    'Netherlands': [52.13, 5.29],
    'New Zealand': [-40.90, 174.89],
    'Niger': [17.61, 8.08],
    'Nigeria': [9.08, 8.68],
    'North Korea': [40.34, 127.51],
    'Norway': [60.47, 8.47],
    'Pakistan': [30.38, 69.35],
    'Paraguay': [-23.44, -58.44],
    'Peru': [-9.19, -75.02],
    'Philippines': [12.88, 121.77],
    'Portugal': [39.40, -8.22],
    'Romania': [45.94, 24.97],
    'Russia': [61.52, 105.32],
    'Rwanda': [-1.94, 29.87],
    'Saudi Arabia': [23.89, 45.08],
    'Senegal': [14.50, -14.45],
    'Serbia': [44.02, 21.01],
    'Sierra Leone': [8.46, -11.78],
    'Singapore': [1.35, 103.82],
    'Somalia': [5.15, 46.20],
    'South Africa': [-30.56, 22.94],
    'South Korea': [35.91, 127.77],
    'South Sudan': [6.88, 31.31],
    'Spain': [40.46, -3.75],
    'Sri Lanka': [7.87, 80.77],
    'Sweden': [60.13, 18.64],
    'Switzerland': [46.82, 8.23],
    'Syria': [34.80, 38.99],
    'Tanzania': [-6.37, 34.89],
    'Thailand': [15.87, 100.99],
    'Togo': [8.62, 0.82],
    'Tunisia': [33.89, 9.54],
    'Turkey': [38.96, 35.24],
    'Turkmenistan': [38.97, 59.56],
    'UAE': [23.42, 53.85],
    'Uganda': [1.37, 32.29],
    'UK': [55.38, -3.44],
    'Ukraine': [48.38, 31.17],
    'USA': [37.09, -95.71],
    'Vietnam': [14.06, 108.28],
    'Yemen': [15.55, 48.52],
    'Zambia': [-13.13, 27.85],
    'Zimbabwe': [-19.02, 29.15],
}

def get_intervention_type(num_interveners):
    """Categorize intervention by number of interveners"""
    if num_interveners <= 3:
        return 'direct'  # Direct military intervention
    elif num_interveners <= 15:
        return 'coalition'  # Military coalition
    else:
        return 'peacekeeping'  # UN peacekeeping mission

# UCDP code mappings
INCOMPATIBILITY_MAP = {
    1: 'Territory',
    2: 'Government'
}

CONFLICT_TYPE_MAP = {
    1: 'Colonial/imperial',
    2: 'Interstate war',
    3: 'Civil war',
    4: 'Internationalized civil war'
}


def main():
    # Load UCDP BattleDeaths
    df = pd.read_csv(raw_data_path / 'UCDP' / 'BattleDeaths_v25_1.csv')

    # Filter to 2015-2024
    df = df[(df['year'] >= 2015) & (df['year'] <= 2024)]

    # Filter to records with interventions
    df_int = df[df['side_a_2nd'].notna() & (df['side_a_2nd'] != '')].copy()

    # Exclude records where location is a Western country (these are usually misattributed casualty counts)
    western_locations = ['United States of America', 'United Kingdom', 'France', 'Germany', 'Canada', 'Australia']
    for loc in western_locations:
        df_int = df_int[~df_int['location_inc'].str.contains(loc, na=False)]

    print(f'Processing {len(df_int)} intervention records...')

    # Build flow data
    flows = []
    missing_centroids = set()

    for _, row in df_int.iterrows():
        # Parse interveners
        interveners_raw = [x.strip().replace('Government of ', '') for x in str(row['side_a_2nd']).split(',')]
        num_interveners = len(interveners_raw)
        intervention_type = get_intervention_type(num_interveners)

        # Get location - handle multi-country locations by taking first
        location_raw = str(row['location_inc']).split(',')[0].strip()

        # Get opponent (side_b) - clean up "Government of" prefix
        opponent_raw = str(row['side_b']).replace('Government of ', '').strip()
        opponent = ucdp_name_mapping.get(opponent_raw, opponent_raw)

        # Get conflict context
        incomp_code = row.get('incompatibility', 0)
        conflict_type_code = row.get('type_of_conflict', 0)
        conflict_issue = INCOMPATIBILITY_MAP.get(incomp_code, 'Unknown')
        conflict_type = CONFLICT_TYPE_MAP.get(conflict_type_code, 'Armed conflict')

        # Get territory name if available
        territory = str(row.get('territory_name', '')).strip()
        if territory and territory != 'nan':
            conflict_issue = f'{conflict_issue} ({territory})'

        # Clean names
        interveners = [ucdp_name_mapping.get(i, i) for i in interveners_raw]
        location = ucdp_name_mapping.get(location_raw, location_raw)

        year = int(row['year'])
        deaths = int(row['bd_best'])

        for intervener in interveners:
            # Skip if same country (domestic)
            if intervener == location:
                continue
            # Check for missing centroids
            if intervener not in centroids:
                missing_centroids.add(intervener)
                continue
            if location not in centroids:
                missing_centroids.add(location)
                continue

            flows.append({
                'from': intervener,
                'to': location,
                'year': year,
                'deaths': deaths,
                'type': intervention_type,
                'num_interveners': num_interveners,
                'opponent': opponent,
                'issue': conflict_issue,
                'conflict_type': conflict_type
            })

    if missing_centroids:
        print(f'Missing centroids for: {missing_centroids}')

    print(f'Raw flows: {len(flows)}')

    # Aggregate by (from, to, year) - keep type info and collect opponents/issues
    flow_df = pd.DataFrame(flows)
    flow_agg = flow_df.groupby(['from', 'to', 'year', 'type']).agg({
        'deaths': 'sum',
        'num_interveners': 'first',
        'opponent': lambda x: ', '.join(sorted(set(x))),
        'issue': lambda x: ', '.join(sorted(set(x))),
        'conflict_type': 'first'
    }).reset_index()
    flow_agg['deaths'] = flow_agg['deaths'].astype(int)

    print(f'Aggregated flows: {len(flow_agg)}')

    # Check year distribution
    print('\nFlows by year:')
    print(flow_agg.groupby('year').size())

    # Build output JSON
    output = {
        'metadata': {
            'title': 'Military Interventions in Armed Conflicts',
            'source': 'UCDP Battle Deaths Dataset v25.1',
            'date_range': '2015-2024',
            'note': 'Deaths in internationalized conflicts where foreign governments provided military support'
        },
        'centroids': centroids,
        'flows': flow_agg.to_dict(orient='records')
    }

    # Save
    output_file = viz_datasets_path / 'viz9_intervention_flows.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)

    print(f'\n[OK] Saved: {output_file} ({output_file.stat().st_size / 1024:.1f} KB)')

    # Show sample
    print('\nTop 10 flows by deaths:')
    print(flow_agg.nlargest(10, 'deaths').to_string())

if __name__ == '__main__':
    main()
