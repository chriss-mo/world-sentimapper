import streamlit as st
import pandas as pd
import sqlite3
import json
import random
import pydeck as pdk

# 1. Expanded dictionary of country coordinates
#    (For demonstration, includes some major countries. Add more as needed.)
country_coords = {
    # North America
    "United States": {"lat": 37.0902, "lon": -95.7129},
    "Canada": {"lat": 56.1304, "lon": -106.3468},
    "Mexico": {"lat": 23.6345, "lon": -102.5528},

    # Central America & Caribbean
    "Guatemala": {"lat": 15.7835, "lon": -90.2308},
    "Cuba": {"lat": 21.5218, "lon": -77.7812},
    "Haiti": {"lat": 18.9712, "lon": -72.2852},
    "Dominican Republic": {"lat": 18.7357, "lon": -70.1627},
    "Costa Rica": {"lat": 9.7489, "lon": -83.7534},
    "Panama": {"lat": 8.5379, "lon": -80.7821},

    # South America
    "Brazil": {"lat": -14.2350, "lon": -51.9253},
    "Argentina": {"lat": -38.4161, "lon": -63.6167},
    "Chile": {"lat": -35.6751, "lon": -71.5430},
    "Peru": {"lat": -9.1900, "lon": -75.0152},
    "Colombia": {"lat": 4.5709, "lon": -74.2973},
    "Ecuador": {"lat": -1.8312, "lon": -78.1834},
    "Venezuela": {"lat": 6.4238, "lon": -66.5897},
    "Paraguay": {"lat": -23.4425, "lon": -58.4438},
    "Uruguay": {"lat": -32.5228, "lon": -55.7658},
    "Bolivia": {"lat": -16.2902, "lon": -63.5887},

    # Europe
    "United Kingdom": {"lat": 55.3781, "lon": -3.4360},
    "France": {"lat": 46.2276, "lon": 2.2137},
    "Germany": {"lat": 51.1657, "lon": 10.4515},
    "Spain": {"lat": 40.4637, "lon": -3.7492},
    "Italy": {"lat": 41.8719, "lon": 12.5674},
    "Netherlands": {"lat": 52.1326, "lon": 5.2913},
    "Belgium": {"lat": 50.8503, "lon": 4.3517},
    "Switzerland": {"lat": 46.8182, "lon": 8.2275},
    "Austria": {"lat": 47.5162, "lon": 14.5501},
    "Sweden": {"lat": 60.1282, "lon": 18.6435},
    "Norway": {"lat": 60.4720, "lon": 8.4689},
    "Denmark": {"lat": 56.2639, "lon": 9.5018},
    "Finland": {"lat": 61.9241, "lon": 25.7482},
    "Poland": {"lat": 51.9194, "lon": 19.1451},
    "Czech Republic": {"lat": 49.8175, "lon": 15.4730},
    "Hungary": {"lat": 47.1625, "lon": 19.5033},
    "Greece": {"lat": 39.0742, "lon": 21.8243},
    "Portugal": {"lat": 39.3999, "lon": -8.2245},
    "Ireland": {"lat": 53.1424, "lon": -7.6921},
    "Romania": {"lat": 45.9432, "lon": 24.9668},
    "Ukraine": {"lat": 48.3794, "lon": 31.1656},
    "Russia": {"lat": 61.5240, "lon": 105.3188},
    "Serbia": {"lat": 44.0165, "lon": 21.0059},
    "Croatia": {"lat": 45.1000, "lon": 15.2000},

    # Middle East
    "Turkey": {"lat": 38.9637, "lon": 35.2433},
    "Saudi Arabia": {"lat": 23.8859, "lon": 45.0792},
    "United Arab Emirates": {"lat": 23.4241, "lon": 53.8478},
    "Israel": {"lat": 31.0461, "lon": 34.8516},
    "Iran": {"lat": 32.4279, "lon": 53.6880},
    "Iraq": {"lat": 33.2232, "lon": 43.6793},
    "Syria": {"lat": 34.8021, "lon": 38.9968},
    "Lebanon": {"lat": 33.8547, "lon": 35.8623},

    # Africa
    "Egypt": {"lat": 26.8206, "lon": 30.8025},
    "South Africa": {"lat": -30.5595, "lon": 22.9375},
    "Nigeria": {"lat": 9.0820, "lon": 8.6753},
    "Kenya": {"lat": -0.0236, "lon": 37.9062},
    "Morocco": {"lat": 31.7917, "lon": -7.0926},
    "Ghana": {"lat": 7.9465, "lon": -1.0232},
    "Algeria": {"lat": 28.0339, "lon": 1.6596},
    "Ethiopia": {"lat": 9.1450, "lon": 40.4897},
    "Uganda": {"lat": 1.3733, "lon": 32.2903},
    "Tanzania": {"lat": -6.3690, "lon": 34.8888},
    "Sudan": {"lat": 12.8628, "lon": 30.2176},
    "Angola": {"lat": -11.2027, "lon": 17.8739},

    # Asia
    "India": {"lat": 20.5937, "lon": 78.9629},
    "China": {"lat": 35.8617, "lon": 104.1954},
    "Japan": {"lat": 36.2048, "lon": 138.2529},
    "South Korea": {"lat": 35.9078, "lon": 127.7669},
    "North Korea": {"lat": 40.3399, "lon": 127.5101},
    "Pakistan": {"lat": 30.3753, "lon": 69.3451},
    "Bangladesh": {"lat": 23.6850, "lon": 90.3563},
    "Indonesia": {"lat": -0.7893, "lon": 113.9213},
    "Vietnam": {"lat": 14.0583, "lon": 108.2772},
    "Thailand": {"lat": 15.8700, "lon": 100.9925},
    "Philippines": {"lat": 12.8797, "lon": 121.7740},

    # Oceania
    "Australia": {"lat": -25.2744, "lon": 133.7751},
    "New Zealand": {"lat": -40.9006, "lon": 174.8860},
    "Fiji": {"lat": -17.7134, "lon": 178.0650},
    "Papua New Guinea": {"lat": -6.3149, "lon": 143.9555},
}


# 2. Jitter function to spread out points in the same country
def jitter_coords(lat, lon, offset=0.5):
    """
    offset in degrees; larger offset = more spread.
    For large countries, you can use a bigger offset.
    """
    lat += random.uniform(-offset, offset)
    lon += random.uniform(-offset, offset)
    return lat, lon

# 3. Define colors for sentiments
sentiment_colors = {
    "Positive": [0, 200, 0, 160],   # green
    "Neutral": [200, 200, 0, 160],  # yellow
    "Negative": [200, 0, 0, 160],   # red
    "Unknown": [128, 128, 128, 160] # gray default
}

def get_data():
    conn = sqlite3.connect("sentiment.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT content, country, sentiment, themes, created_at
        FROM messages
        ORDER BY id DESC
    """)
    rows = cursor.fetchall()
    conn.close()

    data = []
    for row in rows:
        content, country, sentiment, themes_json, created_at = row
        themes = json.loads(themes_json)

        if country in country_coords:
            lat = country_coords[country]["lat"]
            lon = country_coords[country]["lon"]

            # Jitter each article's coordinates so multiple articles
            # in the same country won't perfectly overlap
            lat_jittered, lon_jittered = jitter_coords(lat, lon)

            data.append({
                "content": content,
                "country": country,
                "sentiment": sentiment,
                "themes": themes,
                "created_at": created_at,
                "lat": lat_jittered,
                "lon": lon_jittered
            })
    return data

# 4. Main Streamlit code
data = get_data()
if not data:
    st.write("No data available yet. Waiting for new messages...")
else:
    df = pd.DataFrame(data)
    st.title("🌍 News Sentiment and Geographical Dashboard")

    # Display data in a table
    st.write("### Latest Articles")
    st.dataframe(df[["content", "country", "sentiment", "themes", "created_at"]])

    # Create a column for marker colors based on sentiment
    def get_color(sentiment):
        return sentiment_colors.get(sentiment, [128, 128, 128, 160])  # default gray if not found

    df["color"] = df["sentiment"].apply(get_color)

    # 5. Build a ScatterplotLayer in Pydeck
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=df,
        get_position='[lon, lat]',
        get_color='color',
        get_radius=500000,  # Adjust radius for better visibility
        pickable=True,
    )

    # 6. Set the viewport / initial camera position
    view_state = pdk.ViewState(
        latitude=df["lat"].mean() if not df.empty else 20,
        longitude=df["lon"].mean() if not df.empty else 0,
        zoom=1,
        pitch=0,
    )

    tooltip = {
        "html": "<b>Country:</b> {country} <br/><b>Sentiment:</b> {sentiment}",
        "style": {
            "backgroundColor": "steelblue",
            "color": "white"
        }
    }

    # 7. Render the map using Pydeck
    st.pydeck_chart(
        pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            tooltip=tooltip
        )
    )
