from __future__ import annotations

import csv
import json
import time
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from pathlib import Path


ROOT = Path(__file__).resolve().parent
INSTAGRAM_URL = "https://www.instagram.com/coast2coast4charity/"
OSRM_BASE = "https://router.project-osrm.org/route/v1/cycling/"
OVERPASS_URL = "https://overpass-api.de/api/interpreter"


FRIEND_DAYS = [
    {"day": 1, "miles": 120, "start": "Washington, DC", "finish": "Williamsport, MD", "basis": "caption", "note": "Saw a black bear on the trail; long day out of DC."},
    {"day": 2, "miles": None, "start": "Williamsport, MD", "finish": "Cumberland, MD", "basis": "caption", "note": "Tunnel day on the C&O / GAP transition."},
    {"day": 3, "miles": None, "start": "Cumberland, MD", "finish": "South of Pittsburgh (likely Perryopolis area), PA", "basis": "caption", "note": "Breakfast with New Zealand riders; Ohiopyle lunch; major climbing."},
    {"day": 4, "miles": None, "start": "South of Pittsburgh, PA", "finish": "Steubenville, OH", "basis": "caption", "note": "Tunnels, steep rollers, deer, and Fourth of July riding."},
    {"day": 5, "miles": 91, "start": "Steubenville, OH", "finish": "Millersburg, OH", "basis": "caption", "note": "Very hilly; Amish country; light drizzle."},
    {"day": 6, "miles": 125, "start": "Millersburg, OH", "finish": "Lilly Chapel, OH", "basis": "caption", "note": "Fast, flatter Ohio trail miles into Columbus outskirts and farm country."},
    {"day": 7, "miles": 100, "start": "Lilly Chapel, OH", "finish": "Richmond, IN", "basis": "caption", "note": "Strong day into Indiana; heat and sun."},
    {"day": 8, "miles": 118, "start": "Richmond, IN", "finish": "Logansport, IN", "basis": "caption", "note": "Cardinal Greenway corridor; cornfields and wind."},
    {"day": 9, "miles": 113, "start": "Logansport, IN", "finish": "Chicago Heights, IL", "basis": "caption", "note": "Raced Hurricane Beryl and storm warnings; broken spoke discovered."},
    {"day": 10, "miles": 0, "start": "Chicago Heights, IL", "finish": "Chicago Heights, IL", "basis": "caption", "note": "Bike repair and recovery day."},
    {"day": 11, "miles": 113, "start": "Chicago, IL metro", "finish": "Rock Falls, IL", "basis": "caption", "note": "Trails early, then country roads, turbines, and corn."},
    {"day": 12, "miles": 122, "start": "Rock Falls, IL", "finish": "Cedar Rapids, IA", "basis": "caption", "note": "Crossed the Mississippi; first crash in deep gravel; shoulder bruised."},
    {"day": 13, "miles": 116, "start": "Cedar Rapids, IA", "finish": "Ames, IA", "basis": "caption", "note": "Heavy Iowa crosswind."},
    {"day": 14, "miles": 105, "start": "Ames, IA", "finish": "Denison, IA", "basis": "caption", "note": "Another broken spoke; major cross/headwind."},
    {"day": 15, "miles": 72, "start": "Denison, IA", "finish": "Norfolk, NE", "basis": "caption", "note": "Mechanical day; rear wheel failure cut the ride short."},
    {"day": 16, "miles": 40, "start": "Norfolk, NE", "finish": "Neligh, NE", "basis": "caption", "note": "Bike fixed; restarted on the Cowboy Trail."},
    {"day": 17, "miles": 160, "start": "Neligh, NE", "finish": "Valentine, NE", "basis": "caption", "note": "Huge Sandhills day; more broken spokes; route advice helped."},
    {"day": 18, "miles": 82, "start": "Valentine, NE", "finish": "Near Gordon, NE", "basis": "caption", "note": "Sandhills, cows, and a 20 mph headwind."},
    {"day": 19, "miles": 60, "start": "Near Gordon, NE", "finish": "Short of Custer, SD", "basis": "caption", "note": "Late mechanical start; severe thunder and lightning."},
    {"day": 20, "miles": 85, "start": "Custer, SD", "finish": "Moorcroft, WY", "basis": "caption", "note": "Black Hills morning; entered a more open Wyoming landscape."},
    {"day": 21, "miles": 127, "start": "Sheridan, WY", "finish": "Lovell, WY", "basis": "caption", "note": "10,000 feet of gain/loss over the Bighorns."},
    {"day": 22, "miles": 126, "start": "Red Lodge, MT", "finish": "Near Bozeman, MT", "basis": "caption", "note": "Very hot and smoky; family pause after this stretch."},
    {"day": 23, "miles": 109, "start": "Near Bozeman, MT", "finish": "Butte, MT", "basis": "caption", "note": "Smoke worsened; hard headwind into Butte."},
    {"day": 24, "miles": 108, "start": "Butte, MT", "finish": "Outside Missoula, MT", "basis": "caption", "note": "Cold morning, smoke, and strong afternoon wind."},
    {"day": 25, "miles": 74, "start": "Outside Missoula, MT", "finish": "Outside Spokane, WA", "basis": "caption", "note": "Trail of the Coeur d'Alenes day after morning rain."},
    {"day": 26, "miles": 66, "start": "Spokane, WA", "finish": "Ellensburg area, WA", "basis": "caption", "note": "Trail closures and fire impacts forced route changes."},
    {"day": 27, "miles": 106, "start": "Ellensburg area, WA", "finish": "Seattle, WA", "basis": "caption", "note": "Finished through Snoqualmie Tunnel and into Seattle."},
]


PLAN_COMMON = [
    {"day": 1, "stop": "Annapolis, MD", "miles": 90, "segment": "common", "note": "Start at Cape Henlopen for the Atlantic tire dip, then ride inland."},
    {"day": 2, "stop": "Williamsport, MD", "miles": 100, "segment": "common", "note": "Joins your friend's eastern corridor and the C&O / GAP approach."},
    {"day": 3, "stop": "Cumberland, MD", "miles": 65, "segment": "common", "note": "Trail-heavy day."},
    {"day": 4, "stop": "South of Pittsburgh / Perryopolis area, PA", "miles": 90, "segment": "common", "note": "GAP-based push west."},
    {"day": 5, "stop": "Steubenville, OH", "miles": 80, "segment": "common", "note": "Ohio River side of the eastern rail-trail network."},
    {"day": 6, "stop": "Millersburg, OH", "miles": 90, "segment": "common", "note": "Hilly Amish-country day."},
    {"day": 7, "stop": "Lilly Chapel / west Columbus, OH", "miles": 120, "segment": "common", "note": "Fast central Ohio mileage if legs feel good."},
    {"day": 8, "stop": "Richmond, IN", "miles": 100, "segment": "common", "note": "Cross into Indiana."},
    {"day": 9, "stop": "Logansport, IN", "miles": 115, "segment": "common", "note": "Longer Indiana day to preserve the 30-day target."},
    {"day": 10, "stop": "Chicago Heights, IL", "miles": 110, "segment": "common", "note": "Urban fringe and weather exposure."},
    {"day": 11, "stop": "Rock Falls, IL", "miles": 110, "segment": "common", "note": "Illinois farm-country day."},
    {"day": 12, "stop": "Cedar Rapids, IA", "miles": 120, "segment": "common", "note": "Cross the Mississippi and settle into Iowa rollers and gravel connectors."},
    {"day": 13, "stop": "Ames, IA", "miles": 105, "segment": "common", "note": "Wind management day."},
    {"day": 14, "stop": "Denison, IA", "miles": 95, "segment": "common", "note": "Friend-proven overnight."},
    {"day": 15, "stop": "Norfolk, NE", "miles": 100, "segment": "common", "note": "Pivot point: decide on the LA desert branch or the SF fallback."},
]


PLAN_LA = [
    {"day": 16, "stop": "Kearney, NE", "miles": 110, "segment": "la", "note": "More direct than staying on the northern GART line."},
    {"day": 17, "stop": "McCook, NE", "miles": 120, "segment": "la", "note": "Plains mileage; stock up before eastern Colorado."},
    {"day": 18, "stop": "Sterling, CO", "miles": 100, "segment": "la", "note": "Enter Colorado on a serviceable but exposed corridor."},
    {"day": 19, "stop": "Denver, CO", "miles": 105, "segment": "la", "note": "Major resupply and weather checkpoint."},
    {"day": 20, "stop": "Silverthorne / Frisco, CO", "miles": 75, "segment": "la", "note": "Shorter day because of the Front Range climb and altitude."},
    {"day": 21, "stop": "Glenwood Springs, CO", "miles": 85, "segment": "la", "note": "I-70 corridor / bike path mix depending exact routing."},
    {"day": 22, "stop": "Grand Junction, CO", "miles": 90, "segment": "la", "note": "Western Colorado services before the desert begins."},
    {"day": 23, "stop": "Green River, UT", "miles": 100, "segment": "la", "note": "Long, exposed desert day; start before sunrise."},
    {"day": 24, "stop": "Richfield, UT", "miles": 120, "segment": "la", "note": "Another big Utah day; heat and water planning are decisive."},
    {"day": 25, "stop": "Cedar City, UT", "miles": 100, "segment": "la", "note": "High-desert riding with services."},
    {"day": 26, "stop": "Mesquite, NV", "miles": 90, "segment": "la", "note": "Good checkpoint before Vegas traffic."},
    {"day": 27, "stop": "Las Vegas, NV", "miles": 80, "segment": "la", "note": "Last big-city service stop."},
    {"day": 28, "stop": "Baker or Barstow, CA", "miles": 95, "segment": "la", "note": "Mojave exposure; if wind is bad, stop in Baker instead of forcing Barstow."},
    {"day": 29, "stop": "Victorville / San Bernardino, CA", "miles": 85, "segment": "la", "note": "Gives you margin if the Mojave day is slower than planned."},
    {"day": 30, "stop": "Santa Monica, CA", "miles": 75, "segment": "la", "note": "Pacific tire dip at the pier."},
]


PLAN_SF = [
    {"day": 16, "stop": "Kearney, NE", "miles": 110, "segment": "sf", "note": "Direct westbound move."},
    {"day": 17, "stop": "McCook, NE", "miles": 120, "segment": "sf", "note": "Plains mileage."},
    {"day": 18, "stop": "Sterling, CO", "miles": 100, "segment": "sf", "note": "Eastern Colorado exposure."},
    {"day": 19, "stop": "Denver, CO", "miles": 105, "segment": "sf", "note": "Decision point before the mountain section."},
    {"day": 20, "stop": "Silverthorne / Frisco, CO", "miles": 75, "segment": "sf", "note": "Shorter altitude day."},
    {"day": 21, "stop": "Glenwood Springs, CO", "miles": 85, "segment": "sf", "note": "Western Express style movement."},
    {"day": 22, "stop": "Grand Junction, CO", "miles": 90, "segment": "sf", "note": "Last major Colorado resupply."},
    {"day": 23, "stop": "Green River, UT", "miles": 100, "segment": "sf", "note": "Start of the long dry western run."},
    {"day": 24, "stop": "Richfield, UT", "miles": 120, "segment": "sf", "note": "Big mileage needed to stay on the 30-day schedule."},
    {"day": 25, "stop": "Milford, UT", "miles": 95, "segment": "sf", "note": "Dry corridor toward Nevada."},
    {"day": 26, "stop": "Ely, NV", "miles": 85, "segment": "sf", "note": "Join the official USBR 50 / US 50 corridor regionally."},
    {"day": 27, "stop": "Eureka or Austin, NV", "miles": 100, "segment": "sf", "note": "Classic Great Basin day; services are sparse and early closures happen."},
    {"day": 28, "stop": "Carson City / South Lake Tahoe", "miles": 110, "segment": "sf", "note": "High-basin to Sierra transition."},
    {"day": 29, "stop": "Sacramento, CA", "miles": 85, "segment": "sf", "note": "Lets you clear the Sierra before the final Bay push."},
    {"day": 30, "stop": "San Francisco, CA", "miles": 85, "segment": "sf", "note": "Pacific finish."},
]

PLAN_DECISION_COMMON = [
    {"day": 1, "stop": "Annapolis, MD", "miles": 90, "segment": "common", "note": "Atlantic start from Cape Henlopen."},
    {"day": 2, "stop": "Williamsport, MD", "miles": 100, "segment": "common", "note": "Join the eastern corridor."},
    {"day": 3, "stop": "Cumberland, MD", "miles": 65, "segment": "common", "note": "C&O / GAP transition."},
    {"day": 4, "stop": "South of Pittsburgh / Perryopolis area, PA", "miles": 90, "segment": "common", "note": "GAP westbound."},
    {"day": 5, "stop": "Steubenville, OH", "miles": 80, "segment": "common", "note": "Ohio River side."},
    {"day": 6, "stop": "Millersburg, OH", "miles": 90, "segment": "common", "note": "Hilly Amish-country day."},
    {"day": 7, "stop": "Lilly Chapel / west Columbus, OH", "miles": 120, "segment": "common", "note": "Fast central Ohio mileage."},
    {"day": 8, "stop": "Richmond, IN", "miles": 100, "segment": "common", "note": "Cross into Indiana."},
    {"day": 9, "stop": "Logansport, IN", "miles": 115, "segment": "common", "note": "Longer Indiana day."},
    {"day": 10, "stop": "Chicago Heights, IL", "miles": 110, "segment": "common", "note": "Urban fringe and weather exposure."},
    {"day": 11, "stop": "Rock Falls, IL", "miles": 110, "segment": "common", "note": "Illinois farm-country day."},
    {"day": 12, "stop": "Cedar Rapids, IA", "miles": 120, "segment": "common", "note": "Cross the Mississippi."},
    {"day": 13, "stop": "Ames, IA", "miles": 105, "segment": "common", "note": "Wind management day."},
    {"day": 14, "stop": "Denison, IA", "miles": 95, "segment": "common", "note": "Decision checkpoint: continue toward the mountains or drop south."},
]

PLAN_MOUNTAIN_BRANCH = [
    {"day": 15, "stop": "Norfolk, NE", "miles": 100, "segment": "mountain", "note": "Late-branch option; preserves the 30-day target."},
    {"day": 16, "stop": "Kearney, NE", "miles": 110, "segment": "mountain", "note": "Direct westbound move."},
    {"day": 17, "stop": "McCook, NE", "miles": 120, "segment": "mountain", "note": "Plains mileage."},
    {"day": 18, "stop": "Sterling, CO", "miles": 100, "segment": "mountain", "note": "Enter Colorado."},
    {"day": 19, "stop": "Denver, CO", "miles": 105, "segment": "mountain", "note": "Major resupply and weather checkpoint."},
    {"day": 20, "stop": "Silverthorne / Frisco, CO", "miles": 75, "segment": "mountain", "note": "High-altitude climb day."},
    {"day": 21, "stop": "Glenwood Springs, CO", "miles": 85, "segment": "mountain", "note": "Mountain corridor; contingent on late-spring conditions."},
    {"day": 22, "stop": "Grand Junction, CO", "miles": 90, "segment": "mountain", "note": "Western Colorado services."},
    {"day": 23, "stop": "Green River, UT", "miles": 100, "segment": "mountain", "note": "Long exposed desert day."},
    {"day": 24, "stop": "Richfield, UT", "miles": 120, "segment": "mountain", "note": "Big Utah mileage."},
    {"day": 25, "stop": "Cedar City, UT", "miles": 100, "segment": "mountain", "note": "High desert."},
    {"day": 26, "stop": "Mesquite, NV", "miles": 90, "segment": "mountain", "note": "Before the Las Vegas traffic."},
    {"day": 27, "stop": "Las Vegas, NV", "miles": 80, "segment": "mountain", "note": "Last major service stop."},
    {"day": 28, "stop": "Baker or Barstow, CA", "miles": 95, "segment": "mountain", "note": "Mojave exposure."},
    {"day": 29, "stop": "Victorville / San Bernardino, CA", "miles": 85, "segment": "mountain", "note": "Margin day if Mojave slows you down."},
    {"day": 30, "stop": "Santa Monica, CA", "miles": 75, "segment": "mountain", "note": "Pacific finish."},
]

PLAN_SOUTHERN_BRANCH = [
    {"day": 15, "stop": "Lincoln, NE", "miles": 125, "segment": "southern", "note": "Early southward pivot; this is the more completion-oriented branch."},
    {"day": 16, "stop": "Hastings, NE", "miles": 106, "segment": "southern", "note": "Keep moving southwest."},
    {"day": 17, "stop": "Smith Center, KS", "miles": 74, "segment": "southern", "note": "Serviceable Kansas day."},
    {"day": 18, "stop": "Great Bend, KS", "miles": 114, "segment": "southern", "note": "Flatter Plains mileage."},
    {"day": 19, "stop": "Dodge City, KS", "miles": 84, "segment": "southern", "note": "Start bending toward Route 66 country."},
    {"day": 20, "stop": "Liberal, KS", "miles": 83, "segment": "southern", "note": "Service stop before the Panhandle."},
    {"day": 21, "stop": "Dalhart, TX", "miles": 113, "segment": "southern", "note": "High-plains mileage."},
    {"day": 22, "stop": "Tucumcari, NM", "miles": 94, "segment": "southern", "note": "Join the Route 66 corridor."},
    {"day": 23, "stop": "Santa Rosa, NM", "miles": 60, "segment": "southern", "note": "Shorter day that helps manage New Mexico wind or fatigue."},
    {"day": 24, "stop": "Albuquerque, NM", "miles": 118, "segment": "southern", "note": "Big service city and bike-shop checkpoint."},
    {"day": 25, "stop": "Grants, NM", "miles": 77, "segment": "southern", "note": "Dry but manageable."},
    {"day": 26, "stop": "Gallup, NM", "miles": 62, "segment": "southern", "note": "High desert, but lower risk than the Colorado mountains."},
    {"day": 27, "stop": "Holbrook, AZ", "miles": 96, "segment": "southern", "note": "Route 66 mileage day."},
    {"day": 28, "stop": "Flagstaff, AZ", "miles": 91, "segment": "southern", "note": "One notable high town, but without the Colorado pass chain."},
    {"day": 29, "stop": "Seligman, AZ", "miles": 75, "segment": "southern", "note": "Stage for western Arizona."},
    {"day": 30, "stop": "Kingman, AZ", "miles": 74, "segment": "southern", "note": "At this point you are still two to three days from LA."},
    {"day": 31, "stop": "Needles, CA", "miles": 62, "segment": "southern", "note": "Cross the Colorado River into California."},
    {"day": 32, "stop": "Barstow, CA", "miles": 145, "segment": "southern", "note": "The hardest desert day on this branch."},
    {"day": 33, "stop": "Santa Monica, CA", "miles": 131, "segment": "southern", "note": "Pacific finish."},
]


COORDS = {
    "Cape Henlopen State Park, DE": [38.7709, -75.1033],
    "Annapolis, MD": [38.9786, -76.4928],
    "Williamsport, MD": [39.5994, -77.8215],
    "Cumberland, MD": [39.6526, -78.7624],
    "South of Pittsburgh / Perryopolis area, PA": [40.0884, -79.7509],
    "Steubenville, OH": [40.3601, -80.6151],
    "Millersburg, OH": [40.5545, -81.9179],
    "Lilly Chapel / west Columbus, OH": [39.8834, -83.4334],
    "Richmond, IN": [39.8287, -84.8899],
    "Logansport, IN": [40.7542, -86.3625],
    "Chicago Heights, IL": [41.5063, -87.6357],
    "Rock Falls, IL": [41.7816, -89.6926],
    "Cedar Rapids, IA": [41.9759, -91.6704],
    "Ames, IA": [42.0268, -93.6170],
    "Denison, IA": [42.0178, -95.3553],
    "Norfolk, NE": [42.0283, -97.4170],
    "Kearney, NE": [40.6995, -99.0819],
    "McCook, NE": [40.2007, -100.6258],
    "Sterling, CO": [40.6255, -103.2077],
    "Denver, CO": [39.7392, -104.9849],
    "Silverthorne / Frisco, CO": [39.5920, -106.0970],
    "Glenwood Springs, CO": [39.5466, -107.3247],
    "Grand Junction, CO": [39.0673, -108.5645],
    "Green River, UT": [38.9952, -110.1617],
    "Richfield, UT": [38.7725, -112.0841],
    "Cedar City, UT": [37.6774, -113.0618],
    "Mesquite, NV": [36.8036, -114.0671],
    "Las Vegas, NV": [36.1674, -115.1484],
    "Baker or Barstow, CA": [35.0800, -116.5500],
    "Victorville / San Bernardino, CA": [34.3917, -117.2948],
    "Santa Monica, CA": [34.0195, -118.4912],
    "Milford, UT": [38.3969, -113.0108],
    "Ely, NV": [39.2481, -114.8917],
    "Eureka or Austin, NV": [39.7250, -116.6900],
    "Carson City / South Lake Tahoe": [39.0490, -119.8420],
    "Sacramento, CA": [38.5811, -121.4939],
    "San Francisco, CA": [37.7879, -122.4075],
    "Lincoln, NE": [40.8089, -96.7078],
    "Hastings, NE": [40.5861, -98.3899],
    "Smith Center, KS": [39.7792, -98.7851],
    "Great Bend, KS": [38.3625, -98.7804],
    "Dodge City, KS": [37.7528, -100.0171],
    "Liberal, KS": [37.0431, -100.9210],
    "Dalhart, TX": [36.0616, -102.5222],
    "Tucumcari, NM": [35.1719, -103.7250],
    "Santa Rosa, NM": [34.9387, -104.6825],
    "Albuquerque, NM": [35.0841, -106.6510],
    "Grants, NM": [35.1473, -107.8514],
    "Gallup, NM": [35.5284, -108.7439],
    "Holbrook, AZ": [34.9037, -110.1593],
    "Flagstaff, AZ": [35.1988, -111.6518],
    "Seligman, AZ": [35.3269, -112.8763],
    "Kingman, AZ": [35.1896, -114.0533],
    "Needles, CA": [34.8383, -114.6039],
    "Barstow, CA": [34.8986, -117.0244],
}


SOURCES = [
    {
        "label": "Friend Instagram",
        "url": INSTAGRAM_URL,
        "note": "Daily captions scraped from the public Instagram API endpoint behind the profile page.",
    },
    {
        "label": "Great American Rail-Trail Route Map",
        "url": "https://www.railstotrails.org/site/greatamericanrailtrail/content/route/",
        "note": "Official route overview from Rails to Trails Conservancy.",
    },
    {
        "label": "Great American Rail-Trail Route Assessment 2025",
        "url": "https://www.railstotrails.org/wp-content/uploads/2025/07/2025-GRTRouteAssessment_Final_Reduced.pdf",
        "note": "RTC's current route assessment PDF; states that the route is 3,700+ miles and more than 55% complete.",
    },
    {
        "label": "Western Express",
        "url": "https://www.adventurecycling.org/routes-and-maps/adventure-cycling-route-network/western-express/",
        "note": "Official ACA page for the Colorado-to-California corridor relevant to the SF fallback.",
    },
    {
        "label": "Bicycle Route 66",
        "url": "https://www.adventurecycling.org/routes-and-maps/adventure-cycling-route-network/bicycle-route-66/",
        "note": "Official ACA page for the Santa Monica finish corridor and desert cautions.",
    },
]


def load_instagram_items() -> list[dict]:
    path = ROOT / "instagram_raw.json"
    return json.loads(path.read_text(encoding="utf-8"))


def caption_lookup(items: list[dict]) -> dict[int, dict]:
    lookup: dict[int, dict] = {}
    for item in items:
        caption = (item.get("caption") or {}).get("text", "")
        first = caption.splitlines()[0] if caption else ""
        if "Day " not in first and "DAY " not in first:
            continue
        token = first.replace("DAY ", "Day ")
        token = token.split("Day ", 1)[1]
        digits = []
        for ch in token:
            if ch.isdigit():
                digits.append(ch)
            else:
                break
        if not digits:
            continue
        day = int("".join(digits))
        lookup[day] = {
            "shortcode": item.get("code"),
            "caption": caption,
            "url": f"https://www.instagram.com/p/{item.get('code')}/" if item.get("code") else INSTAGRAM_URL,
        }
    return lookup


def write_friend_csv(day_posts: dict[int, dict]) -> None:
    path = ROOT / "friend_instagram_daybook.csv"
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["day", "miles", "start", "finish", "basis", "instagram_url", "note", "caption_excerpt"],
        )
        writer.writeheader()
        for row in FRIEND_DAYS:
            post = day_posts.get(row["day"], {})
            caption = post.get("caption", "").replace("\n", " ").strip()
            writer.writerow(
                {
                    "day": row["day"],
                    "miles": row["miles"] if row["miles"] is not None else "",
                    "start": row["start"],
                    "finish": row["finish"],
                    "basis": row["basis"],
                    "instagram_url": post.get("url", INSTAGRAM_URL),
                    "note": row["note"],
                    "caption_excerpt": caption[:280],
                }
            )


def lines_for_plan(plan: list[dict]) -> list[str]:
    out = []
    total = 0
    for row in plan:
        total += row["miles"]
        out.append(
            f"| {row['day']} | {row['stop']} | {row['miles']} | {row['note']} |"
        )
    out.append(f"\nApproximate subtotal: **{total} miles**")
    return out


def write_markdown() -> None:
    common_total = sum(x["miles"] for x in PLAN_COMMON)
    la_total = common_total + sum(x["miles"] for x in PLAN_LA)
    sf_total = common_total + sum(x["miles"] for x in PLAN_SF)

    md = [
        "# Bike Trip Planning Brief",
        "",
        "## Bottom Line",
        "",
        f"- The official Great American Rail-Trail is **3,700+ miles** and more than **55% complete**, so a strict coast-to-coast rail-trail ride does **not** fit your 30-day, 80-100 mile/day target.",
        f"- Your friend's DC-to-Seattle ride was **2,632 miles in 26 riding days**, which is much closer to your pace target and is the best practical eastern template.",
        "- The cleanest compromise is: use the eastern rail-trail / friend spine through Nebraska, then branch southwest for LA or continue west for an SF fallback.",
        "",
        "## Recommended Start",
        "",
        "- Start at **Cape Henlopen State Park, Delaware**. It gives you an actual Atlantic tire dip, is reachable from the Philly area, and is also the eastern terminus corridor used in the planned USBR 50 concept.",
        "",
        "## Why This Is Not A Pure GART Plan",
        "",
        "- The Great American Rail-Trail trends toward **Wyoming, Montana, Idaho, and Washington**.",
        "- That northern line is excellent for a Seattle finish, but it pulls you away from both Los Angeles and San Francisco if you only have 30 days.",
        "- For your goals, the rail-trail is best used as the **eastern backbone**, not as the full end-to-end line.",
        "",
        "## 30-Day Shared Spine",
        "",
        "| Day | Overnight | Target Miles | Why It Works |",
        "| --- | --- | ---: | --- |",
        *lines_for_plan(PLAN_COMMON),
        "",
        "## LA Primary Finish",
        "",
        "- This is the higher-risk branch because of heat, water gaps, desert wind, and the Mojave finish.",
        "- Use it only if the Colorado high country and the Utah/Nevada/California forecast look stable when you reach Nebraska/Colorado.",
        "",
        "| Day | Overnight | Target Miles | Why It Works |",
        "| --- | --- | ---: | --- |",
        *lines_for_plan(PLAN_LA),
        f"\nApproximate 30-day total from Cape Henlopen to Santa Monica: **{la_total} miles**",
        "",
        "## SF Fallback",
        "",
        "- This is still demanding, but it gives you a cleaner official-western framework via the Western Express / US 50 region instead of forcing the Mojave finish.",
        "- If Sierra weather, wildfire smoke, or timing look bad near Nevada, Sacramento is the sensible backup finish before adding a Bay connector.",
        "",
        "| Day | Overnight | Target Miles | Why It Works |",
        "| --- | --- | ---: | --- |",
        *lines_for_plan(PLAN_SF),
        f"\nApproximate 30-day total from Cape Henlopen to San Francisco: **{sf_total} miles**",
        "",
        "## Western Reality Check",
        "",
        "- **LA branch**: feasible only if you are willing to accept several 100+ mile days and adapt overnight stops to heat and wind.",
        "- **SF branch**: still hard, but operationally stronger because the finish is less dependent on the Mojave segment.",
        "- If you arrive in Colorado behind schedule, take the SF branch or reduce the finish target to Sacramento.",
        "",
        "## Friend-Derived Data",
        "",
        "- See `friend_instagram_daybook.csv` for the scraped day-by-day record from your friend's posts.",
        "",
        "## Sources",
        "",
    ]

    for source in SOURCES:
        md.append(f"- [{source['label']}]({source['url']}): {source['note']}")

    (ROOT / "bike_trip_plan.md").write_text("\n".join(md), encoding="utf-8")


def write_decision_markdown() -> None:
    mountain_total = sum(x["miles"] for x in PLAN_DECISION_COMMON) + sum(x["miles"] for x in PLAN_MOUNTAIN_BRANCH)
    southern_total = sum(x["miles"] for x in PLAN_DECISION_COMMON) + sum(x["miles"] for x in PLAN_SOUTHERN_BRANCH)
    md = [
        "# Westbound Decision Brief",
        "",
        "## Purpose",
        "",
        "- This page carries two western options at once so you can decide on the road instead of locking the whole trip in before departure.",
        "- The realistic decision point is **Denison, Iowa (Day 14)**. If you wait much longer, the lower-risk southern branch becomes too long to preserve your 30-day target.",
        "",
        "## Shared Eastern Spine To Decision Point",
        "",
        "| Day | Overnight | Target Miles | Notes |",
        "| --- | --- | ---: | --- |",
    ]
    for row in PLAN_DECISION_COMMON:
        md.append(f"| {row['day']} | {row['stop']} | {row['miles']} | {row['note']} |")
    md += [
        "",
        "## Option A: Mountain LA Branch",
        "",
        "- Better match for a **30-day Atlantic-to-LA finish**.",
        "- Higher risk because it depends on Colorado mountain conditions, late snow, and the Glenwood Canyon timing window.",
        "",
        "| Day | Overnight | Target Miles | Notes |",
        "| --- | --- | ---: | --- |",
    ]
    for row in PLAN_MOUNTAIN_BRANCH:
        md.append(f"| {row['day']} | {row['stop']} | {row['miles']} | {row['note']} |")
    md += [
        f"",
        f"Approximate total: **{mountain_total} miles in 30 days**",
        "",
        "## Option B: Southern Completion Branch",
        "",
        "- Lower weather and pass risk overall.",
        "- More compatible with a first tour and a loaded touring bike.",
        "- The tradeoff is distance: on this schedule it lands in **33 days**, not 30.",
        "",
        "| Day | Overnight | Target Miles | Notes |",
        "| --- | --- | ---: | --- |",
    ]
    for row in PLAN_SOUTHERN_BRANCH:
        md.append(f"| {row['day']} | {row['stop']} | {row['miles']} | {row['note']} |")
    md += [
        f"",
        f"Approximate total: **{southern_total} miles in 33 days**",
        "",
        "## Practical Read",
        "",
        "- If you are healthy, on schedule, and Colorado conditions look stable when you reach Iowa/Nebraska, the mountain branch preserves the 30-day goal.",
        "- If weather, bike issues, fatigue, or risk tolerance argue against Colorado, the southern branch is the more robust completion route, but you should expect roughly three extra days.",
    ]
    (ROOT / "bike_trip_decision.md").write_text("\n".join(md), encoding="utf-8")


def map_points(plan: list[dict]) -> list[dict]:
    return [
        {
            "day": row["day"],
            "stop": row["stop"],
            "miles": row["miles"],
            "segment": row["segment"],
            "note": row["note"],
            "lat": COORDS[row["stop"]][0],
            "lon": COORDS[row["stop"]][1],
        }
        for row in plan
    ]


def branch_points(plan: list[dict]) -> list[dict]:
    return [
        {
            "day": 0,
            "stop": "Cape Henlopen State Park, DE",
            "miles": 0,
            "segment": "common",
            "note": "Atlantic tire dip start.",
            "lat": COORDS["Cape Henlopen State Park, DE"][0],
            "lon": COORDS["Cape Henlopen State Park, DE"][1],
        }
    ] + map_points(PLAN_COMMON) + map_points(plan)


def route_cache_path() -> Path:
    return ROOT / "bike_trip_route_cache.json"


def load_route_cache() -> dict:
    path = route_cache_path()
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def save_route_cache(cache: dict) -> None:
    route_cache_path().write_text(json.dumps(cache, indent=2), encoding="utf-8")


def lodging_cache_path() -> Path:
    return ROOT / "bike_trip_lodging_cache.json"


def load_lodging_cache() -> dict:
    path = lodging_cache_path()
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def save_lodging_cache(cache: dict) -> None:
    lodging_cache_path().write_text(json.dumps(cache, indent=2), encoding="utf-8")


def osrm_route(start: dict, finish: dict, cache: dict) -> dict:
    key = f"{start['stop']}|||{finish['stop']}"
    if key in cache:
        return cache[key]

    coords = f"{start['lon']},{start['lat']};{finish['lon']},{finish['lat']}"
    query = urlencode({"overview": "full", "geometries": "geojson", "steps": "false"})
    url = f"{OSRM_BASE}{coords}?{query}"
    with urlopen(url, timeout=60) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    route = data["routes"][0]
    payload = {
        "distance_miles": round(route["distance"] / 1609.344, 1),
        "duration_hours": round(route["duration"] / 3600, 1),
        "geometry": route["geometry"],
    }
    cache[key] = payload
    time.sleep(0.2)
    return payload


def routed_segments(points: list[dict], color: str, branch_name: str, cache: dict) -> list[dict]:
    segments = []
    for start, finish in zip(points, points[1:]):
        route = osrm_route(start, finish, cache)
        segments.append(
            {
                "branch": branch_name,
                "color": color,
                "start_day": start["day"],
                "finish_day": finish["day"],
                "start_stop": start["stop"],
                "finish_stop": finish["stop"],
                "target_miles": finish["miles"],
                "mapped_miles": route["distance_miles"],
                "mapped_hours": route["duration_hours"],
                "note": finish["note"],
                "geometry": route["geometry"],
            }
        )
    return segments


def fetch_lodging_for_stop(stop: dict, cache: dict, radius_m: int = 16000) -> list[dict]:
    key = f"{stop['stop']}|||{radius_m}"
    if key in cache:
        return cache[key]

    query = f"""
[out:json][timeout:60];
(
  node(around:{radius_m},{stop['lat']},{stop['lon']})["tourism"~"hotel|motel|guest_house|hostel"];
  way(around:{radius_m},{stop['lat']},{stop['lon']})["tourism"~"hotel|motel|guest_house|hostel"];
  node(around:{radius_m},{stop['lat']},{stop['lon']})["building"="hotel"];
  way(around:{radius_m},{stop['lat']},{stop['lon']})["building"="hotel"];
  node(around:{radius_m},{stop['lat']},{stop['lon']})["amenity"="hotel"];
  way(around:{radius_m},{stop['lat']},{stop['lon']})["amenity"="hotel"];
);
out center;
"""
    req = Request(
        OVERPASS_URL,
        data=query.encode("utf-8"),
        headers={"User-Agent": "bike-trip-planner"},
    )
    with urlopen(req, timeout=90) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    lodgings = []
    for el in data.get("elements", []):
        tags = el.get("tags", {})
        lat = el.get("lat", el.get("center", {}).get("lat"))
        lon = el.get("lon", el.get("center", {}).get("lon"))
        if lat is None or lon is None:
            continue
        name = tags.get("name")
        if not name:
            continue
        lodgings.append(
            {
                "name": name,
                "lat": lat,
                "lon": lon,
                "kind": tags.get("tourism") or tags.get("amenity") or tags.get("building", "lodging"),
                "website": tags.get("website") or tags.get("contact:website") or "",
                "phone": tags.get("phone") or tags.get("contact:phone") or "",
            }
        )

    unique = []
    seen = set()
    for item in lodgings:
        sig = (item["name"], round(item["lat"], 4), round(item["lon"], 4))
        if sig in seen:
            continue
        seen.add(sig)
        unique.append(item)

    cache[key] = unique[:25]
    time.sleep(0.3)
    return cache[key]


def add_lodging(points: list[dict], cache: dict) -> list[dict]:
    out = []
    for point in points:
        row = dict(point)
        row["lodging"] = fetch_lodging_for_stop(point, cache)
        out.append(row)
    return out


def write_routed_map() -> None:
    cache = load_route_cache()
    common_points = branch_points([])
    la_points = branch_points(PLAN_LA)
    sf_points = branch_points(PLAN_SF)

    common_segments = routed_segments(common_points, "#d97706", "Shared", cache)
    la_segments = routed_segments(la_points[len(common_points) - 1 :], "#dc2626", "LA", cache)
    sf_segments = routed_segments(sf_points[len(common_points) - 1 :], "#2563eb", "SF", cache)
    save_route_cache(cache)

    points = {
        "common": common_points,
        "la": la_points,
        "sf": sf_points,
    }
    segments = {
        "common": common_segments,
        "la": la_segments,
        "sf": sf_segments,
    }

    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Bike Trip Routed Options</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
  <style>
    html, body, #map {{ height: 100%; margin: 0; }}
    .panel {{
      position: absolute;
      top: 12px;
      right: 12px;
      z-index: 1000;
      width: 360px;
      max-width: calc(100% - 24px);
      background: rgba(255, 248, 240, 0.96);
      border: 1px solid #caa57a;
      border-radius: 12px;
      padding: 14px 16px;
      font: 14px/1.4 Georgia, serif;
      box-shadow: 0 10px 24px rgba(0, 0, 0, 0.18);
    }}
    .panel h1 {{ margin: 0 0 8px; font-size: 18px; }}
    .panel p {{ margin: 0 0 8px; }}
    .panel button {{
      margin: 6px 6px 0 0;
      border: 1px solid #8b6b46;
      background: #fff8f0;
      border-radius: 999px;
      padding: 6px 10px;
      cursor: pointer;
      font: inherit;
    }}
    .panel button.active {{ background: #f4d9b5; }}
    .key {{ display: flex; gap: 10px; flex-wrap: wrap; margin-top: 8px; }}
    .chip {{ display: inline-flex; align-items: center; gap: 6px; }}
    .swatch {{ width: 12px; height: 12px; border-radius: 99px; display: inline-block; }}
  </style>
</head>
<body>
  <div id="map"></div>
  <div class="panel">
    <h1>Routed Cross-Country Plan</h1>
    <p>This version follows mapped cycling-road geometry segment by segment instead of drawing straight stop-to-stop lines.</p>
    <p>Routing source: OSRM cycling profile on OpenStreetMap data. This is much closer to a real ride line, but it is still not a substitute for final ACA / DOT cue-sheet checks.</p>
    <div>
      <button id="toggle-common" class="active">Shared Spine</button>
      <button id="toggle-la" class="active">LA Branch</button>
      <button id="toggle-sf" class="active">SF Branch</button>
    </div>
    <div class="key">
      <span class="chip"><span class="swatch" style="background:#d97706"></span>Shared</span>
      <span class="chip"><span class="swatch" style="background:#dc2626"></span>LA</span>
      <span class="chip"><span class="swatch" style="background:#2563eb"></span>SF</span>
    </div>
  </div>
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
  <script>
    const points = {json.dumps(points)};
    const segments = {json.dumps(segments)};

    const map = L.map('map').setView([39.5, -98.35], 5);
    L.tileLayer('https://tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
      maxZoom: 18,
      attribution: '&copy; OpenStreetMap contributors'
    }}).addTo(map);

    const layers = {{}};

    function markerFor(point, color) {{
      return L.circleMarker([point.lat, point.lon], {{
        radius: point.day === 0 ? 6 : 4,
        color,
        fillColor: color,
        fillOpacity: 0.95,
        weight: 1
      }}).bindPopup(
        `<strong>Day ${{point.day}}</strong><br>${{point.stop}}<br>${{point.miles}} target miles<br>${{point.note}}`
      );
    }}

    function segmentLayerSet(name, color) {{
      const group = L.layerGroup();
      for (const seg of segments[name]) {{
        const geo = L.geoJSON(seg.geometry, {{
          style: {{
            color,
            weight: 4,
            opacity: 0.9
          }}
        }});
        geo.bindPopup(
          `<strong>${{seg.branch}} route</strong><br>Day ${{seg.start_day}} to Day ${{seg.finish_day}}<br>${{seg.start_stop}} to ${{seg.finish_stop}}<br>Target: ${{seg.target_miles}} mi<br>Mapped: ${{seg.mapped_miles}} mi<br>Estimated moving time: ${{seg.mapped_hours}} h<br>${{seg.note}}`
        );
        group.addLayer(geo);
      }}
      const pointColor = color;
      for (const point of points[name]) {{
        group.addLayer(markerFor(point, pointColor));
      }}
      return group;
    }}

    layers.common = segmentLayerSet('common', '#d97706');
    layers.la = segmentLayerSet('la', '#dc2626');
    layers.sf = segmentLayerSet('sf', '#2563eb');

    layers.common.addTo(map);
    layers.la.addTo(map);
    layers.sf.addTo(map);

    function hookToggle(id, key) {{
      const button = document.getElementById(id);
      button.addEventListener('click', () => {{
        if (map.hasLayer(layers[key])) {{
          map.removeLayer(layers[key]);
          button.classList.remove('active');
        }} else {{
          layers[key].addTo(map);
          button.classList.add('active');
        }}
      }});
    }}

    hookToggle('toggle-common', 'common');
    hookToggle('toggle-la', 'la');
    hookToggle('toggle-sf', 'sf');
  </script>
</body>
</html>
"""
    (ROOT / "bike_trip_map_routed.html").write_text(html, encoding="utf-8")


def write_lodging_map() -> None:
    cache = load_lodging_cache()
    common_points = add_lodging(branch_points([]), cache)
    la_points = add_lodging(branch_points(PLAN_LA), cache)
    sf_points = add_lodging(branch_points(PLAN_SF), cache)
    save_lodging_cache(cache)

    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Bike Trip Lodging Stops</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
  <style>
    html, body, #map {{ height: 100%; margin: 0; }}
    .panel {{
      position: absolute;
      top: 12px;
      right: 12px;
      z-index: 1000;
      width: 370px;
      max-width: calc(100% - 24px);
      background: rgba(255, 248, 240, 0.97);
      border: 1px solid #caa57a;
      border-radius: 12px;
      padding: 14px 16px;
      font: 14px/1.4 Georgia, serif;
      box-shadow: 0 10px 24px rgba(0, 0, 0, 0.18);
    }}
    .panel h1 {{ margin: 0 0 8px; font-size: 18px; }}
    .panel p {{ margin: 0 0 8px; }}
    .panel button {{
      margin: 6px 6px 0 0;
      border: 1px solid #8b6b46;
      background: #fff8f0;
      border-radius: 999px;
      padding: 6px 10px;
      cursor: pointer;
      font: inherit;
    }}
    .panel button.active {{ background: #f4d9b5; }}
  </style>
</head>
<body>
  <div id="map"></div>
  <div class="panel">
    <h1>Overnight Stops + Lodging</h1>
    <p>Each overnight stop includes nearby mapped lodging pulled from OpenStreetMap POI data within roughly 10 miles.</p>
    <p>This is useful for planning, but you should still verify availability, prices, and whether a place still operates.</p>
    <div>
      <button id="toggle-common" class="active">Shared Spine</button>
      <button id="toggle-la" class="active">LA Branch</button>
      <button id="toggle-sf" class="active">SF Branch</button>
      <button id="toggle-lodging" class="active">Lodging POIs</button>
    </div>
  </div>
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
  <script>
    const common = {json.dumps(common_points)};
    const la = {json.dumps(la_points)};
    const sf = {json.dumps(sf_points)};

    const map = L.map('map').setView([39.5, -98.35], 5);
    L.tileLayer('https://tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
      maxZoom: 18,
      attribution: '&copy; OpenStreetMap contributors'
    }}).addTo(map);

    const groups = {{
      common: L.layerGroup().addTo(map),
      la: L.layerGroup().addTo(map),
      sf: L.layerGroup().addTo(map),
      lodging: L.layerGroup().addTo(map)
    }};

    function colorFor(name) {{
      return name === 'common' ? '#d97706' : (name === 'la' ? '#dc2626' : '#2563eb');
    }}

    function drawStopSet(name, points) {{
      const color = colorFor(name);
      const latlngs = points.map(p => [p.lat, p.lon]);
      L.polyline(latlngs, {{ color, weight: 3, opacity: 0.85 }}).addTo(groups[name]);
      points.forEach(point => {{
        const lodgingLines = point.lodging.slice(0, 8).map(l =>
          `<li>${{l.name}}${{l.kind ? ` (${{l.kind}})` : ''}}</li>`
        ).join('');
        const lodgingHtml = lodgingLines ? `<ul>${{lodgingLines}}</ul>` : '<em>No mapped lodging returned nearby.</em>';
        L.circleMarker([point.lat, point.lon], {{
          radius: point.day === 0 ? 6 : 5,
          color,
          fillColor: color,
          fillOpacity: 0.95
        }}).addTo(groups[name]).bindPopup(
          `<strong>Day ${{point.day}}</strong><br>${{point.stop}}<br>${{point.miles}} target miles<br>${{point.note}}<br><br><strong>Nearby lodging:</strong>${{lodgingHtml}}`
        );
      }});
    }}

    const lodgingSeen = new Set();
    function drawLodging(points) {{
      points.forEach(point => {{
        point.lodging.forEach(l => {{
          const key = `${{l.name}}|${{l.lat.toFixed(4)}}|${{l.lon.toFixed(4)}}`;
          if (lodgingSeen.has(key)) return;
          lodgingSeen.add(key);
          const website = l.website ? `<br><a href="${{l.website}}" target="_blank" rel="noreferrer">${{l.website}}</a>` : '';
          const phone = l.phone ? `<br>${{l.phone}}` : '';
          L.circleMarker([l.lat, l.lon], {{
            radius: 4,
            color: '#444',
            fillColor: '#fff',
            fillOpacity: 0.9,
            weight: 1
          }}).addTo(groups.lodging).bindPopup(
            `<strong>${{l.name}}</strong><br>${{l.kind}}${{website}}${{phone}}`
          );
        }});
      }});
    }}

    drawStopSet('common', common);
    drawStopSet('la', la);
    drawStopSet('sf', sf);
    drawLodging(common);
    drawLodging(la);
    drawLodging(sf);

    function hookToggle(id, key) {{
      const button = document.getElementById(id);
      button.addEventListener('click', () => {{
        if (map.hasLayer(groups[key])) {{
          map.removeLayer(groups[key]);
          button.classList.remove('active');
        }} else {{
          groups[key].addTo(map);
          button.classList.add('active');
        }}
      }});
    }}

    hookToggle('toggle-common', 'common');
    hookToggle('toggle-la', 'la');
    hookToggle('toggle-sf', 'sf');
    hookToggle('toggle-lodging', 'lodging');
  </script>
</body>
</html>
"""
    (ROOT / "bike_trip_map_lodging.html").write_text(html, encoding="utf-8")


def write_decision_map() -> None:
    cache = load_route_cache()
    common_points = [
        {
            "day": 0,
            "stop": "Cape Henlopen State Park, DE",
            "miles": 0,
            "segment": "common",
            "note": "Atlantic tire dip start.",
            "lat": COORDS["Cape Henlopen State Park, DE"][0],
            "lon": COORDS["Cape Henlopen State Park, DE"][1],
        }
    ] + map_points(PLAN_DECISION_COMMON)
    mountain_points = common_points + map_points(PLAN_MOUNTAIN_BRANCH)
    southern_points = common_points + map_points(PLAN_SOUTHERN_BRANCH)

    common_segments = routed_segments(common_points, "#d97706", "Shared", cache)
    mountain_segments = routed_segments(mountain_points[len(common_points) - 1 :], "#b91c1c", "Mountain", cache)
    southern_segments = routed_segments(southern_points[len(common_points) - 1 :], "#1d4ed8", "Southern", cache)
    save_route_cache(cache)

    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Bike Trip Decision Routes</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
  <style>
    html, body, #map {{ height: 100%; margin: 0; }}
    .panel {{
      position: absolute;
      top: 12px;
      right: 12px;
      z-index: 1000;
      width: 380px;
      max-width: calc(100% - 24px);
      background: rgba(255, 248, 240, 0.96);
      border: 1px solid #caa57a;
      border-radius: 12px;
      padding: 14px 16px;
      font: 14px/1.4 Georgia, serif;
      box-shadow: 0 10px 24px rgba(0, 0, 0, 0.18);
    }}
    .panel h1 {{ margin: 0 0 8px; font-size: 18px; }}
    .panel p {{ margin: 0 0 8px; }}
    .panel button {{
      margin: 6px 6px 0 0;
      border: 1px solid #8b6b46;
      background: #fff8f0;
      border-radius: 999px;
      padding: 6px 10px;
      cursor: pointer;
      font: inherit;
    }}
    .panel button.active {{ background: #f4d9b5; }}
  </style>
</head>
<body>
  <div id="map"></div>
  <div class="panel">
    <h1>Mountain vs Southern Split</h1>
    <p>The common route runs to Denison, Iowa. That is the meaningful on-road decision point.</p>
    <p>Red preserves the 30-day target but uses the Colorado/Utah mountain-desert line. Blue is the lower-risk completion branch but lands closer to 33 days.</p>
    <div>
      <button id="toggle-common" class="active">Shared</button>
      <button id="toggle-mountain" class="active">Mountain</button>
      <button id="toggle-southern" class="active">Southern</button>
    </div>
  </div>
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
  <script>
    const commonPoints = {json.dumps(common_points)};
    const mountainPoints = {json.dumps(mountain_points)};
    const southernPoints = {json.dumps(southern_points)};
    const commonSegments = {json.dumps(common_segments)};
    const mountainSegments = {json.dumps(mountain_segments)};
    const southernSegments = {json.dumps(southern_segments)};

    const map = L.map('map').setView([39.2, -97.7], 5);
    L.tileLayer('https://tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
      maxZoom: 18,
      attribution: '&copy; OpenStreetMap contributors'
    }}).addTo(map);

    const groups = {{
      common: L.layerGroup().addTo(map),
      mountain: L.layerGroup().addTo(map),
      southern: L.layerGroup().addTo(map)
    }};

    function addSegments(group, color, segments) {{
      for (const seg of segments) {{
        const geo = L.geoJSON(seg.geometry, {{ style: {{ color, weight: 4, opacity: 0.9 }} }});
        geo.bindPopup(
          `<strong>${{seg.branch}} branch</strong><br>Day ${{seg.start_day}} to Day ${{seg.finish_day}}<br>${{seg.start_stop}} to ${{seg.finish_stop}}<br>Target: ${{seg.target_miles}} mi<br>Mapped: ${{seg.mapped_miles}} mi<br>${{seg.note}}`
        );
        geo.addTo(group);
      }}
    }}

    function addMarkers(group, color, points) {{
      for (const point of points) {{
        L.circleMarker([point.lat, point.lon], {{
          radius: point.day === 14 ? 6 : 4,
          color,
          fillColor: color,
          fillOpacity: 0.95
        }}).addTo(group).bindPopup(
          `<strong>Day ${{point.day}}</strong><br>${{point.stop}}<br>${{point.miles}} target miles<br>${{point.note}}`
        );
      }}
    }}

    addSegments(groups.common, '#d97706', commonSegments);
    addMarkers(groups.common, '#d97706', commonPoints);
    addSegments(groups.mountain, '#b91c1c', mountainSegments);
    addMarkers(groups.mountain, '#b91c1c', mountainPoints.slice(commonPoints.length - 1));
    addSegments(groups.southern, '#1d4ed8', southernSegments);
    addMarkers(groups.southern, '#1d4ed8', southernPoints.slice(commonPoints.length - 1));

    function hookToggle(id, key) {{
      const button = document.getElementById(id);
      button.addEventListener('click', () => {{
        if (map.hasLayer(groups[key])) {{
          map.removeLayer(groups[key]);
          button.classList.remove('active');
        }} else {{
          groups[key].addTo(map);
          button.classList.add('active');
        }}
      }});
    }}

    hookToggle('toggle-common', 'common');
    hookToggle('toggle-mountain', 'mountain');
    hookToggle('toggle-southern', 'southern');
  </script>
</body>
</html>
"""
    (ROOT / "bike_trip_map_decision.html").write_text(html, encoding="utf-8")


def write_map() -> None:
    common = branch_points([])
    la = branch_points(PLAN_LA)
    sf = branch_points(PLAN_SF)

    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Bike Trip Route Options</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
  <style>
    html, body, #map {{ height: 100%; margin: 0; }}
    .panel {{
      position: absolute;
      top: 12px;
      right: 12px;
      z-index: 1000;
      width: 340px;
      max-width: calc(100% - 24px);
      background: rgba(255, 248, 240, 0.95);
      border: 1px solid #caa57a;
      border-radius: 12px;
      padding: 14px 16px;
      font: 14px/1.4 Georgia, serif;
      box-shadow: 0 10px 24px rgba(0, 0, 0, 0.18);
    }}
    .panel h1 {{ margin: 0 0 8px; font-size: 18px; }}
    .panel p {{ margin: 0 0 8px; }}
    .key {{ display: flex; gap: 10px; flex-wrap: wrap; margin-top: 8px; }}
    .chip {{ display: inline-flex; align-items: center; gap: 6px; }}
    .swatch {{ width: 12px; height: 12px; border-radius: 99px; display: inline-block; }}
  </style>
</head>
<body>
  <div id="map"></div>
  <div class="panel">
    <h1>Cross-Country Bike Plan</h1>
    <p>Common eastern spine from Cape Henlopen to Norfolk, then two western finish options.</p>
    <p>Orange = shared route. Red = Los Angeles branch. Blue = San Francisco fallback.</p>
    <div class="key">
      <span class="chip"><span class="swatch" style="background:#d97706"></span>Shared</span>
      <span class="chip"><span class="swatch" style="background:#dc2626"></span>LA</span>
      <span class="chip"><span class="swatch" style="background:#2563eb"></span>SF</span>
    </div>
  </div>
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
  <script>
    const common = {json.dumps(common)};
    const la = {json.dumps(la)};
    const sf = {json.dumps(sf)};

    const map = L.map('map').setView([39.5, -98.35], 5);
    L.tileLayer('https://tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
      maxZoom: 18,
      attribution: '&copy; OpenStreetMap contributors'
    }}).addTo(map);

    function draw(points, color) {{
      const latlngs = points.map(p => [p.lat, p.lon]);
      L.polyline(latlngs, {{ color, weight: 4, opacity: 0.9 }}).addTo(map);
      points.forEach(p => {{
        L.circleMarker([p.lat, p.lon], {{
          radius: 5,
          color,
          fillColor: color,
          fillOpacity: 0.9
        }}).addTo(map).bindPopup(
          `<strong>Day ${{p.day}}</strong><br>${{p.stop}}<br>${{p.miles}} target miles<br>${{p.note}}`
        );
      }});
    }}

    draw(common, '#d97706');
    draw(la, '#dc2626');
    draw(sf, '#2563eb');
  </script>
</body>
</html>
"""
    (ROOT / "bike_trip_map.html").write_text(html, encoding="utf-8")


def main() -> None:
    items = load_instagram_items()
    day_posts = caption_lookup(items)
    write_friend_csv(day_posts)
    write_markdown()
    write_decision_markdown()
    write_map()
    write_routed_map()
    write_lodging_map()
    write_decision_map()


if __name__ == "__main__":
    main()
