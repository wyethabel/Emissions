import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import geopandas as gpd

TITLE = 'Food Processing Emissions from 2000-2020'
SUB_TITLE = 'Source: Food and Agriculture Organization of the United Nations'

# Plots our map on streamlit
def map_visual(year, element):
    df = pd.read_csv('Food_Processing_Emissions.csv')
    df = df[(df['Year'] == year) & (df['Element'] == element)]
    geo_data = (f'World.geojson')

    df_geo_unmerged = gpd.read_file(f'World.geojson')
    df_geo_unmerged = df_geo_unmerged[['name', 'geometry']]
    df_geo_merged = df_geo_unmerged.merge(df, left_on='name', right_on='Area', how='outer')
    df_geo_merged = df_geo_merged[~df_geo_merged['geometry'].isna()]

    # Map Build
    map = folium.Map(
        location=(20, 0),
        zoom_start=2,
        max_bounds=True,
        min_zoom=1,
        max_zoom=7,
        tiles='CartoDB positron'
    )

    # Map Features
    choropleth = folium.Choropleth(
        geo_data=geo_data,
        data=df_geo_merged,
        columns=('Area', 'Value'),
        key_on='feature.properties.name',
        threshold_scale=(df_geo_merged['Value'].quantile((0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1))).tolist(),
        fill_color='RdYlGn_r',
        fill_opacity=0.8,
        line_opacity=0.3,
        highlight=True,
        nan_fill_color='black',
        legend_name='Yearly Emissions'
    )
    choropleth.geojson.add_to(map)

    # Popup Features
    folium.features.GeoJson(data=df_geo_merged,
                            name='Country Emissions',
                            smooth_factor=2,
                            style_function=lambda x: {'color': 'black', 'fillColor': 'transparent', 'weight': 0.0},
                            tooltip=folium.features.GeoJsonTooltip(
                                fields=['Area', 'Value'],
                                aliases=['Country Name: ', 'Emissions (Kilotonnes): '],
                                localize=True,
                                sticky=False,
                                labels=True,
                                style='''
                                background-color: #F0EFEF;
                                border: 0px solid black;
                                border-radius: 0px;
                                box-shadow: 0px;
                                '''
                            )).add_to(map)
    st_map = st_folium(map, width=900, height=500)


def main():
    # Page config
    st.set_page_config(TITLE, layout='wide')
    st.title(TITLE)
    st.caption(SUB_TITLE)
    st.markdown('---')

    # Sidebar
    st.sidebar.header('Map and Yearly Metric Filters')
    st.sidebar.caption('---')

    # Load and build initial metrics
    df = pd.read_csv('Food_Processing_Emissions.csv')
    total_CO2 = df[df['Element'] == 'Emissions (CO2)']['Value'].sum()
    total_N2O = df[df['Element'] == 'Emissions (N2O)']['Value'].sum()
    st.markdown('### 20 Year Metrics:')
    col1, col2 = st.columns(2)
    col1.metric('Total CO2 Emissions (Kilotonnes)', "{:,}".format(round(total_CO2, 2)))
    col2.metric('Total N2O Emissions (Kilotonnes)', "{:,}".format(round(total_N2O, 2)))
    st.markdown('---')

    # Display Filters and Map
    year = st.sidebar.selectbox('Year', df['Year'].unique())
    element = st.sidebar.radio('Emission Type', df['Element'].unique())
    st.header(f'{year} {element}')
    map_visual(year, element)
    st.sidebar.markdown('---')
    st.sidebar.markdown('Made by Wyeth Abel')

    # Metrics
    st.markdown('### Yearly Metrics:')
    yearly_CO2 = df[(df['Element'] == 'Emissions (CO2)') & (df['Year'] == year)]['Value'].sum()
    yearly_N2O = df[(df['Element'] == 'Emissions (N2O)') & (df['Year'] == year)]['Value'].sum()
    col3, col4 = st.columns(2)
    col3.metric(f'{year} CO2 Emissions (Kilotonnes)', "{:,}".format(round(yearly_CO2, 2)))
    col4.metric(f'{year} N2O Emissions (Kilotonnes)', "{:,}".format(round(yearly_N2O, 2)))

    # Lineplot
    st.markdown('---')
    total_value_CO2 = df[df['Element'] == 'Emissions (CO2)'].groupby('Year')['Value'].sum().reset_index()
    st.markdown('CO2 Emissions Per Year')
    st.line_chart(data=total_value_CO2, x='Year', y='Value')
    total_value_N2O = df[df['Element'] == 'Emissions (N2O)'].groupby('Year')['Value'].sum().reset_index()
    st.markdown('N2O Emissions Per Year')
    st.line_chart(data=total_value_N2O, x='Year', y='Value')

if __name__ == '__main__':
    main()
