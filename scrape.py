import os
import requests
import pandas as pd
from bs4 import BeautifulSoup
from supabase import create_client
from datetime import datetime

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]

# Scraper
url = "https://www.worldometers.info/coronavirus/"
response = requests.get(url, timeout=20, headers={"User-Agent": "Mozilla/5.0"})
soup = BeautifulSoup(response.text, "html.parser")

table = soup.find("table", id="main_table_countries_today")
rows_html = table.find_all("tr", class_="total_row_world row_continent")

scrape_time = datetime.now().isoformat()
data = []

for row in rows_html:
    cells = row.find_all("td")
    continent = cells[1].get_text(strip=True)
    total_cases = cells[2].get_text(strip=True)
    total_deaths = cells[4].get_text(strip=True)
    total_recovered = cells[6].get_text(strip=True)
    data.append({
        "continent":       continent,
        "total_cases":     float(total_cases.replace(",", "")) if total_cases else 0,
        "total_deaths":    float(total_deaths.replace(",", "")) if total_deaths else 0,
        "total_recovered": float(total_recovered.replace(",", "")) if total_recovered else 0,
        "scraped_at":      scrape_time,
    })

df = pd.DataFrame(data)
df = df[df["continent"] != ""]

# Supabase insert
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
supabase.table("covid-scrape").insert(data).execute()
print(f"✅ Inserted {len(df)} rows into Supabase")