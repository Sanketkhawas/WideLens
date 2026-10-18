"""Shared constants for WideLens (Nagpur, Maharashtra)."""

CITY = "Nagpur"
STATE = "Maharashtra"
CITY_CENTER = (21.1458, 79.0882)

# area, latitude, longitude, population (approx. ward-level, illustrative),
# avg_rent (Rs / sq ft / month, illustrative), competitor_count (illustrative)
NAGPUR_AREAS = [
    ("Sitabuldi",      21.1458, 79.0882, 52000, 150, 14),
    ("Dharampeth",     21.1380, 79.0650, 61000, 140, 12),
    ("Manish Nagar",   21.0930, 79.0650, 72000,  55,  3),
    ("Pratap Nagar",   21.1180, 79.0560, 66000,  70,  5),
    ("Trimurti Nagar", 21.1140, 79.0620, 58000,  72,  5),
    ("Somalwada",      21.1000, 79.0700, 47000,  60,  3),
    ("Khamla",         21.1210, 79.0700, 44000,  85,  6),
    ("Nandanvan",      21.1200, 79.1250, 63000,  50,  4),
    ("Sakkardara",     21.1140, 79.1230, 51000,  52,  4),
    ("Laxmi Nagar",    21.1250, 79.0640, 39000, 105,  8),
    ("Narendra Nagar", 21.1089, 79.0740, 42000,  68,  4),
    ("Sadar",          21.1640, 79.0830, 36000, 110,  9),
    ("Ramdaspeth",     21.1370, 79.0750, 33000, 135, 10),
    ("Bajaj Nagar",    21.1280, 79.0620, 28000, 115,  7),
    ("Medical Square", 21.1230, 79.0950, 46000,  80,  6),
    ("Civil Lines",    21.1520, 79.0780, 30000, 130,  8),
    ("Dighori",        21.0990, 79.1100, 49000,  48,  3),
    ("Ambazari",       21.1350, 79.0450, 27000, 100,  5),
    ("Mahal",          21.1500, 79.1050, 54000,  75,  7),
    ("Itwari",         21.1490, 79.1180, 57000,  60,  5),
    ("Gandhibagh",     21.1480, 79.1100, 41000,  95,  8),
    ("Besa",           21.0700, 79.1000, 45000,  38,  2),
    ("Beltarodi",      21.0800, 79.1230, 43000,  40,  2),
    ("Jaripatka",      21.1810, 79.1170, 38000,  45,  3),
    ("Mankapur",       21.1740, 79.0640, 34000,  65,  4),
    ("Wadi",           21.1450, 79.0200, 52000,  42,  3),
    ("Katol Road",     21.1700, 79.0450, 40000,  50,  3),
    ("Kamptee Road",   21.1800, 79.1250, 37000,  44,  3),
    ("Koradi Road",    21.2000, 79.1100, 26000,  35,  2),
    ("Hingna",         21.1000, 78.9900, 48000,  33,  2),
    ("MIHAN",          21.0300, 79.0200, 22000,  45,  1),
]

# store footprint & economics used for the payback estimate (all editable in the UI)
DEFAULT_STORE_SQFT = 2500
DEFAULT_CATCHMENT_KM = 3.0
DEFAULT_CAPTURE_RATE = 0.20     # share of not-yet-served catchment spend a new store wins
DEFAULT_MARGIN = 0.12           # net margin before rent
MIN_STORE_GAP_KM = 2.5          # closer than this to an existing store = cannibalisation risk

DEFAULT_WEIGHTS = {
    "demand": 0.30,        # customers / revenue in catchment
    "gap": 0.25,           # demand not served by an existing store
    "spend": 0.10,         # avg spend per customer
    "competition": 0.15,   # fewer rivals = better
    "rent": 0.10,          # lower rent = better
    "population": 0.10,    # headroom for growth
}
FACTOR_LABELS = {
    "demand": "Customer demand nearby",
    "gap": "Unserved demand (far from existing stores)",
    "spend": "Spend per customer",
    "competition": "Low competition",
    "rent": "Affordable rent",
    "population": "Population headroom",
}
