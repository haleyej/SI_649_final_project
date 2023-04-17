import os
import pandas as pd
import numpy as np 
import altair as alt
import geopandas as gpd
from food_data import create_points_df



def generate_plots(grouped_food_df, grouped_walk_df, points_df, gdf, color_palette = ['#3877eb', '#38eb38']):
    #select types of locations
    radio_options = list(points_df['loc_type'].unique()) 
    radio_labels = list(points_df['loc_type'].unique())

    input_dropdown = alt.binding_radio(
        options = [None] + radio_options + [f'~({radio_options[0]}&{radio_options[1]})'],
        labels =  ['All'] + radio_labels + ['None'],
        name = 'Location Type: '
    )
    loc_selection = alt.selection_single(fields = ['loc_type'], bind = input_dropdown)


    ct_base = alt.Chart(gdf).mark_geoshape(color = '#ebebeb').encode()

    walkability = alt.Chart(gdf).mark_geoshape().transform_lookup(
        lookup = 'ct2010', 
        from_ = alt.LookupData(data = grouped_walk_df, key = 'ct2010', 
                            fields = ['D3A', 'Pct_AO0', 'NatWalkInd', 'ct2010'])
    ).encode(
        color = alt.Color('NatWalkInd:Q', scale = alt.Scale(scheme = 'plasma', reverse = True, domain = [5, 20]), 
                        legend = alt.Legend(title = 'Walkability Score')), 
        tooltip = [alt.Tooltip('NatWalkInd:Q', title = 'Walkability Score', format = '.2f')]
    )

    points = alt.Chart(points_df).add_selection(loc_selection).mark_circle(
        size = 30, 
        opacity = 0.6
    ).encode(
        latitude = 'lat:Q', 
        longitude = 'long:Q', 
        color = alt.Color('loc_type:N', legend = alt.Legend(title = 'Location Type'), 
                        scale = alt.Scale(range = color_palette)), 
        tooltip = [alt.Tooltip('loc_type:N', title = 'Location Type')]
    ).transform_filter(
        loc_selection
    )

    side_1 = alt.layer(ct_base, walkability, points).properties(height = 350, width = 350)


    snap_layer = alt.Chart(gdf).mark_geoshape().transform_lookup(
        lookup = 'ct2010', 
        from_ = alt.LookupData(data = grouped_food_df, key = 'ct2010', 
                            fields = ['snap_pct_median', 'ct2010'])
    ).encode(
        color = alt.Color('snap_pct_median:Q', scale = alt.Scale(scheme = 'plasma', reverse = True), 
                        legend = alt.Legend(title = 'Percent of resident receiving SNAP benefits', format = '0%')), 
        tooltip = [alt.Tooltip('snap_pct_median:Q', title = 'Percent on SNAP', format = '.2%')]
    )

    side_2 = alt.layer(ct_base, snap_layer, points)


    final = alt.hconcat(side_1, side_2).properties(title = alt.TitleParams('Commmunity gardens and farmers markets are in more walkable neighborhoods', 
                                                               subtitle = "These are not necessarily the areas with the higher rates of food insecurity, where residents need access to fresh food", 
                                                               fontSize = 25, 
                                                               subtitleFontSize = 15))
    return final


gdf = gpd.read_file("../data/census_tracts_2010/geo_export_15e54104-230b-46ff-831d-f8f2bcaa8f59.shp")

grouped_food_df = pd.read_csv("../data/food_security_by_tract.csv")
grouped_walk_df = pd.read_csv("../data/walkability_by_tract.csv")
cd = gpd.read_file("../data/community_districts/geo_export_7b678860-455d-4c2b-8175-8482e297e882.shp")

farmers_markets = pd.read_csv("../data/point_data/DOHMH_Farmers_Markets.csv")
garden_sites = gpd.read_file("../data/community_gardens/geo_export_719c88a3-5724-4f23-b587-e754c0844c6d.shp")
points_df = create_points_df(farmers_markets, garden_sites)


generate_plots(grouped_food_df, grouped_walk_df, points_df, gdf).save("plot_plot_plot.html")