import pandas as pd
import os
import sys
from dataclasses import dataclass, asdict, field
from playwright.sync_api import sync_playwright
import argparse

# Load locations from CSV
locations_file = "trip_plans_recommend.csv"

try:
    df_locations = pd.read_csv(locations_file)
    locations = df_locations["Địa điểm"].dropna().tolist()  # Remove NaN or empty values
except Exception as e:
    print(f"Lỗi khi đọc file CSV: {e}")
    locations = []

if not locations:
    print("Không có địa điểm nào trong file CSV.")
    exit()

data = []

@dataclass
class Business:
    """holds business data"""
    name: str = None
    address: str = None
    website: str = None
    phone_number: str = None
    reviews_count: int = None
    reviews_average: float = None
    latitude: float = None
    longitude: float = None

@dataclass
class BusinessList:
    """holds list of Business objects and saves to Excel/CSV"""
    business_list: list[Business] = field(default_factory=list)
    save_at = 'output'

    def dataframe(self):
        return pd.json_normalize(
            (asdict(business) for business in self.business_list), sep="_"
        )

    def save_to_excel(self, filename):
        if not os.path.exists(self.save_at):
            os.makedirs(self.save_at)
        self.dataframe().to_excel(f"{self.save_at}/{filename}.xlsx", index=False)

    def save_to_csv(self, filename):
        if not os.path.exists(self.save_at):
            os.makedirs(self.save_at)
        self.dataframe().to_csv(f"{self.save_at}/{filename}.csv", index=False)

def extract_coordinates_from_url(url: str) -> tuple[float, float]:
    coordinates = url.split('/@')[-1].split('/')[0]
    return float(coordinates.split(',')[0]), float(coordinates.split(',')[1])

def main():
    total = 1000  # Number of results to scrape per location
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        page.goto("https://www.google.com/maps", timeout=60000)
        page.wait_for_timeout(5000)

        for index, location in enumerate(locations):
            print(f"Scraping location {index + 1}/{len(locations)}: {location.strip()}")
            
            page.locator('//input[@id="searchboxinput"]').fill(location)
            page.wait_for_timeout(3000)
            page.keyboard.press("Enter")
            page.wait_for_timeout(5000)

            page.hover('//a[contains(@href, "https://www.google.com/maps/place")]')

            business_list = BusinessList()

            listings = page.locator(
                '//a[contains(@href, "https://www.google.com/maps/place")]'
            ).all()[:total]

            for listing in listings:
                try:
                    listing.click()
                    page.wait_for_timeout(5000)

                    business = Business(
                        name=listing.get_attribute('aria-label') or '',
                        address=page.locator('//button[@data-item-id="address"]//div').inner_text() or '',
                        website=page.locator('//a[@data-item-id="authority"]//div').inner_text() or '',
                        phone_number=page.locator('//button[contains(@data-item-id, "phone:tel:")]//div').inner_text() or '',
                        reviews_count=int(
                            page.locator('//button[@jsaction="pane.reviewChart.moreReviews"]//span').inner_text()
                            .replace(',', '')
                        ) if page.locator('//button[@jsaction="pane.reviewChart.moreReviews"]//span').count() > 0 else 0,
                        reviews_average=float(
                            page.locator('//div[@jsaction="pane.reviewChart.moreReviews"]//div[@role="img"]').get_attribute('aria-label')
                            .split()[0].replace(',', '.')
                        ) if page.locator('//div[@jsaction="pane.reviewChart.moreReviews"]//div[@role="img"]').count() > 0 else 0.0,
                        latitude=extract_coordinates_from_url(page.url)[0],
                        longitude=extract_coordinates_from_url(page.url)[1]
                    )

                    business_list.business_list.append(business)
                except Exception as e:
                    print(f"Error while scraping business: {e}")

            # Save results for the current location
            sanitized_location = location.replace(' ', '_').replace('/', '_')
            business_list.save_to_excel(f"google_maps_data_{sanitized_location}")
            business_list.save_to_csv(f"google_maps_data_{sanitized_location}")

        browser.close()

if __name__ == "__main__":
    main()
