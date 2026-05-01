# Google Maps Business Scraper

Scrapes Google Maps to find local businesses without a website — used for cold outreach targeting.

## How it works

1. `scraper.py` — searches a grid of points across a region and pulls businesses by category, outputs to `leads.txt`
2. `remove_no_phone.py` — filters out any leads without a phone number, outputs to `leads_with_phones.txt`
3. `remove_duplicates.py` — removes duplicate entries, outputs to `leads_clean.txt`

## Setup

1. Get a Google Maps API key from the [Google Cloud Console](https://console.cloud.google.com/)
2. Paste it into `scraper.py` where it says `YOUR_API_KEY_HERE`
3. Set your `LAT` and `LNG` to your target area's coordinates
4. Install dependencies:
5. Run `scraper.py` first, then the cleaning scripts in order

## Categories

Edit the `CATEGORIES` list in `scraper.py` to target different business types. Uses standard Google Maps place types.
