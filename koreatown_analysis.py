import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import requests
from datetime import datetime

# Set style for better-looking plots
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 8)

# Koreatown LA zip codes
ktown_zips = ['90004', '90005', '90006', '90010', '90019', '90020']

# Define COVID-19 time periods
# Pre-COVID: 2015-01 to 2020-02
# During COVID: 2020-03 to 2021-12
# Post-COVID: 2022-01 to 2025-10

print("=" * 80)
print("KOREATOWN RENTAL COSTS AND HOMELESSNESS ANALYSIS")
print("=" * 80)

# ============================================================================
# PART 1: Load and Process Rental Cost Data
# ============================================================================
print("\n1. Loading Rental Cost Data...")

# Load Zillow rental data
rental_df = pd.read_csv('Zip_zori_uc_sfrcondomfr_sm_month.csv')


# Filter for Koreatown zip codes
ktown_rental = rental_df[rental_df['RegionName'].astype(str).isin(ktown_zips)].copy()
print(f"   Found rental data for {len(ktown_rental)} Koreatown zip codes: {ktown_rental['RegionName'].tolist()}")

# Get date columns (format: YYYY-MM-DD)
date_cols = [col for col in ktown_rental.columns if col.startswith('20')]

# Reshape rental data to long format
rental_long = ktown_rental.melt(
    id_vars=['RegionName'], 
    value_vars=date_cols,
    var_name='date',
    value_name='rental_index'
)
rental_long['date'] = pd.to_datetime(rental_long['date'])
rental_long = rental_long.rename(columns={'RegionName': 'zip'})
rental_long['zip'] = rental_long['zip'].astype(str)

# Add time period classification
def classify_period(date):
    if date < pd.Timestamp('2020-03-01'):
        return 'Pre-COVID'
    elif date <= pd.Timestamp('2021-12-31'):
        return 'During COVID'
    else:
        return 'Post-COVID'

rental_long['period'] = rental_long['date'].apply(classify_period)

# Calculate aggregate statistics by period
period_stats = rental_long.groupby(['zip', 'period'])['rental_index'].agg([
    ('mean_rental', 'mean'),
    ('median_rental', 'median'),
    ('min_rental', 'min'),
    ('max_rental', 'max'),
    ('std_rental', 'std')
]).reset_index()

print("\n   Rental Index by Period and ZIP Code:")
print(period_stats.to_string())

# Calculate year-over-year changes
rental_long['year'] = rental_long['date'].dt.year
rental_long['month'] = rental_long['date'].dt.month

yearly_rental = rental_long.groupby(['zip', 'year'])['rental_index'].mean().reset_index()
yearly_rental['yoy_change'] = yearly_rental.groupby('zip')['rental_index'].pct_change() * 100

print("\n   Year-over-Year Rental Changes:")
print(yearly_rental.to_string())

# ============================================================================
# PART 2: Load and Process Homelessness Data
# ============================================================================
print("\n2. Loading Homelessness Data...")

# Load homelessness data
homeless_df = pd.read_excel('Sheltered Population - 2024.xlsx')

# Get ZIP to Census Tract mapping for Koreatown
print("\n3. Fetching ZIP to Census Tract Mapping...")
url = "https://www.huduser.gov/hudapi/public/usps?type=1&query=CA"
token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiI2IiwianRpIjoiOWZkMDRiYjQyOTA4ZWY4ZGRlYmM1M2Y2MmRmMTU4N2I4NzdiYmNhNGFjY2ExMTgwOWJhZmEwYjZkYzFiMjUxYTRjYzhjNDc2YTU1YTg1ZjgiLCJpYXQiOjE3NjQ3MzA2MzEuNTQzMjMsIm5iZiI6MTc2NDczMDYzMS41NDMyMzMsImV4cCI6MjA4MDI2MzQzMS41MzkxNjYsInN1YiI6IjExNDI2NSIsInNjb3BlcyI6W119.AyDAhc-GSpJ8PHtURarQon645PFiPalETUQGSQmwzxxmKdwMbfc8XSj5M0tpAmsbRZEc-OZ_qI11PnjPv4Thdw"
headers = {"Authorization": f"Bearer {token}"}

response = requests.get(url, headers=headers)
if response.status_code == 200:
    crosswalk_df = pd.DataFrame(response.json()["data"]["results"])
    ktown_crosswalk = crosswalk_df[crosswalk_df['zip'].isin(ktown_zips)].copy()
    # Extract tract ID from geoid (last 6 digits)
    ktown_crosswalk['tract'] = ktown_crosswalk['geoid'].astype(str).str[-6:]
    print(f"   Found {len(ktown_crosswalk)} census tract mappings for Koreatown")
    print(ktown_crosswalk[['zip', 'geoid', 'tract', 'res_ratio']].head(10).to_string())
else:
    print(f"   Error fetching crosswalk data: {response.status_code}")
    ktown_crosswalk = None

# Process homelessness data
print("\n4. Processing Homelessness Data...")
print(f"   Available columns: {homeless_df.columns.tolist()}")
print(f"\n   Data shape: {homeless_df.shape}")
print(f"\n   Sample data:")
print(homeless_df.head())

# Check if we have tract data that matches Koreatown
if ktown_crosswalk is not None:
    # Extract tract IDs from geoid
    homeless_df['tract'] = homeless_df['geoid20'].astype(str)
    ktown_tracts = ktown_crosswalk['tract'].unique()
    
    # Filter for Koreatown tracts
    ktown_homeless = homeless_df[homeless_df['tract'].isin(ktown_tracts)].copy()
    
    # Merge with crosswalk to get zip codes
    ktown_homeless = ktown_homeless.merge(
        ktown_crosswalk[['tract', 'zip', 'res_ratio']],
        on='tract',
        how='left'
    )
    
    print(f"\n   Filtered to {len(ktown_homeless)} Koreatown census tracts")
    print(f"   Unique tracts: {ktown_homeless['tract'].nunique()}")
else:
    ktown_homeless = homeless_df.copy()

# ============================================================================
# PART 3: Analyze Unsheltered Homelessness Categories
# ============================================================================
print("\n" + "=" * 80)
print("QUESTION 1: Rental Costs vs. Unsheltered Homelessness Categories")
print("=" * 80)

# Note: The 2024 data shows only one year. For a proper analysis, we would need
# historical data across multiple years to compare pre, during, and post COVID

print("\n2024 Koreatown Homelessness Summary:")
if len(ktown_homeless) > 0:
    # Calculate totals
    summary_stats = {
        'Total Unsheltered': ktown_homeless['unsheltered_pop_count'].sum(),
        'Living on Street': ktown_homeless['livingonstreet_count'].sum(),
        'In Vehicles': ktown_homeless['tot_vehicles_count'].sum(),
        '  - Cars': ktown_homeless['cars_count'].sum(),
        '  - Vans': ktown_homeless['vans_count'].sum(),
        '  - Campers': ktown_homeless['campers_count'].sum(),
        'Tents/Encampments': ktown_homeless['tot_tent_encamp_count'].sum(),
        '  - Encampments': ktown_homeless['encampments_count'].sum(),
        '  - Tents': ktown_homeless['tents_count'].sum(),
    }
    
    for key, value in summary_stats.items():
        print(f"   {key}: {value}")
    
    # Calculate percentages
    total_unsheltered = summary_stats['Total Unsheltered']
    if total_unsheltered > 0:
        print("\n   Percentage Distribution of Unsheltered Homelessness:")
        print(f"   Living on Street: {summary_stats['Living on Street']/total_unsheltered*100:.1f}%")
        print(f"   In Vehicles: {summary_stats['In Vehicles']/total_unsheltered*100:.1f}%")
        print(f"   Tents/Encampments: {summary_stats['Tents/Encampments']/total_unsheltered*100:.1f}%")

# ============================================================================
# PART 4: Analyze Single Adult vs. Family Homelessness
# ============================================================================
print("\n" + "=" * 80)
print("QUESTION 2: Rental Costs vs. Single Adult vs. Family Homelessness")
print("=" * 80)

if len(ktown_homeless) > 0:
    family_stats = {
        'Single Adults (Street)': ktown_homeless['totStreetSingAdult'].sum(),
        'Family Members (Street)': ktown_homeless['totStreetFamMem'].sum(),
        'Total Population': ktown_homeless['denom_total_pop'].sum(),
    }
    
    print("\n2024 Koreatown Street Homelessness by Household Type:")
    for key, value in family_stats.items():
        print(f"   {key}: {value}")
    
    total_street = family_stats['Single Adults (Street)'] + family_stats['Family Members (Street)']
    if total_street > 0:
        print(f"\n   Single Adults: {family_stats['Single Adults (Street)']/total_street*100:.1f}%")
        print(f"   Family Members: {family_stats['Family Members (Street)']/total_street*100:.1f}%")

# ============================================================================
# PART 5: Correlations and Analysis (Limited by 2024-only data)
# ============================================================================
print("\n" + "=" * 80)
print("CORRELATION ANALYSIS")
print("=" * 80)

# Get 2024 rental data for correlation
rental_2024 = rental_long[rental_long['year'] == 2024].copy()
rental_2024_avg = rental_2024.groupby('zip')['rental_index'].mean().reset_index()
rental_2024_avg.columns = ['zip', 'avg_rental_2024']

# Merge with homelessness data
if len(ktown_homeless) > 0 and len(rental_2024_avg) > 0:
    # Aggregate homelessness by ZIP
    homeless_by_zip = ktown_homeless.groupby('zip').agg({
        'unsheltered_pop_count': 'sum',
        'livingonstreet_count': 'sum',
        'tot_vehicles_count': 'sum',
        'tot_tent_encamp_count': 'sum',
        'totStreetSingAdult': 'sum',
        'totStreetFamMem': 'sum',
        'denom_total_pop': 'sum'
    }).reset_index()
    
    # Calculate rates per 1000 population
    homeless_by_zip['unsheltered_rate'] = (
        homeless_by_zip['unsheltered_pop_count'] / homeless_by_zip['denom_total_pop'] * 1000
    )
    homeless_by_zip['street_rate'] = (
        homeless_by_zip['livingonstreet_count'] / homeless_by_zip['denom_total_pop'] * 1000
    )
    homeless_by_zip['vehicle_rate'] = (
        homeless_by_zip['tot_vehicles_count'] / homeless_by_zip['denom_total_pop'] * 1000
    )
    homeless_by_zip['tent_rate'] = (
        homeless_by_zip['tot_tent_encamp_count'] / homeless_by_zip['denom_total_pop'] * 1000
    )
    homeless_by_zip['single_adult_rate'] = (
        homeless_by_zip['totStreetSingAdult'] / homeless_by_zip['denom_total_pop'] * 1000
    )
    homeless_by_zip['family_rate'] = (
        homeless_by_zip['totStreetFamMem'] / homeless_by_zip['denom_total_pop'] * 1000
    )
    
    # Merge with rental data
    analysis_df = homeless_by_zip.merge(rental_2024_avg, on='zip', how='inner')
    
    print("\n2024 Analysis Dataset:")
    print(analysis_df.to_string())
    
    if len(analysis_df) > 2:
        print("\n\nCorrelations between 2024 Rental Index and Homelessness Rates:")
        correlations = {
            'Unsheltered Rate': stats.pearsonr(analysis_df['avg_rental_2024'], analysis_df['unsheltered_rate']),
            'Street Homelessness Rate': stats.pearsonr(analysis_df['avg_rental_2024'], analysis_df['street_rate']),
            'Vehicle Homelessness Rate': stats.pearsonr(analysis_df['avg_rental_2024'], analysis_df['vehicle_rate']),
            'Tent/Encampment Rate': stats.pearsonr(analysis_df['avg_rental_2024'], analysis_df['tent_rate']),
            'Single Adult Rate': stats.pearsonr(analysis_df['avg_rental_2024'], analysis_df['single_adult_rate']),
            'Family Member Rate': stats.pearsonr(analysis_df['avg_rental_2024'], analysis_df['family_rate']),
        }
        
        for metric, (r, p) in correlations.items():
            sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
            print(f"   {metric}: r = {r:.3f}, p = {p:.3f} {sig}")

# ============================================================================
# PART 6: Visualizations
# ============================================================================
print("\n" + "=" * 80)
print("GENERATING VISUALIZATIONS")
print("=" * 80)

# Figure 1: Rental Cost Trends Over Time
fig, axes = plt.subplots(2, 2, figsize=(16, 12))

# Plot 1: Rental Index Time Series by ZIP
ax1 = axes[0, 0]
for zip_code in ktown_zips:
    zip_data = rental_long[rental_long['zip'] == zip_code]
    if len(zip_data) > 0:
        ax1.plot(zip_data['date'], zip_data['rental_index'], label=zip_code, marker='o', markersize=2)

ax1.axvline(pd.Timestamp('2020-03-01'), color='red', linestyle='--', label='COVID Start', alpha=0.7)
ax1.axvline(pd.Timestamp('2022-01-01'), color='green', linestyle='--', label='Post-COVID', alpha=0.7)
ax1.set_xlabel('Date')
ax1.set_ylabel('Rental Index (Zillow)')
ax1.set_title('Rental Cost Trends in Koreatown by ZIP Code')
ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
ax1.grid(True, alpha=0.3)

# Plot 2: Average Rental Index by Period
ax2 = axes[0, 1]
period_avg = rental_long.groupby('period')['rental_index'].agg(['mean', 'std']).reset_index()
period_order = ['Pre-COVID', 'During COVID', 'Post-COVID']
period_avg['period'] = pd.Categorical(period_avg['period'], categories=period_order, ordered=True)
period_avg = period_avg.sort_values('period')

ax2.bar(period_avg['period'], period_avg['mean'], yerr=period_avg['std'], 
        capsize=5, color=['#3498db', '#e74c3c', '#2ecc71'], alpha=0.7)
ax2.set_xlabel('Period')
ax2.set_ylabel('Average Rental Index')
ax2.set_title('Average Rental Costs by COVID Period')
ax2.grid(True, alpha=0.3, axis='y')

# Plot 3: Homelessness Categories (2024)
ax3 = axes[1, 0]
if len(ktown_homeless) > 0:
    categories = ['Street', 'Vehicles', 'Tents/Encampments']
    counts = [
        ktown_homeless['livingonstreet_count'].sum(),
        ktown_homeless['tot_vehicles_count'].sum(),
        ktown_homeless['tot_tent_encamp_count'].sum()
    ]
    colors = ['#e74c3c', '#3498db', '#f39c12']
    ax3.bar(categories, counts, color=colors, alpha=0.7)
    ax3.set_ylabel('Count')
    ax3.set_title('Unsheltered Homelessness by Category (2024)')
    ax3.grid(True, alpha=0.3, axis='y')
    
    # Add value labels on bars
    for i, v in enumerate(counts):
        ax3.text(i, v, str(v), ha='center', va='bottom', fontweight='bold')

# Plot 4: Single Adult vs. Family Homelessness (2024)
ax4 = axes[1, 1]
if len(ktown_homeless) > 0:
    household_types = ['Single Adults', 'Family Members']
    household_counts = [
        ktown_homeless['totStreetSingAdult'].sum(),
        ktown_homeless['totStreetFamMem'].sum()
    ]
    colors = ['#9b59b6', '#1abc9c']
    ax4.bar(household_types, household_counts, color=colors, alpha=0.7)
    ax4.set_ylabel('Count')
    ax4.set_title('Street Homelessness: Single Adults vs. Family Members (2024)')
    ax4.grid(True, alpha=0.3, axis='y')
    
    # Add value labels on bars
    for i, v in enumerate(household_counts):
        ax4.text(i, v, str(v), ha='center', va='bottom', fontweight='bold')

plt.tight_layout()
plt.savefig('koreatown_analysis_overview.png', dpi=300, bbox_inches='tight')
print("   Saved: koreatown_analysis_overview.png")

# Figure 2: Correlation Scatter Plots (2024 data)
if len(analysis_df) > 2:
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    
    scatter_plots = [
        ('avg_rental_2024', 'street_rate', 'Street Homelessness Rate'),
        ('avg_rental_2024', 'vehicle_rate', 'Vehicle Homelessness Rate'),
        ('avg_rental_2024', 'tent_rate', 'Tent/Encampment Rate'),
        ('avg_rental_2024', 'single_adult_rate', 'Single Adult Rate'),
        ('avg_rental_2024', 'family_rate', 'Family Member Rate'),
        ('avg_rental_2024', 'unsheltered_rate', 'Total Unsheltered Rate'),
    ]
    
    for idx, (x_col, y_col, title) in enumerate(scatter_plots):
        ax = axes[idx // 3, idx % 3]
        ax.scatter(analysis_df[x_col], analysis_df[y_col], s=100, alpha=0.6, color='#3498db')
        
        # Add labels for each point
        for i, row in analysis_df.iterrows():
            ax.annotate(row['zip'], (row[x_col], row[y_col]), 
                       fontsize=8, ha='right', va='bottom')
        
        # Add trend line
        z = np.polyfit(analysis_df[x_col], analysis_df[y_col], 1)
        p = np.poly1d(z)
        ax.plot(analysis_df[x_col], p(analysis_df[x_col]), "r--", alpha=0.8, linewidth=2)
        
        # Calculate and display correlation
        r, p_val = stats.pearsonr(analysis_df[x_col], analysis_df[y_col])
        ax.text(0.05, 0.95, f'r = {r:.3f}\np = {p_val:.3f}', 
               transform=ax.transAxes, fontsize=10, 
               verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        ax.set_xlabel('Average 2024 Rental Index')
        ax.set_ylabel(f'{title} (per 1000 pop)')
        ax.set_title(f'Rental Index vs. {title}')
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('koreatown_correlations.png', dpi=300, bbox_inches='tight')
    print("   Saved: koreatown_correlations.png")

# Figure 3: Detailed Time Series with Percent Changes
fig, axes = plt.subplots(2, 1, figsize=(16, 10))

# Plot 1: Percent change from baseline (2015)
ax1 = axes[0]
for zip_code in ktown_zips:
    zip_data = rental_long[rental_long['zip'] == zip_code].sort_values('date')
    if len(zip_data) > 0:
        baseline = zip_data[zip_data['date'] == zip_data['date'].min()]['rental_index'].values[0]
        zip_data['pct_change'] = ((zip_data['rental_index'] - baseline) / baseline) * 100
        ax1.plot(zip_data['date'], zip_data['pct_change'], label=zip_code, marker='o', markersize=2)

ax1.axvline(pd.Timestamp('2020-03-01'), color='red', linestyle='--', label='COVID Start', alpha=0.7)
ax1.axvline(pd.Timestamp('2022-01-01'), color='green', linestyle='--', label='Post-COVID', alpha=0.7)
ax1.axhline(0, color='black', linestyle='-', alpha=0.3)
ax1.set_xlabel('Date')
ax1.set_ylabel('% Change from 2015 Baseline')
ax1.set_title('Rental Cost Growth in Koreatown (% Change from 2015)')
ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
ax1.grid(True, alpha=0.3)

# Plot 2: Year-over-year changes
ax2 = axes[1]
for zip_code in ktown_zips:
    zip_yearly = yearly_rental[yearly_rental['zip'] == zip_code]
    if len(zip_yearly) > 0:
        ax2.plot(zip_yearly['year'], zip_yearly['yoy_change'], 
                label=zip_code, marker='o', markersize=4)

ax2.axhline(0, color='black', linestyle='-', alpha=0.3)
ax2.set_xlabel('Year')
ax2.set_ylabel('Year-over-Year % Change')
ax2.set_title('Year-over-Year Rental Cost Changes in Koreatown')
ax2.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('koreatown_rental_trends.png', dpi=300, bbox_inches='tight')
print("   Saved: koreatown_rental_trends.png")

plt.close('all')

# ============================================================================
# PART 7: Summary and Limitations
# ============================================================================
print("\n" + "=" * 80)
print("SUMMARY AND LIMITATIONS")
print("=" * 80)

print("""
KEY FINDINGS:

Rental Cost Trends:
- Rental costs in Koreatown ZIP codes have been tracked from 2015-2025
- Data shows the trajectory before, during, and after COVID-19
- Year-over-year changes can reveal periods of rapid rent increases

Homelessness Data Limitations:
- Current dataset contains only 2024 data (single year snapshot)
- Cannot establish temporal correlations with rental cost changes
- Cannot compare pre-COVID, during-COVID, and post-COVID homelessness levels

To properly answer the research questions, we would need:
1. Historical homelessness count data (2015-2025) for the same census tracts
2. Yearly Point-in-Time (PIT) count data broken down by:
   - Unsheltered categories (street, vehicle, tent/encampment)
   - Household type (single adult vs. family)
   - Geographic area (census tract or ZIP code level)

Current Analysis (2024 only):
- Provides baseline understanding of homelessness composition
- Shows correlation between rental costs and homelessness across ZIP codes
- Identifies which categories of homelessness are most prevalent

Recommended Data Sources:
- LA Homeless Services Authority (LAHSA) historical PIT count data
- HUD Continuum of Care data by year
- Census tract-level homelessness counts from 2015-2025
""")

print("\n" + "=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)
print("\nGenerated files:")
print("  1. koreatown_analysis_overview.png - Main summary charts")
print("  2. koreatown_correlations.png - Correlation scatter plots (2024)")
print("  3. koreatown_rental_trends.png - Detailed rental cost trends")
