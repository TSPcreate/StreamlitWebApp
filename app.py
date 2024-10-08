import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px


URL = r"https://raw.githubusercontent.com/TSPcreate/StreamlitWebApp/main/Motor_Vehicle_Collisions.csv"


st.title("Motor vehicle Collisions in New York City")
st.markdown("This is a simple Streamlit app to display data on vehicle collisions.")


@st.cache_data
def load_data(nrows): 
    data = pd.read_csv(URL, nrows=nrows, parse_dates=[['CRASH_DATE', 'CRASH_TIME']])
    data.dropna(subset=['LATITUDE', 'LONGITUDE'], inplace=True) 
    lowercase = lambda x: str(x).lower() 
    data.rename(lowercase, axis='columns', inplace=True)
    data.rename(columns={"crash_date_crash_time": "date/time"}, inplace=True)
    return data 

data = load_data(100000)
original_data = data

st.header("Where are most people injured in NYC?")
injured_people = st.slider("Number of persons injured", 0, 19)
st.map(data.query("number_of_persons_injured >= @injured_people")[["latitude", "longitude"]].dropna(how="any"))

st.header("How many collisions occure in a given time of the day") 
hour = st.slider("Hour to look at", 0, 23)
data = data[data['date/time'].dt.hour==hour]

st.markdown("Vehicle Collissions %i:00 and %i:00" % (hour, (hour + 1) % 24))


st.write(pdk.Deck(
    map_style = "mapbox://styles/mapbox/light-v9", 
    initial_view_state={ 
        "latitude": 40.69521517498908, 
        "longitude":-73.89489071462244, 
        "zoom": 10, 
        "pitch": 50,
    },
    layers = [ 
        pdk.Layer( 
            "HexagonLayer", 
            data = data[['date/time', 'latitude', 'longitude']],
            get_position=['longitude', 'latitude'], 
            radius=300, 
            extruded=True, 
            pickable = True, 
            elevation_scale = 4, 
            elevation_range=[0, 3000],
        )
    ]
))
st.subheader("Vehicle Collissions %i:00 and %i:00" % (hour, (hour + 1) % 24))
filtered = data[ 
    (data['date/time'].dt.hour >= hour) & (data['date/time'].dt.hour < (hour + 1))

]
hist = np.histogram(filtered['date/time'].dt.minute, bins=60, range=(0,60))[0]
chart_data = pd.DataFrame({'minute': range(60), 'crashes':hist})
fig = px.bar(chart_data, x='minute', y='crashes', hover_data=['minute', 'crashes'], height=400)
st.write(fig)

st.header("Top 5 dangerous streets by affected type")
select = st.selectbox('Affected type of people', ['Pedestrians', 'Cyclists', 'Motorists'])

if select == 'Pedestrians': 
    st.write(original_data.query('number_of_pedestrians_injured >= 1')[["on_street_name", "number_of_pedestrians_injured"]].sort_values(by=['number_of_pedestrians_injured'], ascending=False).dropna(how="any")[:5])

elif select == 'Cyclists': 
    st.write(original_data.query('number_of_cyclist_injured >= 1')[['on_street_name', 'number_of_cyclist_injured']].sort_values(by=['number_of_cyclist_injured'], ascending=False).dropna(how="any")[:5])

else: 
    st.write(original_data.query('number_of_motorist_injured >= 1')[['on_street_name', 'number_of_motorist_injured']].sort_values(by=['number_of_motorist_injured'], ascending=False).dropna(how="any")[:5])


if st.checkbox("Show Raw Data", True): 
    st.subheader('Raw Data')
    st.write(data)


