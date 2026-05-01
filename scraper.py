import requests
import time
import math

# --- Configuration ---
API_KEY = "YOUR_API_KEY_HERE"
LAT = YOUR_LAT_HERE        # Your center latitude
LNG = YOUR_LNG_HERE        # Your center longitude
GRID_STEP = 5000           # Distance between grid points in meters
SEARCH_RADIUS = 50000      # How far out to search from center (meters)

# Business types to search for — add or remove any Google Maps place types
CATEGORIES = [
    "restaurant",
    "cafe",
    "bar",
    "plumber",
    "electrician",
    "painter",
    "locksmith",
    "roofing_contractor",
    "general_contractor",
    "lawyer",
    "accounting",
    "dentist",
    "doctor",
    "physiotherapist",
    "car_repair",
    "car_dealer",
]


def get_grid_points(center_lat, center_lng, search_radius, step):
    # Build a grid of lat/lng points covering the search area
    points = []
    lat_step = step / 111000
    lng_step = step / (111000 * math.cos(math.radians(center_lat)))
    steps = int(search_radius / step) + 1

    for i in range(-steps, steps + 1):
        for j in range(-steps, steps + 1):
            lat = center_lat + i * lat_step
            lng = center_lng + j * lng_step
            # Only include points within the circular search radius
            dist = math.sqrt((lat - center_lat)**2 / lat_step**2 + (lng - center_lng)**2 / lng_step**2) * step
            if dist <= search_radius:
                points.append((lat, lng))
    return points


def safe_get(url, params, retries=5, backoff=3):
    # Wrapper around requests.get with automatic retry + exponential backoff
    for attempt in range(retries):
        try:
            response = requests.get(url, params=params, timeout=10)
            return response.json()
        except Exception as e:
            print(f"  Request failed (attempt {attempt+1}/{retries}): {e}")
            if attempt < retries - 1:
                time.sleep(backoff * (attempt + 1))
    return None


def get_nearby_places(lat, lng, place_type):
    # Search for businesses of a given type near a lat/lng point
    # Handles pagination automatically (Google returns max 20 results per page)
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "location": f"{lat},{lng}",
        "radius": GRID_STEP,
        "type": place_type,
        "key": API_KEY,
    }
    results = []
    while True:
        data = safe_get(url, params)
        if data is None:
            break
        results.extend(data.get("results", []))
        next_page_token = data.get("next_page_token")
        if not next_page_token:
            break
        time.sleep(2)  # Google requires a short delay before using a page token
        params = {"pagetoken": next_page_token, "key": API_KEY}
    return results


def get_place_details(place_id):
    # Fetch full details for a place — we only care about name, address, phone, and website
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "fields": "name,formatted_address,formatted_phone_number,website",
        "key": API_KEY,
    }
    data = safe_get(url, params)
    if data is None:
        return None
    if data.get("status") != "OK":
        print(f"  Details API error: {data.get('status')} — {data.get('error_message', '')}")
        return None
    return data.get("result", {})


def append_category_to_file(category, leads, filename="leads.txt"):
    # Append a category's leads to the output file in a readable format
    with open(filename, "a", encoding="utf-8") as f:
        f.write(f"{'='*40}\n")
        f.write(f"{category.upper().replace('_', ' ')} ({len(leads)} leads)\n")
        f.write(f"{'='*40}\n\n")
        for lead in leads:
            f.write(f"Name:    {lead['name']}\n")
            f.write(f"Address: {lead['address']}\n")
            f.write(f"Phone:   {lead['phone']}\n\n")


def main():
    # Clear the output file before starting a fresh run
    with open("leads.txt", "w", encoding="utf-8") as f:
        f.write("")

    print("Calculating grid points...")
    points = get_grid_points(LAT, LNG, SEARCH_RADIUS, GRID_STEP)
    print(f"Grid has {len(points)} points. Starting search...\n")

    total_leads = 0

    for category in CATEGORIES:
        print(f"\n{'='*40}")
        print(f"Category: {category.upper()}")
        print(f"{'='*40}")

        seen_ids = set()  # Track place IDs to avoid duplicates across grid points
        places = []

        for i, (lat, lng) in enumerate(points):
            print(f"  Searching point {i+1}/{len(points)}...")
            results = get_nearby_places(lat, lng, category)
            for r in results:
                if r["place_id"] not in seen_ids:
                    seen_ids.add(r["place_id"])
                    places.append(r)
            time.sleep(0.2)  # Small delay to avoid hitting rate limits

        print(f"  Found {len(places)} unique places. Checking for websites...")

        no_website = []
        for i, place in enumerate(places):
            name = place.get("name", "?")
            print(f"  Checking {i+1}/{len(places)}: {name}")
            details = get_place_details(place["place_id"])
            time.sleep(0.15)

            if details is None:
                continue

            # Only keep businesses that have no website listed
            if not details.get("website"):
                no_website.append({
                    "name": details.get("name") or place.get("name", "N/A"),
                    "address": details.get("formatted_address") or place.get("vicinity", "N/A"),
                    "phone": details.get("formatted_phone_number", "N/A"),
                })

        append_category_to_file(category, no_website)
        total_leads += len(no_website)
        print(f"  {len(no_website)} leads found in {category} — saved to leads.txt")

    # Write the total lead count at the bottom of the file
    with open("leads.txt", "a", encoding="utf-8") as f:
        f.write(f"{'='*40}\n")
        f.write(f"TOTAL LEADS: {total_leads}\n")

    print(f"\nDone! All leads saved to leads.txt")


if __name__ == "__main__":
    main()