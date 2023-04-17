import os
import pandas as pd
import numpy as np 
import altair as alt
import geopandas as gpd


alt.data_transformers.disable_max_rows()
pd.options.mode.chained_assignment = None


def fix_walk_scores_tracts(s):
    s = str(s)
    if len(s) != 6:
        num_zeros = 6 - len(s)
        s = ((num_zeros) * '0') + s 
    return s

def fix_food_scores_tracts(s):
    s = str(s)
    if len(s) != 11:
        num_zeros = 11 - len(s)
        s = ((num_zeros) * '0') + s 
    return s

def process_walk_data(walk_df, gdf, target_cols = ['D3A', 'Pct_AO0', 'NatWalkInd']):
    walk_df = walk_df[(walk_df['STATEFP'] == 36) & (walk_df['CSA_Name'] == 'New York-Newark, NY-NJ-CT-PA')]
    walk_df['ct2010'] = walk_df['TRACTCE'].apply(fix_walk_scores_tracts)
    park_zips = ['107202', '070203', '070202', '091602', '091800', '097203']
    walk_df = walk_df[~walk_df['ct2010'].isin(park_zips)]
    grouped_walk_df = walk_df.groupby('ct2010')[target_cols].agg(func = np.median).reset_index()
    return grouped_walk_df

def process_food_data(food_df):
    food_df = food_df[food_df['OHU2010'] >= food_df['TractSNAP']]

    counties = ['Bronx County', 'Kings County', 'Queens County', 'New York County', 'Richmond Counnty']
    food_df = food_df[(food_df['State'] == 'New York') & (food_df['County'].isin(counties))]
    food_df['ct2010'] = food_df['CensusTract'].apply(fix_food_scores_tracts)
    food_df['ct2010'] = food_df['ct2010'].apply(lambda s: s[-6:])
    park_zips = ['107202', '070203', '070202', '091602', '091800', '097203']
    food_df = food_df[~food_df['ct2010'].isin(park_zips)]
    food_df['snap_pct'] = food_df['TractSNAP'] / food_df['OHU2010']

    grouped_food_df = food_df.groupby('ct2010').agg(func = ['mean', np.median])
    cols = [(col[0] + "_" + col[1]) for col in grouped_food_df.columns]
    grouped_food_df.columns = cols
    grouped_food_df = grouped_food_df.reset_index()

    return grouped_food_df

def create_points_df(farmers_markets, garden_sites):
    farmers_markets = farmers_markets[farmers_markets['Market Name'] != 'Saratoga Farm Stand']
    farmers_markets['loc_type'] = 'Farmers market'
    farmers_markets = farmers_markets[['Latitude', 'Longitude', 'Borough', 'loc_type']]
    farmers_markets = farmers_markets.rename(columns = {'Borough': 'borough', 'Latitude': 'lat', 'Longitude': 'long'})

    garden_sites['lat'] = garden_sites.centroid.y
    garden_sites['long'] = garden_sites.centroid.x
    garden_sites['loc_type'] = 'Community garden'
    garden_sites = garden_sites[['lat', 'long', 'borough', 'loc_type']] 

    points_df = pd.concat([farmers_markets, garden_sites], axis = 0)
    return points_df




gdf = gpd.read_file("../data/census_tracts_2010/geo_export_15e54104-230b-46ff-831d-f8f2bcaa8f59.shp")
food_df = pd.read_excel("../data/food_access.xlsx", sheet_name = "Food Access Research Atlas")
walk_df = pd.read_csv("../data/epa_smart_locations.csv.gz", compression = "gzip")
# farmers_markets = pd.read_csv("../data/point_data/DOHMH_Farmers_Markets.csv")
# garden_sites = gpd.read_file("../data/community_gardens/geo_export_719c88a3-5724-4f23-b587-e754c0844c6d.shp")

# cd = gpd.read_file("../data/community_districts/geo_export_7b678860-455d-4c2b-8175-8482e297e882.shp")

grouped_food_df = process_food_data(food_df)
grouped_walk_df = process_walk_data(walk_df, gdf)
# points_df = create_points_df(farmers_markets, garden_sites)

grouped_food_df.to_csv("../data/food_security_by_tract.csv")
grouped_walk_df.to_csv("../data/walkability_by_tract.csv")
