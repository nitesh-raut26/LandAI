"""
Indian Cities Database — Tier 1/2/3 cities across all major states & UTs.

Data provenance
---------------
This is a *curated* reference dataset, not a live scrape. City names and GPS
coordinates are real; population is census-aligned (2001/2011) with a 2021
projection; urban area, land price and infrastructure figures are plausible,
expert-set approximations at realistic scale. They are intended for modelling
and demonstration — not verified real-time market quotes. A production build
would replace these tuples with feeds from Census, RERA, NHAI and listing
sources (see LAND_AI_VISION.md).
"""
import math

# Compact city data: (id, name, state, tier, lat, lng,
#   pop01, pop11, pop21,             # population
#   area01, area11, area21,          # urban area sq km
#   price10, price15, price21,       # land INR/sqft (city average)
#   railway, airport, nhwy,          # infrastructure booleans + int
#   univ, medcol,                    # education
#   industry, metro, distmetro,      # economic + nearest metro
#   schemes, twin, twinlag,          # govt schemes, twin city
#   dirs, phase, desc)               # growth dirs, phase, description
_RAW = [
    # ── BIHAR ──────────────────────────────────────────────────────────────
    ("patna", "Patna", "Bihar", 2, 25.5941, 85.1376,
     1366000, 1683000, 2050000, 100, 165, 230,
     2500, 4500, 7500,
     True, True, 3, True, True,
     "government", "Delhi", 1000,
     "Smart City,AMRUT", None, 0,
     "N,E,W", "maturing",
     "State capital of Bihar, fastest growing Tier-2 in East India"),

    ("gaya", "Gaya", "Bihar", 2, 24.7955, 85.0002,
     383197, 470839, 570000, 25, 40, 58,
     800, 1500, 2500,
     True, True, 2, True, True,
     "tourism", "Patna", 100,
     "Smart City,AMRUT", None, 0,
     "N,NE,E", "accelerating",
     "Religious and tourist city, Buddhist circuit hub"),

    ("muzaffarpur", "Muzaffarpur", "Bihar", 2, 26.1197, 85.3910,
     305936, 393724, 480000, 22, 35, 52,
     700, 1200, 2000,
     True, False, 2, True, True,
     "agriculture", "Patna", 75,
     "AMRUT", None, 0,
     "N,E,SE", "accelerating",
     "Commercial hub of North Bihar, litchi export centre"),

    ("bhagalpur", "Bhagalpur", "Bihar", 2, 25.2425, 86.9842,
     340767, 410210, 500000, 28, 44, 63,
     600, 1100, 1800,
     True, False, 2, True, True,
     "textile", "Patna", 220,
     "AMRUT", None, 0,
     "W,NW,N", "accelerating",
     "Silk city of India, Bhagalpuri silk capital"),

    ("darbhanga", "Darbhanga", "Bihar", 2, 26.1542, 85.8918,
     218391, 296194, 390000, 15, 28, 45,
     300, 550, 1000,
     True, True, 2, True, True,
     "agriculture", "Patna", 140,
     "AMRUT,Smart City", None, 0,
     "N,E,SE", "accelerating",
     "Cultural capital of Mithila, airport boosted growth"),

    ("jhanjharpur", "Jhanjharpur", "Bihar", 3, 26.2659, 86.2823,
     18000, 28000, 40000, 3.2, 6.5, 10.8,
     200, 400, 700,
     True, False, 1, False, False,
     "agriculture", "Darbhanga", 45,
     "AMRUT", "darbhanga", 15,
     "N,E", "emerging",
     "Fastest growing Tier-3 near Darbhanga, 15-yr lagged twin"),

    ("purnia", "Purnia", "Bihar", 3, 25.7771, 87.4753,
     171196, 236393, 300000, 14, 23, 35,
     400, 700, 1200,
     True, False, 2, False, True,
     "agriculture", "Patna", 340,
     "AMRUT", None, 0,
     "N,W,SW", "accelerating",
     "North Bihar trade hub, close to Bangladesh border"),

    ("begusarai", "Begusarai", "Bihar", 3, 25.4182, 86.1272,
     114882, 151878, 195000, 8, 14, 22,
     300, 550, 950,
     True, False, 2, False, False,
     "industry", "Patna", 120,
     "AMRUT", None, 0,
     "E,SE,S", "accelerating",
     "Industrial town with IOCL refinery"),

    ("samastipur", "Samastipur", "Bihar", 3, 25.8710, 85.7808,
     103890, 136400, 175000, 7, 12, 19,
     250, 450, 800,
     True, False, 1, False, False,
     "agriculture", "Patna", 70,
     "AMRUT", None, 0,
     "N,E,S", "emerging",
     "Railway junction and agricultural market town"),

    ("arrah", "Arrah", "Bihar", 3, 25.5560, 84.6627,
     205432, 261395, 330000, 16, 25, 38,
     350, 600, 1100,
     True, False, 2, False, True,
     "agriculture", "Patna", 60,
     "AMRUT", None, 0,
     "N,W,NW", "accelerating",
     "Bhojpur district HQ, highway NH30 proximity"),

    ("chapra", "Chapra", "Bihar", 3, 25.7813, 84.7511,
     177975, 225289, 285000, 13, 22, 34,
     300, 500, 900,
     True, False, 2, False, False,
     "agriculture", "Patna", 80,
     "AMRUT", None, 0,
     "N,E,S", "accelerating",
     "Saran district HQ on Ganga-Ghaghra confluence"),

    ("bettiah", "Bettiah", "Bihar", 3, 27.0191, 84.5048,
     90000, 118000, 155000, 7, 12, 18,
     200, 380, 680,
     True, False, 1, False, False,
     "agriculture", "Gorakhpur", 80,
     "AMRUT", None, 0,
     "E,SE,S", "emerging",
     "West Champaran HQ near Valmiki Tiger Reserve"),

    ("motihari", "Motihari", "Bihar", 3, 26.6492, 84.9183,
     83125, 123904, 165000, 6, 11, 17,
     200, 370, 650,
     True, False, 1, False, False,
     "agriculture", "Gorakhpur", 100,
     "AMRUT", None, 0,
     "E,S,SW", "emerging",
     "East Champaran HQ, Mahatma Gandhi birthplace district"),

    ("sasaram", "Sasaram", "Bihar", 3, 24.9468, 84.0288,
     134350, 147051, 190000, 9, 15, 23,
     250, 420, 750,
     True, False, 2, False, False,
     "agriculture", "Patna", 165,
     "AMRUT", None, 0,
     "N,E,NE", "emerging",
     "Historical town on Grand Trunk Road NH2"),

    ("sitamarhi", "Sitamarhi", "Bihar", 3, 26.5925, 85.4776,
     72578, 100146, 135000, 5, 9, 14,
     180, 320, 580,
     True, False, 1, False, False,
     "agriculture", "Muzaffarpur", 75,
     "AMRUT", None, 0,
     "S,SE,E", "emerging",
     "Religious town near Nepal border, birthplace of Sita"),

    # ── UTTAR PRADESH ──────────────────────────────────────────────────────
    ("lucknow", "Lucknow", "Uttar Pradesh", 2, 26.8467, 80.9462,
     2245509, 2901474, 3800000, 200, 310, 420,
     3000, 5000, 8000,
     True, True, 4, True, True,
     "government", "Delhi", 510,
     "Smart City,AMRUT", None, 0,
     "N,E,NE,W", "maturing",
     "State capital, Nawabi culture + modern IT parks"),

    ("kanpur", "Kanpur", "Uttar Pradesh", 2, 26.4499, 80.3319,
     2690486, 2920496, 3500000, 230, 310, 380,
     2000, 3500, 5500,
     True, True, 3, True, True,
     "industry", "Delhi", 480,
     "Smart City,AMRUT", None, 0,
     "N,NE,E", "maturing",
     "Industrial city, leather and textile capital"),

    ("agra", "Agra", "Uttar Pradesh", 2, 27.1767, 78.0081,
     1321410, 1574542, 2000000, 110, 165, 220,
     2500, 4000, 6000,
     True, True, 3, True, True,
     "tourism", "Delhi", 220,
     "Smart City,AMRUT", None, 0,
     "N,NW,W", "maturing",
     "City of Taj Mahal, tourism + real-estate boom"),

    ("varanasi", "Varanasi", "Uttar Pradesh", 2, 25.3176, 82.9739,
     1091918, 1201815, 1600000, 90, 135, 185,
     2000, 3500, 5500,
     True, True, 2, True, True,
     "tourism", "Prayagraj", 125,
     "Smart City,AMRUT", None, 0,
     "N,NE,E", "accelerating",
     "Oldest living city, Ganga Expressway catalyst"),

    ("prayagraj", "Prayagraj", "Uttar Pradesh", 2, 25.4358, 81.8463,
     1049591, 1212395, 1550000, 85, 130, 180,
     1500, 2800, 4500,
     True, True, 3, True, True,
     "government", "Lucknow", 210,
     "Smart City,AMRUT", None, 0,
     "N,NE,W", "accelerating",
     "Sangam city, legal + educational hub, Kumbh investment"),

    ("gorakhpur", "Gorakhpur", "Uttar Pradesh", 2, 26.7606, 83.3732,
     624570, 673446, 860000, 48, 72, 100,
     800, 1500, 2800,
     True, True, 3, True, True,
     "agriculture", "Lucknow", 275,
     "Smart City,AMRUT", None, 0,
     "N,E,SE", "accelerating",
     "Educational and agricultural hub, AIIMS + fertiliser plant"),

    ("meerut", "Meerut", "Uttar Pradesh", 2, 28.9845, 77.7064,
     1161716, 1305429, 1700000, 95, 145, 200,
     2500, 4000, 6500,
     True, True, 3, True, True,
     "industry", "Delhi", 65,
     "Smart City,AMRUT", None, 0,
     "N,E,S", "accelerating",
     "Sports goods + industrial city, RapidX corridor to Delhi"),

    ("bareilly", "Bareilly", "Uttar Pradesh", 2, 28.3670, 79.4304,
     718395, 903668, 1150000, 55, 85, 120,
     1000, 1800, 3000,
     True, True, 2, True, True,
     "industry", "Delhi", 250,
     "AMRUT", None, 0,
     "N,NE,E", "accelerating",
     "Furniture and sugar industry hub"),

    ("aligarh", "Aligarh", "Uttar Pradesh", 3, 27.8974, 78.0880,
     669087, 874408, 1100000, 52, 80, 112,
     1200, 2000, 3500,
     True, False, 2, True, False,
     "industry", "Delhi", 135,
     "AMRUT", None, 0,
     "N,E,NE", "accelerating",
     "Lock industry and AMU, Yamuna Expressway proximity"),

    ("moradabad", "Moradabad", "Uttar Pradesh", 3, 28.8386, 78.7733,
     641583, 889810, 1130000, 50, 78, 110,
     1200, 2000, 3500,
     True, True, 2, True, False,
     "industry", "Delhi", 165,
     "Smart City", None, 0,
     "N,E,SE", "accelerating",
     "Brass metalwork capital, major export hub"),

    ("mathura", "Mathura", "Uttar Pradesh", 3, 27.4924, 77.6737,
     298827, 349626, 450000, 22, 34, 48,
     1500, 2500, 4000,
     True, False, 2, False, False,
     "tourism", "Delhi", 148,
     "AMRUT", None, 0,
     "N,E,NE", "accelerating",
     "Birthplace of Krishna, religious tourism + IOCL refinery"),

    ("jhansi", "Jhansi", "Uttar Pradesh", 3, 25.4484, 78.5685,
     383248, 507293, 640000, 29, 46, 65,
     700, 1300, 2200,
     True, True, 3, True, False,
     "industry", "Delhi", 445,
     "Smart City", None, 0,
     "N,NE,E", "accelerating",
     "Defense and industrial city, Bundelkhand Expressway"),

    # ── MAHARASHTRA ────────────────────────────────────────────────────────
    ("mumbai", "Mumbai", "Maharashtra", 1, 19.0760, 72.8777,
     11914398, 12478447, 13500000, 580, 620, 650,
     15000, 22000, 30000,
     True, True, 5, True, True,
     "finance", "Mumbai", 0,
     "Smart City,AMRUT", None, 0,
     "N,NE,E", "mature",
     "Financial capital of India, BKC and Thane corridor"),

    ("pune", "Pune", "Maharashtra", 1, 18.5204, 73.8567,
     2538473, 3115431, 4500000, 220, 320, 440,
     4000, 7000, 11000,
     True, True, 4, True, True,
     "IT", "Mumbai", 160,
     "Smart City,AMRUT", None, 0,
     "N,NE,E,W", "maturing",
     "Oxford of East, Hinjewadi IT park, Pune Metro boom"),

    ("nagpur", "Nagpur", "Maharashtra", 2, 21.1458, 79.0882,
     2052066, 2405421, 3100000, 180, 265, 370,
     2500, 4000, 6500,
     True, True, 4, True, True,
     "government", "Mumbai", 870,
     "Smart City,AMRUT", None, 0,
     "N,E,S,W", "accelerating",
     "Zero Mile city, MIHAN aerospace SEZ, future capital"),

    ("nashik", "Nashik", "Maharashtra", 2, 19.9975, 73.7898,
     1077236, 1486053, 1950000, 88, 135, 190,
     2000, 3500, 5500,
     True, True, 3, True, True,
     "agri-industrial", "Mumbai", 185,
     "Smart City,AMRUT", None, 0,
     "N,NE,E", "accelerating",
     "Wine capital + Mumbai-Agra highway industrial corridor"),

    ("aurangabad", "Aurangabad", "Maharashtra", 2, 19.8762, 75.3433,
     872667, 1175116, 1550000, 72, 110, 156,
     1500, 2800, 4500,
     True, True, 3, True, True,
     "industrial", "Mumbai", 335,
     "Smart City,AMRUT", None, 0,
     "N,E,SE", "accelerating",
     "Industrial belt near Ajanta/Ellora, Shambhaji Nagar"),

    ("solapur", "Solapur", "Maharashtra", 2, 17.6599, 75.9064,
     872478, 951558, 1200000, 70, 100, 138,
     1000, 1800, 3000,
     True, True, 2, True, True,
     "textile", "Pune", 245,
     "AMRUT", None, 0,
     "N,NW,W", "accelerating",
     "Textile and sugar hub, Pune-Hyderabad axis"),

    ("thane", "Thane", "Maharashtra", 1, 19.2183, 72.9781,
     1261517, 1818872, 2600000, 107, 162, 230,
     5000, 8000, 12000,
     True, False, 3, True, True,
     "IT", "Mumbai", 35,
     "Smart City,AMRUT", None, 0,
     "N,NE,E", "maturing",
     "Mumbai satellite city, fastest growing metro fringe"),

    # ── KARNATAKA ──────────────────────────────────────────────────────────
    ("bangalore", "Bangalore", "Karnataka", 1, 12.9716, 77.5946,
     5438065, 8425970, 13800000, 460, 700, 1020,
     4000, 7000, 12000,
     True, True, 5, True, True,
     "IT", "Hyderabad", 570,
     "Smart City,AMRUT", None, 0,
     "N,E,S,W,NE", "maturing",
     "Silicon Valley of India, Peripheral Ring Road expansion"),

    ("mysore", "Mysore", "Karnataka", 2, 12.2958, 76.6394,
     755379, 920550, 1200000, 62, 94, 132,
     1800, 3000, 5000,
     True, True, 3, True, True,
     "tourism-IT", "Bangalore", 150,
     "Smart City,AMRUT", None, 0,
     "N,NE,E", "accelerating",
     "Cultural capital, Infosys campus, Bangalore spillover"),

    ("hubli", "Hubli-Dharwad", "Karnataka", 2, 15.3647, 75.1240,
     786195, 943857, 1200000, 64, 97, 136,
     1200, 2200, 3600,
     True, True, 3, True, True,
     "industrial", "Bangalore", 410,
     "Smart City,AMRUT", None, 0,
     "N,NW,W", "accelerating",
     "Twin city hub, commercial north Karnataka"),

    ("mangalore", "Mangalore", "Karnataka", 2, 12.9141, 74.8560,
     398745, 488968, 630000, 32, 49, 69,
     1800, 3200, 5200,
     True, True, 2, True, True,
     "port-finance", "Bangalore", 352,
     "Smart City,AMRUT", None, 0,
     "N,NE,E", "accelerating",
     "Major port + banking capital of Coastal Karnataka"),

    ("davangere", "Davangere", "Karnataka", 3, 14.4644, 75.9218,
     363954, 435128, 550000, 29, 44, 62,
     600, 1100, 1800,
     True, True, 2, True, True,
     "textile", "Bangalore", 270,
     "AMRUT", None, 0,
     "E,SE,S", "accelerating",
     "Cotton and textile hub, central Karnataka"),

    # ── TAMIL NADU ─────────────────────────────────────────────────────────
    ("chennai", "Chennai", "Tamil Nadu", 1, 13.0827, 80.2707,
     4343645, 4646732, 7100000, 390, 430, 520,
     5000, 8000, 13000,
     True, True, 5, True, True,
     "IT-auto", "Hyderabad", 625,
     "Smart City,AMRUT", None, 0,
     "N,NW,W,SW", "maturing",
     "Detroit of India + IT, OMR IT corridor boom"),

    ("coimbatore", "Coimbatore", "Tamil Nadu", 1, 11.0168, 76.9558,
     1456079, 1601438, 2300000, 125, 175, 250,
     2500, 4000, 6500,
     True, True, 3, True, True,
     "textile-IT", "Chennai", 508,
     "Smart City,AMRUT", None, 0,
     "N,E,NE", "accelerating",
     "Manchester of South India, growing IT hub"),

    ("madurai", "Madurai", "Tamil Nadu", 2, 9.9252, 78.1198,
     1194665, 1462420, 1900000, 98, 150, 215,
     1500, 2600, 4200,
     True, True, 3, True, True,
     "textile-tourism", "Chennai", 456,
     "Smart City,AMRUT", None, 0,
     "N,NE,E", "accelerating",
     "Temple city + textile hub, Third largest TN city"),

    ("tiruchirappalli", "Tiruchirappalli", "Tamil Nadu", 2, 10.7905, 78.7047,
     746062, 916857, 1200000, 62, 94, 132,
     1200, 2000, 3300,
     True, True, 2, True, True,
     "industrial", "Chennai", 332,
     "Smart City,AMRUT", None, 0,
     "N,NE,E", "accelerating",
     "BHEL defense industry, central TN hub"),

    ("salem", "Salem", "Tamil Nadu", 2, 11.6643, 78.1460,
     693236, 831038, 1080000, 56, 85, 120,
     1000, 1700, 2800,
     True, True, 2, True, True,
     "steel-textile", "Chennai", 340,
     "AMRUT", None, 0,
     "N,NW,W", "accelerating",
     "Steel city, expressway to Chennai = land boom"),

    ("tirunelveli", "Tirunelveli", "Tamil Nadu", 3, 8.7139, 77.7567,
     432566, 473637, 590000, 35, 53, 74,
     700, 1200, 2000,
     True, True, 2, True, True,
     "agri-industry", "Chennai", 665,
     "AMRUT", None, 0,
     "N,NE,E", "accelerating",
     "Wind energy + agriculture, deep south TN"),

    # ── GUJARAT ────────────────────────────────────────────────────────────
    ("ahmedabad", "Ahmedabad", "Gujarat", 1, 23.0225, 72.5714,
     3520085, 5570585, 8000000, 310, 480, 700,
     3500, 5500, 9000,
     True, True, 5, True, True,
     "industry-IT", "Mumbai", 555,
     "Smart City,AMRUT", None, 0,
     "N,E,S,W,NE", "maturing",
     "Business capital of Gujarat, GIFT City financial hub"),

    ("surat", "Surat", "Gujarat", 1, 21.1702, 72.8311,
     2433787, 4462002, 7200000, 220, 390, 640,
     2500, 4000, 7000,
     True, True, 4, True, True,
     "textile-diamond", "Ahmedabad", 265,
     "Smart City,AMRUT", None, 0,
     "N,NE,E,S", "maturing",
     "Diamond and textile capital, fastest growing Tier-1"),

    ("vadodara", "Vadodara", "Gujarat", 2, 22.3072, 73.1812,
     1306035, 1666703, 2200000, 115, 170, 240,
     1800, 3000, 5000,
     True, True, 4, True, True,
     "industrial", "Ahmedabad", 113,
     "Smart City,AMRUT", None, 0,
     "N,NE,E", "accelerating",
     "Petrochemicals + cultural city, Baroda"),

    ("rajkot", "Rajkot", "Gujarat", 2, 22.3039, 70.8022,
     1002160, 1286678, 1700000, 87, 130, 184,
     1500, 2500, 4000,
     True, True, 3, True, True,
     "industrial", "Ahmedabad", 220,
     "Smart City,AMRUT", None, 0,
     "N,E,SE", "accelerating",
     "Engineering + watch industry, Smart City model"),

    ("bhavnagar", "Bhavnagar", "Gujarat", 3, 21.7645, 72.1519,
     510958, 605882, 775000, 42, 63, 89,
     700, 1200, 2000,
     True, True, 2, False, True,
     "port-ship", "Ahmedabad", 195,
     "AMRUT", None, 0,
     "N,NE,NW", "accelerating",
     "Port city, ship-breaking industry Alang"),

    ("jamnagar", "Jamnagar", "Gujarat", 3, 22.4707, 70.0577,
     443518, 600943, 780000, 36, 55, 78,
     800, 1400, 2300,
     True, True, 2, True, False,
     "oil-port", "Ahmedabad", 298,
     "AMRUT", None, 0,
     "N,NE,E", "accelerating",
     "Reliance refinery city, largest refinery complex in world"),

    # ── RAJASTHAN ──────────────────────────────────────────────────────────
    ("jaipur", "Jaipur", "Rajasthan", 1, 26.9124, 75.7873,
     2322575, 3073350, 4500000, 205, 300, 425,
     2500, 4500, 7500,
     True, True, 5, True, True,
     "tourism-IT", "Delhi", 268,
     "Smart City,AMRUT", None, 0,
     "N,E,S,W,NE", "maturing",
     "Pink City, tourism + IT boom, Metro expansion"),

    ("jodhpur", "Jodhpur", "Rajasthan", 2, 26.2389, 73.0243,
     851051, 1033918, 1400000, 72, 108, 155,
     1200, 2200, 3800,
     True, True, 3, True, True,
     "tourism-industrial", "Jaipur", 330,
     "Smart City,AMRUT", None, 0,
     "N,NE,E", "accelerating",
     "Blue City + defense air base, AIIMS campus"),

    ("udaipur", "Udaipur", "Rajasthan", 2, 24.5854, 73.7125,
     389317, 451100, 600000, 32, 48, 68,
     1500, 2500, 4200,
     True, True, 2, True, True,
     "tourism", "Ahmedabad", 255,
     "Smart City,AMRUT", None, 0,
     "N,NE,NW", "accelerating",
     "City of Lakes, luxury + heritage tourism"),

    ("kota", "Kota", "Rajasthan", 2, 25.2138, 75.8648,
     696899, 1001694, 1350000, 58, 88, 125,
     1200, 2100, 3500,
     True, True, 2, True, True,
     "education-industrial", "Jaipur", 240,
     "AMRUT", None, 0,
     "N,E,SE", "accelerating",
     "Coaching capital of India + Kota Super Thermal Plant"),

    ("ajmer", "Ajmer", "Rajasthan", 3, 26.4499, 74.6399,
     402700, 551360, 700000, 33, 51, 72,
     800, 1400, 2500,
     True, True, 2, True, False,
     "religious-industrial", "Jaipur", 132,
     "AMRUT", None, 0,
     "N,NW,W", "accelerating",
     "Dargah Sharif, NH-8 industrial corridor"),

    ("bikaner", "Bikaner", "Rajasthan", 3, 28.0229, 73.3119,
     416289, 644406, 840000, 35, 53, 76,
     600, 1100, 1900,
     True, True, 2, True, False,
     "tourism-agri", "Jaipur", 330,
     "AMRUT", None, 0,
     "E,SE,S", "accelerating",
     "Desert city, camel fair + Bikaner Expressway"),

    # ── MADHYA PRADESH ─────────────────────────────────────────────────────
    ("bhopal", "Bhopal", "Madhya Pradesh", 2, 23.2599, 77.4126,
     1437354, 1795648, 2400000, 125, 190, 268,
     1800, 3000, 5000,
     True, True, 4, True, True,
     "government-IT", "Delhi", 770,
     "Smart City,AMRUT", None, 0,
     "N,E,NE,W", "accelerating",
     "City of Lakes + state capital, IT Park Bhopal"),

    ("indore", "Indore", "Madhya Pradesh", 1, 22.7196, 75.8577,
     1597441, 1964086, 2900000, 140, 215, 308,
     2500, 4000, 7000,
     True, True, 4, True, True,
     "business-IT", "Mumbai", 600,
     "Smart City,AMRUT", None, 0,
     "N,E,S,W", "maturing",
     "Cleanest city 6 yrs, commercial capital, Super Corridor"),

    ("jabalpur", "Jabalpur", "Madhya Pradesh", 2, 23.1815, 79.9864,
     1098697, 1267564, 1650000, 95, 142, 200,
     900, 1600, 2700,
     True, True, 3, True, True,
     "defense-industrial", "Bhopal", 290,
     "AMRUT", None, 0,
     "N,NE,E", "accelerating",
     "Ordnance factory + defense hub, Marble rocks city"),

    ("gwalior", "Gwalior", "Madhya Pradesh", 2, 26.2183, 78.1828,
     826919, 1069276, 1400000, 72, 108, 152,
     1000, 1800, 3000,
     True, True, 3, True, True,
     "industrial", "Delhi", 320,
     "Smart City,AMRUT", None, 0,
     "N,NW,W", "accelerating",
     "Historical fort city + MSME industrial hub"),

    ("ujjain", "Ujjain", "Madhya Pradesh", 2, 23.1765, 75.7885,
     430427, 515215, 680000, 36, 54, 76,
     700, 1200, 2100,
     True, True, 2, True, False,
     "religious-industrial", "Indore", 55,
     "AMRUT", None, 0,
     "N,NE,E", "accelerating",
     "Kumbh Mela city + Ujjain Corridor industrial zone"),

    ("sagar", "Sagar", "Madhya Pradesh", 3, 23.8388, 78.7378,
     232133, 274543, 360000, 19, 29, 41,
     400, 700, 1200,
     True, True, 2, True, False,
     "agriculture-education", "Bhopal", 185,
     "AMRUT", None, 0,
     "N,E,NE", "emerging",
     "Educational town, Sagar University, agriculture belt"),

    # ── WEST BENGAL ────────────────────────────────────────────────────────
    ("kolkata", "Kolkata", "West Bengal", 1, 22.5726, 88.3639,
     4580544, 4486679, 5200000, 400, 430, 468,
     3000, 5000, 8000,
     True, True, 5, True, True,
     "finance-industry", "Delhi", 1340,
     "Smart City,AMRUT", None, 0,
     "N,E,S,W", "mature",
     "Cultural capital of India, New Town Rajarhat tech hub"),

    ("durgapur", "Durgapur", "West Bengal", 2, 23.5204, 87.3119,
     492734, 566517, 725000, 42, 63, 89,
     600, 1100, 1900,
     True, True, 3, True, True,
     "steel-industrial", "Kolkata", 165,
     "AMRUT", None, 0,
     "N,NE,E", "accelerating",
     "Steel city of India, SAIL + Durgapur IT corridor"),

    ("asansol", "Asansol", "West Bengal", 2, 23.6836, 86.9522,
     564491, 563917, 720000, 48, 72, 101,
     500, 900, 1600,
     True, True, 2, True, True,
     "coal-industrial", "Kolkata", 200,
     "Smart City,AMRUT", None, 0,
     "N,E,SE", "accelerating",
     "Coal and steel industrial center, Raniganj coalfields"),

    ("siliguri", "Siliguri", "West Bengal", 2, 26.7271, 88.3952,
     470275, 513264, 720000, 39, 59, 84,
     1000, 1800, 3000,
     True, True, 3, True, True,
     "trade", "Kolkata", 600,
     "Smart City,AMRUT", None, 0,
     "N,NE,E", "accelerating",
     "Gateway to Northeast + Bhutan, e-commerce hub"),

    ("kharagpur", "Kharagpur", "West Bengal", 3, 22.3460, 87.3320,
     194795, 207986, 265000, 16, 24, 34,
     500, 900, 1500,
     True, False, 2, True, False,
     "education-industry", "Kolkata", 120,
     "AMRUT", None, 0,
     "N,NE,E", "emerging",
     "IIT Kharagpur campus city, major railway junction"),

    ("bardhaman", "Bardhaman", "West Bengal", 3, 23.2324, 87.8615,
     285630, 314265, 405000, 24, 36, 51,
     500, 900, 1600,
     True, True, 2, True, True,
     "agriculture-industry", "Kolkata", 95,
     "AMRUT", None, 0,
     "N,E,SE", "emerging",
     "Rice bowl of WB, coal mines + agriculture belt"),

    # ── TELANGANA / ANDHRA PRADESH ─────────────────────────────────────────
    ("hyderabad", "Hyderabad", "Telangana", 1, 17.3850, 78.4867,
     3637483, 6731790, 10500000, 320, 540, 870,
     3000, 6000, 10000,
     True, True, 5, True, True,
     "IT-pharma", "Bangalore", 570,
     "Smart City,AMRUT", None, 0,
     "N,E,S,W,NE", "maturing",
     "HITEC City + pharma hub, Genome Valley"),

    ("visakhapatnam", "Visakhapatnam", "Andhra Pradesh", 1, 17.6868, 83.2185,
     969608, 1730320, 2600000, 84, 155, 245,
     1500, 2800, 5000,
     True, True, 4, True, True,
     "port-industrial", "Hyderabad", 625,
     "Smart City,AMRUT", None, 0,
     "N,NW,W,SW", "maturing",
     "Jewel of East Coast, Vizag Steel + IT corridor"),

    ("vijayawada", "Vijayawada", "Andhra Pradesh", 2, 16.5062, 80.6480,
     851282, 1048240, 1400000, 72, 110, 157,
     1200, 2200, 3800,
     True, True, 3, True, True,
     "commercial", "Hyderabad", 280,
     "Smart City,AMRUT", None, 0,
     "N,NW,W", "accelerating",
     "AP commercial capital, Amaravati capital region proximity"),

    ("guntur", "Guntur", "Andhra Pradesh", 2, 16.3067, 80.4365,
     514707, 743354, 980000, 43, 67, 95,
     800, 1400, 2400,
     True, True, 2, True, True,
     "agriculture-commercial", "Hyderabad", 260,
     "AMRUT", None, 0,
     "N,NW,W", "accelerating",
     "Chilli + tobacco market, Amaravati adjacency benefit"),

    ("warangal", "Warangal", "Telangana", 2, 17.9784, 79.5941,
     528570, 811844, 1100000, 44, 73, 104,
     600, 1100, 2000,
     True, True, 2, True, True,
     "industrial", "Hyderabad", 148,
     "Smart City,AMRUT", None, 0,
     "N,NE,E", "accelerating",
     "Granite city + growing IT, 150 km from Hyderabad"),

    ("tirupati", "Tirupati", "Andhra Pradesh", 3, 13.6288, 79.4192,
     228499, 374260, 520000, 19, 34, 48,
     800, 1500, 2700,
     True, True, 2, False, True,
     "religious-IT", "Chennai", 135,
     "Smart City,AMRUT", None, 0,
     "N,NW,W", "accelerating",
     "Temple city + growing IT, TTD trust economy"),

    # ── PUNJAB / HARYANA ───────────────────────────────────────────────────
    ("chandigarh", "Chandigarh", "Chandigarh", 1, 30.7333, 76.7794,
     900635, 1025682, 1400000, 80, 105, 140,
     4000, 6500, 10000,
     True, True, 4, True, True,
     "government-IT", "Delhi", 250,
     "Smart City,AMRUT", None, 0,
     "N,E,S,W", "maturing",
     "Planned city, tech + startup hub, Aerocity SAS Nagar"),

    ("ludhiana", "Ludhiana", "Punjab", 2, 30.9010, 75.8573,
     1398467, 1613878, 2100000, 122, 178, 254,
     2000, 3500, 5800,
     True, True, 3, True, True,
     "textile-bicycle", "Chandigarh", 95,
     "Smart City,AMRUT", None, 0,
     "N,E,NE", "accelerating",
     "Textile + bicycle capital of India"),

    ("amritsar", "Amritsar", "Punjab", 2, 31.6340, 74.8723,
     1011327, 1132761, 1500000, 88, 130, 185,
     1500, 2600, 4200,
     True, True, 3, True, True,
     "tourism-trade", "Chandigarh", 200,
     "Smart City,AMRUT", None, 0,
     "N,E,NE", "accelerating",
     "Golden Temple city, border trade hub, Amritsar-Kolkata corridor"),

    ("gurgaon", "Gurugram", "Haryana", 1, 28.4595, 77.0266,
     228831, 876969, 2200000, 25, 108, 260,
     4000, 8000, 14000,
     True, True, 4, True, True,
     "IT-finance", "Delhi", 30,
     "Smart City,AMRUT", None, 0,
     "N,NE,E,S", "maturing",
     "Millennium City, Cyber Hub IT + financial district"),

    # ── DELHI ──────────────────────────────────────────────────────────────
    ("delhi", "Delhi", "Delhi", 1, 28.6139, 77.2090,
     12877470, 16314838, 20000000, 1083, 1225, 1484,
     8000, 14000, 22000,
     True, True, 10, True, True,
     "government-IT", "Delhi", 0,
     "Smart City,AMRUT", None, 0,
     "N,E,S,W,NE,NW,SE,SW", "mature",
     "National capital, largest urban agglomeration in India"),

    # ── JHARKHAND / ODISHA / ASSAM / CHHATTISGARH ─────────────────────────
    ("ranchi", "Ranchi", "Jharkhand", 2, 23.3441, 85.3096,
     847093, 1073440, 1450000, 74, 114, 162,
     900, 1600, 2800,
     True, True, 3, True, True,
     "government-mining", "Kolkata", 400,
     "Smart City,AMRUT", None, 0,
     "N,E,NE", "accelerating",
     "Capital of Jharkhand, steel + mining hub, AIIMS Ranchi"),

    ("jamshedpur", "Jamshedpur", "Jharkhand", 2, 22.8046, 86.2029,
     1104713, 1337131, 1750000, 96, 145, 205,
     1000, 1800, 3200,
     True, True, 3, True, True,
     "steel-industrial", "Kolkata", 270,
     "AMRUT", None, 0,
     "N,E,NE", "accelerating",
     "Tata Steel city, model planned industrial township"),

    ("bhubaneswar", "Bhubaneswar", "Odisha", 2, 20.2961, 85.8245,
     647302, 837737, 1200000, 57, 87, 125,
     1200, 2200, 3800,
     True, True, 4, True, True,
     "government-IT", "Kolkata", 440,
     "Smart City,AMRUT", None, 0,
     "N,E,NE,S", "accelerating",
     "Temple city, growing IT + startup hub, Infocity"),

    ("cuttack", "Cuttack", "Odisha", 3, 20.4625, 85.8830,
     535139, 606007, 780000, 45, 67, 96,
     600, 1100, 1900,
     True, True, 2, True, True,
     "commercial", "Bhubaneswar", 26,
     "AMRUT", None, 0,
     "N,NW,W", "accelerating",
     "Commercial capital of Odisha, silver filigree craft"),

    ("guwahati", "Guwahati", "Assam", 2, 26.1445, 91.7362,
     808021, 957352, 1400000, 70, 106, 152,
     1000, 1800, 3200,
     True, True, 3, True, True,
     "trade-government", "Kolkata", 1000,
     "Smart City,AMRUT", None, 0,
     "N,NE,E,W", "accelerating",
     "Gateway to Northeast India, e-commerce + trade boom"),

    ("raipur", "Raipur", "Chhattisgarh", 2, 21.2514, 81.6296,
     605747, 1010433, 1450000, 53, 92, 134,
     900, 1600, 2800,
     True, True, 3, True, True,
     "government-industrial", "Nagpur", 310,
     "Smart City,AMRUT", None, 0,
     "N,E,NE", "accelerating",
     "Capital of CG, steel + mining, Naya Raipur greenfield"),

    # ── KERALA ─────────────────────────────────────────────────────────────
    ("kochi", "Kochi", "Kerala", 2, 9.9312, 76.2673,
     1355972, 2117990, 2300000, 180, 280, 360,
     3500, 5000, 8500,
     True, True, 3, True, True,
     "port-finance", "Kochi", 0,
     "Smart City,AMRUT", None, 0,
     "N,E,S", "maturing",
     "Commercial capital of Kerala, port + IT hub with metro rail"),

    ("thiruvananthapuram", "Thiruvananthapuram", "Kerala", 2, 8.5241, 76.9366,
     744983, 957730, 1050000, 90, 130, 165,
     3000, 4500, 7000,
     True, True, 2, True, True,
     "government-IT", "Kochi", 200,
     "Smart City,AMRUT", None, 0,
     "N,E,NW", "maturing",
     "Kerala capital, Technopark IT hub and space research centre"),

    ("kozhikode", "Kozhikode", "Kerala", 2, 11.2588, 75.7804,
     436527, 609224, 700000, 60, 90, 120,
     2500, 3800, 6000,
     True, True, 2, True, True,
     "trade", "Kochi", 180,
     "Smart City", None, 0,
     "N,S,E", "accelerating",
     "Historic Malabar trade port, NRI-driven real estate"),

    ("thrissur", "Thrissur", "Kerala", 3, 10.5276, 76.2144,
     317474, 315957, 360000, 40, 55, 72,
     2200, 3400, 5200,
     True, False, 2, True, True,
     "trade", "Kochi", 75,
     "AMRUT", None, 0,
     "N,E,S", "accelerating",
     "Cultural capital of Kerala, gold and banking hub"),

    # ── UTTARAKHAND ────────────────────────────────────────────────────────
    ("dehradun", "Dehradun", "Uttarakhand", 2, 30.3165, 78.0322,
     426674, 578420, 760000, 60, 95, 135,
     3000, 4800, 7500,
     True, True, 2, True, True,
     "government-IT", "Delhi", 240,
     "Smart City,AMRUT", None, 0,
     "S,SE,E", "accelerating",
     "Uttarakhand capital, education + IT, Himalayan gateway"),

    ("haridwar", "Haridwar", "Uttarakhand", 3, 29.9457, 78.1642,
     175010, 228832, 310000, 28, 42, 60,
     1800, 2900, 4500,
     True, False, 1, True, False,
     "religious-industrial", "Dehradun", 55,
     "AMRUT", None, 0,
     "S,SE", "emerging",
     "Pilgrimage city on the Ganga, BHEL industrial belt"),

    ("rishikesh", "Rishikesh", "Uttarakhand", 3, 30.0869, 78.2676,
     59671, 70499, 110000, 12, 20, 30,
     2000, 3200, 5000,
     False, False, 1, False, False,
     "tourism", "Dehradun", 45,
     "", None, 0,
     "S,SW", "emerging",
     "Yoga capital of the world, adventure + wellness tourism"),

    # ── GOA ────────────────────────────────────────────────────────────────
    ("panaji", "Panaji", "Goa", 3, 15.4909, 73.8278,
     99677, 114405, 140000, 22, 32, 45,
     4000, 6500, 11000,
     True, True, 1, True, True,
     "tourism", "Panaji", 0,
     "Smart City", None, 0,
     "E,NE,N", "maturing",
     "Goa capital, tourism and second-home property market"),

    # ── HIMACHAL PRADESH ───────────────────────────────────────────────────
    ("shimla", "Shimla", "Himachal Pradesh", 3, 31.1048, 77.1734,
     142161, 169578, 215000, 18, 26, 35,
     3500, 5200, 8000,
     True, True, 1, True, True,
     "tourism", "Chandigarh", 115,
     "Smart City", None, 0,
     "S,SW,W", "emerging",
     "Himachal capital, hill-station tourism and education"),

    # ── JAMMU & KASHMIR ────────────────────────────────────────────────────
    ("srinagar", "Srinagar", "Jammu & Kashmir", 2, 34.0837, 74.7973,
     898440, 1180570, 1300000, 90, 130, 170,
     2500, 3800, 6000,
     True, True, 1, True, True,
     "tourism", "Jammu", 260,
     "Smart City,AMRUT", None, 0,
     "N,S,E", "accelerating",
     "Summer capital of J&K, tourism and horticulture hub"),

    ("jammu", "Jammu", "Jammu & Kashmir", 2, 32.7266, 74.8570,
     369959, 502197, 660000, 55, 85, 120,
     2200, 3400, 5500,
     True, True, 2, True, True,
     "government", "Jammu", 0,
     "Smart City,AMRUT", None, 0,
     "N,NE,S", "accelerating",
     "Winter capital of J&K, gateway and pilgrimage transit"),

    # ── PUDUCHERRY ─────────────────────────────────────────────────────────
    ("puducherry", "Puducherry", "Puducherry", 3, 11.9416, 79.8083,
     220865, 244377, 280000, 30, 42, 58,
     2500, 3800, 5800,
     True, False, 1, True, True,
     "tourism", "Chennai", 160,
     "Smart City", None, 0,
     "N,W,NW", "accelerating",
     "Former French colony, coastal tourism and education"),

    # ── UTTAR PRADESH (more) ───────────────────────────────────────────────
    ("noida", "Noida", "Uttar Pradesh", 1, 28.5355, 77.3910,
     305058, 642381, 950000, 80, 150, 215,
     6000, 9500, 16000,
     True, True, 3, True, True,
     "IT", "Delhi", 20,
     "Smart City", None, 0,
     "E,SE,S", "maturing",
     "NCR tech + corporate hub, expressway and metro connected"),

    ("ghaziabad", "Ghaziabad", "Uttar Pradesh", 2, 28.6692, 77.4538,
     968256, 1729000, 2100000, 110, 180, 240,
     4500, 7000, 11000,
     True, False, 3, True, True,
     "industrial", "Delhi", 30,
     "Smart City,AMRUT", None, 0,
     "E,NE,SE", "maturing",
     "NCR industrial city, RapidX rail and residential boom"),

    ("ayodhya", "Ayodhya", "Uttar Pradesh", 3, 26.7922, 82.1998,
     49593, 55890, 120000, 12, 20, 42,
     1200, 2200, 5500,
     True, True, 2, True, False,
     "religious-industrial", "Lucknow", 135,
     "Smart City", None, 0,
     "N,E,SE", "emerging",
     "Ram Mandir pilgrimage boom, new airport and tourism surge"),

    # ── MAHARASHTRA (more) ─────────────────────────────────────────────────
    ("kolhapur", "Kolhapur", "Maharashtra", 3, 16.7050, 74.2433,
     485183, 549236, 620000, 50, 68, 88,
     2200, 3400, 5200,
     True, False, 2, True, True,
     "agri-industrial", "Pune", 230,
     "AMRUT", None, 0,
     "N,E,NE", "emerging",
     "Western Maharashtra trade hub, sugar and foundry industry"),

    ("amravati", "Amravati", "Maharashtra", 3, 20.9374, 77.7796,
     549510, 647057, 720000, 55, 75, 95,
     1400, 2200, 3400,
     True, False, 2, True, True,
     "textile", "Nagpur", 155,
     "AMRUT", None, 0,
     "N,W,NW", "emerging",
     "Cotton belt city, textile park and storage hub"),

    # ── KARNATAKA (more) ───────────────────────────────────────────────────
    ("belagavi", "Belagavi", "Karnataka", 3, 15.8497, 74.4977,
     399653, 488292, 560000, 48, 70, 92,
     1800, 2800, 4200,
     True, True, 2, True, True,
     "defense-industrial", "Bangalore", 500,
     "Smart City,AMRUT", None, 0,
     "N,NE,E", "accelerating",
     "Border city, foundry cluster and second-capital push"),

    ("kalaburagi", "Kalaburagi", "Karnataka", 3, 17.3297, 76.8343,
     430651, 543147, 620000, 45, 65, 85,
     1300, 2100, 3200,
     True, True, 2, True, True,
     "agri-industrial", "Hyderabad", 220,
     "AMRUT", None, 0,
     "N,NE,W", "emerging",
     "North Karnataka hub, toor dal trade and cement industry"),

    # ── ANDHRA PRADESH (more) ──────────────────────────────────────────────
    ("nellore", "Nellore", "Andhra Pradesh", 3, 14.4426, 79.9865,
     378947, 505258, 600000, 42, 60, 80,
     1500, 2400, 3800,
     True, False, 2, True, True,
     "agri-industrial", "Chennai", 175,
     "AMRUT", None, 0,
     "N,E,NE", "emerging",
     "Aquaculture and solar hub on the Chennai-Vijayawada corridor"),

    ("kakinada", "Kakinada", "Andhra Pradesh", 3, 16.9891, 82.2475,
     296329, 312538, 380000, 35, 50, 68,
     1600, 2500, 3900,
     True, True, 1, True, True,
     "oil-port", "Visakhapatnam", 160,
     "Smart City,AMRUT", None, 0,
     "N,W,SW", "accelerating",
     "Port and petrochemical hub, fertiliser and SEZ growth"),

    # ── TAMIL NADU (more) ──────────────────────────────────────────────────
    ("vellore", "Vellore", "Tamil Nadu", 3, 12.9165, 79.1325,
     386746, 423425, 500000, 40, 58, 78,
     1800, 2800, 4300,
     True, False, 2, True, True,
     "education-industrial", "Chennai", 140,
     "AMRUT", None, 0,
     "E,SE,S", "emerging",
     "Medical and education hub (CMC, VIT), leather industry"),

    ("erode", "Erode", "Tamil Nadu", 3, 11.3410, 77.7172,
     151184, 498000, 560000, 38, 55, 72,
     1600, 2500, 3800,
     True, False, 2, True, False,
     "textile", "Coimbatore", 90,
     "AMRUT", None, 0,
     "E,W,S", "emerging",
     "Textile and turmeric trade centre of west Tamil Nadu"),

    # ── RAJASTHAN (more) ───────────────────────────────────────────────────
    ("sikar", "Sikar", "Rajasthan", 3, 27.6094, 75.1399,
     185925, 237579, 300000, 28, 42, 58,
     1400, 2200, 3400,
     True, False, 2, True, False,
     "agriculture-education", "Jaipur", 115,
     "AMRUT", None, 0,
     "S,SE,E", "emerging",
     "Shekhawati education hub, coaching and agri trade"),

    # ── GUJARAT (more) ─────────────────────────────────────────────────────
    ("gandhinagar", "Gandhinagar", "Gujarat", 2, 23.2156, 72.6369,
     195891, 292797, 410000, 50, 80, 120,
     3000, 4800, 8000,
     True, True, 2, True, True,
     "government-IT", "Ahmedabad", 28,
     "Smart City", None, 0,
     "N,NE,E", "accelerating",
     "Gujarat capital, GIFT City fintech SEZ and planned growth"),

    # ── HARYANA (more) ─────────────────────────────────────────────────────
    ("faridabad", "Faridabad", "Haryana", 2, 28.4089, 77.3178,
     1054981, 1404653, 1700000, 120, 175, 230,
     4000, 6500, 10000,
     True, False, 3, True, True,
     "industrial", "Delhi", 30,
     "Smart City,AMRUT", None, 0,
     "S,SE,E", "maturing",
     "NCR industrial belt, metro-connected manufacturing city"),

    ("panipat", "Panipat", "Haryana", 3, 29.3909, 76.9635,
     261740, 294292, 360000, 32, 48, 66,
     2500, 3800, 5800,
     True, False, 2, True, False,
     "textile", "Delhi", 90,
     "AMRUT", None, 0,
     "N,NW,S", "emerging",
     "Textile and refinery city on NH-44, handloom export hub"),

    # ── TELANGANA (more) ───────────────────────────────────────────────────
    ("karimnagar", "Karimnagar", "Telangana", 3, 18.4386, 79.1288,
     218391, 261185, 320000, 30, 45, 62,
     1300, 2100, 3300,
     True, False, 2, True, True,
     "agri-industrial", "Hyderabad", 165,
     "Smart City,AMRUT", None, 0,
     "N,NE,E", "emerging",
     "Granite and agri hub, Smart City in north Telangana"),

    ("nizamabad", "Nizamabad", "Telangana", 3, 18.6725, 78.0941,
     288722, 311152, 380000, 32, 46, 62,
     1200, 1900, 3000,
     True, False, 2, True, True,
     "agriculture", "Hyderabad", 175,
     "AMRUT", None, 0,
     "N,NW,E", "emerging",
     "Turmeric and maize trade centre of north Telangana"),

    # ── WEST BENGAL (more) ─────────────────────────────────────────────────
    ("haldia", "Haldia", "West Bengal", 3, 22.0667, 88.0698,
     130000, 200762, 270000, 30, 48, 68,
     1500, 2400, 3800,
     True, False, 2, False, False,
     "oil-port", "Kolkata", 120,
     "AMRUT", None, 0,
     "N,NW,W", "accelerating",
     "Port and petrochemical hub on the Hooghly, industrial zone"),
]


def _interpolate(a, b, steps=5):
    """Linear interpolate between two values in given steps."""
    return [a + (b - a) * i / (steps - 1) for i in range(steps)]


def _score_infrastructure(railway, airport, nhwy, univ, medcol):
    score = 0
    if railway:   score += 25
    if airport:   score += 30
    score += min(nhwy * 8, 24)
    if univ:      score += 12
    if medcol:    score += 9
    return min(score, 100)


def _score_connectivity(railway, airport, nhwy, dist_metro):
    score = 0
    if railway:  score += 20
    if airport:  score += 25
    score += min(nhwy * 10, 30)
    if dist_metro < 100:   score += 25
    elif dist_metro < 300: score += 15
    elif dist_metro < 600: score += 8
    return min(score, 100)


def _score_economic(industry, pop21, pop01, schemes_list, tier):
    base = {"IT": 85, "IT-auto": 90, "IT-pharma": 90, "IT-finance": 88,
            "finance": 92, "port-finance": 80, "tourism-IT": 78,
            "steel-industrial": 72, "industrial": 68,
            "textile-IT": 75, "government-IT": 70,
            "business-IT": 82, "coal-industrial": 65,
            "government": 60, "tourism": 58, "agriculture": 42,
            "agri-industrial": 50, "textile": 55, "mining": 52,
            "defense-industrial": 65, "religious-IT": 62,
            "agri-industry": 48, "education-industrial": 58,
            "port-ship": 55, "oil-port": 68, "tourism-agri": 45,
            "agriculture-education": 40, "agriculture-commercial": 48,
            "commercial": 55, "trade-government": 55, "trade": 58,
            "government-mining": 55, "government-industrial": 58,
            "education-industry": 50, "religious-industrial": 52,
            "agri-industrial": 50}.get(industry, 50)
    pop_growth = (pop21 / max(pop01, 1)) - 1
    growth_bonus = min(pop_growth * 20, 20)
    scheme_bonus = len(schemes_list) * 5
    return round(min(base + growth_bonus + scheme_bonus, 100), 1)


def _investment_score(tier, phase, inf_score, eco_score, conn_score):
    phase_mult = {"emerging": 1.4, "accelerating": 1.15,
                  "maturing": 0.90, "mature": 0.65}
    base = (inf_score * 0.30 + eco_score * 0.40 + conn_score * 0.30)
    raw = base * phase_mult.get(phase, 1.0)
    # Tier 3 emerging cities get a slight bonus for high-potential
    if tier == 3 and phase == "emerging":
        raw = min(raw * 1.1, 95)
    return round(min(raw, 95), 1)


def _build_city(t):
    (cid, name, state, tier, lat, lng,
     pop01, pop11, pop21, area01, area11, area21,
     price10, price15, price21,
     railway, airport, nhwy, univ, medcol,
     industry, metro, dist_metro,
     schemes_str, twin_id, twin_lag,
     dirs_str, phase, desc) = t

    schemes = [s.strip() for s in schemes_str.split(",") if s.strip()]
    dirs = [d.strip() for d in dirs_str.split(",") if d.strip()]

    # Interpolate area for 2006 and 2016
    area06 = round(area01 + (area11 - area01) * 0.5, 2)
    area16 = round(area11 + (area21 - area11) * 0.5, 2)

    inf_s = _score_infrastructure(railway, airport, nhwy, univ, medcol)
    conn_s = _score_connectivity(railway, airport, nhwy, dist_metro)
    eco_s = _score_economic(industry, pop21, pop01, schemes, tier)
    inv_s = _investment_score(tier, phase, inf_s, eco_s, conn_s)

    # Growth triggers derived from infrastructure
    triggers = []
    if railway:     triggers.append("railway_connectivity")
    if airport:     triggers.append("airport_access")
    if nhwy >= 2:   triggers.append("national_highway_junction")
    if "Smart City" in schemes: triggers.append("smart_city_mission")
    if "AMRUT" in schemes:      triggers.append("amrut_scheme")
    if tier == 3:               triggers.append("tier3_emerging_market")

    return {
        "id": cid,
        "name": name,
        "state": state,
        "tier": tier,
        "lat": lat,
        "lng": lng,
        "population": {"2001": pop01, "2011": pop11, "2021": pop21},
        "urban_area_sqkm": {
            "2001": area01, "2006": area06,
            "2011": area11, "2016": area16, "2021": area21
        },
        "land_price_inr_per_sqft": {
            "2010": price10, "2015": price15, "2021": price21
        },
        "infrastructure": {
            "has_railway": railway,
            "has_airport": airport,
            "num_national_highways": nhwy,
            "has_university": univ,
            "has_medical_college": medcol,
            "industry_type": industry
        },
        "scores": {
            "infrastructure": inf_s,
            "connectivity": conn_s,
            "economic_activity": eco_s,
            "overall": round((inf_s + conn_s + eco_s) / 3, 1)
        },
        "growth_triggers": triggers,
        "growth_directions": dirs,
        "nearest_metro": metro,
        "dist_to_metro_km": dist_metro,
        "government_schemes": schemes,
        "twin_city_id": twin_id,
        "twin_city_lag_years": twin_lag,
        "growth_phase": phase,
        "investment_score": inv_s,
        "description": desc
    }


# Build the full city lookup dict
CITIES: dict[str, dict] = {c[0]: _build_city(c) for c in _RAW}

# Group by state
STATES: dict[str, list[str]] = {}
for cid, city in CITIES.items():
    s = city["state"]
    STATES.setdefault(s, []).append(cid)


def get_all_cities() -> list[dict]:
    return list(CITIES.values())


def get_city(city_id: str) -> dict | None:
    return CITIES.get(city_id)


def search_cities(q: str = "", state: str = "", tier: int | None = None) -> list[dict]:
    results = list(CITIES.values())
    if q:
        q_lower = q.lower()
        results = [c for c in results
                   if q_lower in c["name"].lower() or q_lower in c["state"].lower()]
    if state:
        results = [c for c in results if c["state"].lower() == state.lower()]
    if tier is not None:
        results = [c for c in results if c["tier"] == tier]
    return results


def get_states() -> list[str]:
    return sorted(STATES.keys())
