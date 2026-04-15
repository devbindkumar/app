import { 
  Megaphone, Target, DollarSign, Image, Settings, 
  Users, Clock, Shield, BarChart3, Globe, 
  Smartphone, Monitor, Tv, Radio, MapPin, Check
} from "lucide-react";

// ==================== STEP CONFIGURATION ====================

export const STEPS = [
  { id: 1, key: "overview", title: "Campaign overview", icon: Megaphone },
  { id: 2, key: "budget", title: "Budget & bidding", icon: DollarSign },
  { id: 3, key: "targeting", title: "Targeting", icon: Target },
  { id: 4, key: "audience", title: "Audience", icon: Users },
  { id: 5, key: "creatives", title: "Creatives", icon: Image },
  { id: 6, key: "schedule", title: "Schedule & pacing", icon: Clock },
  { id: 7, key: "safety", title: "Brand safety", icon: Shield },
  { id: 8, key: "measurement", title: "Measurement", icon: BarChart3 },
];

// ==================== CAMPAIGN GOALS & KPIs ====================

export const CAMPAIGN_GOALS = [
  { value: "brand_awareness", label: "Brand Awareness", desc: "Increase visibility" },
  { value: "reach", label: "Reach", desc: "Maximize unique users" },
  { value: "traffic", label: "Traffic", desc: "Drive website visits" },
  { value: "engagement", label: "Engagement", desc: "Increase interactions" },
  { value: "app_installs", label: "App Installs", desc: "Drive app downloads" },
  { value: "video_views", label: "Video Views", desc: "Maximize video consumption" },
  { value: "lead_generation", label: "Lead Generation", desc: "Collect leads" },
  { value: "conversions", label: "Conversions", desc: "Drive purchases/actions" },
];

export const KPI_TYPES = [
  { value: "cpm", label: "CPM", desc: "Cost per 1,000 impressions" },
  { value: "cpc", label: "CPC", desc: "Cost per click" },
  { value: "cpa", label: "CPA", desc: "Cost per acquisition" },
  { value: "cpv", label: "CPV", desc: "Cost per view" },
  { value: "cpcv", label: "CPCV", desc: "Cost per completed view" },
  { value: "cps", label: "CPS", desc: "Cost per session/visit" },
  { value: "cptv", label: "CPTV", desc: "Cost per true view" },
  { value: "vcpm", label: "vCPM", desc: "Viewable CPM" },
  { value: "roas", label: "ROAS", desc: "Return on ad spend" },
];

// ==================== BIDDING & BUDGET ====================

export const BIDDING_STRATEGIES = [
  { value: "manual_cpm", label: "Manual CPM", desc: "Set your own CPM bid", basis: "cpm" },
  { value: "manual_cpc", label: "Manual CPC", desc: "Set your own CPC bid", basis: "cpc" },
  { value: "target_cpa", label: "Target CPA", desc: "Optimize for conversions", basis: "cpm" },
  { value: "target_roas", label: "Target ROAS", desc: "Optimize for return", basis: "cpm" },
  { value: "target_cpcv", label: "Target CPCV", desc: "Optimize for video completions", basis: "cpm" },
  { value: "target_cps", label: "Target CPS", desc: "Optimize for sessions/visits", basis: "cpm" },
  { value: "maximize_conversions", label: "Maximize Conversions", desc: "Auto-optimize for conversions", basis: "cpm" },
  { value: "maximize_clicks", label: "Maximize Clicks", desc: "Auto-optimize for clicks", basis: "cpm" },
  { value: "maximize_completed_views", label: "Maximize Completed Views", desc: "Auto-optimize for video completions", basis: "cpm" },
];

export const BID_PRICING_TYPES = [
  { value: "cpm", label: "CPM - Cost per 1,000 impressions" },
  { value: "cpc", label: "CPC - Cost per click" },
  { value: "cpa", label: "CPA - Cost per action" },
  { value: "cpv", label: "CPV - Cost per view" },
  { value: "cpcv", label: "CPCV - Cost per completed view" },
  { value: "cps", label: "CPS - Cost per session" },
];

export const CURRENCIES = [
  { value: "USD", label: "$ USD - US Dollar" },
  { value: "AED", label: "AED - UAE Dirham" },
  { value: "INR", label: "Rs INR - Indian Rupee" },
  { value: "EUR", label: "EUR - Euro" },
  { value: "GBP", label: "GBP - British Pound" },
];

export const PACING_TYPES = [
  { value: "even", label: "Even", desc: "Spread evenly throughout the day" },
  { value: "accelerated", label: "Accelerated", desc: "Spend budget as fast as possible" },
  { value: "front_loaded", label: "Front-loaded", desc: "Spend more early in campaign" },
];

// ==================== INVENTORY & ENVIRONMENT ====================

export const INVENTORY_SOURCES = [
  { value: "open_exchange", label: "Open Exchange", icon: Globe, desc: "Programmatic open market" },
  { value: "pmp", label: "Private Marketplace", icon: Shield, desc: "Curated deals" },
  { value: "pg", label: "Programmatic Guaranteed", icon: Check, desc: "Reserved inventory" },
  { value: "youtube", label: "YouTube", icon: Tv, desc: "Video ads on YouTube" },
  { value: "gdn", label: "Google Display Network", icon: Monitor, desc: "Display across Google" },
  { value: "ctv", label: "Connected TV", icon: Tv, desc: "Streaming TV ads" },
  { value: "audio", label: "Audio", icon: Radio, desc: "Podcast & streaming audio" },
];

export const ENVIRONMENTS = [
  { value: "web", label: "Web", icon: Monitor },
  { value: "app", label: "Mobile App", icon: Smartphone },
  { value: "ctv", label: "Connected TV", icon: Tv },
  { value: "dooh", label: "Digital Out-of-Home", icon: MapPin },
];

// ==================== DEMOGRAPHICS ====================

export const AGE_RANGES = ["18-24", "25-34", "35-44", "45-54", "55-64", "65+"];
export const GENDERS = ["male", "female", "unknown"];
export const INCOME_SEGMENTS = ["low", "medium", "high", "affluent"];
export const PARENTAL_STATUSES = ["parent", "not_parent"];

export const LANGUAGES = [
  { code: "en", name: "English" }, { code: "es", name: "Spanish" },
  { code: "fr", name: "French" }, { code: "de", name: "German" },
  { code: "pt", name: "Portuguese" }, { code: "zh", name: "Chinese" },
  { code: "ja", name: "Japanese" }, { code: "ko", name: "Korean" },
  { code: "ar", name: "Arabic" }, { code: "hi", name: "Hindi" },
  { code: "ru", name: "Russian" }, { code: "it", name: "Italian" },
  { code: "nl", name: "Dutch" }, { code: "pl", name: "Polish" },
  { code: "tr", name: "Turkish" }, { code: "vi", name: "Vietnamese" },
  { code: "th", name: "Thai" }, { code: "id", name: "Indonesian" },
  { code: "ms", name: "Malay" }, { code: "tl", name: "Filipino" },
];

// ==================== DEVICE & TECHNICAL ====================

export const DEVICE_TYPES = [
  { value: 4, label: "Phone", icon: Smartphone },
  { value: 5, label: "Tablet", icon: Monitor },
  { value: 2, label: "Desktop", icon: Monitor },
  { value: 3, label: "Connected TV", icon: Tv },
];

export const OS_LIST = [
  { value: "Android", label: "Android" },
  { value: "iOS", label: "iOS" },
  { value: "Windows", label: "Windows" },
  { value: "macOS", label: "macOS" },
  { value: "Linux", label: "Linux" },
];

export const OS_VERSIONS = {
  Android: ["Android 14", "Android 13", "Android 12", "Android 11", "Android 10", "Android 9", "Android 8"],
  iOS: ["iOS 18", "iOS 17", "iOS 16", "iOS 15", "iOS 14", "iOS 13"],
  Windows: ["Windows 11", "Windows 10", "Windows 8", "Windows 7"],
  macOS: ["macOS 14", "macOS 13", "macOS 12", "macOS 11"],
};

export const BROWSERS = [
  "Chrome", "Safari", "Firefox", "Edge", "Opera", 
  "Samsung Internet", "UC Browser", "Brave", "IE", "Other/Unknown"
];

export const CONNECTION_SPEEDS = [
  { value: "2g", label: "2G" },
  { value: "3g", label: "3G" },
  { value: "4g", label: "4G/LTE" },
  { value: "5g", label: "5G" },
  { value: "wifi", label: "WiFi" },
];

// ==================== DEVICE MAKES & MODELS ====================

export const DEVICE_MAKES = [
  { value: "Apple", label: "Apple" },
  { value: "Samsung", label: "Samsung" },
  { value: "Google", label: "Google" },
  { value: "Xiaomi", label: "Xiaomi" },
  { value: "OnePlus", label: "OnePlus" },
  { value: "Oppo", label: "Oppo" },
  { value: "Vivo", label: "Vivo" },
  { value: "Realme", label: "Realme" },
  { value: "Huawei", label: "Huawei" },
  { value: "Motorola", label: "Motorola" },
  { value: "Nokia", label: "Nokia" },
  { value: "Sony", label: "Sony" },
  { value: "LG", label: "LG" },
  { value: "Asus", label: "Asus" },
  { value: "Lenovo", label: "Lenovo" },
  { value: "HP", label: "HP" },
  { value: "Dell", label: "Dell" },
  { value: "Microsoft", label: "Microsoft" },
  { value: "Acer", label: "Acer" },
  { value: "TCL", label: "TCL" },
  { value: "Honor", label: "Honor" },
  { value: "Nothing", label: "Nothing" },
  { value: "iQOO", label: "iQOO" },
  { value: "Poco", label: "Poco" },
];

export const DEVICE_MODELS = {
  Apple: [
    "iPhone 15 Pro Max", "iPhone 15 Pro", "iPhone 15 Plus", "iPhone 15",
    "iPhone 14 Pro Max", "iPhone 14 Pro", "iPhone 14 Plus", "iPhone 14",
    "iPhone 13 Pro Max", "iPhone 13 Pro", "iPhone 13", "iPhone 13 Mini",
    "iPhone 12 Pro Max", "iPhone 12 Pro", "iPhone 12", "iPhone 12 Mini",
    "iPhone SE (3rd Gen)", "iPhone SE (2nd Gen)",
    "iPad Pro 12.9", "iPad Pro 11", "iPad Air", "iPad Mini", "iPad"
  ],
  Samsung: [
    "Galaxy S24 Ultra", "Galaxy S24+", "Galaxy S24",
    "Galaxy S23 Ultra", "Galaxy S23+", "Galaxy S23",
    "Galaxy S22 Ultra", "Galaxy S22+", "Galaxy S22",
    "Galaxy Z Fold 5", "Galaxy Z Flip 5", "Galaxy Z Fold 4", "Galaxy Z Flip 4",
    "Galaxy A54", "Galaxy A34", "Galaxy A24", "Galaxy A14",
    "Galaxy M54", "Galaxy M34", "Galaxy M14",
    "Galaxy Tab S9", "Galaxy Tab S8", "Galaxy Tab A8"
  ],
  Google: [
    "Pixel 8 Pro", "Pixel 8", "Pixel 8a",
    "Pixel 7 Pro", "Pixel 7", "Pixel 7a",
    "Pixel 6 Pro", "Pixel 6", "Pixel 6a",
    "Pixel Fold", "Pixel Tablet"
  ],
  Xiaomi: [
    "14 Ultra", "14 Pro", "14",
    "13 Ultra", "13 Pro", "13", "13T Pro", "13T",
    "Redmi Note 13 Pro+", "Redmi Note 13 Pro", "Redmi Note 13",
    "Redmi 13C", "Redmi 12", "Redmi A3",
    "Pad 6", "Pad 5"
  ],
  OnePlus: [
    "12", "12R", "11", "11R",
    "Open", "Nord 3", "Nord CE 3", "Nord N30"
  ],
  Oppo: [
    "Find X7 Ultra", "Find X7", "Find X6 Pro",
    "Reno 11 Pro", "Reno 11", "Reno 10 Pro+",
    "A79", "A58", "A38"
  ],
  Vivo: [
    "X100 Pro", "X100", "X90 Pro",
    "V30 Pro", "V30", "V29 Pro",
    "Y100", "Y56"
  ],
  Realme: [
    "GT 5 Pro", "GT 5", "GT 3",
    "12 Pro+", "12 Pro", "12",
    "Narzo 60 Pro", "Narzo 60", "C55"
  ],
  Huawei: [
    "Mate 60 Pro", "Mate 60", "P60 Pro", "P60",
    "Nova 12 Pro", "Nova 12"
  ],
  Motorola: [
    "Edge 40 Pro", "Edge 40", "Edge 30 Ultra",
    "Razr 40 Ultra", "Razr 40",
    "G84", "G54", "G34"
  ],
  Nokia: [
    "G42", "G22", "C32", "C22"
  ],
  Sony: [
    "Xperia 1 V", "Xperia 5 V", "Xperia 10 V"
  ],
  Microsoft: [
    "Surface Pro 9", "Surface Pro 8", "Surface Laptop 5",
    "Surface Go 3", "Surface Duo 2"
  ],
  Honor: [
    "Magic 6 Pro", "Magic 6", "Magic V2",
    "90 Pro", "90", "X9b"
  ],
  Nothing: [
    "Phone 2", "Phone 1", "Phone 2a"
  ],
  iQOO: [
    "12", "11", "Neo 9 Pro", "Neo 9", "Z9"
  ],
  Poco: [
    "F6 Pro", "F6", "X6 Pro", "X6", "M6 Pro"
  ]
};

// ==================== GEO TARGETING ====================

export const COUNTRIES = [
  { code: "USA", name: "United States" }, { code: "GBR", name: "United Kingdom" },
  { code: "CAN", name: "Canada" }, { code: "AUS", name: "Australia" },
  { code: "DEU", name: "Germany" }, { code: "FRA", name: "France" },
  { code: "JPN", name: "Japan" }, { code: "IND", name: "India" },
  { code: "BRA", name: "Brazil" }, { code: "MEX", name: "Mexico" },
  { code: "ESP", name: "Spain" }, { code: "ITA", name: "Italy" },
  { code: "NLD", name: "Netherlands" }, { code: "CHE", name: "Switzerland" },
  { code: "SWE", name: "Sweden" }, { code: "NOR", name: "Norway" },
  { code: "DNK", name: "Denmark" }, { code: "FIN", name: "Finland" },
  { code: "BEL", name: "Belgium" }, { code: "AUT", name: "Austria" },
  { code: "POL", name: "Poland" }, { code: "PRT", name: "Portugal" },
  { code: "IRL", name: "Ireland" }, { code: "NZL", name: "New Zealand" },
  { code: "SGP", name: "Singapore" }, { code: "HKG", name: "Hong Kong" },
  { code: "KOR", name: "South Korea" }, { code: "TWN", name: "Taiwan" },
  { code: "MYS", name: "Malaysia" }, { code: "THA", name: "Thailand" },
  { code: "IDN", name: "Indonesia" }, { code: "PHL", name: "Philippines" },
  { code: "VNM", name: "Vietnam" }, { code: "ARE", name: "UAE" },
  { code: "SAU", name: "Saudi Arabia" }, { code: "ISR", name: "Israel" },
  { code: "ZAF", name: "South Africa" }, { code: "EGY", name: "Egypt" },
  { code: "NGA", name: "Nigeria" }, { code: "KEN", name: "Kenya" },
  { code: "ARG", name: "Argentina" }, { code: "CHL", name: "Chile" },
  { code: "COL", name: "Colombia" }, { code: "PER", name: "Peru" },
  { code: "RUS", name: "Russia" }, { code: "TUR", name: "Turkey" },
  { code: "PAK", name: "Pakistan" }, { code: "BGD", name: "Bangladesh" },
  { code: "UKR", name: "Ukraine" }, { code: "CZE", name: "Czech Republic" },
];

export const COUNTRY_STATES = {
  USA: ["California", "Texas", "Florida", "New York", "Illinois", "Pennsylvania", "Ohio", "Georgia", "North Carolina", "Michigan"],
  IND: [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh", 
    "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", 
    "Karnataka", "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", 
    "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Punjab", 
    "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura", 
    "Uttar Pradesh", "Uttarakhand", "West Bengal",
    // Union Territories
    "Andaman and Nicobar Islands", "Chandigarh", "Dadra and Nagar Haveli and Daman and Diu", 
    "Delhi", "Jammu and Kashmir", "Ladakh", "Lakshadweep", "Puducherry"
  ],
  GBR: ["England", "Scotland", "Wales", "Northern Ireland"],
  CAN: ["Ontario", "Quebec", "British Columbia", "Alberta", "Manitoba", "Saskatchewan"],
  AUS: ["New South Wales", "Victoria", "Queensland", "Western Australia", "South Australia"],
};

// India State-wise Cities with Tier Classification
export const INDIA_STATE_CITIES = {
  "Andhra Pradesh": {
    tier1: ["Visakhapatnam", "Vijayawada"],
    tier2: ["Guntur", "Nellore", "Kurnool", "Rajahmundry", "Tirupati", "Kakinada"],
    tier3: ["Kadapa", "Anantapur", "Eluru", "Ongole", "Vizianagaram", "Machilipatnam"]
  },
  "Arunachal Pradesh": {
    tier1: [],
    tier2: ["Itanagar"],
    tier3: ["Naharlagun", "Pasighat", "Tawang"]
  },
  "Assam": {
    tier1: ["Guwahati"],
    tier2: ["Silchar", "Dibrugarh", "Jorhat", "Nagaon"],
    tier3: ["Tezpur", "Tinsukia", "Bongaigaon", "Dhubri"]
  },
  "Bihar": {
    tier1: ["Patna"],
    tier2: ["Gaya", "Bhagalpur", "Muzaffarpur", "Darbhanga"],
    tier3: ["Purnia", "Arrah", "Begusarai", "Katihar", "Munger", "Chhapra"]
  },
  "Chhattisgarh": {
    tier1: ["Raipur"],
    tier2: ["Bhilai", "Bilaspur", "Korba", "Durg"],
    tier3: ["Rajnandgaon", "Raigarh", "Jagdalpur", "Ambikapur"]
  },
  "Goa": {
    tier1: [],
    tier2: ["Panaji", "Margao", "Vasco da Gama"],
    tier3: ["Mapusa", "Ponda", "Bicholim"]
  },
  "Gujarat": {
    tier1: ["Ahmedabad", "Surat", "Vadodara", "Rajkot"],
    tier2: ["Bhavnagar", "Jamnagar", "Junagadh", "Gandhinagar", "Anand"],
    tier3: ["Nadiad", "Morbi", "Mehsana", "Bharuch", "Vapi", "Navsari", "Veraval"]
  },
  "Haryana": {
    tier1: ["Gurugram", "Faridabad"],
    tier2: ["Panipat", "Ambala", "Yamunanagar", "Rohtak", "Hisar", "Karnal"],
    tier3: ["Sonipat", "Panchkula", "Bhiwani", "Sirsa", "Bahadurgarh", "Jind"]
  },
  "Himachal Pradesh": {
    tier1: [],
    tier2: ["Shimla", "Dharamshala", "Solan"],
    tier3: ["Mandi", "Palampur", "Baddi", "Nahan", "Kullu", "Hamirpur"]
  },
  "Jharkhand": {
    tier1: ["Ranchi", "Jamshedpur"],
    tier2: ["Dhanbad", "Bokaro", "Hazaribagh"],
    tier3: ["Deoghar", "Giridih", "Ramgarh", "Phusro", "Medininagar"]
  },
  "Karnataka": {
    tier1: ["Bengaluru", "Mysuru"],
    tier2: ["Hubli-Dharwad", "Mangaluru", "Belagavi", "Davangere", "Ballari"],
    tier3: ["Shimoga", "Tumkur", "Gulbarga", "Udupi", "Hassan", "Bidar", "Raichur"]
  },
  "Kerala": {
    tier1: ["Kochi", "Thiruvananthapuram"],
    tier2: ["Kozhikode", "Thrissur", "Kollam", "Kannur", "Alappuzha"],
    tier3: ["Kottayam", "Palakkad", "Malappuram", "Kasaragod", "Pathanamthitta"]
  },
  "Madhya Pradesh": {
    tier1: ["Indore", "Bhopal"],
    tier2: ["Jabalpur", "Gwalior", "Ujjain", "Sagar"],
    tier3: ["Dewas", "Satna", "Ratlam", "Rewa", "Murwara", "Singrauli", "Burhanpur"]
  },
  "Maharashtra": {
    tier1: ["Mumbai", "Pune", "Nagpur"],
    tier2: ["Nashik", "Aurangabad", "Solapur", "Thane", "Kolhapur", "Navi Mumbai"],
    tier3: ["Amravati", "Nanded", "Sangli", "Malegaon", "Jalgaon", "Akola", "Latur", "Dhule", "Ahmednagar"]
  },
  "Manipur": {
    tier1: [],
    tier2: ["Imphal"],
    tier3: ["Thoubal", "Bishnupur", "Churachandpur"]
  },
  "Meghalaya": {
    tier1: [],
    tier2: ["Shillong"],
    tier3: ["Tura", "Jowai", "Nongstoin"]
  },
  "Mizoram": {
    tier1: [],
    tier2: ["Aizawl"],
    tier3: ["Lunglei", "Champhai", "Serchhip"]
  },
  "Nagaland": {
    tier1: [],
    tier2: ["Dimapur", "Kohima"],
    tier3: ["Mokokchung", "Tuensang", "Wokha"]
  },
  "Odisha": {
    tier1: ["Bhubaneswar"],
    tier2: ["Cuttack", "Rourkela", "Berhampur", "Sambalpur"],
    tier3: ["Puri", "Balasore", "Bhadrak", "Baripada", "Jharsuguda", "Jeypore", "Angul"]
  },
  "Punjab": {
    tier1: ["Ludhiana", "Amritsar"],
    tier2: ["Jalandhar", "Patiala", "Bathinda"],
    tier3: ["Mohali", "Pathankot", "Hoshiarpur", "Moga", "Batala", "Abohar", "Malerkotla"]
  },
  "Rajasthan": {
    tier1: ["Jaipur", "Jodhpur"],
    tier2: ["Kota", "Bikaner", "Ajmer", "Udaipur", "Bhilwara"],
    tier3: ["Alwar", "Bharatpur", "Sikar", "Pali", "Sri Ganganagar", "Beawar", "Kishangarh"]
  },
  "Sikkim": {
    tier1: [],
    tier2: ["Gangtok"],
    tier3: ["Namchi", "Gyalshing", "Mangan"]
  },
  "Tamil Nadu": {
    tier1: ["Chennai", "Coimbatore", "Madurai"],
    tier2: ["Tiruchirappalli", "Salem", "Tirunelveli", "Tiruppur", "Vellore"],
    tier3: ["Erode", "Thoothukudi", "Dindigul", "Thanjavur", "Ranipet", "Sivakasi", "Karur", "Hosur"]
  },
  "Telangana": {
    tier1: ["Hyderabad"],
    tier2: ["Warangal", "Nizamabad", "Karimnagar", "Khammam"],
    tier3: ["Ramagundam", "Mahbubnagar", "Nalgonda", "Adilabad", "Suryapet", "Miryalaguda"]
  },
  "Tripura": {
    tier1: [],
    tier2: ["Agartala"],
    tier3: ["Udaipur", "Dharmanagar", "Kailashahar"]
  },
  "Uttar Pradesh": {
    tier1: ["Lucknow", "Kanpur", "Noida", "Ghaziabad"],
    tier2: ["Agra", "Varanasi", "Meerut", "Allahabad", "Bareilly", "Aligarh", "Moradabad"],
    tier3: ["Gorakhpur", "Saharanpur", "Jhansi", "Firozabad", "Muzaffarnagar", "Mathura", "Rampur", "Shahjahanpur"]
  },
  "Uttarakhand": {
    tier1: ["Dehradun"],
    tier2: ["Haridwar", "Roorkee", "Haldwani"],
    tier3: ["Rudrapur", "Kashipur", "Rishikesh", "Nainital", "Mussoorie"]
  },
  "West Bengal": {
    tier1: ["Kolkata"],
    tier2: ["Asansol", "Siliguri", "Durgapur", "Howrah"],
    tier3: ["Bardhaman", "Malda", "Baharampur", "Habra", "Kharagpur", "Shantipur", "Dankuni"]
  },
  "Delhi": {
    tier1: ["New Delhi", "Delhi"],
    tier2: [],
    tier3: []
  },
  "Chandigarh": {
    tier1: ["Chandigarh"],
    tier2: [],
    tier3: []
  },
  "Puducherry": {
    tier1: [],
    tier2: ["Puducherry"],
    tier3: ["Karaikal", "Mahe", "Yanam"]
  },
  "Jammu and Kashmir": {
    tier1: [],
    tier2: ["Srinagar", "Jammu"],
    tier3: ["Anantnag", "Baramulla", "Sopore", "Kathua", "Udhampur"]
  },
  "Ladakh": {
    tier1: [],
    tier2: ["Leh"],
    tier3: ["Kargil"]
  },
  "Andaman and Nicobar Islands": {
    tier1: [],
    tier2: ["Port Blair"],
    tier3: []
  },
  "Dadra and Nagar Haveli and Daman and Diu": {
    tier1: [],
    tier2: ["Silvassa", "Daman"],
    tier3: ["Diu"]
  },
  "Lakshadweep": {
    tier1: [],
    tier2: ["Kavaratti"],
    tier3: []
  }
};

export const COUNTRY_CITIES = {
  USA: ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia", "San Antonio", "San Diego", "Dallas", "San Jose"],
  IND: ["Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai", "Kolkata", "Pune", "Ahmedabad", "Jaipur", "Surat", "Visakhapatnam"],
  GBR: ["London", "Birmingham", "Manchester", "Glasgow", "Liverpool", "Leeds", "Sheffield", "Edinburgh"],
  CAN: ["Toronto", "Montreal", "Vancouver", "Calgary", "Edmonton", "Ottawa"],
  AUS: ["Sydney", "Melbourne", "Brisbane", "Perth", "Adelaide"],
};

export const TELECOM_OPERATORS = {
  USA: ["AT&T", "Verizon", "T-Mobile", "Sprint", "US Cellular"],
  IND: ["Jio", "Airtel", "Vi", "BSNL"],
  GBR: ["EE", "O2", "Vodafone", "Three"],
};

// ==================== AUDIENCE SEGMENTS ====================

export const AFFINITY_SEGMENTS = [
  "Tech Enthusiasts", "Auto Enthusiasts", "Sports Fans", "Fashion Lovers",
  "Foodies", "Travel Buffs", "Music Lovers", "Movie Buffs", "Gamers",
  "Home Improvement", "Pet Lovers", "Fitness Enthusiasts", "Beauty & Wellness",
  "News Junkies", "Business Professionals"
];

export const IN_MARKET_SEGMENTS = [
  "Autos & Vehicles", "Real Estate", "Financial Services", "Travel",
  "Consumer Electronics", "Apparel & Accessories", "Beauty & Personal Care",
  "Home & Garden", "Software", "Telecommunications", "Education",
  "Employment", "Dating Services", "Baby & Children's Products",
  "Business Services", "Legal Services"
];

// ==================== SUPPLY SOURCES ====================

export const SUPPLY_SOURCES = [
  "Google AdX", "Xandr", "Magnite", "PubMatic", "OpenX",
  "Index Exchange", "TripleLift", "Sovrn", "GumGum", "33Across",
  "Sharethrough", "Media.net", "Criteo", "Taboola"
];

// ==================== PLACEMENT & VIEWABILITY ====================

export const AD_PLACEMENTS_DISPLAY = [
  { value: "above_fold", label: "Above the Fold" },
  { value: "below_fold", label: "Below the Fold" },
  { value: "unknown", label: "Unknown" },
];

export const AD_PLACEMENTS_INCONTENT = [
  { value: "in_article", label: "In-article" },
  { value: "in_feed", label: "In-feed" },
  { value: "interstitial", label: "Interstitial" },
  { value: "in_banner", label: "In-banner" },
  { value: "unknown", label: "Unknown" },
];

export const AD_PLACEMENTS_NATIVE = [
  { value: "in_article", label: "In-article" },
  { value: "in_feed", label: "In-feed" },
  { value: "peripheral", label: "Peripheral" },
  { value: "recommendation", label: "Recommendation" },
  { value: "unknown", label: "Unknown" },
];

// ==================== BRAND SAFETY ====================

export const BRAND_SAFETY_LEVELS = [
  { value: "standard", label: "Standard", desc: "Basic safety controls" },
  { value: "strict", label: "Strict", desc: "Enhanced safety controls" },
  { value: "custom", label: "Custom", desc: "Define your own rules" },
];

export const BLOCKED_CATEGORIES = [
  "Adult", "Violence", "Gambling", "Alcohol", "Tobacco",
  "Drugs", "Politics", "Religion", "Hate Speech", "Fake News",
  "Crime", "Death & Injury", "Military Conflict", "Sensitive Social Issues"
];

// ==================== ATTRIBUTION ====================

export const ATTRIBUTION_MODELS = [
  { value: "last_touch", label: "Last Touch", desc: "Credit to last interaction" },
  { value: "first_touch", label: "First Touch", desc: "Credit to first interaction" },
  { value: "linear", label: "Linear", desc: "Equal credit across all touchpoints" },
  { value: "time_decay", label: "Time Decay", desc: "More credit to recent interactions" },
  { value: "position_based", label: "Position Based", desc: "40/20/40 split" },
  { value: "data_driven", label: "Data Driven", desc: "ML-based attribution" },
];

// ==================== IAB CATEGORIES ====================

export const IAB_CATEGORIES = [
  { code: "IAB1", name: "Arts & Entertainment" },
  { code: "IAB2", name: "Automotive" },
  { code: "IAB3", name: "Business" },
  { code: "IAB4", name: "Careers" },
  { code: "IAB5", name: "Education" },
  { code: "IAB6", name: "Family & Parenting" },
  { code: "IAB7", name: "Health & Fitness" },
  { code: "IAB8", name: "Food & Drink" },
  { code: "IAB9", name: "Hobbies & Interests" },
  { code: "IAB10", name: "Home & Garden" },
  { code: "IAB11", name: "Law, Gov't & Politics" },
  { code: "IAB12", name: "News" },
  { code: "IAB13", name: "Personal Finance" },
  { code: "IAB14", name: "Society" },
  { code: "IAB15", name: "Science" },
  { code: "IAB16", name: "Pets" },
  { code: "IAB17", name: "Sports" },
  { code: "IAB18", name: "Style & Fashion" },
  { code: "IAB19", name: "Technology & Computing" },
  { code: "IAB20", name: "Travel" },
  { code: "IAB21", name: "Real Estate" },
  { code: "IAB22", name: "Shopping" },
  { code: "IAB23", name: "Religion & Spirituality" },
];

// ==================== INITIAL FORM STATE ====================

export const INITIAL_FORM_STATE = {
  // Campaign Overview
  name: "",
  iab_categories: [],
  description: "",
  primary_goal: "brand_awareness",
  kpi_type: "cpm",
  kpi_target: 5.0,
  
  // Budget & Bidding
  bidding_strategy: "manual_cpm",
  bid_pricing_type: "cpm",
  bid_floor: 0.5,
  bid_price: 2.0,
  currency: "USD",
  daily_budget: 100,
  total_budget: 3000,
  pacing_type: "even",
  
  // Inventory
  inventory_sources: ["open_exchange"],
  environments: ["web", "app"],
  
  // Geographic Targeting - Include
  geo_countries: [],
  geo_states: [],
  geo_cities: [],
  geo_pincodes: [],
  geo_regions: [],
  // Geographic Targeting - Exclude
  geo_countries_exclude: [],
  geo_states_exclude: [],
  geo_cities_exclude: [],
  geo_pincodes_exclude: [],
  geo_regions_exclude: [],
  // Lat/Long Targeting
  lat_long_targeting: false,
  lat_long_points: [],
  geo_latitude: "",
  geo_longitude: "",
  radius_km: 10,
  lat_long_type: "include",
  
  // Telecom
  telecom_operators: [],
  
  // Device Targeting
  device_types: [],
  device_makes: [],
  device_models: [],
  os_list: [],
  os_versions: [],
  browsers_include: [],
  browsers_exclude: [],
  carriers: [],
  connection_types: [],
  
  // Demographics
  age_ranges: [],
  genders: [],
  income_segments: [],
  parental_status: [],
  languages: [],
  languages_exclude: [],
  
  // Contextual Targeting
  contextual_keywords: [],
  contextual_categories: [],
  keyword_match_type: "broad",
  
  // Audience Segments
  affinity_segments: [],
  in_market_segments: [],
  
  // Placement & Viewability
  ad_placements_display_include: [],
  ad_placements_display_exclude: [],
  ad_placements_incontent_include: [],
  ad_placements_incontent_exclude: [],
  ad_placements_native_include: [],
  ad_placements_native_exclude: [],
  viewability_threshold: 50,
  exclude_non_viewable: false,
  
  // Inventory Control
  domain_allowlist: [],
  domain_blocklist: [],
  app_allowlist: [],
  app_blocklist: [],
  
  // Supply Source Control
  supply_sources_include: [],
  supply_sources_exclude: [],
  
  // Time Targeting
  time_targeting_enabled: false,
  days_of_week: [0, 1, 2, 3, 4, 5, 6],
  hours_of_day: Array.from({ length: 24 }, (_, i) => i),
  timezone: "UTC",
  
  // Brand Safety
  brand_safety_level: "standard",
  blocked_categories: [],
  blocked_keywords: [],
  blocked_domains: [],
  exclude_ugc: false,
  exclude_live_streaming: false,
  
  // Audience
  first_party_audiences: [],
  third_party_audiences: [],
  first_party_audience_input: "",
  third_party_audience_input: "",
  lookalike_enabled: false,
  lookalike_expansion: 3,
  audience_exclusions: [],
  
  // Creatives
  creative_id: "",
  creative_ids: [],
  
  // Schedule
  start_date: new Date().toISOString().split('T')[0],
  end_date: "",
  
  // Frequency Capping
  frequency_cap_enabled: false,
  frequency_cap_count: 5,
  frequency_cap_period: "day",
  frequency_cap_type: "user",
  frequency_cap_daily: 0,
  frequency_cap_lifetime: 0,
  
  // Advanced
  priority: 5,
  bid_shading_enabled: false,
  ml_prediction_enabled: false,
  spo_enabled: false,
  
  // Measurement
  conversion_tracking_enabled: false,
  conversion_pixel_id: "",
  attribution_model: "last_touch",
  click_through_window: 30,
  view_through_window: 1,
};
