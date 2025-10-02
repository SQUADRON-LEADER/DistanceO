import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import networkx as nx
import heapq
from datetime import datetime
import folium
from streamlit_folium import st_folium
import pydeck as pdk

# Set page configuration
st.set_page_config(
    page_title="Smart Path Finder",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #2c3e50 0%, #34495e 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.3);
        border-left: 4px solid #3498db;
        color: #ecf0f1;
    }
    
    .path-step {
        background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%);
        padding: 0.8rem;
        margin: 0.25rem 0;
        border-radius: 8px;
        border-left: 4px solid #27ae60;
        color: #ffffff;
        font-weight: 500;
    }
    
    .stSelectbox > div > div {
        background: linear-gradient(135deg, #34495e 0%, #2c3e50 100%) !important;
        color: #ecf0f1 !important;
        border: 1px solid #3498db !important;
        border-radius: 8px !important;
    }
    
    /* Main app background */
    .stApp {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        color: #ecf0f1;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
    }
    
    /* Additional CSS for warning suppression and improved iframe handling */
    .stApp > iframe {
        border: none !important;
        background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%) !important;
    }
    
    /* Reduce console warnings from components and improve iframe stability */
    iframe[src*="streamlit_folium"] {
        border: none !important;
        overflow: hidden !important;
        background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%) !important;
        position: relative !important;
        z-index: 1 !important;
    }
    
    /* Improve iframe container stability */
    .element-container iframe {
        min-height: 500px !important;
        width: 100% !important;
        display: block !important;
    }
    
    /* Prevent iframe from disappearing */
    .stHTML iframe,
    [data-testid="stIFrame"] iframe {
        opacity: 1 !important;
        visibility: visible !important;
        position: relative !important;
    }
    
    /* Improve map container styling */
    .element-container div[data-testid="stPydeckChart"] {
        border-radius: 15px;
        box-shadow: 0 8px 16px rgba(0,0,0,0.4);
        background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
        border: 2px solid #3498db;
    }
    
    /* Custom info box styling */
    .info-box {
        background: linear-gradient(135deg, #34495e 0%, #2c3e50 100%);
        border: 2px solid #3498db;
        border-radius: 10px;
        padding: 15px;
        margin: 15px 0;
        color: #ecf0f1;
        font-weight: 500;
    }
    
    /* Streamlit widgets styling */
    .stButton > button {
        background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 10px 20px;
        font-weight: bold;
        box-shadow: 0 4px 8px rgba(0,0,0,0.3);
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #c0392b 0%, #e74c3c 100%);
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.4);
    }
    
    /* Text and content styling */
    .stMarkdown {
        color: #ecf0f1;
    }
    
    /* Metric containers */
    .metric {
        background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 4px 8px rgba(0,0,0,0.3);
    }
    
    /* Data frames and tables */
    .stDataFrame {
        background: linear-gradient(135deg, #34495e 0%, #2c3e50 100%);
        border-radius: 10px;
        padding: 10px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.3);
        color: #ecf0f1;
    }
    
    /* Additional dark theme improvements */
    .stApp [data-testid="stSidebar"] {
        background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
    }
    
    .stApp [data-testid="stHeader"] {
        background: transparent;
    }
    
    /* Text input and selectbox styling */
    .stTextInput > div > div > input {
        background-color: #34495e;
        color: #ecf0f1;
        border: 1px solid #3498db;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: #34495e;
        color: #ecf0f1;
    }
    
    /* Info/warning/error message styling */
    .stAlert {
        background-color: rgba(52, 73, 94, 0.8);
        color: #ecf0f1;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Enhanced graph with more cities and realistic distances
@st.cache_data
def get_cities_graph():
    return {
        "Mumbai": {"Delhi": 1400, "Bangalore": 980, "Hyderabad": 710, "Chennai": 1330, "Pune": 150, "Ahmedabad": 530, "Surat": 270, "Nagpur": 840},
        "Delhi": {"Mumbai": 1400, "Bangalore": 2150, "Hyderabad": 1580, "Chennai": 2200, "Jaipur": 280, "Lucknow": 550, "Bhopal": 780, "Patna": 1100},
        "Bangalore": {"Mumbai": 980, "Delhi": 2150, "Hyderabad": 570, "Chennai": 350, "Kolkata": 1860, "Pune": 840, "Kochi": 480},
        "Hyderabad": {"Mumbai": 710, "Delhi": 1580, "Bangalore": 570, "Chennai": 630, "Kolkata": 1490, "Nagpur": 500, "Pune": 560},
        "Chennai": {"Mumbai": 1330, "Delhi": 2200, "Bangalore": 350, "Hyderabad": 630, "Kolkata": 1660, "Kochi": 680, "Coimbatore": 500},
        "Kolkata": {"Bangalore": 1860, "Hyderabad": 1490, "Chennai": 1660, "Lucknow": 1000, "Patna": 580, "Bhubaneswar": 440},
        "Pune": {"Mumbai": 150, "Bangalore": 840, "Hyderabad": 560, "Nashik": 210, "Solapur": 250},
        "Jaipur": {"Delhi": 280, "Lucknow": 600, "Ahmedabad": 660, "Jodhpur": 340, "Udaipur": 420},
        "Ahmedabad": {"Jaipur": 660, "Mumbai": 530, "Surat": 260, "Indore": 400, "Vadodara": 110},
        "Lucknow": {"Delhi": 550, "Kolkata": 1000, "Jaipur": 600, "Kanpur": 80, "Varanasi": 320, "Bhopal": 580, "Patna": 610},
        "Surat": {"Mumbai": 270, "Ahmedabad": 260, "Vadodara": 150, "Nashik": 350},
        "Nagpur": {"Mumbai": 840, "Hyderabad": 500, "Bhopal": 350, "Raipur": 290, "Jabalpur": 270},
        "Bhopal": {"Nagpur": 350, "Delhi": 780, "Lucknow": 580, "Indore": 190, "Jabalpur": 160},
        "Indore": {"Bhopal": 190, "Ahmedabad": 400, "Jaipur": 520, "Ujjain": 55},
        "Patna": {"Lucknow": 610, "Kolkata": 580, "Delhi": 1100, "Ranchi": 330, "Gaya": 100},
        "Kochi": {"Bangalore": 480, "Chennai": 680, "Thiruvananthapuram": 220, "Coimbatore": 190},
        "Vadodara": {"Ahmedabad": 110, "Surat": 150, "Mumbai": 420},
        "Nashik": {"Pune": 210, "Mumbai": 180, "Surat": 350, "Aurangabad": 120},
        "Kanpur": {"Lucknow": 80, "Delhi": 470, "Allahabad": 120},
        "Coimbatore": {"Chennai": 500, "Kochi": 190, "Bangalore": 370, "Madurai": 210},
        "Jodhpur": {"Jaipur": 340, "Ahmedabad": 490, "Udaipur": 250},
        "Udaipur": {"Jaipur": 420, "Jodhpur": 250, "Ahmedabad": 260},
        "Thiruvananthapuram": {"Kochi": 220, "Madurai": 300},
        "Madurai": {"Chennai": 460, "Coimbatore": 210, "Thiruvananthapuram": 300},
        "Ranchi": {"Patna": 330, "Kolkata": 420, "Bhubaneswar": 390},
        "Bhubaneswar": {"Kolkata": 440, "Ranchi": 390, "Visakhapatnam": 440},
        "Visakhapatnam": {"Hyderabad": 620, "Bhubaneswar": 440, "Chennai": 770},
        "Jabalpur": {"Nagpur": 270, "Bhopal": 160, "Allahabad": 420},
        "Allahabad": {"Lucknow": 200, "Kanpur": 120, "Varanasi": 135, "Jabalpur": 420},
        "Varanasi": {"Lucknow": 320, "Patna": 250, "Allahabad": 135},
        "Gaya": {"Patna": 100, "Varanasi": 240},
        "Raipur": {"Nagpur": 290, "Bhubaneswar": 530},
        "Ujjain": {"Indore": 55, "Bhopal": 180},
        "Solapur": {"Pune": 250, "Hyderabad": 300},
        "Aurangabad": {"Nashik": 120, "Mumbai": 340, "Hyderabad": 470}
    }

# City coordinates for visualization
@st.cache_data
def get_city_coordinates():
    return {
        "Mumbai": [19.0760, 72.8777], "Delhi": [28.7041, 77.1025], "Bangalore": [12.9716, 77.5946],
        "Hyderabad": [17.3850, 78.4867], "Chennai": [13.0827, 80.2707], "Kolkata": [22.5726, 88.3639],
        "Pune": [18.5204, 73.8567], "Jaipur": [26.9124, 75.7873], "Ahmedabad": [23.0225, 72.5714],
        "Lucknow": [26.8467, 80.9462], "Surat": [21.1702, 72.8311], "Nagpur": [21.1458, 79.0882],
        "Bhopal": [23.2599, 77.4126], "Indore": [22.7196, 75.8577], "Patna": [25.5941, 85.1376],
        "Kochi": [9.9312, 76.2673], "Vadodara": [22.3072, 73.1812], "Nashik": [19.9975, 73.7898],
        "Kanpur": [26.4499, 80.3319], "Coimbatore": [11.0168, 76.9558], "Jodhpur": [26.2389, 73.0243],
        "Udaipur": [24.5854, 73.7125], "Thiruvananthapuram": [8.5241, 76.9366], "Madurai": [9.9252, 78.1198],
        "Ranchi": [23.3441, 85.3096], "Bhubaneswar": [20.2961, 85.8245], "Visakhapatnam": [17.6868, 83.2185],
        "Jabalpur": [23.1815, 79.9864], "Allahabad": [25.4358, 81.8463], "Varanasi": [25.3176, 82.9739],
        "Gaya": [24.7914, 85.0002], "Raipur": [21.2514, 81.6296], "Ujjain": [23.1793, 75.7849],
        "Solapur": [17.6599, 75.9064], "Aurangabad": [19.8762, 75.3433]
    }

# Dijkstra's algorithm implementation
def dijkstra(graph, start, end):
    distances = {node: float('inf') for node in graph}
    previous = {node: None for node in graph}
    distances[start] = 0
    queue = [(0, start)]
    visited = set()

    while queue:
        current_distance, current_node = heapq.heappop(queue)
        
        if current_node in visited:
            continue
            
        visited.add(current_node)
        
        if current_node == end:
            break

        for neighbor, weight in graph[current_node].items():
            distance = current_distance + weight
            
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                previous[neighbor] = current_node
                heapq.heappush(queue, (distance, neighbor))

    # Reconstruct path
    path = []
    total_distance = distances[end]
    current = end
    
    while current is not None:
        path.insert(0, current)
        current = previous[current]
    
    return path if distances[end] != float('inf') else [], total_distance

# A* algorithm implementation
def heuristic(city1, city2, coordinates):
    lat1, lon1 = coordinates[city1]
    lat2, lon2 = coordinates[city2]
    # Simplified distance calculation
    return ((lat1 - lat2) ** 2 + (lon1 - lon2) ** 2) ** 0.5 * 100

def a_star(graph, start, end, coordinates):
    open_set = [(0, start)]
    came_from = {}
    g_score = {node: float('inf') for node in graph}
    g_score[start] = 0
    f_score = {node: float('inf') for node in graph}
    f_score[start] = heuristic(start, end, coordinates)
    
    while open_set:
        current = heapq.heappop(open_set)[1]
        
        if current == end:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            path.reverse()
            return path, g_score[end]
        
        for neighbor, weight in graph[current].items():
            tentative_g_score = g_score[current] + weight
            
            if tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = g_score[neighbor] + heuristic(neighbor, end, coordinates)
                heapq.heappush(open_set, (f_score[neighbor], neighbor))
    
    return [], float('inf')

# Create interactive Leaflet map visualization
def create_interactive_leaflet_map(path, graph, coordinates, all_cities=None):
    """Create an interactive Folium/Leaflet map with the path visualization"""
    try:
        # Validate inputs
        if not path or len(path) == 0:
            st.warning("No path provided for map visualization")
            return None
            
        if not coordinates:
            st.error("No coordinates data available")
            return None
            
        if all_cities is None:
            all_cities = path  # Use path cities if all_cities not provided
        
        # Create a folium map centered on India
        india_center = [20.5937, 78.9629]
        
        # Initialize map with error handling
        m = folium.Map(
            location=india_center,
            zoom_start=5,
            tiles='OpenStreetMap'
        )
        
        # Add alternative tile layers safely
        try:
            folium.TileLayer('CartoDB positron', name='Light Map', overlay=False, control=True).add_to(m)
            folium.TileLayer('CartoDB dark_matter', name='Dark Map', overlay=False, control=True).add_to(m)
        except Exception as tile_error:
            # Continue without alternative tiles if they fail
            pass
        
        # Validate that we have coordinates for path cities
        valid_path_cities = [city for city in path if city in coordinates]
        if len(valid_path_cities) < len(path):
            missing_cities = [city for city in path if city not in coordinates]
            st.warning(f"Missing coordinates for cities: {missing_cities}")
        
        if len(valid_path_cities) == 0:
            st.error("No valid coordinates found for any city in the path")
            return None
        
        # Add all cities as markers with error handling
        markers_added = 0
        for city in all_cities:
            if city in coordinates:
                try:
                    lat, lon = coordinates[city]
                    
                    # Validate coordinates
                    if not isinstance(lat, (int, float)) or not isinstance(lon, (int, float)):
                        st.warning(f"Invalid coordinates for {city}: {lat}, {lon}")
                        continue
                        
                    # Determine marker color based on path
                    if path and city in path:
                        if city == path[0]:
                            color = 'green'
                            icon = 'play'
                            popup_text = f"🏠 START: {city}"
                        elif city == path[-1]:
                            color = 'red'
                            icon = 'stop'
                            popup_text = f"🎯 END: {city}"
                        else:
                            color = 'orange'
                            icon = 'info-sign'
                            popup_text = f"📍 STOP: {city}"
                    else:
                        color = 'blue'
                        icon = 'info-sign'
                        popup_text = f"🏙️ {city}"
                    
                    # Create marker with improved styling
                    folium.Marker(
                        [lat, lon],
                        popup=folium.Popup(popup_text, max_width=200),
                        tooltip=f"{city} (Click for details)",
                        icon=folium.Icon(color=color, icon=icon, prefix='glyphicon')
                    ).add_to(m)
                    markers_added += 1
                    
                except Exception as marker_error:
                    # Continue without this marker if it fails
                    continue
        
        # Add path if provided with enhanced error handling
        if path and len(path) > 1:
            try:
                # Create the route line
                route_coords = []
                for city in path:
                    if city in coordinates:
                        lat, lon = coordinates[city]
                        route_coords.append([lat, lon])
                    else:
                        st.warning(f"Missing coordinates for city in path: {city}")
                
                if len(route_coords) > 1:
                    # Add the main route line
                    folium.PolyLine(
                        route_coords,
                        color='red',
                        weight=5,
                        opacity=0.8,
                        popup=f"Route: {' → '.join(path)}",
                        tooltip="Click for route details"
                    ).add_to(m)
                    
                    # Add step markers with numbers
                    for i, city in enumerate(path):
                        if city in coordinates:
                            try:
                                lat, lon = coordinates[city]
                                
                                # Add numbered circle marker
                                folium.CircleMarker(
                                    [lat, lon],
                                    radius=15,
                                    popup=f"Step {i+1}: {city}",
                                    color='white',
                                    fill=True,
                                    fillColor='red',
                                    fillOpacity=0.8,
                                    weight=3
                                ).add_to(m)
                                
                                # Add step number with improved styling
                                folium.Marker(
                                    [lat, lon],
                                    icon=folium.DivIcon(
                                        html=f"""<div style="
                                            font-size: 14px; 
                                            font-weight: bold; 
                                            color: white; 
                                            text-align: center;
                                            width: 25px;
                                            height: 25px;
                                            line-height: 25px;
                                            background-color: red;
                                            border-radius: 50%;
                                            border: 2px solid white;
                                            box-shadow: 0 2px 4px rgba(0,0,0,0.3);
                                        ">{i+1}</div>""",
                                        icon_size=(25, 25),
                                        icon_anchor=(12, 12)
                                    )
                                ).add_to(m)
                            except Exception as step_error:
                                # Continue without this step marker if it fails
                                continue
                else:
                    # Continue without route line if not enough coordinates
                    pass
                    
            except Exception as path_error:
                # Continue without path visualization if it fails
                pass
        else:
            # Continue without path if not provided
            pass
        
        # Add layer control safely
        try:
            folium.LayerControl().add_to(m)
        except Exception as layer_error:
            # Continue without layer control if it fails
            pass
        
        # Add a legend with dark theme styling
        legend_html = '''
        <div style="position: fixed; 
                    bottom: 50px; left: 50px; width: 240px; height: 160px; 
                    background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%); 
                    border: 2px solid #3498db; 
                    border-radius: 15px;
                    z-index: 9999; 
                    font-size: 14px; 
                    padding: 20px;
                    box-shadow: 0 8px 16px rgba(0,0,0,0.4);">
        <h4 style="margin-top: 0; margin-bottom: 15px; color: #ecf0f1; text-align: center; font-weight: bold;">🗺️ Map Legend</h4>
        <p style="margin: 8px 0; color: #ecf0f1;"><span style="color: #27ae60; font-size: 16px;">🟢</span> <strong>Start City</strong></p>
        <p style="margin: 8px 0; color: #ecf0f1;"><span style="color: #e74c3c; font-size: 16px;">🔴</span> <strong>End City</strong></p>
        <p style="margin: 8px 0; color: #ecf0f1;"><span style="color: #f39c12; font-size: 16px;">🟠</span> <strong>Route Stop</strong></p>
        <p style="margin: 8px 0; color: #ecf0f1;"><span style="color: #3498db; font-size: 16px;">🔵</span> <strong>Other Cities</strong></p>
        <p style="margin: 8px 0; color: #ecf0f1;"><span style="color: #e74c3c; font-size: 18px;">━━━</span> <strong>Path Route</strong></p>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(legend_html))
        
        return m
        
    except Exception as e:
        st.error(f"Error creating Leaflet map: {str(e)}")
        return None

# Create enhanced coordinate visualization as backup
def create_enhanced_coordinate_visualization(path, graph, coordinates, all_cities=None):
    if all_cities is None:
        all_cities = list(coordinates.keys())
    
    # Create a more map-like visualization using pydeck
    try:
        # Prepare city data
        city_data = []
        for city in all_cities:
            if city in coordinates:
                lat, lon = coordinates[city]
                if path and city in path:
                    if city == path[0]:
                        color = [0, 255, 0, 200]  # Green for start
                        size = 100
                    elif city == path[-1]:
                        color = [255, 0, 0, 200]  # Red for end
                        size = 100
                    else:
                        color = [255, 165, 0, 200]  # Orange for path
                        size = 80
                else:
                    color = [173, 216, 230, 160]  # Light blue for others
                    size = 60
                
                city_data.append({
                    'lat': lat,
                    'lon': lon,
                    'name': city,
                    'color': color,
                    'size': size
                })
        
        # Create the pydeck map
        view_state = pdk.ViewState(
            latitude=20.5937,
            longitude=78.9629,
            zoom=5,
            pitch=0
        )
        
        # City markers layer
        city_layer = pdk.Layer(
            'ScatterplotLayer',
            data=city_data,
            get_position=['lon', 'lat'],
            get_fill_color='color',  # Updated from get_color
            get_radius='size',
            radius_scale=100,
            pickable=True,
            filled=True,
            stroked=True,
            get_line_color=[255, 255, 255, 255],
            get_line_width=2
        )
        
        layers = [city_layer]
        
        # Add path layer if available
        if path and len(path) > 1:
            path_data = []
            for i in range(len(path) - 1):
                if path[i] in coordinates and path[i+1] in coordinates:
                    start_lat, start_lon = coordinates[path[i]]
                    end_lat, end_lon = coordinates[path[i+1]]
                    path_data.append({
                        'start': [start_lon, start_lat],
                        'end': [end_lon, end_lat]
                    })
            
            path_layer = pdk.Layer(
                'LineLayer',
                data=path_data,
                get_source_position='start',
                get_target_position='end',
                get_color=[255, 0, 0, 200],
                get_width=3,
                width_scale=1000
            )
            layers.append(path_layer)
        
        # Create the deck
        deck = pdk.Deck(
            map_style='mapbox://styles/mapbox/light-v9',
            initial_view_state=view_state,
            layers=layers,
            tooltip={'text': '{name}'}
        )
        
        return deck
        
    except Exception as e:
        # Fallback to simple plotly if pydeck fails
        return create_simple_coordinate_plot(path, graph, coordinates, all_cities)

# Simple coordinate plot as final fallback
def create_simple_coordinate_plot(path, graph, coordinates, all_cities=None):
    if all_cities is None:
        all_cities = list(coordinates.keys())
    
    fig = go.Figure()
    
    # Add all cities as scatter points
    city_lats = [coordinates[city][0] for city in all_cities]
    city_lons = [coordinates[city][1] for city in all_cities]
    
    fig.add_trace(go.Scatter(
        x=city_lons,
        y=city_lats,
        mode='markers+text',
        marker=dict(size=8, color='lightblue', opacity=0.7),
        text=all_cities,
        textposition="top center",
        name="All Cities",
        hovertemplate="<b>%{text}</b><br>Lat: %{y:.2f}<br>Lon: %{x:.2f}<extra></extra>"
    ))
    
    # Add path if provided
    if path and len(path) > 1:
        path_lats = [coordinates[city][0] for city in path]
        path_lons = [coordinates[city][1] for city in path]
        
        # Add path line
        fig.add_trace(go.Scatter(
            x=path_lons,
            y=path_lats,
            mode='lines+markers',
            line=dict(width=4, color='red'),
            marker=dict(size=12, color='red'),
            name="Shortest Path",
            text=path,
            hovertemplate="<b>%{text}</b><br>Step %{pointNumber}<extra></extra>"
        ))
        
        # Highlight start and end points
        fig.add_trace(go.Scatter(
            x=[path_lons[0], path_lons[-1]],
            y=[path_lats[0], path_lats[-1]],
            mode='markers+text',
            marker=dict(size=15, color=['green', 'red'], symbol=['circle', 'square']),
            text=[f"START: {path[0]}", f"END: {path[-1]}"],
            textposition="top center",
            name="Start/End Points",
            hovertemplate="<b>%{text}</b><extra></extra>"
        ))
    
    # Update layout
    fig.update_layout(
        title="Interactive Route Map",
        xaxis_title="Longitude",
        yaxis_title="Latitude",
        height=600,
        margin=dict(l=0, r=0, t=40, b=0),
        showlegend=True,
        hovermode='closest',
        plot_bgcolor='#f0f8ff',
        yaxis=dict(scaleanchor="x", scaleratio=1)
    )
    
    return fig

# Create simple route table
def create_route_table(path, graph):
    if not path or len(path) < 2:
        return None
    
    route_data = []
    total_distance = 0
    
    for i in range(len(path)):
        if i == 0:
            route_data.append({
                "Step": 1,
                "From": "START",
                "To": path[i],
                "Distance (km)": 0,
                "Cumulative (km)": 0
            })
        else:
            distance = graph[path[i-1]][path[i]] if path[i] in graph[path[i-1]] else 0
            total_distance += distance
            route_data.append({
                "Step": i + 1,
                "From": path[i-1],
                "To": path[i],
                "Distance (km)": distance,
                "Cumulative (km)": total_distance
            })
    
    return pd.DataFrame(route_data)

# Create network graph visualization
def create_network_graph(graph, path=None):
    G = nx.Graph()
    coordinates = get_city_coordinates()
    
    # Add nodes
    for city in graph:
        if city in coordinates:
            G.add_node(city, pos=coordinates[city])
    
    # Add edges
    for city, connections in graph.items():
        for connected_city, distance in connections.items():
            if city in coordinates and connected_city in coordinates:
                G.add_edge(city, connected_city, weight=distance)
    
    # Get positions
    pos = nx.get_node_attributes(G, 'pos')
    
    # Create edge traces
    edge_x = []
    edge_y = []
    
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
    
    edge_trace = go.Scatter(x=edge_x, y=edge_y,
                           line=dict(width=1, color='#888'),
                           hoverinfo='none',
                           mode='lines')
    
    # Create node traces
    node_x = []
    node_y = []
    node_text = []
    node_colors = []
    
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_text.append(node)
        
        # Color nodes based on path
        if path and node in path:
            if node == path[0]:
                node_colors.append('green')
            elif node == path[-1]:
                node_colors.append('red')
            else:
                node_colors.append('orange')
        else:
            node_colors.append('lightblue')
    
    node_trace = go.Scatter(x=node_x, y=node_y,
                           mode='markers+text',
                           text=node_text,
                           textposition="middle center",
                           hoverinfo='text',
                           marker=dict(size=15, color=node_colors, line=dict(width=2)))
    
    # Create figure
    fig = go.Figure(data=[edge_trace, node_trace],
                   layout=go.Layout(
                       title=dict(
                           text='City Network Graph',
                           font=dict(size=16)
                       ),
                       showlegend=False,
                       hovermode='closest',
                       margin=dict(b=20,l=5,r=5,t=40),
                       annotations=[ dict(
                           text="Node colors: Green=Start, Red=End, Orange=Path, Blue=Other",
                           showarrow=False,
                           xref="paper", yref="paper",
                           x=0.005, y=-0.002,
                           xanchor="left", yanchor="bottom",
                           font=dict(color="#888", size=12)
                       )],
                       xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                       yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                       height=500))
    
    return fig

# Main application
def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🗺️ Smart Path Finder</h1>
        <p>Find the shortest route between Indian cities using advanced algorithms</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'search_history' not in st.session_state:
        st.session_state.search_history = []
    
    graph = get_cities_graph()
    coordinates = get_city_coordinates()
    cities = sorted(list(graph.keys()))
    
    # Sidebar
    with st.sidebar:
        st.header("🚀 Path Finding Options")
        
        # Algorithm selection
        algorithm = st.selectbox(
            "Choose Algorithm:",
            ["Dijkstra's Algorithm", "A* Algorithm"],
            help="Dijkstra finds the absolute shortest path. A* is faster but uses heuristics."
        )
        
        # City selection
        col1, col2 = st.columns(2)
        with col1:
            start_city = st.selectbox("🏠 Start City:", cities)
        with col2:
            end_city = st.selectbox("🎯 End City:", cities)
        
        # Advanced options
        st.subheader("⚙️ Advanced Options")
        show_all_cities = st.checkbox("Show all cities on map", value=True)
        show_network_graph = st.checkbox("Show network graph", value=False)
        
        # Performance settings
        st.subheader("🔧 Performance Settings")
        suppress_warnings = st.checkbox("Minimize browser warnings", value=True, 
                                       help="Optimizes settings to reduce console warnings")
        enable_fallbacks = st.checkbox("Enable automatic fallbacks", value=True,
                                     help="Automatically switch to backup visualization if primary fails")
        
        # Add JavaScript to suppress common warnings when option is enabled
        if suppress_warnings:
            st.markdown("""
            <script>
            // More comprehensive warning suppression
            (function() {
                // Suppress console warnings
                if (typeof console !== 'undefined') {
                    const originalWarn = console.warn;
                    const originalError = console.error;
                    
                    console.warn = function(...args) {
                        const message = args.join(' ');
                        // Filter out known harmless warnings
                        if (message.includes('Unrecognized feature:') || 
                            message.includes('browser is not defined') ||
                            message.includes('iframe') ||
                            message.includes('sandbox') ||
                            message.includes('ambient-light-sensor') ||
                            message.includes('battery') ||
                            message.includes('document-domain') ||
                            message.includes('layout-animations') ||
                            message.includes('legacy-image-formats') ||
                            message.includes('oversized-images') ||
                            message.includes('vr') ||
                            message.includes('wake-lock')) {
                            return; // Don't show these warnings
                        }
                        originalWarn.apply(console, args);
                    };
                    
                    console.error = function(...args) {
                        const message = args.join(' ');
                        // Filter out iframe-related errors
                        if (message.includes('escape its sandboxing') ||
                            message.includes('streamlit_folium')) {
                            return; // Don't show these errors
                        }
                        originalError.apply(console, args);
                    };
                }
                
                // Suppress iframe warnings at document level
                document.addEventListener('DOMContentLoaded', function() {
                    const iframes = document.querySelectorAll('iframe');
                    iframes.forEach(iframe => {
                        iframe.setAttribute('sandbox', 'allow-scripts allow-same-origin allow-forms');
                    });
                });
            })();
            </script>
            """, unsafe_allow_html=True)
        
        # Map visualization options
        st.subheader("🗺️ Map Type")
        
        # Add warning about browser console messages
        with st.expander("ℹ️ About Browser Console Messages"):
            st.write("""
            **Note:** You might see browser console warnings when using this app. These are harmless and don't affect functionality:
            - Feature policy warnings are from Streamlit's iframe handling
            - Browser extension conflicts (if you have ad blockers, etc.)
            - Component deprecation warnings (we're using the latest versions)
            
            **Recommendation:** Use 'Streamlit Native Map' for the cleanest experience with minimal warnings.
            """)
        
        map_type = st.selectbox(
            "Choose Map Visualization:",
            ["Streamlit Native Map", "Enhanced 3D Map", "Simple Coordinate Plot", "Interactive Leaflet Map"],
            help="Streamlit Native Map provides the cleanest experience with minimal browser warnings."
        )
        
        # Search button
        search_button = st.button("🔍 Find Shortest Path", type="primary", use_container_width=True)
    
    # Main content
    if search_button and start_city != end_city:
        # Initialize session state for map persistence
        if 'map_data' not in st.session_state:
            st.session_state.map_data = {}
        
        with st.spinner("Calculating shortest path..."):
            # Calculate path based on selected algorithm
            if algorithm == "Dijkstra's Algorithm":
                path, total_distance = dijkstra(graph, start_city, end_city)
            else:
                path, total_distance = a_star(graph, start_city, end_city, coordinates)
            
            if path:
                # Add to search history
                search_entry = {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "start": start_city,
                    "end": end_city,
                    "algorithm": algorithm,
                    "distance": total_distance,
                    "path": path
                }
                st.session_state.search_history.insert(0, search_entry)
                if len(st.session_state.search_history) > 10:
                    st.session_state.search_history.pop()
                
                # Display results
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown("""
                    <div class="metric-card">
                        <h3>📍 Route Information</h3>
                        <p><strong>From:</strong> {}</p>
                        <p><strong>To:</strong> {}</p>
                        <p><strong>Algorithm:</strong> {}</p>
                    </div>
                    """.format(start_city, end_city, algorithm), unsafe_allow_html=True)
                
                with col2:
                    st.markdown("""
                    <div class="metric-card">
                        <h3>📏 Distance</h3>
                        <h2 style="color: #667eea;">{:.0f} km</h2>
                        <p>{} stops</p>
                    </div>
                    """.format(total_distance, len(path) - 1), unsafe_allow_html=True)
                
                with col3:
                    estimated_time = total_distance / 60  # Assuming 60 km/h average speed
                    st.markdown("""
                    <div class="metric-card">
                        <h3>⏱️ Estimated Time</h3>
                        <h2 style="color: #28a745;">{:.1f} hours</h2>
                        <p>At 60 km/h avg</p>
                    </div>
                    """.format(estimated_time), unsafe_allow_html=True)
                
                # Path details
                st.subheader("🛣️ Route Details")
                
                path_col1, path_col2 = st.columns([2, 1])
                
                with path_col1:
                    st.write("**Step-by-step route:**")
                    for i, city in enumerate(path):
                        if i == 0:
                            st.markdown(f"""
                            <div class="path-step">
                                🏠 <strong>Start:</strong> {city}
                            </div>
                            """, unsafe_allow_html=True)
                        elif i == len(path) - 1:
                            distance_to_prev = graph[path[i-1]][city] if city in graph[path[i-1]] else 0
                            st.markdown(f"""
                            <div class="path-step">
                                🎯 <strong>Destination:</strong> {city} ({distance_to_prev} km from {path[i-1]})
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            distance_to_prev = graph[path[i-1]][city] if city in graph[path[i-1]] else 0
                            st.markdown(f"""
                            <div class="path-step">
                                📍 <strong>Stop {i}:</strong> {city} ({distance_to_prev} km from {path[i-1]})
                            </div>
                            """, unsafe_allow_html=True)
                
                with path_col2:
                    # Create a simple distance chart
                    if len(path) > 1:
                        distances = []
                        labels = []
                        for i in range(1, len(path)):
                            dist = graph[path[i-1]][path[i]] if path[i] in graph[path[i-1]] else 0
                            distances.append(dist)
                            labels.append(f"{path[i-1]}\n→ {path[i]}")
                        
                        fig_bar = px.bar(
                            x=labels,
                            y=distances,
                            title="Segment Distances",
                            labels={'x': 'Route Segments', 'y': 'Distance (km)'}
                        )
                        fig_bar.update_layout(height=300, showlegend=False)
                        st.plotly_chart(fig_bar, use_container_width=True)
                
                # Map visualization
                st.subheader("🗺️ Interactive Route Map")
                cities_to_show = list(coordinates.keys()) if show_all_cities else path
                
                if map_type == "Interactive Leaflet Map":
                    # Create the leaflet map without fallbacks
                    if not suppress_warnings:
                        st.info("🌍 Loading interactive Leaflet map with actual Indian geography...")
                    
                    # Create the leaflet map
                    leaflet_map = create_interactive_leaflet_map(path, graph, coordinates, cities_to_show)
                    
                    if leaflet_map is not None:
                        # Store the map in session state to prevent disappearing
                        map_key = f"map_{start_city}_{end_city}_{len(path)}"
                        st.session_state.map_data[map_key] = leaflet_map
                        
                        # Use a stable container to prevent disappearing
                        map_container = st.container()
                        with map_container:
                            st.subheader("🗺️ Interactive Leaflet Map")
                            
                            # Create a placeholder for the map
                            map_placeholder = st.empty()
                            
                            with map_placeholder.container():
                                # Use streamlit-folium with properly supported parameters
                                try:
                                    map_data = st_folium(
                                        fig=leaflet_map,
                                        key=f"leaflet_map_{start_city}_{end_city}",
                                        width=700,
                                        height=500,
                                        returned_objects=["last_clicked"],
                                        use_container_width=True
                                    )
                                    
                                    st.success("✅ Interactive Leaflet map loaded successfully!")
                                    
                                except Exception as folium_error:
                                    st.error(f"Error displaying Leaflet map: {folium_error}")
                                    st.info("🔄 Try refreshing the page or reselecting the cities.")
                                    
                                    # Show more detailed error info
                                    with st.expander("🔍 Detailed Error Information"):
                                        st.code(str(folium_error))
                                        st.write("**Possible solutions:**")
                                        st.write("- Update streamlit-folium: `pip install --upgrade streamlit-folium`")
                                        st.write("- Check internet connection for map tiles")
                                        st.write("- Try selecting different cities")
                            
                            # Show map interaction info in a separate container
                            interaction_container = st.container()
                            with interaction_container:
                                if 'map_data' in locals() and map_data and map_data.get('last_clicked'):
                                    clicked_data = map_data['last_clicked']
                                    st.info(f"📍 Last clicked: {clicked_data['lat']:.4f}, {clicked_data['lng']:.4f}")
                        
                        # Add map instructions in a collapsible section
                        with st.expander("🗺️ Map Usage Instructions", expanded=False):
                            st.write("""
                            **How to use the Interactive Map:**
                            - 🖱️ **Click and drag** to pan around
                            - 🔍 **Mouse wheel** to zoom in/out
                            - 📍 **Click markers** for city information
                            - 🗂️ **Use layer control** (top right) to switch map styles
                            - 📊 **Legend** (bottom left) explains marker colors
                            
                            **Map Features:**
                            - 🟢 Green: Start city
                            - 🔴 Red: End city  
                            - 🟠 Orange: Route stops
                            - 🔵 Blue: Other cities
                            - ➡️ Red line: Shortest path route
                            
                            **Troubleshooting:**
                            - If map doesn't load: Refresh the page
                            - If map disappears: Reselect cities and search again
                            - Check browser console for specific errors
                            """)
                    else:
                        st.error("❌ Failed to create Interactive Leaflet Map")
                        st.info("""
                        **Possible solutions:**
                        - Check if all cities have valid coordinates
                        - Ensure a valid path exists between selected cities
                        - Try refreshing the page
                        - Check your internet connection for map tiles
                        """)
                        
                        # Show debug info
                        with st.expander("🔍 Debug Information"):
                            st.write(f"**Path:** {path}")
                            st.write(f"**Cities to show:** {cities_to_show}")
                            st.write(f"**Available coordinates:** {list(coordinates.keys())[:10]}...")  # Show first 10
                
                elif map_type == "Enhanced 3D Map":
                    try:
                        if not suppress_warnings:
                            st.info("🎯 Loading enhanced 3D map visualization...")
                        enhanced_map = create_enhanced_coordinate_visualization(path, graph, coordinates, cities_to_show)
                        st.pydeck_chart(enhanced_map)
                    except Exception as e:
                        if enable_fallbacks:
                            st.warning("⚠️ Enhanced map visualization encountered an issue. Using simple plot.")
                            simple_map = create_simple_coordinate_plot(path, graph, coordinates, cities_to_show)
                            st.plotly_chart(simple_map, use_container_width=True)
                        else:
                            st.error(f"Enhanced map failed: {e}")
                
                elif map_type == "Streamlit Native Map":
                    try:
                        if not suppress_warnings:
                            st.info("📍 Loading native Streamlit map...")
                        if path and len(path) > 1:
                            # Create dataframe for Streamlit map
                            map_data = []
                            for i, city in enumerate(path):
                                if city in coordinates:
                                    map_data.append({
                                        'lat': coordinates[city][0],
                                        'lon': coordinates[city][1],
                                        'city': city,
                                        'size': 300 if i == 0 or i == len(path)-1 else 200,
                                        'color': [255, 0, 0, 255] if i == 0 else [0, 255, 0, 255] if i == len(path)-1 else [0, 100, 255, 255]
                                    })
                            
                            if map_data:
                                map_df = pd.DataFrame(map_data)
                                # Center the map on India
                                st.map(map_df, latitude=20.5937, longitude=78.9629, zoom=4)
                            else:
                                st.error("No valid coordinates found for the path")
                    except Exception as e:
                        if enable_fallbacks:
                            st.warning("⚠️ Native map failed. Using simple coordinate plot.")
                            simple_map = create_simple_coordinate_plot(path, graph, coordinates, cities_to_show)
                            st.plotly_chart(simple_map, use_container_width=True)
                        else:
                            st.error(f"Native map failed: {e}")
                
                else:  # Simple Coordinate Plot
                    try:
                        simple_map = create_simple_coordinate_plot(path, graph, coordinates, cities_to_show)
                        st.plotly_chart(simple_map, use_container_width=True)
                    except Exception as e:
                        st.error(f"Simple coordinate plot failed: {e}")
                
                # Additional Streamlit native map
                with st.expander("📍 Streamlit Native Map View"):
                    if path and len(path) > 1:
                        # Create dataframe for Streamlit map
                        map_data = []
                        for i, city in enumerate(path):
                            if city in coordinates:
                                lat, lon = coordinates[city]
                                map_data.append({
                                    'lat': lat,
                                    'lon': lon,
                                    'city': city,
                                    'step': i + 1,
                                    'size': 20 if i == 0 or i == len(path)-1 else 15
                                })
                        
                        map_df = pd.DataFrame(map_data)
                        
                        # Display the native Streamlit map
                        st.map(map_df, size='size')
                        
                        # Display route info
                        st.write("**Route Path:**")
                        for i, row in map_df.iterrows():
                            if i == 0:
                                st.write(f"🏠 **Start:** {row['city']}")
                            elif i == len(map_df) - 1:
                                st.write(f"🎯 **End:** {row['city']}")
                            else:
                                st.write(f"📍 **Stop {row['step']}:** {row['city']}")
                    else:
                        st.info("Select a route to see the map visualization.")
                with st.expander("📋 Detailed Route Table"):
                    route_df = create_route_table(path, graph)
                    if route_df is not None:
                        st.dataframe(route_df, use_container_width=True)
                
                # Network graph
                if show_network_graph:
                    st.subheader("🕸️ Network Graph")
                    try:
                        network_fig = create_network_graph(graph, path)
                        st.plotly_chart(network_fig, use_container_width=True)
                    except Exception as e:
                        st.error(f"❌ Network graph error: {str(e)}")
                        st.info("💡 Try unchecking 'Show network graph' in the sidebar.")
                
            else:
                st.error("❌ No path found between the selected cities!")
    
    elif search_button and start_city == end_city:
        st.warning("⚠️ Please select different start and end cities!")
    
    # Search History
    if st.session_state.search_history:
        st.subheader("📚 Search History")
        
        # Display as expandable sections
        for i, entry in enumerate(st.session_state.search_history[:5]):  # Show last 5 searches
            with st.expander(f"🔍 {entry['start']} → {entry['end']} ({entry['distance']:.0f} km) - {entry['timestamp']}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Algorithm:** {entry['algorithm']}")
                    st.write(f"**Distance:** {entry['distance']:.0f} km")
                    st.write(f"**Stops:** {len(entry['path']) - 1}")
                with col2:
                    st.write(f"**Route:** {' → '.join(entry['path'])}")
    
    # Statistics Dashboard
    with st.expander("📊 City Network Statistics"):
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Cities", len(cities))
        
        with col2:
            total_connections = sum(len(connections) for connections in graph.values())
            st.metric("Total Connections", total_connections // 2)  # Divide by 2 for undirected graph
        
        with col3:
            avg_connections = total_connections / len(cities)
            st.metric("Avg Connections/City", f"{avg_connections:.1f}")
        
        with col4:
            all_distances = [dist for connections in graph.values() for dist in connections.values()]
            avg_distance = sum(all_distances) / len(all_distances)
            st.metric("Avg Distance", f"{avg_distance:.0f} km")
        
        # City connectivity chart
        connectivity_data = {city: len(connections) for city, connections in graph.items()}
        connectivity_df = pd.DataFrame(list(connectivity_data.items()), columns=['City', 'Connections'])
        connectivity_df = connectivity_df.sort_values('Connections', ascending=True)
        
        fig_connectivity = px.bar(
            connectivity_df,
            x='Connections',
            y='City',
            orientation='h',
            title="City Connectivity (Number of Direct Connections)",
            color='Connections',
            color_continuous_scale='viridis'
        )
        fig_connectivity.update_layout(height=600)
        st.plotly_chart(fig_connectivity, use_container_width=True)

if __name__ == "__main__":
    main()