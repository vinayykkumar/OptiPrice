import requests
import pandas as pd
from bs4 import BeautifulSoup
import datetime

# ============================
# 🔹 1️⃣ Define URLs for Oil Prices
# ============================

oil_urls = {
    "Brent Oil": "https://markets.businessinsider.com/commodities/brent-oil",
    "Crude Oil WTI": "https://markets.businessinsider.com/commodities/oil-price",
    "Natural Gas": "https://markets.businessinsider.com/commodities/natural-gas-price",
    "Heating Oil": "https://markets.businessinsider.com/commodities/heating-oil-price"
}

# ============================
# 🔹 2️⃣ Scrape Oil Prices
# ============================

oil_data = []

for oil, url in oil_urls.items():
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract price (Look for elements with latest market price)
        price_tag = soup.find("span", {"class": "price-section__current-value"})
        if price_tag:
            price = float(price_tag.text.replace(",", ""))
        else:
            price = None

        # Extract volume (Not all sources provide this, so setting None for now)
        volume_sold = None  

        oil_data.append([oil, datetime.date.today().strftime("%Y-%m-%d"), price, volume_sold])
        print(f"✅ {oil} Price: ${price}")

    except Exception as e:
        print(f"❌ Failed to fetch data for {oil}: {e}")
        oil_data.append([oil, datetime.date.today().strftime("%Y-%m-%d"), None, None])

# ============================
# 🔹 3️⃣ Save to CSV
# ============================

df_scraped = pd.DataFrame(oil_data, columns=["Symbol", "Date", "Closing Price", "Volume Sold"])
csv_path = r"D:\studies related\projects\optiprice- prognasticator\scraped_oil_prices.csv"
df_scraped.to_csv(csv_path, index=False)

print(f"🚀 Data saved to {csv_path}")
