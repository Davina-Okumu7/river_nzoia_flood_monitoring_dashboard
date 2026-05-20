import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import json
import time


# ------------------------------------------------
# PAGE CONFIG
# ------------------------------------------------
st.set_page_config(
    page_title="River Nzoia Digital Twin",
    layout="wide"
)

st.title("Nzoia Floodplain Flood Monitoring Dashboard")

# ------------------------------------------------
# LOAD DATA
# ------------------------------------------------
from pathlib import Path
import pandas as pd

file_path = Path(__file__).parent / "calbrated_values.csv"
df = pd.read_csv(file_path)
#data = pd.read_csv(
    #r"C:\Users\User\Desktop\FINAL YEAR MAPS\PROTOTYPE TRIAL\calbrated_values.csv"
#)

# ------------------------------------------------
# LOAD FLOOD GEOJSON
# ------------------------------------------------
with open(
    "maps/Flood_hazard_streamlit_vector.geojson"
) as f:

    geojson_data = json.load(f)

# ------------------------------------------------
# LOAD SCHOOLS GEOJSON
# ------------------------------------------------
with open(
    "maps/Schools.geojson"
) as f:

    schools_data = json.load(f)

# ------------------------------------------------
# CREATE LAYOUT COLUMNS
# ------------------------------------------------
# TOP STATUS ROW
# ------------------------------------------------
top1, top2 = st.columns(2)

with top1:

    level_placeholder = st.empty()

with top2:

    status_placeholder = st.empty()
# ------------------------------------------------
col1, col2 = st.columns([1, 1.3])

# ------------------------------------------------
# ALERT PLACEHOLDER
# ------------------------------------------------
alert_placeholder = st.empty()

# ------------------------------------------------
# STATUS PLACEHOLDER
# ------------------------------------------------
status_placeholder = st.empty()

# ------------------------------------------------
# GRAPH COLUMN
# ------------------------------------------------
with col1:

    st.subheader("Live Flood Depth")

    # chart created ONCE
    chart = st.line_chart()

# ------------------------------------------------
# MAP CREATION
# ------------------------------------------------
m = folium.Map(
    location=[0.5, 34.1],
    zoom_start=10,
    tiles="OpenStreetMap"
)

# ------------------------------------------------
# STYLE FUNCTION
# ------------------------------------------------
def style_function(feature):

    props = feature.get("properties", {})
    dn = props.get("DN", 1)

    try:
        dn = int(dn)

    except:
        dn = 1

    color_map = {
        1: "blue",
        2: "lightblue",
        3: "yellow",
        4: "orange",
        5: "red",
        6: "darkred"
    }

    color = color_map.get(dn, "gray")

    return {
        "fillColor": color,
        "color": color,
        "weight": 1,
        "fillOpacity": 0.6
    }

# ------------------------------------------------
# ADD FLOOD LAYER
# ------------------------------------------------
folium.GeoJson(
    geojson_data,
    name="Flood Hazard",
    style_function=style_function,
    tooltip=folium.GeoJsonTooltip(
        fields=["DN"],
        aliases=["Hazard Level:"]
    )
).add_to(m)

# ------------------------------------------------
# ADD SCHOOL POINTS
# ------------------------------------------------
school_group = folium.FeatureGroup(
    name="Schools"
)

for feature in schools_data["features"]:

    coords = feature["geometry"]["coordinates"]

    lon = coords[0]
    lat = coords[1]

    properties = feature.get("properties", {})

    school_name = properties.get(
        "name",
        "Unnamed School"
    )

    folium.CircleMarker(
        location=[lat, lon],
        radius=5,
        color="black",
        weight=1,
        fill=True,
        fill_color="cyan",
        fill_opacity=1,
        tooltip=school_name
    ).add_to(school_group)

school_group.add_to(m)

# ------------------------------------------------
# LAYER CONTROL
# ------------------------------------------------
folium.LayerControl().add_to(m)

# ------------------------------------------------
# LEGEND
# ------------------------------------------------
legend_html = """
<div style="
position: fixed;
bottom: 50px;
left: 50px;
width: 180px;
height: 220px;
background-color: white;
color: black;
border:2px solid grey;
z-index:9999;
font-size:14px;
padding: 10px;
">
<b>Flood Hazard Levels</b><br>
<i style="background:darkred;color:darkred;">.....</i> Extreme<br>
<i style="background:red;color:red;">.....</i> Very High<br>
<i style="background:orange;color:orange;">.....</i> High<br>
<i style="background:yellow;color:yellow;">.....</i> Moderate<br>
<i style="background:lightblue;color:lightblue;">.....</i> Low<br>
<i style="background:blue;color:blue;">.....</i> Very Low
</div>
"""

m.get_root().html.add_child(
    folium.Element(legend_html)
)

# ------------------------------------------------
# MAP COLUMN
# ------------------------------------------------
with col2:

    st.subheader("Flood Hazard Map")

    # MAP DISPLAYED ONLY ONCE
    st_folium(
        m,
        width=900,
        height=420,
        returned_objects=[]
    )

# ------------------------------------------------
# LIVE DATA LOOP
# ------------------------------------------------
for i in range(len(df)):

    level = float(
        df.iloc[i]["Calibrated"]
    )

    # --------------------------------------------
    # UPDATE GRAPH
    # --------------------------------------------
    chart.add_rows(
        pd.DataFrame(
            {"Calibrated": [level]}
        )
    )

    # --------------------------------------------
    # ALERTS
    # --------------------------------------------
    with alert_placeholder.container():

        if level > 3.4:

            st.error(
                f"EXTREME FLOOD RISK: {level:.2f} m"
            )

        elif level > 3.2:

            st.warning(
                f"MODERATE FLOOD RISK: {level:.2f} m"
            )

        else:

            st.success(
                f"LOW FLOOD RISK: {level:.2f} m"
            )

    # --------------------------------------------
    # STATUS PANEL
    # --------------------------------------------
    with status_placeholder.container():

        st.subheader(
            "Current Flood Status"
        )

        if level > 3.4:

            st.markdown("""
            ### 🔴 Extreme Flood Conditions
            - Extreme hazard zones activated
            - Critical infrastructure risk
            - Immediate response required
            """)

        elif level > 3.2:

            st.markdown("""
            ### 🟠 Moderate Flood Conditions
            - High hazard zones increasing
            - Localized infrastructure impacts
            """)

        else:

            st.markdown("""
            ### 🔵 Low Flood Conditions
            - Flooding within manageable levels
            """)

    # --------------------------------------------
    # STREAM SPEED
    # --------------------------------------------
    time.sleep(1)