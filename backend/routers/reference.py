"""
Reference data endpoints - IAB categories, device types, video placements, etc.
"""
from fastapi import APIRouter

router = APIRouter(tags=["Reference Data"])

# ==================== REFERENCE DATA ====================

IAB_CATEGORIES = {
    "IAB1": "Arts & Entertainment",
    "IAB1-1": "Books & Literature",
    "IAB1-2": "Celebrity Fan/Gossip",
    "IAB1-3": "Fine Art",
    "IAB1-4": "Humor",
    "IAB1-5": "Movies",
    "IAB1-6": "Music",
    "IAB1-7": "Television",
    "IAB2": "Automotive",
    "IAB2-1": "Auto Parts",
    "IAB2-2": "Auto Repair",
    "IAB2-3": "Buying/Selling Cars",
    "IAB2-4": "Car Culture",
    "IAB2-5": "Certified Pre-Owned",
    "IAB2-6": "Convertible",
    "IAB2-7": "Coupe",
    "IAB2-8": "Crossover",
    "IAB3": "Business",
    "IAB3-1": "Advertising",
    "IAB3-2": "Agriculture",
    "IAB3-3": "Biotech/Biomedical",
    "IAB3-4": "Business Software",
    "IAB3-5": "Construction",
    "IAB4": "Careers",
    "IAB4-1": "Career Planning",
    "IAB4-2": "College",
    "IAB4-3": "Financial Aid",
    "IAB4-4": "Job Fairs",
    "IAB4-5": "Job Search",
    "IAB5": "Education",
    "IAB5-1": "7-12 Education",
    "IAB5-2": "Adult Education",
    "IAB5-3": "Art History",
    "IAB6": "Family & Parenting",
    "IAB6-1": "Adoption",
    "IAB6-2": "Babies & Toddlers",
    "IAB6-3": "Daycare/Pre School",
    "IAB7": "Health & Fitness",
    "IAB7-1": "Exercise",
    "IAB7-2": "ADD",
    "IAB7-3": "AIDS/HIV",
    "IAB8": "Food & Drink",
    "IAB8-1": "American Cuisine",
    "IAB8-2": "Barbecues & Grilling",
    "IAB8-3": "Cajun/Creole",
    "IAB9": "Hobbies & Interests",
    "IAB9-1": "Art/Technology",
    "IAB9-2": "Arts & Crafts",
    "IAB9-3": "Beadwork",
    "IAB10": "Home & Garden",
    "IAB10-1": "Appliances",
    "IAB10-2": "Entertaining",
    "IAB10-3": "Environmental Safety",
    "IAB11": "Law, Government & Politics",
    "IAB11-1": "Immigration",
    "IAB11-2": "Legal Issues",
    "IAB11-3": "U.S. Government Resources",
    "IAB12": "News",
    "IAB12-1": "International News",
    "IAB12-2": "National News",
    "IAB12-3": "Local News",
    "IAB13": "Personal Finance",
    "IAB13-1": "Beginning Investing",
    "IAB13-2": "Credit/Debt & Loans",
    "IAB13-3": "Financial News",
    "IAB14": "Society",
    "IAB14-1": "Dating",
    "IAB14-2": "Divorce Support",
    "IAB14-3": "Gay Life",
    "IAB15": "Science",
    "IAB15-1": "Astrology",
    "IAB15-2": "Biology",
    "IAB15-3": "Chemistry",
    "IAB16": "Pets",
    "IAB16-1": "Aquariums",
    "IAB16-2": "Birds",
    "IAB16-3": "Cats",
    "IAB17": "Sports",
    "IAB17-1": "Auto Racing",
    "IAB17-2": "Baseball",
    "IAB17-3": "Bicycling",
    "IAB18": "Style & Fashion",
    "IAB18-1": "Beauty",
    "IAB18-2": "Body Art",
    "IAB18-3": "Fashion",
    "IAB19": "Technology & Computing",
    "IAB19-1": "3-D Graphics",
    "IAB19-2": "Animation",
    "IAB19-3": "Antivirus Software",
    "IAB20": "Travel",
    "IAB20-1": "Adventure Travel",
    "IAB20-2": "Africa",
    "IAB20-3": "Air Travel",
    "IAB21": "Real Estate",
    "IAB21-1": "Apartments",
    "IAB21-2": "Architects",
    "IAB21-3": "Buying/Selling Homes",
    "IAB22": "Shopping",
    "IAB22-1": "Contests & Freebies",
    "IAB22-2": "Couponing",
    "IAB22-3": "Comparison",
    "IAB23": "Religion & Spirituality",
    "IAB23-1": "Alternative Religions",
    "IAB23-2": "Atheism/Agnosticism",
    "IAB23-3": "Buddhism",
    "IAB24": "Uncategorized",
    "IAB25": "Non-Standard Content",
    "IAB26": "Illegal Content"
}

VIDEO_PLACEMENTS = {
    1: "In-Stream (Pre/Mid/Post-roll)",
    2: "In-Banner",
    3: "In-Article",
    4: "In-Feed",
    5: "Interstitial/Slider/Floating"
}

VIDEO_PLCMT = {
    1: "In-Stream (Sound On)",
    2: "Accompanying Content",
    3: "Interstitial",
    4: "No Content/Standalone"
}

VIDEO_PROTOCOLS = {
    1: "VAST 1.0",
    2: "VAST 2.0",
    3: "VAST 3.0",
    4: "VAST 1.0 Wrapper",
    5: "VAST 2.0 Wrapper",
    6: "VAST 3.0 Wrapper",
    7: "VAST 4.0",
    8: "VAST 4.0 Wrapper",
    9: "DAAST 1.0",
    10: "DAAST 1.0 Wrapper",
    11: "VAST 4.1",
    12: "VAST 4.1 Wrapper",
    13: "VAST 4.2",
    14: "VAST 4.2 Wrapper"
}

VIDEO_MIMES = [
    {"value": "video/mp4", "label": "MP4 (video/mp4)"},
    {"value": "video/webm", "label": "WebM (video/webm)"},
    {"value": "video/ogg", "label": "OGG (video/ogg)"},
    {"value": "video/x-flv", "label": "FLV (video/x-flv)"},
    {"value": "video/3gpp", "label": "3GPP (video/3gpp)"},
    {"value": "application/javascript", "label": "VPAID JS"},
    {"value": "application/x-shockwave-flash", "label": "SWF Flash"}
]

POD_POSITIONS = {
    1: "First Position",
    2: "Last Position",
    3: "First or Last",
    4: "First and Last",
    0: "Any Position"
}

AD_PLACEMENTS = [
    {"value": "in_app", "label": "In-App"},
    {"value": "in_stream", "label": "In-Stream"},
    {"value": "in_stream_non_skip", "label": "In-Stream (Non-Skippable)"},
    {"value": "in_banner", "label": "In-Banner"},
    {"value": "in_article", "label": "In-Article"},
    {"value": "in_feed", "label": "In-Feed"},
    {"value": "interstitial", "label": "Interstitial"},
    {"value": "side_banner", "label": "Side Banner"},
    {"value": "above_fold", "label": "Above Fold"},
    {"value": "below_fold", "label": "Below Fold"},
    {"value": "sticky", "label": "Sticky"},
    {"value": "floating", "label": "Floating"},
    {"value": "rewarded", "label": "Rewarded"}
]

DEVICE_TYPES = {
    1: "Mobile/Tablet",
    2: "Personal Computer",
    3: "Connected TV",
    4: "Phone",
    5: "Tablet",
    6: "Connected Device",
    7: "Set Top Box"
}

CONNECTION_TYPES = {
    0: "Unknown",
    1: "Ethernet",
    2: "WiFi",
    3: "Cellular (Unknown)",
    4: "Cellular 2G",
    5: "Cellular 3G",
    6: "Cellular 4G",
    7: "Cellular 5G"
}

CARRIERS_BY_COUNTRY = {
    "USA": [
        {"name": "Verizon", "mcc": "311", "mnc": "480"},
        {"name": "AT&T", "mcc": "310", "mnc": "410"},
        {"name": "T-Mobile", "mcc": "310", "mnc": "260"},
        {"name": "Sprint", "mcc": "312", "mnc": "530"},
        {"name": "US Cellular", "mcc": "311", "mnc": "580"}
    ],
    "GBR": [
        {"name": "EE", "mcc": "234", "mnc": "30"},
        {"name": "O2 UK", "mcc": "234", "mnc": "10"},
        {"name": "Vodafone UK", "mcc": "234", "mnc": "15"},
        {"name": "Three UK", "mcc": "234", "mnc": "20"}
    ],
    "DEU": [
        {"name": "Telekom", "mcc": "262", "mnc": "01"},
        {"name": "Vodafone DE", "mcc": "262", "mnc": "02"},
        {"name": "O2 Germany", "mcc": "262", "mnc": "07"}
    ],
    "FRA": [
        {"name": "Orange France", "mcc": "208", "mnc": "01"},
        {"name": "SFR", "mcc": "208", "mnc": "10"},
        {"name": "Bouygues", "mcc": "208", "mnc": "20"},
        {"name": "Free Mobile", "mcc": "208", "mnc": "15"}
    ],
    "IND": [
        {"name": "Jio", "mcc": "405", "mnc": "857"},
        {"name": "Airtel", "mcc": "404", "mnc": "10"},
        {"name": "Vodafone Idea", "mcc": "404", "mnc": "20"},
        {"name": "BSNL", "mcc": "404", "mnc": "72"}
    ],
    "BRA": [
        {"name": "Claro", "mcc": "724", "mnc": "05"},
        {"name": "Vivo", "mcc": "724", "mnc": "06"},
        {"name": "TIM", "mcc": "724", "mnc": "04"},
        {"name": "Oi", "mcc": "724", "mnc": "31"}
    ],
    "JPN": [
        {"name": "NTT Docomo", "mcc": "440", "mnc": "10"},
        {"name": "au (KDDI)", "mcc": "440", "mnc": "50"},
        {"name": "SoftBank", "mcc": "440", "mnc": "20"},
        {"name": "Rakuten", "mcc": "440", "mnc": "11"}
    ],
    "CAN": [
        {"name": "Rogers", "mcc": "302", "mnc": "720"},
        {"name": "Bell", "mcc": "302", "mnc": "610"},
        {"name": "Telus", "mcc": "302", "mnc": "220"},
        {"name": "Freedom", "mcc": "302", "mnc": "490"}
    ],
    "AUS": [
        {"name": "Telstra", "mcc": "505", "mnc": "01"},
        {"name": "Optus", "mcc": "505", "mnc": "02"},
        {"name": "Vodafone AU", "mcc": "505", "mnc": "03"}
    ]
}

COUNTRIES = [
    {"code": "USA", "name": "United States"},
    {"code": "GBR", "name": "United Kingdom"},
    {"code": "CAN", "name": "Canada"},
    {"code": "AUS", "name": "Australia"},
    {"code": "DEU", "name": "Germany"},
    {"code": "FRA", "name": "France"},
    {"code": "JPN", "name": "Japan"},
    {"code": "BRA", "name": "Brazil"},
    {"code": "IND", "name": "India"},
    {"code": "CHN", "name": "China"},
    {"code": "KOR", "name": "South Korea"},
    {"code": "MEX", "name": "Mexico"},
    {"code": "ESP", "name": "Spain"},
    {"code": "ITA", "name": "Italy"},
    {"code": "NLD", "name": "Netherlands"},
    {"code": "RUS", "name": "Russia"},
    {"code": "SGP", "name": "Singapore"},
    {"code": "HKG", "name": "Hong Kong"},
    {"code": "TWN", "name": "Taiwan"},
    {"code": "THA", "name": "Thailand"},
    {"code": "IDN", "name": "Indonesia"},
    {"code": "MYS", "name": "Malaysia"},
    {"code": "PHL", "name": "Philippines"},
    {"code": "VNM", "name": "Vietnam"},
    {"code": "ARE", "name": "United Arab Emirates"},
    {"code": "SAU", "name": "Saudi Arabia"},
    {"code": "ZAF", "name": "South Africa"},
    {"code": "NGA", "name": "Nigeria"},
    {"code": "EGY", "name": "Egypt"},
    {"code": "TUR", "name": "Turkey"},
    {"code": "POL", "name": "Poland"},
    {"code": "SWE", "name": "Sweden"},
    {"code": "NOR", "name": "Norway"},
    {"code": "DNK", "name": "Denmark"},
    {"code": "FIN", "name": "Finland"},
    {"code": "BEL", "name": "Belgium"},
    {"code": "AUT", "name": "Austria"},
    {"code": "CHE", "name": "Switzerland"},
    {"code": "PRT", "name": "Portugal"},
    {"code": "GRC", "name": "Greece"},
    {"code": "CZE", "name": "Czech Republic"},
    {"code": "ROU", "name": "Romania"},
    {"code": "HUN", "name": "Hungary"},
    {"code": "IRL", "name": "Ireland"},
    {"code": "NZL", "name": "New Zealand"},
    {"code": "ARG", "name": "Argentina"},
    {"code": "CHL", "name": "Chile"},
    {"code": "COL", "name": "Colombia"},
    {"code": "PER", "name": "Peru"},
    {"code": "VEN", "name": "Venezuela"},
    {"code": "PAK", "name": "Pakistan"},
    {"code": "BGD", "name": "Bangladesh"},
    {"code": "ISR", "name": "Israel"},
    {"code": "UKR", "name": "Ukraine"},
    {"code": "KEN", "name": "Kenya"}
]


# ==================== ENDPOINTS ====================

@router.get("/reference/iab-categories")
async def get_iab_categories():
    """Get IAB content categories"""
    return IAB_CATEGORIES


@router.get("/reference/video-placements")
async def get_video_placements():
    """Get video placement types"""
    return VIDEO_PLACEMENTS


@router.get("/reference/video-plcmt")
async def get_video_plcmt():
    """Get video plcmt values (OpenRTB 2.6)"""
    return VIDEO_PLCMT


@router.get("/reference/video-protocols")
async def get_video_protocols():
    """Get supported video protocols"""
    return VIDEO_PROTOCOLS


@router.get("/reference/video-mimes")
async def get_video_mimes():
    """Get supported video MIME types"""
    return VIDEO_MIMES


@router.get("/reference/pod-positions")
async def get_pod_positions():
    """Get pod sequence positions"""
    return POD_POSITIONS


@router.get("/reference/ad-placements")
async def get_ad_placements():
    """Get ad placement options"""
    return AD_PLACEMENTS


@router.get("/reference/device-types")
async def get_device_types():
    """Get device types"""
    return DEVICE_TYPES


@router.get("/reference/connection-types")
async def get_connection_types():
    """Get connection types"""
    return CONNECTION_TYPES


@router.get("/reference/carriers/{country_code}")
async def get_carriers_by_country(country_code: str):
    """Get carriers by country code"""
    country_code = country_code.upper()
    if country_code in CARRIERS_BY_COUNTRY:
        return CARRIERS_BY_COUNTRY[country_code]
    return []


@router.get("/reference/carriers")
async def get_all_carriers():
    """Get all carriers grouped by country"""
    return CARRIERS_BY_COUNTRY


@router.get("/reference/all")
async def get_all_reference_data():
    """Get all reference data in one call"""
    return {
        "iab_categories": IAB_CATEGORIES,
        "video_placements": VIDEO_PLACEMENTS,
        "video_plcmt": VIDEO_PLCMT,
        "video_protocols": VIDEO_PROTOCOLS,
        "video_mimes": VIDEO_MIMES,
        "pod_positions": POD_POSITIONS,
        "ad_placements": AD_PLACEMENTS,
        "device_types": DEVICE_TYPES,
        "connection_types": CONNECTION_TYPES,
        "carriers": CARRIERS_BY_COUNTRY,
        "countries": COUNTRIES
    }
