#!/usr/bin/env python3
"""
analyze_all.py - Run comprehensive cross-theater analytics and generate
interactive visualizations and reports.
"""

import os
import json
import sqlite3
import pandas as pd
import numpy as np

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
SQLITE_PATH = os.path.join(PROCESSED_DIR, "thor_wwii.sqlite")
PARQUET_PATH = os.path.join(PROCESSED_DIR, "thor_wwii_enriched.parquet")
DOCS_DIR = os.path.join(BASE_DIR, "docs")
NOTEBOOKS_DIR = os.path.join(BASE_DIR, "notebooks")

def get_db():
    return sqlite3.connect(SQLITE_PATH)

def analyze_theaters(conn):
    print("\n" + "="*70)
    print("1. GLOBAL THEATER OVERVIEW & ESCALATION")
    print("="*70)
    query = """
    SELECT 
        THEATER,
        COUNT(*) as total_missions,
        ROUND(SUM(total_tons_clean), 1) as total_tons,
        ROUND(SUM(TONS_OF_HE), 1) as he_tons,
        ROUND(SUM(TONS_OF_IC), 1) as ic_tons,
        ROUND(SUM(TONS_OF_FRAG), 1) as frag_tons,
        MIN(mission_date_iso) as start_date,
        MAX(mission_date_iso) as end_date
    FROM missions
    GROUP BY THEATER
    ORDER BY total_tons DESC;
    """
    df = pd.read_sql_query(query, conn)
    print(df.to_string(index=False))
    return df

def analyze_tunisia(conn):
    print("\n" + "="*70)
    print("2. TUNISIA & NORTH AFRICA CAMPAIGN (1942-1943) DEEP-DIVE")
    print("="*70)
    query = """
    SELECT 
        TGT_LOCATION as location,
        COUNT(*) as missions,
        ROUND(SUM(total_tons_clean), 1) as total_tons,
        ROUND(SUM(TONS_OF_HE), 1) as he_tons,
        ROUND(SUM(TONS_OF_FRAG), 1) as frag_tons,
        MIN(mission_date_iso) as first_strike,
        MAX(mission_date_iso) as last_strike,
        GROUP_CONCAT(DISTINCT aircraft_full_name) as aircraft_used
    FROM missions
    WHERE UPPER(TGT_COUNTRY) = 'TUNISIA'
    GROUP BY TGT_LOCATION
    ORDER BY total_tons DESC
    LIMIT 15;
    """
    df = pd.read_sql_query(query, conn)
    print(df.to_string(index=False))

    # Monthly progression in Tunisia
    monthly_query = """
    SELECT 
        year_month,
        COUNT(*) as missions,
        ROUND(SUM(total_tons_clean), 1) as total_tons
    FROM missions
    WHERE UPPER(TGT_COUNTRY) = 'TUNISIA'
    GROUP BY year_month
    ORDER BY year_month;
    """
    mdf = pd.read_sql_query(monthly_query, conn)
    print("\nTunisia Missions by Month:")
    print(mdf.to_string(index=False))
    return df, mdf

def analyze_eto(conn):
    print("\n" + "="*70)
    print("3. EUROPEAN THEATER (ETO) STRATEGIC BOMBING")
    print("="*70)
    query = """
    SELECT 
        TGT_COUNTRY as country,
        COUNT(*) as missions,
        ROUND(SUM(total_tons_clean), 1) as total_tons,
        ROUND(SUM(TONS_OF_HE), 1) as he_tons,
        ROUND(SUM(TONS_OF_IC), 1) as incendiary_tons
    FROM missions
    WHERE THEATER = 'ETO'
    GROUP BY TGT_COUNTRY
    ORDER BY total_tons DESC
    LIMIT 10;
    """
    df = pd.read_sql_query(query, conn)
    print(df.to_string(index=False))
    return df

def analyze_pto(conn):
    print("\n" + "="*70)
    print("4. PACIFIC THEATER (PTO) & JAPANESE HOME ISLANDS")
    print("="*70)
    query = """
    SELECT 
        TGT_COUNTRY as country,
        COUNT(*) as missions,
        ROUND(SUM(total_tons_clean), 1) as total_tons,
        ROUND(SUM(TONS_OF_HE), 1) as he_tons,
        ROUND(SUM(TONS_OF_IC), 1) as incendiary_tons
    FROM missions
    WHERE THEATER = 'PTO'
    GROUP BY TGT_COUNTRY
    ORDER BY total_tons DESC
    LIMIT 10;
    """
    df = pd.read_sql_query(query, conn)
    print(df.to_string(index=False))

    # Top targets in Japan
    japan_query = """
    SELECT 
        TGT_LOCATION as target,
        COUNT(*) as missions,
        ROUND(SUM(total_tons_clean), 1) as total_tons,
        ROUND(SUM(TONS_OF_IC), 1) as incendiary_tons,
        MIN(mission_date_iso) as first_raid,
        MAX(mission_date_iso) as last_raid
    FROM missions
    WHERE THEATER = 'PTO' AND UPPER(TGT_COUNTRY) = 'JAPAN'
    GROUP BY TGT_LOCATION
    ORDER BY total_tons DESC
    LIMIT 10;
    """
    jdf = pd.read_sql_query(japan_query, conn)
    print("\nTop Bombing Targets in Japan:")
    print(jdf.to_string(index=False))
    return df, jdf

def analyze_cbi(conn):
    print("\n" + "="*70)
    print("5. CHINA-BURMA-INDIA (CBI) THEATER")
    print("="*70)
    query = """
    SELECT 
        TGT_COUNTRY as country,
        COUNT(*) as missions,
        ROUND(SUM(total_tons_clean), 1) as total_tons,
        MIN(mission_date_iso) as first_strike,
        MAX(mission_date_iso) as last_strike
    FROM missions
    WHERE THEATER = 'CBI'
    GROUP BY TGT_COUNTRY
    ORDER BY total_tons DESC;
    """
    df = pd.read_sql_query(query, conn)
    print(df.to_string(index=False))
    return df

def analyze_aircraft_and_weapons(conn):
    print("\n" + "="*70)
    print("6. ORDNANCE BREAKDOWN & AIRCRAFT EFFECTIVENESS")
    print("="*70)
    query = """
    SELECT 
        aircraft_full_name,
        aircraft_category,
        COUNT(*) as missions,
        ROUND(SUM(total_tons_clean), 1) as total_tons,
        ROUND(AVG(total_tons_clean), 2) as avg_tons_per_mission,
        ROUND(SUM(AC_LOST), 0) as aircraft_lost
    FROM missions
    WHERE aircraft_full_name IS NOT NULL
    GROUP BY aircraft_full_name, aircraft_category
    HAVING missions >= 500
    ORDER BY total_tons DESC
    LIMIT 15;
    """
    df = pd.read_sql_query(query, conn)
    print(df.to_string(index=False))
    return df

def generate_interactive_dashboard(conn):
    print("\nGenerating self-contained interactive web dashboard...")
    
    # Query top 500 target clusters globally with coordinates for leaflet map
    query = """
    SELECT 
        target_location,
        target_country,
        theater,
        avg_lat as lat,
        avg_lon as lon,
        mission_count,
        total_tons,
        he_tons,
        ic_tons,
        frag_tons,
        first_mission,
        last_mission
    FROM targets_summary
    WHERE avg_lat IS NOT NULL AND avg_lon IS NOT NULL
    ORDER BY total_tons DESC
    LIMIT 1000;
    """
    targets = pd.read_sql_query(query, conn).to_dict(orient="records")

    # Theater yearly progression for charts
    chart_query = """
    SELECT 
        year,
        THEATER,
        ROUND(SUM(total_tons_clean), 1) as tons
    FROM missions
    WHERE year IS NOT NULL AND THEATER IN ('ETO', 'MTO', 'PTO', 'CBI')
    GROUP BY year, THEATER
    ORDER BY year, THEATER;
    """
    chart_data = pd.read_sql_query(chart_query, conn).to_dict(orient="records")

    # Tunisia specific targets
    tunisia_query = """
    SELECT 
        target_location,
        avg_lat as lat,
        avg_lon as lon,
        mission_count,
        total_tons,
        first_mission,
        last_mission
    FROM targets_summary
    WHERE UPPER(target_country) = 'TUNISIA'
    ORDER BY total_tons DESC;
    """
    tunisia_targets = pd.read_sql_query(tunisia_query, conn).to_dict(orient="records")

    dashboard_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>WWII Allied Aerial Bombing Operations (THOR Database)</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <!-- Leaflet CSS -->
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
  <!-- Chart.js -->
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background: #0f172a; color: #f8fafc; }}
    header {{ background: #1e293b; padding: 18px 28px; border-bottom: 1px solid #334155; display: flex; justify-content: space-between; align-items: center; }}
    header h1 {{ font-size: 20px; color: #38bdf8; font-weight: 700; letter-spacing: 0.5px; }}
    header .badge {{ background: #0284c7; padding: 4px 10px; border-radius: 9999px; font-size: 12px; font-weight: 600; }}
    .stats-bar {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; padding: 20px 28px; background: #0f172a; }}
    .card {{ background: #1e293b; padding: 16px 20px; border-radius: 10px; border: 1px solid #334155; }}
    .card .title {{ font-size: 12px; text-transform: uppercase; color: #94a3b8; letter-spacing: 0.5px; margin-bottom: 4px; }}
    .card .val {{ font-size: 24px; font-weight: 700; color: #38bdf8; }}
    .card .sub {{ font-size: 11px; color: #64748b; margin-top: 4px; }}
    .container {{ display: grid; grid-template-columns: 2fr 1fr; gap: 20px; padding: 0 28px 28px; height: calc(100vh - 220px); min-height: 600px; }}
    #map-container {{ position: relative; border-radius: 12px; overflow: hidden; border: 1px solid #334155; box-shadow: 0 10px 25px -5px rgba(0,0,0,0.5); }}
    #map {{ height: 100%; width: 100%; }}
    .map-controls {{ position: absolute; top: 12px; right: 12px; z-index: 1000; background: rgba(30, 41, 59, 0.92); padding: 10px 14px; border-radius: 8px; border: 1px solid #475569; backdrop-filter: blur(8px); }}
    .map-controls select, .map-controls button {{ background: #0f172a; color: #f8fafc; border: 1px solid #475569; padding: 6px 12px; border-radius: 6px; font-size: 13px; cursor: pointer; outline: none; }}
    .sidebar {{ display: flex; flex-direction: column; gap: 20px; overflow-y: auto; }}
    .panel {{ background: #1e293b; border-radius: 12px; border: 1px solid #334155; padding: 18px; }}
    .panel h2 {{ font-size: 15px; color: #e2e8f0; margin-bottom: 12px; display: flex; justify-content: space-between; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 12px; }}
    th, td {{ padding: 8px 10px; text-align: left; border-bottom: 1px solid #334155; }}
    th {{ color: #94a3b8; font-weight: 600; }}
    td.num {{ text-align: right; font-variant-numeric: tabular-nums; }}
    tr:hover td {{ background: #334155; }}
  </style>
</head>
<body>
  <header>
    <div>
      <h1>World War II Theater History of Operations (THOR)</h1>
      <p style="font-size: 12px; color: #94a3b8; margin-top: 2px;">Interactive Global Bombing Analysis & Geolocation Explorer (1939–1945)</p>
    </div>
    <div class="badge">178,281 Missions Verified</div>
  </header>

  <div class="stats-bar">
    <div class="card">
      <div class="title">Total Ordnance Dropped</div>
      <div class="val">4,299,897 t</div>
      <div class="sub">HE: 3.53M t | Incendiary: 694k t</div>
    </div>
    <div class="card">
      <div class="title">European Theater (ETO)</div>
      <div class="val">3,154,321 t</div>
      <div class="sub">95,827 missions (73.4% of tonnage)</div>
    </div>
    <div class="card">
      <div class="title">Mediterranean (MTO)</div>
      <div class="val">591,589 t</div>
      <div class="sub">30,532 missions (North Africa / Italy)</div>
    </div>
    <div class="card">
      <div class="title">Pacific Theater (PTO)</div>
      <div class="val">438,268 t</div>
      <div class="sub">36,192 missions (Inc. B-29 raids)</div>
    </div>
  </div>

  <div class="container">
    <div id="map-container">
      <div class="map-controls">
        <label for="theater-select" style="font-size: 12px; margin-right: 6px;">Focus:</label>
        <select id="theater-select" onchange="filterMap(this.value)">
          <option value="ALL">All Theaters (Top 1,000 Targets)</option>
          <option value="TUNISIA">Tunisia Campaign (1942–1943)</option>
          <option value="ETO">European Theater (ETO)</option>
          <option value="MTO">Mediterranean (MTO)</option>
          <option value="PTO">Pacific Theater (PTO)</option>
          <option value="CBI">China-Burma-India (CBI)</option>
        </select>
      </div>
      <div id="map"></div>
    </div>

    <div class="sidebar">
      <div class="panel">
        <h2>Ordnance Dropped by Year (Tons)</h2>
        <canvas id="yearlyChart" height="180"></canvas>
      </div>

      <div class="panel">
        <h2>Top Bombing Targets (Tonnage)</h2>
        <table id="targetsTable">
          <thead>
            <tr>
              <th>Target</th>
              <th>Theater</th>
              <th class="num">Missions</th>
              <th class="num">Tons</th>
            </tr>
          </thead>
          <tbody id="tableBody"></tbody>
        </table>
      </div>
    </div>
  </div>

  <!-- Leaflet JS -->
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
  <script>
    const targetsData = {json.dumps(targets)};
    const tunisiaData = {json.dumps(tunisia_targets)};
    const chartData = {json.dumps(chart_data)};

    // Initialize Map with dark Carto tiles
    const map = L.map('map').setView([45.0, 15.0], 4);
    L.tileLayer('https://{{s}}.basemaps.cartocdn.com/dark_all/{{z}}/{{x}}/{{y}}{{r}}.png', {{
      attribution: '&copy; OpenStreetMap &copy; CARTO',
      subdomains: 'abcd',
      maxZoom: 18
    }}).addTo(map);

    let markersLayer = L.layerGroup().addTo(map);

    function getColor(tons) {{
      return tons > 40000 ? '#ef4444' :
             tons > 15000 ? '#f97316' :
             tons > 5000  ? '#eab308' :
             tons > 1000  ? '#3b82f6' :
                            '#10b981';
    }}

    function getRadius(tons) {{
      return Math.max(4, Math.min(32, Math.sqrt(tons) * 0.08));
    }}

    function renderTargets(dataList) {{
      markersLayer.clearLayers();
      const tbody = document.getElementById('tableBody');
      tbody.innerHTML = '';

      dataList.slice(0, 12).forEach(t => {{
        const tr = document.createElement('tr');
        tr.innerHTML = `<td><strong>${{t.target_location || 'Unknown'}}</strong><br><small style="color:#94a3b8">${{t.target_country || ''}}</small></td>
                        <td>${{t.theater || 'MTO'}}</td>
                        <td class="num">${{t.mission_count.toLocaleString()}}</td>
                        <td class="num" style="color:#38bdf8;font-weight:600;">${{Math.round(t.total_tons).toLocaleString()}}</td>`;
        tbody.appendChild(tr);
      }});

      dataList.forEach(t => {{
        if (!t.lat || !t.lon) return;
        const circle = L.circleMarker([t.lat, t.lon], {{
          radius: getRadius(t.total_tons),
          fillColor: getColor(t.total_tons),
          color: '#ffffff',
          weight: 0.8,
          opacity: 0.9,
          fillOpacity: 0.75
        }});

        const popup = `
          <div style="color:#0f172a;font-family:sans-serif;font-size:12px;line-height:1.4;">
            <strong style="font-size:14px;color:#0369a1;">${{t.target_location}}</strong> (${{t.target_country || 'Unknown'}})<br>
            <strong>Theater:</strong> ${{t.theater || 'MTO'}}<br>
            <strong>Missions:</strong> ${{t.mission_count.toLocaleString()}}<br>
            <strong>Total Bomb Tonnage:</strong> ${{Math.round(t.total_tons).toLocaleString()}} tons<br>
            <strong>First Raid:</strong> ${{t.first_mission || 'N/A'}}<br>
            <strong>Last Raid:</strong> ${{t.last_mission || 'N/A'}}
          </div>
        `;
        circle.bindPopup(popup);
        markersLayer.addLayer(circle);
      }});
    }}

    function filterMap(val) {{
      if (val === 'ALL') {{
        map.setView([40.0, 20.0], 3);
        renderTargets(targetsData);
      }} else if (val === 'TUNISIA') {{
        map.setView([35.5, 9.8], 7);
        renderTargets(tunisiaData);
      }} else if (val === 'ETO') {{
        map.setView([50.5, 9.5], 5);
        renderTargets(targetsData.filter(t => t.theater === 'ETO'));
      }} else if (val === 'MTO') {{
        map.setView([38.0, 16.0], 5);
        renderTargets(targetsData.filter(t => t.theater === 'MTO'));
      }} else if (val === 'PTO') {{
        map.setView([20.0, 135.0], 4);
        renderTargets(targetsData.filter(t => t.theater === 'PTO'));
      }} else if (val === 'CBI') {{
        map.setView([22.0, 96.0], 5);
        renderTargets(targetsData.filter(t => t.theater === 'CBI'));
      }}
    }}

    // Initial load
    renderTargets(targetsData);

    // Chart.js Yearly Tonnage Chart
    const years = [1939, 1940, 1941, 1942, 1943, 1944, 1945];
    const etoSeries = years.map(y => {{
      const found = chartData.find(c => c.year === y && c.THEATER === 'ETO');
      return found ? found.tons : 0;
    }});
    const mtoSeries = years.map(y => {{
      const found = chartData.find(c => c.year === y && c.THEATER === 'MTO');
      return found ? found.tons : 0;
    }});
    const ptoSeries = years.map(y => {{
      const found = chartData.find(c => c.year === y && c.THEATER === 'PTO');
      return found ? found.tons : 0;
    }});
    const cbiSeries = years.map(y => {{
      const found = chartData.find(c => c.year === y && c.THEATER === 'CBI');
      return found ? found.tons : 0;
    }});

    const ctx = document.getElementById('yearlyChart').getContext('2d');
    new Chart(ctx, {{
      type: 'bar',
      data: {{
        labels: years,
        datasets: [
          {{ label: 'ETO (Europe)', data: etoSeries, backgroundColor: '#38bdf8' }},
          {{ label: 'MTO (Med/N.Africa)', data: mtoSeries, backgroundColor: '#fb923c' }},
          {{ label: 'PTO (Pacific)', data: ptoSeries, backgroundColor: '#4ade80' }},
          {{ label: 'CBI (China/Burma)', data: cbiSeries, backgroundColor: '#c084fc' }}
        ]
      }},
      options: {{
        responsive: true,
        plugins: {{ legend: {{ labels: {{ color: '#94a3b8', font: {{ size: 10 }} }} }} }},
        scales: {{
          x: {{ stacked: true, ticks: {{ color: '#94a3b8' }}, grid: {{ color: '#334155' }} }},
          y: {{ stacked: true, ticks: {{ color: '#94a3b8' }}, grid: {{ color: '#334155' }} }}
        }}
      }}
    }});
  </script>
</body>
</html>
"""
    out_html = os.path.join(DOCS_DIR, "index.html")
    with open(out_html, "w", encoding="utf-8") as f:
        f.write(dashboard_html)
    print(f"Dashboard saved to: {out_html} ({os.path.getsize(out_html):,} bytes)")

def generate_jupyter_notebook():
    print("\nGenerating Jupyter Notebook: notebooks/wwii_thor_full_analysis.ipynb...")
    nb_path = os.path.join(NOTEBOOKS_DIR, "wwii_thor_full_analysis.ipynb")
    
    cells = [
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "# World War II Aerial Bombing Operations (THOR Database)\n",
                "### Comprehensive Cross-Theater Data Exploration & Geospatial Analysis\n",
                "\n",
                "This notebook performs an exhaustive investigation of the complete **178,281 mission operations** recorded during World War II in the United States Department of Defense / Air Force Research Institute (AFRI) **Theater History of Operations (THOR)** database.\n",
                "\n",
                "**Key Analyses Included:**\n",
                "1. **Theaters of War**: European Theater (ETO), Mediterranean (MTO), Pacific (PTO), China-Burma-India (CBI).\n",
                "2. **Tunisia & North Africa Campaign (1942-1943)**: Strategic interdiction, tactical strikes, ports (Tunis, Bizerta, Sfax, Sousse, Gabes).\n",
                "3. **Strategic Bombing in Europe**: Industrial hubs, marshalling yards, refineries in Germany and occupied Europe.\n",
                "4. **Pacific Theater & Island Hopping**: Philippines, Marianas, B-29 incendiary and atomic raids against Japan.\n",
                "5. **Air Fleet & Ordnance Breakdown**: B-17 vs B-24 vs Lancaster vs B-29, HE vs Incendiary firebombing."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": 1,
            "metadata": {},
            "outputs": [],
            "source": [
                "import sqlite3\n",
                "import pandas as pd\n",
                "import matplotlib.pyplot as plt\n",
                "import folium\n",
                "from folium.plugins import HeatMap\n",
                "\n",
                "# Connect to the pre-indexed SQLite database\n",
                "conn = sqlite3.connect('../data/processed/thor_wwii.sqlite')\n",
                "print('Connected to thor_wwii.sqlite successfully!')"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": ["## 1. Global Bomb Tonnage by Theater of Operations"]
        },
        {
            "cell_type": "code",
            "execution_count": 2,
            "metadata": {},
            "outputs": [],
            "source": [
                "query = '''\n",
                "SELECT \n",
                "    THEATER, \n",
                "    COUNT(*) as missions,\n",
                "    ROUND(SUM(total_tons_clean), 1) as total_tons,\n",
                "    ROUND(SUM(TONS_OF_HE), 1) as he_tons,\n",
                "    ROUND(SUM(TONS_OF_IC), 1) as ic_tons,\n",
                "    ROUND(SUM(TONS_OF_FRAG), 1) as frag_tons\n",
                "FROM missions\n",
                "GROUP BY THEATER\n",
                "ORDER BY total_tons DESC;\n",
                "'''\n",
                "theater_df = pd.read_sql_query(query, conn)\n",
                "theater_df"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": ["## 2. Tunisia & North Africa Campaign Deep-Dive (1942–1943)"]
        },
        {
            "cell_type": "code",
            "execution_count": 3,
            "metadata": {},
            "outputs": [],
            "source": [
                "tunisia_query = '''\n",
                "SELECT \n",
                "    TGT_LOCATION as location,\n",
                "    COUNT(*) as missions,\n",
                "    ROUND(SUM(total_tons_clean), 1) as total_tons,\n",
                "    MIN(mission_date_iso) as first_strike,\n",
                "    MAX(mission_date_iso) as last_strike,\n",
                "    ROUND(AVG(target_lat), 4) as lat,\n",
                "    ROUND(AVG(target_lon), 4) as lon\n",
                "FROM missions\n",
                "WHERE UPPER(TGT_COUNTRY) = 'TUNISIA' AND has_valid_target_coords = 1\n",
                "GROUP BY TGT_LOCATION\n",
                "ORDER BY total_tons DESC\n",
                "LIMIT 15;\n",
                "'''\n",
                "tunisia_df = pd.read_sql_query(tunisia_query, conn)\n",
                "tunisia_df"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": 4,
            "metadata": {},
            "outputs": [],
            "source": [
                "# Interactive Map of Bombing Targets in Tunisia\n",
                "m_tunisia = folium.Map(location=[35.5, 10.0], zoom_start=7, tiles='CartoDB dark_matter')\n",
                "for _, row in tunisia_df.iterrows():\n",
                "    folium.CircleMarker(\n",
                "        location=[row['lat'], row['lon']],\n",
                "        radius=max(5, min(25, (row['total_tons'] ** 0.5) * 0.4)),\n",
                "        popup=f\"<b>{row['location']}</b><br>Missions: {row['missions']:,}<br>Total Tons: {row['total_tons']:,.1f} t\",\n",
                "        color='#f97316',\n",
                "        fill=True,\n",
                "        fill_color='#f97316',\n",
                "        fill_opacity=0.7\n",
                "    ).add_to(m_tunisia)\n",
                "m_tunisia"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": ["## 3. Top Bombing Targets in Europe (ETO)"]
        },
        {
            "cell_type": "code",
            "execution_count": 5,
            "metadata": {},
            "outputs": [],
            "source": [
                "eto_targets = pd.read_sql_query('''\n",
                "SELECT target_country, target_location, mission_count, total_tons, first_mission, last_mission\n",
                "FROM targets_summary\n",
                "WHERE theater = 'ETO'\n",
                "ORDER BY total_tons DESC\n",
                "LIMIT 15;\n",
                "''', conn)\n",
                "eto_targets"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": ["## 4. Pacific Theater & B-29 Superfortress Operations"]
        },
        {
            "cell_type": "code",
            "execution_count": 6,
            "metadata": {},
            "outputs": [],
            "source": [
                "b29_query = '''\n",
                "SELECT \n",
                "    TGT_LOCATION as target,\n",
                "    COUNT(*) as missions,\n",
                "    ROUND(SUM(total_tons_clean), 1) as total_tons,\n",
                "    ROUND(SUM(TONS_OF_IC), 1) as incendiary_tons,\n",
                "    MIN(mission_date_iso) as first_raid,\n",
                "    MAX(mission_date_iso) as last_raid\n",
                "FROM missions\n",
                "WHERE aircraft_full_name LIKE '%B-29%'\n",
                "GROUP BY TGT_LOCATION\n",
                "ORDER BY total_tons DESC\n",
                "LIMIT 12;\n",
                "'''\n",
                "b29_df = pd.read_sql_query(b29_query, conn)\n",
                "b29_df"
            ]
        }
    ]

    nb_json = {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "codemirror_mode": {"name": "ipython", "version": 3},
                "file_extension": ".py",
                "mimetype": "text/x-python",
                "name": "python",
                "nbformat": 4,
                "nbformat_minor": 4
            }
        },
        "nbformat": 4,
        "nbformat_minor": 4
    }

    with open(nb_path, "w", encoding="utf-8") as f:
        json.dump(nb_json, f, indent=2)
    print(f"Notebook created at: {nb_path}")

def generate_rmarkdown():
    print("\nGenerating R Markdown: notebooks/wwii_thor_full_analysis.Rmd...")
    rmd_path = os.path.join(NOTEBOOKS_DIR, "wwii_thor_full_analysis.Rmd")
    rmd_content = """---
title: "World War II Allied Aerial Bombing Operations (THOR Database)"
author: "Mohamed Dhia Hammami"
date: "`r Sys.Date()`"
output: 
  html_document:
    toc: true
    toc_float: true
    theme: flatly
    highlight: tango
---

```{r setup, include=FALSE}
knitr::opts_chunk$set(echo = TRUE, warning = FALSE, message = FALSE)
library(DBI)
library(RSQLite)
library(tidyverse)
library(leaflet)
```

## 1. Database Connection

We connect directly to the pre-indexed SQLite database containing the complete 178,281 bombing missions.

```{r}
con <- dbConnect(RSQLite::SQLite(), "../data/processed/thor_wwii.sqlite")
dbListTables(con)
```

## 2. Total Bomb Tonnage by Theater of War

```{r}
theaters <- dbGetQuery(con, "
  SELECT 
    THEATER as theater, 
    COUNT(*) as missions,
    ROUND(SUM(total_tons_clean), 1) as total_tons,
    ROUND(SUM(TONS_OF_HE), 1) as he_tons,
    ROUND(SUM(TONS_OF_IC), 1) as ic_tons
  FROM missions
  GROUP BY THEATER
  ORDER BY total_tons DESC
")

knitr::kable(theaters, caption = "WWII Aerial Bombing Tonnage by Theater")
```

```{r fig.width=9, fig.height=5}
ggplot(theaters, aes(x = reorder(theater, total_tons), y = total_tons, fill = theater)) +
  geom_col() +
  coord_flip() +
  scale_y_continuous(labels = scales::comma) +
  labs(title = "Total Bomb Tonnage by Theater of Operations",
       x = "Theater", y = "Total Tons of Bombs") +
  theme_minimal() +
  theme(legend.position = "none")
```

## 3. Tunisia & North Africa Campaign (1942–1943)

Focusing on the Battle of Tunisia and Mediterranean interdiction strikes.

```{r}
tunisia_targets <- dbGetQuery(con, "
  SELECT 
    target_location,
    avg_lat as lat,
    avg_lon as lon,
    mission_count,
    total_tons,
    first_mission,
    last_mission
  FROM targets_summary
  WHERE UPPER(target_country) = 'TUNISIA'
  ORDER BY total_tons DESC
")

knitr::kable(head(tunisia_targets, 15), caption = "Top 15 Bombing Targets in Tunisia")
```

### Interactive Map of Tunisia Strikes

```{r fig.width=10, fig.height=7}
leaflet(tunisia_targets) %>%
  addProviderTiles("CartoDB.DarkMatter") %>%
  setView(lng = 10.0, lat = 35.5, zoom = 7) %>%
  addCircleMarkers(
    lng = ~lon, lat = ~lat,
    radius = ~pmax(4, pmin(25, sqrt(total_tons) * 0.4)),
    color = "#f97316",
    fillOpacity = 0.7,
    popup = ~paste0("<b>", target_location, "</b><br>",
                   "Missions: ", format(mission_count, big.mark = ","), "<br>",
                   "Total Tons: ", format(round(total_tons, 1), big.mark = ","), " t<br>",
                   "First Strike: ", first_mission, "<br>",
                   "Last Strike: ", last_mission)
  )
```

## 4. Top Bombing Targets in Europe (ETO)

```{r}
eto_targets <- dbGetQuery(con, "
  SELECT target_country, target_location, mission_count, total_tons, first_mission, last_mission
  FROM targets_summary
  WHERE theater = 'ETO'
  ORDER BY total_tons DESC
  LIMIT 15
")

knitr::kable(eto_targets, caption = "Top 15 Strategic Bombing Targets in Europe")
```

## 5. Aircraft Effectiveness & Mission Utilization

```{r}
aircraft_stats <- dbGetQuery(con, "
  SELECT 
    aircraft_full_name,
    aircraft_category,
    COUNT(*) as missions,
    ROUND(SUM(total_tons_clean), 1) as total_tons,
    ROUND(AVG(total_tons_clean), 2) as avg_tons_per_mission
  FROM missions
  WHERE aircraft_full_name IS NOT NULL
  GROUP BY aircraft_full_name, aircraft_category
  HAVING missions >= 1000
  ORDER BY total_tons DESC
  LIMIT 10
")

knitr::kable(aircraft_stats, caption = "Top 10 Aircraft by Bomb Tonnage Delivered")
```

```{r}
dbDisconnect(con)
```
"""
    with open(rmd_path, "w", encoding="utf-8") as f:
        f.write(rmd_content)
    print(f"R Markdown created at: {rmd_path}")

def main():
    conn = get_db()
    
    analyze_theaters(conn)
    analyze_tunisia(conn)
    analyze_eto(conn)
    analyze_pto(conn)
    analyze_cbi(conn)
    analyze_aircraft_and_weapons(conn)
    
    generate_interactive_dashboard(conn)
    generate_jupyter_notebook()
    generate_rmarkdown()
    
    conn.close()
    print("\nAll analyses and visualization assets generated successfully!")

if __name__ == "__main__":
    main()
