CLIENT_LIST_LOADER_PROMPT = """
You are a client list loader agent. Based on the user's question, provide client coverage and census data.

User Input: {user_input}

Return a simple JSON response with client list data. For example:
- For coverage: {{"total_clients": 1200, "active_clients": 950, "inactive_clients": 250}}
- For census: {{"census_clients": 800, "coverage_percent": "85%"}}
- For geolocated lists: {{"clients": [{{"name": "Client A", "lat": 4.6, "lng": -74.1}}]}}

Focus on clear client coverage and census metrics.
""" 