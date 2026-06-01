// ─── LandAI Mock Data (AUTO-GENERATED from the FastAPI backend) ─────────────
// Fallback dataset used when the backend is offline. Mirrors /api/cities so the
// UI shows identical numbers whether the backend is up or not.
// 116 cities across 25 states. Regenerate: python scripts/generate_mock_data.py

export const MOCK_STATES = ["Andhra Pradesh", "Assam", "Bihar", "Chandigarh", "Chhattisgarh", "Delhi", "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jammu & Kashmir", "Jharkhand", "Karnataka", "Kerala", "Madhya Pradesh", "Maharashtra", "Odisha", "Puducherry", "Punjab", "Rajasthan", "Tamil Nadu", "Telangana", "Uttar Pradesh", "Uttarakhand", "West Bengal"]

export const MOCK_CITIES = [
{
"id": "patna",
"name": "Patna",
"state": "Bihar",
"tier": 2,
"lat": 25.5941,
"lng": 85.1376,
"population": {
"2001": 1366000,
"2011": 1683000,
"2021": 2050000
},
"urban_area_sqkm": {
"2001": 100,
"2006": 132.5,
"2011": 165,
"2016": 197.5,
"2021": 230
},
"land_price_inr_per_sqft": {
"2010": 2500,
"2015": 4500,
"2021": 7500
},
"infrastructure": {
"has_railway": true,
"has_airport": true,
"num_national_highways": 3,
"has_university": true,
"has_medical_college": true,
"industry_type": "government"
},
"scores": {
"infrastructure": 100,
"connectivity": 75,
"economic_activity": 80.0,
"overall": 85.0
},
"growth_triggers": [
"railway_connectivity",
"airport_access",
"national_highway_junction",
"smart_city_mission",
"amrut_scheme"
],
"growth_directions": [
"N",
"E",
"W"
],
"nearest_metro": "Delhi",
"dist_to_metro_km": 1000,
"government_schemes": [
"Smart City",
"AMRUT"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "maturing",
"investment_score": 76.0,
"description": "State capital of Bihar, fastest growing Tier-2 in East India"
},
{
"id": "gaya",
"name": "Gaya",
"state": "Bihar",
"tier": 2,
"lat": 24.7955,
"lng": 85.0002,
"population": {
"2001": 383197,
"2011": 470839,
"2021": 570000
},
"urban_area_sqkm": {
"2001": 25,
"2006": 32.5,
"2011": 40,
"2016": 49.0,
"2021": 58
},
"land_price_inr_per_sqft": {
"2010": 800,
"2015": 1500,
"2021": 2500
},
"infrastructure": {
"has_railway": true,
"has_airport": true,
"num_national_highways": 2,
"has_university": true,
"has_medical_college": true,
"industry_type": "tourism"
},
"scores": {
"infrastructure": 92,
"connectivity": 80,
"economic_activity": 77.7,
"overall": 83.2
},
"growth_triggers": [
"railway_connectivity",
"airport_access",
"national_highway_junction",
"smart_city_mission",
"amrut_scheme"
],
"growth_directions": [
"N",
"NE",
"E"
],
"nearest_metro": "Patna",
"dist_to_metro_km": 100,
"government_schemes": [
"Smart City",
"AMRUT"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "accelerating",
"investment_score": 95,
"description": "Religious and tourist city, Buddhist circuit hub"
},
{
"id": "muzaffarpur",
"name": "Muzaffarpur",
"state": "Bihar",
"tier": 2,
"lat": 26.1197,
"lng": 85.391,
"population": {
"2001": 305936,
"2011": 393724,
"2021": 480000
},
"urban_area_sqkm": {
"2001": 22,
"2006": 28.5,
"2011": 35,
"2016": 43.5,
"2021": 52
},
"land_price_inr_per_sqft": {
"2010": 700,
"2015": 1200,
"2021": 2000
},
"infrastructure": {
"has_railway": true,
"has_airport": false,
"num_national_highways": 2,
"has_university": true,
"has_medical_college": true,
"industry_type": "agriculture"
},
"scores": {
"infrastructure": 62,
"connectivity": 65,
"economic_activity": 58.4,
"overall": 61.8
},
"growth_triggers": [
"railway_connectivity",
"national_highway_junction",
"amrut_scheme"
],
"growth_directions": [
"N",
"E",
"SE"
],
"nearest_metro": "Patna",
"dist_to_metro_km": 75,
"government_schemes": [
"AMRUT"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "accelerating",
"investment_score": 70.7,
"description": "Commercial hub of North Bihar, litchi export centre"
},
{
"id": "bhagalpur",
"name": "Bhagalpur",
"state": "Bihar",
"tier": 2,
"lat": 25.2425,
"lng": 86.9842,
"population": {
"2001": 340767,
"2011": 410210,
"2021": 500000
},
"urban_area_sqkm": {
"2001": 28,
"2006": 36.0,
"2011": 44,
"2016": 53.5,
"2021": 63
},
"land_price_inr_per_sqft": {
"2010": 600,
"2015": 1100,
"2021": 1800
},
"infrastructure": {
"has_railway": true,
"has_airport": false,
"num_national_highways": 2,
"has_university": true,
"has_medical_college": true,
"industry_type": "textile"
},
"scores": {
"infrastructure": 62,
"connectivity": 55,
"economic_activity": 69.3,
"overall": 62.1
},
"growth_triggers": [
"railway_connectivity",
"national_highway_junction",
"amrut_scheme"
],
"growth_directions": [
"W",
"NW",
"N"
],
"nearest_metro": "Patna",
"dist_to_metro_km": 220,
"government_schemes": [
"AMRUT"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "accelerating",
"investment_score": 72.2,
"description": "Silk city of India, Bhagalpuri silk capital"
},
{
"id": "darbhanga",
"name": "Darbhanga",
"state": "Bihar",
"tier": 2,
"lat": 26.1542,
"lng": 85.8918,
"population": {
"2001": 218391,
"2011": 296194,
"2021": 390000
},
"urban_area_sqkm": {
"2001": 15,
"2006": 21.5,
"2011": 28,
"2016": 36.5,
"2021": 45
},
"land_price_inr_per_sqft": {
"2010": 300,
"2015": 550,
"2021": 1000
},
"infrastructure": {
"has_railway": true,
"has_airport": true,
"num_national_highways": 2,
"has_university": true,
"has_medical_college": true,
"industry_type": "agriculture"
},
"scores": {
"infrastructure": 92,
"connectivity": 80,
"economic_activity": 67.7,
"overall": 79.9
},
"growth_triggers": [
"railway_connectivity",
"airport_access",
"national_highway_junction",
"smart_city_mission",
"amrut_scheme"
],
"growth_directions": [
"N",
"E",
"SE"
],
"nearest_metro": "Patna",
"dist_to_metro_km": 140,
"government_schemes": [
"AMRUT",
"Smart City"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "accelerating",
"investment_score": 90.5,
"description": "Cultural capital of Mithila, airport boosted growth"
},
{
"id": "jhanjharpur",
"name": "Jhanjharpur",
"state": "Bihar",
"tier": 3,
"lat": 26.2659,
"lng": 86.2823,
"population": {
"2001": 18000,
"2011": 28000,
"2021": 40000
},
"urban_area_sqkm": {
"2001": 3.2,
"2006": 4.85,
"2011": 6.5,
"2016": 8.65,
"2021": 10.8
},
"land_price_inr_per_sqft": {
"2010": 200,
"2015": 400,
"2021": 700
},
"infrastructure": {
"has_railway": true,
"has_airport": false,
"num_national_highways": 1,
"has_university": false,
"has_medical_college": false,
"industry_type": "agriculture"
},
"scores": {
"infrastructure": 33,
"connectivity": 55,
"economic_activity": 67,
"overall": 51.7
},
"growth_triggers": [
"railway_connectivity",
"amrut_scheme",
"tier3_emerging_market"
],
"growth_directions": [
"N",
"E"
],
"nearest_metro": "Darbhanga",
"dist_to_metro_km": 45,
"government_schemes": [
"AMRUT"
],
"twin_city_id": "darbhanga",
"twin_city_lag_years": 15,
"growth_phase": "emerging",
"investment_score": 81.9,
"description": "Fastest growing Tier-3 near Darbhanga, 15-yr lagged twin"
},
{
"id": "purnia",
"name": "Purnia",
"state": "Bihar",
"tier": 3,
"lat": 25.7771,
"lng": 87.4753,
"population": {
"2001": 171196,
"2011": 236393,
"2021": 300000
},
"urban_area_sqkm": {
"2001": 14,
"2006": 18.5,
"2011": 23,
"2016": 29.0,
"2021": 35
},
"land_price_inr_per_sqft": {
"2010": 400,
"2015": 700,
"2021": 1200
},
"infrastructure": {
"has_railway": true,
"has_airport": false,
"num_national_highways": 2,
"has_university": false,
"has_medical_college": true,
"industry_type": "agriculture"
},
"scores": {
"infrastructure": 50,
"connectivity": 48,
"economic_activity": 62.0,
"overall": 53.3
},
"growth_triggers": [
"railway_connectivity",
"national_highway_junction",
"amrut_scheme",
"tier3_emerging_market"
],
"growth_directions": [
"N",
"W",
"SW"
],
"nearest_metro": "Patna",
"dist_to_metro_km": 340,
"government_schemes": [
"AMRUT"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "accelerating",
"investment_score": 62.3,
"description": "North Bihar trade hub, close to Bangladesh border"
},
{
"id": "begusarai",
"name": "Begusarai",
"state": "Bihar",
"tier": 3,
"lat": 25.4182,
"lng": 86.1272,
"population": {
"2001": 114882,
"2011": 151878,
"2021": 195000
},
"urban_area_sqkm": {
"2001": 8,
"2006": 11.0,
"2011": 14,
"2016": 18.0,
"2021": 22
},
"land_price_inr_per_sqft": {
"2010": 300,
"2015": 550,
"2021": 950
},
"infrastructure": {
"has_railway": true,
"has_airport": false,
"num_national_highways": 2,
"has_university": false,
"has_medical_college": false,
"industry_type": "industry"
},
"scores": {
"infrastructure": 41,
"connectivity": 55,
"economic_activity": 68.9,
"overall": 55.0
},
"growth_triggers": [
"railway_connectivity",
"national_highway_junction",
"amrut_scheme",
"tier3_emerging_market"
],
"growth_directions": [
"E",
"SE",
"S"
],
"nearest_metro": "Patna",
"dist_to_metro_km": 120,
"government_schemes": [
"AMRUT"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "accelerating",
"investment_score": 64.8,
"description": "Industrial town with IOCL refinery"
},
{
"id": "samastipur",
"name": "Samastipur",
"state": "Bihar",
"tier": 3,
"lat": 25.871,
"lng": 85.7808,
"population": {
"2001": 103890,
"2011": 136400,
"2021": 175000
},
"urban_area_sqkm": {
"2001": 7,
"2006": 9.5,
"2011": 12,
"2016": 15.5,
"2021": 19
},
"land_price_inr_per_sqft": {
"2010": 250,
"2015": 450,
"2021": 800
},
"infrastructure": {
"has_railway": true,
"has_airport": false,
"num_national_highways": 1,
"has_university": false,
"has_medical_college": false,
"industry_type": "agriculture"
},
"scores": {
"infrastructure": 33,
"connectivity": 55,
"economic_activity": 60.7,
"overall": 49.6
},
"growth_triggers": [
"railway_connectivity",
"amrut_scheme",
"tier3_emerging_market"
],
"growth_directions": [
"N",
"E",
"S"
],
"nearest_metro": "Patna",
"dist_to_metro_km": 70,
"government_schemes": [
"AMRUT"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "emerging",
"investment_score": 78.0,
"description": "Railway junction and agricultural market town"
},
{
"id": "arrah",
"name": "Arrah",
"state": "Bihar",
"tier": 3,
"lat": 25.556,
"lng": 84.6627,
"population": {
"2001": 205432,
"2011": 261395,
"2021": 330000
},
"urban_area_sqkm": {
"2001": 16,
"2006": 20.5,
"2011": 25,
"2016": 31.5,
"2021": 38
},
"land_price_inr_per_sqft": {
"2010": 350,
"2015": 600,
"2021": 1100
},
"infrastructure": {
"has_railway": true,
"has_airport": false,
"num_national_highways": 2,
"has_university": false,
"has_medical_college": true,
"industry_type": "agriculture"
},
"scores": {
"infrastructure": 50,
"connectivity": 65,
"economic_activity": 59.1,
"overall": 58.0
},
"growth_triggers": [
"railway_connectivity",
"national_highway_junction",
"amrut_scheme",
"tier3_emerging_market"
],
"growth_directions": [
"N",
"W",
"NW"
],
"nearest_metro": "Patna",
"dist_to_metro_km": 60,
"government_schemes": [
"AMRUT"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "accelerating",
"investment_score": 66.9,
"description": "Bhojpur district HQ, highway NH30 proximity"
},
{
"id": "chapra",
"name": "Chapra",
"state": "Bihar",
"tier": 3,
"lat": 25.7813,
"lng": 84.7511,
"population": {
"2001": 177975,
"2011": 225289,
"2021": 285000
},
"urban_area_sqkm": {
"2001": 13,
"2006": 17.5,
"2011": 22,
"2016": 28.0,
"2021": 34
},
"land_price_inr_per_sqft": {
"2010": 300,
"2015": 500,
"2021": 900
},
"infrastructure": {
"has_railway": true,
"has_airport": false,
"num_national_highways": 2,
"has_university": false,
"has_medical_college": false,
"industry_type": "agriculture"
},
"scores": {
"infrastructure": 41,
"connectivity": 65,
"economic_activity": 59.0,
"overall": 55.0
},
"growth_triggers": [
"railway_connectivity",
"national_highway_junction",
"amrut_scheme",
"tier3_emerging_market"
],
"growth_directions": [
"N",
"E",
"S"
],
"nearest_metro": "Patna",
"dist_to_metro_km": 80,
"government_schemes": [
"AMRUT"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "accelerating",
"investment_score": 63.7,
"description": "Saran district HQ on Ganga-Ghaghra confluence"
},
{
"id": "bettiah",
"name": "Bettiah",
"state": "Bihar",
"tier": 3,
"lat": 27.0191,
"lng": 84.5048,
"population": {
"2001": 90000,
"2011": 118000,
"2021": 155000
},
"urban_area_sqkm": {
"2001": 7,
"2006": 9.5,
"2011": 12,
"2016": 15.0,
"2021": 18
},
"land_price_inr_per_sqft": {
"2010": 200,
"2015": 380,
"2021": 680
},
"infrastructure": {
"has_railway": true,
"has_airport": false,
"num_national_highways": 1,
"has_university": false,
"has_medical_college": false,
"industry_type": "agriculture"
},
"scores": {
"infrastructure": 33,
"connectivity": 55,
"economic_activity": 61.4,
"overall": 49.8
},
"growth_triggers": [
"railway_connectivity",
"amrut_scheme",
"tier3_emerging_market"
],
"growth_directions": [
"E",
"SE",
"S"
],
"nearest_metro": "Gorakhpur",
"dist_to_metro_km": 80,
"government_schemes": [
"AMRUT"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "emerging",
"investment_score": 78.5,
"description": "West Champaran HQ near Valmiki Tiger Reserve"
},
{
"id": "motihari",
"name": "Motihari",
"state": "Bihar",
"tier": 3,
"lat": 26.6492,
"lng": 84.9183,
"population": {
"2001": 83125,
"2011": 123904,
"2021": 165000
},
"urban_area_sqkm": {
"2001": 6,
"2006": 8.5,
"2011": 11,
"2016": 14.0,
"2021": 17
},
"land_price_inr_per_sqft": {
"2010": 200,
"2015": 370,
"2021": 650
},
"infrastructure": {
"has_railway": true,
"has_airport": false,
"num_national_highways": 1,
"has_university": false,
"has_medical_college": false,
"industry_type": "agriculture"
},
"scores": {
"infrastructure": 33,
"connectivity": 45,
"economic_activity": 66.7,
"overall": 48.2
},
"growth_triggers": [
"railway_connectivity",
"amrut_scheme",
"tier3_emerging_market"
],
"growth_directions": [
"E",
"S",
"SW"
],
"nearest_metro": "Gorakhpur",
"dist_to_metro_km": 100,
"government_schemes": [
"AMRUT"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "emerging",
"investment_score": 77.1,
"description": "East Champaran HQ, Mahatma Gandhi birthplace district"
},
{
"id": "sasaram",
"name": "Sasaram",
"state": "Bihar",
"tier": 3,
"lat": 24.9468,
"lng": 84.0288,
"population": {
"2001": 134350,
"2011": 147051,
"2021": 190000
},
"urban_area_sqkm": {
"2001": 9,
"2006": 12.0,
"2011": 15,
"2016": 19.0,
"2021": 23
},
"land_price_inr_per_sqft": {
"2010": 250,
"2015": 420,
"2021": 750
},
"infrastructure": {
"has_railway": true,
"has_airport": false,
"num_national_highways": 2,
"has_university": false,
"has_medical_college": false,
"industry_type": "agriculture"
},
"scores": {
"infrastructure": 41,
"connectivity": 55,
"economic_activity": 55.3,
"overall": 50.4
},
"growth_triggers": [
"railway_connectivity",
"national_highway_junction",
"amrut_scheme",
"tier3_emerging_market"
],
"growth_directions": [
"N",
"E",
"NE"
],
"nearest_metro": "Patna",
"dist_to_metro_km": 165,
"government_schemes": [
"AMRUT"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "emerging",
"investment_score": 78.4,
"description": "Historical town on Grand Trunk Road NH2"
},
{
"id": "sitamarhi",
"name": "Sitamarhi",
"state": "Bihar",
"tier": 3,
"lat": 26.5925,
"lng": 85.4776,
"population": {
"2001": 72578,
"2011": 100146,
"2021": 135000
},
"urban_area_sqkm": {
"2001": 5,
"2006": 7.0,
"2011": 9,
"2016": 11.5,
"2021": 14
},
"land_price_inr_per_sqft": {
"2010": 180,
"2015": 320,
"2021": 580
},
"infrastructure": {
"has_railway": true,
"has_airport": false,
"num_national_highways": 1,
"has_university": false,
"has_medical_college": false,
"industry_type": "agriculture"
},
"scores": {
"infrastructure": 33,
"connectivity": 55,
"economic_activity": 64.2,
"overall": 50.7
},
"growth_triggers": [
"railway_connectivity",
"amrut_scheme",
"tier3_emerging_market"
],
"growth_directions": [
"S",
"SE",
"E"
],
"nearest_metro": "Muzaffarpur",
"dist_to_metro_km": 75,
"government_schemes": [
"AMRUT"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "emerging",
"investment_score": 80.2,
"description": "Religious town near Nepal border, birthplace of Sita"
},
{
"id": "lucknow",
"name": "Lucknow",
"state": "Uttar Pradesh",
"tier": 2,
"lat": 26.8467,
"lng": 80.9462,
"population": {
"2001": 2245509,
"2011": 2901474,
"2021": 3800000
},
"urban_area_sqkm": {
"2001": 200,
"2006": 255.0,
"2011": 310,
"2016": 365.0,
"2021": 420
},
"land_price_inr_per_sqft": {
"2010": 3000,
"2015": 5000,
"2021": 8000
},
"infrastructure": {
"has_railway": true,
"has_airport": true,
"num_national_highways": 4,
"has_university": true,
"has_medical_college": true,
"industry_type": "government"
},
"scores": {
"infrastructure": 100,
"connectivity": 83,
"economic_activity": 83.8,
"overall": 88.9
},
"growth_triggers": [
"railway_connectivity",
"airport_access",
"national_highway_junction",
"smart_city_mission",
"amrut_scheme"
],
"growth_directions": [
"N",
"E",
"NE",
"W"
],
"nearest_metro": "Delhi",
"dist_to_metro_km": 510,
"government_schemes": [
"Smart City",
"AMRUT"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "maturing",
"investment_score": 79.6,
"description": "State capital, Nawabi culture + modern IT parks"
},
{
"id": "kanpur",
"name": "Kanpur",
"state": "Uttar Pradesh",
"tier": 2,
"lat": 26.4499,
"lng": 80.3319,
"population": {
"2001": 2690486,
"2011": 2920496,
"2021": 3500000
},
"urban_area_sqkm": {
"2001": 230,
"2006": 270.0,
"2011": 310,
"2016": 345.0,
"2021": 380
},
"land_price_inr_per_sqft": {
"2010": 2000,
"2015": 3500,
"2021": 5500
},
"infrastructure": {
"has_railway": true,
"has_airport": true,
"num_national_highways": 3,
"has_university": true,
"has_medical_college": true,
"industry_type": "industry"
},
"scores": {
"infrastructure": 100,
"connectivity": 83,
"economic_activity": 66.0,
"overall": 83.0
},
"growth_triggers": [
"railway_connectivity",
"airport_access",
"national_highway_junction",
"smart_city_mission",
"amrut_scheme"
],
"growth_directions": [
"N",
"NE",
"E"
],
"nearest_metro": "Delhi",
"dist_to_metro_km": 480,
"government_schemes": [
"Smart City",
"AMRUT"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "maturing",
"investment_score": 73.2,
"description": "Industrial city, leather and textile capital"
},
{
"id": "agra",
"name": "Agra",
"state": "Uttar Pradesh",
"tier": 2,
"lat": 27.1767,
"lng": 78.0081,
"population": {
"2001": 1321410,
"2011": 1574542,
"2021": 2000000
},
"urban_area_sqkm": {
"2001": 110,
"2006": 137.5,
"2011": 165,
"2016": 192.5,
"2021": 220
},
"land_price_inr_per_sqft": {
"2010": 2500,
"2015": 4000,
"2021": 6000
},
"infrastructure": {
"has_railway": true,
"has_airport": true,
"num_national_highways": 3,
"has_university": true,
"has_medical_college": true,
"industry_type": "tourism"
},
"scores": {
"infrastructure": 100,
"connectivity": 90,
"economic_activity": 78.3,
"overall": 89.4
},
"growth_triggers": [
"railway_connectivity",
"airport_access",
"national_highway_junction",
"smart_city_mission",
"amrut_scheme"
],
"growth_directions": [
"N",
"NW",
"W"
],
"nearest_metro": "Delhi",
"dist_to_metro_km": 220,
"government_schemes": [
"Smart City",
"AMRUT"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "maturing",
"investment_score": 79.5,
"description": "City of Taj Mahal, tourism + real-estate boom"
},
{
"id": "varanasi",
"name": "Varanasi",
"state": "Uttar Pradesh",
"tier": 2,
"lat": 25.3176,
"lng": 82.9739,
"population": {
"2001": 1091918,
"2011": 1201815,
"2021": 1600000
},
"urban_area_sqkm": {
"2001": 90,
"2006": 112.5,
"2011": 135,
"2016": 160.0,
"2021": 185
},
"land_price_inr_per_sqft": {
"2010": 2000,
"2015": 3500,
"2021": 5500
},
"infrastructure": {
"has_railway": true,
"has_airport": true,
"num_national_highways": 2,
"has_university": true,
"has_medical_college": true,
"industry_type": "tourism"
},
"scores": {
"infrastructure": 92,
"connectivity": 80,
"economic_activity": 77.3,
"overall": 83.1
},
"growth_triggers": [
"railway_connectivity",
"airport_access",
"national_highway_junction",
"smart_city_mission",
"amrut_scheme"
],
"growth_directions": [
"N",
"NE",
"E"
],
"nearest_metro": "Prayagraj",
"dist_to_metro_km": 125,
"government_schemes": [
"Smart City",
"AMRUT"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "accelerating",
"investment_score": 94.9,
"description": "Oldest living city, Ganga Expressway catalyst"
},
{
"id": "prayagraj",
"name": "Prayagraj",
"state": "Uttar Pradesh",
"tier": 2,
"lat": 25.4358,
"lng": 81.8463,
"population": {
"2001": 1049591,
"2011": 1212395,
"2021": 1550000
},
"urban_area_sqkm": {
"2001": 85,
"2006": 107.5,
"2011": 130,
"2016": 155.0,
"2021": 180
},
"land_price_inr_per_sqft": {
"2010": 1500,
"2015": 2800,
"2021": 4500
},
"infrastructure": {
"has_railway": true,
"has_airport": true,
"num_national_highways": 3,
"has_university": true,
"has_medical_college": true,
"industry_type": "government"
},
"scores": {
"infrastructure": 100,
"connectivity": 90,
"economic_activity": 79.5,
"overall": 89.8
},
"growth_triggers": [
"railway_connectivity",
"airport_access",
"national_highway_junction",
"smart_city_mission",
"amrut_scheme"
],
"growth_directions": [
"N",
"NE",
"W"
],
"nearest_metro": "Lucknow",
"dist_to_metro_km": 210,
"government_schemes": [
"Smart City",
"AMRUT"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "accelerating",
"investment_score": 95,
"description": "Sangam city, legal + educational hub, Kumbh investment"
},
{
"id": "gorakhpur",
"name": "Gorakhpur",
"state": "Uttar Pradesh",
"tier": 2,
"lat": 26.7606,
"lng": 83.3732,
"population": {
"2001": 624570,
"2011": 673446,
"2021": 860000
},
"urban_area_sqkm": {
"2001": 48,
"2006": 60.0,
"2011": 72,
"2016": 86.0,
"2021": 100
},
"land_price_inr_per_sqft": {
"2010": 800,
"2015": 1500,
"2021": 2800
},
"infrastructure": {
"has_railway": true,
"has_airport": true,
"num_national_highways": 3,
"has_university": true,
"has_medical_college": true,
"industry_type": "agriculture"
},
"scores": {
"infrastructure": 100,
"connectivity": 90,
"economic_activity": 59.5,
"overall": 83.2
},
"growth_triggers": [
"railway_connectivity",
"airport_access",
"national_highway_junction",
"smart_city_mission",
"amrut_scheme"
],
"growth_directions": [
"N",
"E",
"SE"
],
"nearest_metro": "Lucknow",
"dist_to_metro_km": 275,
"government_schemes": [
"Smart City",
"AMRUT"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "accelerating",
"investment_score": 92.9,
"description": "Educational and agricultural hub, AIIMS + fertiliser plant"
},
{
"id": "meerut",
"name": "Meerut",
"state": "Uttar Pradesh",
"tier": 2,
"lat": 28.9845,
"lng": 77.7064,
"population": {
"2001": 1161716,
"2011": 1305429,
"2021": 1700000
},
"urban_area_sqkm": {
"2001": 95,
"2006": 120.0,
"2011": 145,
"2016": 172.5,
"2021": 200
},
"land_price_inr_per_sqft": {
"2010": 2500,
"2015": 4000,
"2021": 6500
},
"infrastructure": {
"has_railway": true,
"has_airport": true,
"num_national_highways": 3,
"has_university": true,
"has_medical_college": true,
"industry_type": "industry"
},
"scores": {
"infrastructure": 100,
"connectivity": 100,
"economic_activity": 69.3,
"overall": 89.8
},
"growth_triggers": [
"railway_connectivity",
"airport_access",
"national_highway_junction",
"smart_city_mission",
"amrut_scheme"
],
"growth_directions": [
"N",
"E",
"S"
],
"nearest_metro": "Delhi",
"dist_to_metro_km": 65,
"government_schemes": [
"Smart City",
"AMRUT"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "accelerating",
"investment_score": 95,
"description": "Sports goods + industrial city, RapidX corridor to Delhi"
},
{
"id": "bareilly",
"name": "Bareilly",
"state": "Uttar Pradesh",
"tier": 2,
"lat": 28.367,
"lng": 79.4304,
"population": {
"2001": 718395,
"2011": 903668,
"2021": 1150000
},
"urban_area_sqkm": {
"2001": 55,
"2006": 70.0,
"2011": 85,
"2016": 102.5,
"2021": 120
},
"land_price_inr_per_sqft": {
"2010": 1000,
"2015": 1800,
"2021": 3000
},
"infrastructure": {
"has_railway": true,
"has_airport": true,
"num_national_highways": 2,
"has_university": true,
"has_medical_college": true,
"industry_type": "industry"
},
"scores": {
"infrastructure": 92,
"connectivity": 80,
"economic_activity": 67.0,
"overall": 79.7
},
"growth_triggers": [
"railway_connectivity",
"airport_access",
"national_highway_junction",
"amrut_scheme"
],
"growth_directions": [
"N",
"NE",
"E"
],
"nearest_metro": "Delhi",
"dist_to_metro_km": 250,
"government_schemes": [
"AMRUT"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "accelerating",
"investment_score": 90.2,
"description": "Furniture and sugar industry hub"
},
{
"id": "aligarh",
"name": "Aligarh",
"state": "Uttar Pradesh",
"tier": 3,
"lat": 27.8974,
"lng": 78.088,
"population": {
"2001": 669087,
"2011": 874408,
"2021": 1100000
},
"urban_area_sqkm": {
"2001": 52,
"2006": 66.0,
"2011": 80,
"2016": 96.0,
"2021": 112
},
"land_price_inr_per_sqft": {
"2010": 1200,
"2015": 2000,
"2021": 3500
},
"infrastructure": {
"has_railway": true,
"has_airport": false,
"num_national_highways": 2,
"has_university": true,
"has_medical_college": false,
"industry_type": "industry"
},
"scores": {
"infrastructure": 53,
"connectivity": 55,
"economic_activity": 67.9,
"overall": 58.6
},
"growth_triggers": [
"railway_connectivity",
"national_highway_junction",
"amrut_scheme",
"tier3_emerging_market"
],
"growth_directions": [
"N",
"E",
"NE"
],
"nearest_metro": "Delhi",
"dist_to_metro_km": 135,
"government_schemes": [
"AMRUT"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "accelerating",
"investment_score": 68.5,
"description": "Lock industry and AMU, Yamuna Expressway proximity"
},
{
"id": "moradabad",
"name": "Moradabad",
"state": "Uttar Pradesh",
"tier": 3,
"lat": 28.8386,
"lng": 78.7733,
"population": {
"2001": 641583,
"2011": 889810,
"2021": 1130000
},
"urban_area_sqkm": {
"2001": 50,
"2006": 64.0,
"2011": 78,
"2016": 94.0,
"2021": 110
},
"land_price_inr_per_sqft": {
"2010": 1200,
"2015": 2000,
"2021": 3500
},
"infrastructure": {
"has_railway": true,
"has_airport": true,
"num_national_highways": 2,
"has_university": true,
"has_medical_college": false,
"industry_type": "industry"
},
"scores": {
"infrastructure": 83,
"connectivity": 80,
"economic_activity": 70.2,
"overall": 77.7
},
"growth_triggers": [
"railway_connectivity",
"airport_access",
"national_highway_junction",
"smart_city_mission",
"tier3_emerging_market"
],
"growth_directions": [
"N",
"E",
"SE"
],
"nearest_metro": "Delhi",
"dist_to_metro_km": 165,
"government_schemes": [
"Smart City"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "accelerating",
"investment_score": 88.5,
"description": "Brass metalwork capital, major export hub"
},
{
"id": "mathura",
"name": "Mathura",
"state": "Uttar Pradesh",
"tier": 3,
"lat": 27.4924,
"lng": 77.6737,
"population": {
"2001": 298827,
"2011": 349626,
"2021": 450000
},
"urban_area_sqkm": {
"2001": 22,
"2006": 28.0,
"2011": 34,
"2016": 41.0,
"2021": 48
},
"land_price_inr_per_sqft": {
"2010": 1500,
"2015": 2500,
"2021": 4000
},
"infrastructure": {
"has_railway": true,
"has_airport": false,
"num_national_highways": 2,
"has_university": false,
"has_medical_college": false,
"industry_type": "tourism"
},
"scores": {
"infrastructure": 41,
"connectivity": 55,
"economic_activity": 73.1,
"overall": 56.4
},
"growth_triggers": [
"railway_connectivity",
"national_highway_junction",
"amrut_scheme",
"tier3_emerging_market"
],
"growth_directions": [
"N",
"E",
"NE"
],
"nearest_metro": "Delhi",
"dist_to_metro_km": 148,
"government_schemes": [
"AMRUT"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "accelerating",
"investment_score": 66.7,
"description": "Birthplace of Krishna, religious tourism + IOCL refinery"
},
{
"id": "jhansi",
"name": "Jhansi",
"state": "Uttar Pradesh",
"tier": 3,
"lat": 25.4484,
"lng": 78.5685,
"population": {
"2001": 383248,
"2011": 507293,
"2021": 640000
},
"urban_area_sqkm": {
"2001": 29,
"2006": 37.5,
"2011": 46,
"2016": 55.5,
"2021": 65
},
"land_price_inr_per_sqft": {
"2010": 700,
"2015": 1300,
"2021": 2200
},
"infrastructure": {
"has_railway": true,
"has_airport": true,
"num_national_highways": 3,
"has_university": true,
"has_medical_college": false,
"industry_type": "industry"
},
"scores": {
"infrastructure": 91,
"connectivity": 83,
"economic_activity": 68.4,
"overall": 80.8
},
"growth_triggers": [
"railway_connectivity",
"airport_access",
"national_highway_junction",
"smart_city_mission",
"tier3_emerging_market"
],
"growth_directions": [
"N",
"NE",
"E"
],
"nearest_metro": "Delhi",
"dist_to_metro_km": 445,
"government_schemes": [
"Smart City"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "accelerating",
"investment_score": 91.5,
"description": "Defense and industrial city, Bundelkhand Expressway"
},
{
"id": "mumbai",
"name": "Mumbai",
"state": "Maharashtra",
"tier": 1,
"lat": 19.076,
"lng": 72.8777,
"population": {
"2001": 11914398,
"2011": 12478447,
"2021": 13500000
},
"urban_area_sqkm": {
"2001": 580,
"2006": 600.0,
"2011": 620,
"2016": 635.0,
"2021": 650
},
"land_price_inr_per_sqft": {
"2010": 15000,
"2015": 22000,
"2021": 30000
},
"infrastructure": {
"has_railway": true,
"has_airport": true,
"num_national_highways": 5,
"has_university": true,
"has_medical_college": true,
"industry_type": "finance"
},
"scores": {
"infrastructure": 100,
"connectivity": 100,
"economic_activity": 100,
"overall": 100.0
},
"growth_triggers": [
"railway_connectivity",
"airport_access",
"national_highway_junction",
"smart_city_mission",
"amrut_scheme"
],
"growth_directions": [
"N",
"NE",
"E"
],
"nearest_metro": "Mumbai",
"dist_to_metro_km": 0,
"government_schemes": [
"Smart City",
"AMRUT"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "mature",
"investment_score": 65.0,
"description": "Financial capital of India, BKC and Thane corridor"
},
{
"id": "pune",
"name": "Pune",
"state": "Maharashtra",
"tier": 1,
"lat": 18.5204,
"lng": 73.8567,
"population": {
"2001": 2538473,
"2011": 3115431,
"2021": 4500000
},
"urban_area_sqkm": {
"2001": 220,
"2006": 270.0,
"2011": 320,
"2016": 380.0,
"2021": 440
},
"land_price_inr_per_sqft": {
"2010": 4000,
"2015": 7000,
"2021": 11000
},
"infrastructure": {
"has_railway": true,
"has_airport": true,
"num_national_highways": 4,
"has_university": true,
"has_medical_college": true,
"industry_type": "IT"
},
"scores": {
"infrastructure": 100,
"connectivity": 90,
"economic_activity": 100,
"overall": 96.7
},
"growth_triggers": [
"railway_connectivity",
"airport_access",
"national_highway_junction",
"smart_city_mission",
"amrut_scheme"
],
"growth_directions": [
"N",
"NE",
"E",
"W"
],
"nearest_metro": "Mumbai",
"dist_to_metro_km": 160,
"government_schemes": [
"Smart City",
"AMRUT"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "maturing",
"investment_score": 87.3,
"description": "Oxford of East, Hinjewadi IT park, Pune Metro boom"
},
{
"id": "nagpur",
"name": "Nagpur",
"state": "Maharashtra",
"tier": 2,
"lat": 21.1458,
"lng": 79.0882,
"population": {
"2001": 2052066,
"2011": 2405421,
"2021": 3100000
},
"urban_area_sqkm": {
"2001": 180,
"2006": 222.5,
"2011": 265,
"2016": 317.5,
"2021": 370
},
"land_price_inr_per_sqft": {
"2010": 2500,
"2015": 4000,
"2021": 6500
},
"infrastructure": {
"has_railway": true,
"has_airport": true,
"num_national_highways": 4,
"has_university": true,
"has_medical_college": true,
"industry_type": "government"
},
"scores": {
"infrastructure": 100,
"connectivity": 75,
"economic_activity": 80.2,
"overall": 85.1
},
"growth_triggers": [
"railway_connectivity",
"airport_access",
"national_highway_junction",
"smart_city_mission",
"amrut_scheme"
],
"growth_directions": [
"N",
"E",
"S",
"W"
],
"nearest_metro": "Mumbai",
"dist_to_metro_km": 870,
"government_schemes": [
"Smart City",
"AMRUT"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "accelerating",
"investment_score": 95,
"description": "Zero Mile city, MIHAN aerospace SEZ, future capital"
},
{
"id": "nashik",
"name": "Nashik",
"state": "Maharashtra",
"tier": 2,
"lat": 19.9975,
"lng": 73.7898,
"population": {
"2001": 1077236,
"2011": 1486053,
"2021": 1950000
},
"urban_area_sqkm": {
"2001": 88,
"2006": 111.5,
"2011": 135,
"2016": 162.5,
"2021": 190
},
"land_price_inr_per_sqft": {
"2010": 2000,
"2015": 3500,
"2021": 5500
},
"infrastructure": {
"has_railway": true,
"has_airport": true,
"num_national_highways": 3,
"has_university": true,
"has_medical_college": true,
"industry_type": "agri-industrial"
},
"scores": {
"infrastructure": 100,
"connectivity": 90,
"economic_activity": 76.2,
"overall": 88.7
},
"growth_triggers": [
"railway_connectivity",
"airport_access",
"national_highway_junction",
"smart_city_mission",
"amrut_scheme"
],
"growth_directions": [
"N",
"NE",
"E"
],
"nearest_metro": "Mumbai",
"dist_to_metro_km": 185,
"government_schemes": [
"Smart City",
"AMRUT"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "accelerating",
"investment_score": 95,
"description": "Wine capital + Mumbai-Agra highway industrial corridor"
},
{
"id": "aurangabad",
"name": "Aurangabad",
"state": "Maharashtra",
"tier": 2,
"lat": 19.8762,
"lng": 75.3433,
"population": {
"2001": 872667,
"2011": 1175116,
"2021": 1550000
},
"urban_area_sqkm": {
"2001": 72,
"2006": 91.0,
"2011": 110,
"2016": 133.0,
"2021": 156
},
"land_price_inr_per_sqft": {
"2010": 1500,
"2015": 2800,
"2021": 4500
},
"infrastructure": {
"has_railway": true,
"has_airport": true,
"num_national_highways": 3,
"has_university": true,
"has_medical_college": true,
"industry_type": "industrial"
},
"scores": {
"infrastructure": 100,
"connectivity": 83,
"economic_activity": 93.5,
"overall": 92.2
},
"growth_triggers": [
"railway_connectivity",
"airport_access",
"national_highway_junction",
"smart_city_mission",
"amrut_scheme"
],
"growth_directions": [
"N",
"E",
"SE"
],
"nearest_metro": "Mumbai",
"dist_to_metro_km": 335,
"government_schemes": [
"Smart City",
"AMRUT"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "accelerating",
"investment_score": 95,
"description": "Industrial belt near Ajanta/Ellora, Shambhaji Nagar"
},
{
"id": "solapur",
"name": "Solapur",
"state": "Maharashtra",
"tier": 2,
"lat": 17.6599,
"lng": 75.9064,
"population": {
"2001": 872478,
"2011": 951558,
"2021": 1200000
},
"urban_area_sqkm": {
"2001": 70,
"2006": 85.0,
"2011": 100,
"2016": 119.0,
"2021": 138
},
"land_price_inr_per_sqft": {
"2010": 1000,
"2015": 1800,
"2021": 3000
},
"infrastructure": {
"has_railway": true,
"has_airport": true,
"num_national_highways": 2,
"has_university": true,
"has_medical_college": true,
"industry_type": "textile"
},
"scores": {
"infrastructure": 92,
"connectivity": 80,
"economic_activity": 67.5,
"overall": 79.8
},
"growth_triggers": [
"railway_connectivity",
"airport_access",
"national_highway_junction",
"amrut_scheme"
],
"growth_directions": [
"N",
"NW",
"W"
],
"nearest_metro": "Pune",
"dist_to_metro_km": 245,
"government_schemes": [
"AMRUT"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "accelerating",
"investment_score": 90.4,
"description": "Textile and sugar hub, Pune-Hyderabad axis"
},
{
"id": "thane",
"name": "Thane",
"state": "Maharashtra",
"tier": 1,
"lat": 19.2183,
"lng": 72.9781,
"population": {
"2001": 1261517,
"2011": 1818872,
"2021": 2600000
},
"urban_area_sqkm": {
"2001": 107,
"2006": 134.5,
"2011": 162,
"2016": 196.0,
"2021": 230
},
"land_price_inr_per_sqft": {
"2010": 5000,
"2015": 8000,
"2021": 12000
},
"infrastructure": {
"has_railway": true,
"has_airport": false,
"num_national_highways": 3,
"has_university": true,
"has_medical_college": true,
"industry_type": "IT"
},
"scores": {
"infrastructure": 70,
"connectivity": 75,
"economic_activity": 100,
"overall": 81.7
},
"growth_triggers": [
"railway_connectivity",
"national_highway_junction",
"smart_city_mission",
"amrut_scheme"
],
"growth_directions": [
"N",
"NE",
"E"
],
"nearest_metro": "Mumbai",
"dist_to_metro_km": 35,
"government_schemes": [
"Smart City",
"AMRUT"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "maturing",
"investment_score": 75.2,
"description": "Mumbai satellite city, fastest growing metro fringe"
},
{
"id": "bangalore",
"name": "Bangalore",
"state": "Karnataka",
"tier": 1,
"lat": 12.9716,
"lng": 77.5946,
"population": {
"2001": 5438065,
"2011": 8425970,
"2021": 13800000
},
"urban_area_sqkm": {
"2001": 460,
"2006": 580.0,
"2011": 700,
"2016": 860.0,
"2021": 1020
},
"land_price_inr_per_sqft": {
"2010": 4000,
"2015": 7000,
"2021": 12000
},
"infrastructure": {
"has_railway": true,
"has_airport": true,
"num_national_highways": 5,
"has_university": true,
"has_medical_college": true,
"industry_type": "IT"
},
"scores": {
"infrastructure": 100,
"connectivity": 83,
"economic_activity": 100,
"overall": 94.3
},
"growth_triggers": [
"railway_connectivity",
"airport_access",
"national_highway_junction",
"smart_city_mission",
"amrut_scheme"
],
"growth_directions": [
"N",
"E",
"S",
"W",
"NE"
],
"nearest_metro": "Hyderabad",
"dist_to_metro_km": 570,
"government_schemes": [
"Smart City",
"AMRUT"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "maturing",
"investment_score": 85.4,
"description": "Silicon Valley of India, Peripheral Ring Road expansion"
},
{
"id": "mysore",
"name": "Mysore",
"state": "Karnataka",
"tier": 2,
"lat": 12.2958,
"lng": 76.6394,
"population": {
"2001": 755379,
"2011": 920550,
"2021": 1200000
},
"urban_area_sqkm": {
"2001": 62,
"2006": 78.0,
"2011": 94,
"2016": 113.0,
"2021": 132
},
"land_price_inr_per_sqft": {
"2010": 1800,
"2015": 3000,
"2021": 5000
},
"infrastructure": {
"has_railway": true,
"has_airport": true,
"num_national_highways": 3,
"has_university": true,
"has_medical_college": true,
"industry_type": "tourism-IT"
},
"scores": {
"infrastructure": 100,
"connectivity": 90,
"economic_activity": 99.8,
"overall": 96.6
},
"growth_triggers": [
"railway_connectivity",
"airport_access",
"national_highway_junction",
"smart_city_mission",
"amrut_scheme"
],
"growth_directions": [
"N",
"NE",
"E"
],
"nearest_metro": "Bangalore",
"dist_to_metro_km": 150,
"government_schemes": [
"Smart City",
"AMRUT"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "accelerating",
"investment_score": 95,
"description": "Cultural capital, Infosys campus, Bangalore spillover"
},
{
"id": "hubli",
"name": "Hubli-Dharwad",
"state": "Karnataka",
"tier": 2,
"lat": 15.3647,
"lng": 75.124,
"population": {
"2001": 786195,
"2011": 943857,
"2021": 1200000
},
"urban_area_sqkm": {
"2001": 64,
"2006": 80.5,
"2011": 97,
"2016": 116.5,
"2021": 136
},
"land_price_inr_per_sqft": {
"2010": 1200,
"2015": 2200,
"2021": 3600
},
"infrastructure": {
"has_railway": true,
"has_airport": true,
"num_national_highways": 3,
"has_university": true,
"has_medical_college": true,
"industry_type": "industrial"
},
"scores": {
"infrastructure": 100,
"connectivity": 83,
"economic_activity": 88.5,
"overall": 90.5
},
"growth_triggers": [
"railway_connectivity",
"airport_access",
"national_highway_junction",
"smart_city_mission",
"amrut_scheme"
],
"growth_directions": [
"N",
"NW",
"W"
],
"nearest_metro": "Bangalore",
"dist_to_metro_km": 410,
"government_schemes": [
"Smart City",
"AMRUT"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "accelerating",
"investment_score": 95,
"description": "Twin city hub, commercial north Karnataka"
},
{
"id": "mangalore",
"name": "Mangalore",
"state": "Karnataka",
"tier": 2,
"lat": 12.9141,
"lng": 74.856,
"population": {
"2001": 398745,
"2011": 488968,
"2021": 630000
},
"urban_area_sqkm": {
"2001": 32,
"2006": 40.5,
"2011": 49,
"2016": 59.0,
"2021": 69
},
"land_price_inr_per_sqft": {
"2010": 1800,
"2015": 3200,
"2021": 5200
},
"infrastructure": {
"has_railway": true,
"has_airport": true,
"num_national_highways": 2,
"has_university": true,
"has_medical_college": true,
"industry_type": "port-finance"
},
"scores": {
"infrastructure": 92,
"connectivity": 73,
"economic_activity": 100,
"overall": 88.3
},
"growth_triggers": [
"railway_connectivity",
"airport_access",
"national_highway_junction",
"smart_city_mission",
"amrut_scheme"
],
"growth_directions": [
"N",
"NE",
"E"
],
"nearest_metro": "Bangalore",
"dist_to_metro_km": 352,
"government_schemes": [
"Smart City",
"AMRUT"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "accelerating",
"investment_score": 95,
"description": "Major port + banking capital of Coastal Karnataka"
},
{
"id": "davangere",
"name": "Davangere",
"state": "Karnataka",
"tier": 3,
"lat": 14.4644,
"lng": 75.9218,
"population": {
"2001": 363954,
"2011": 435128,
"2021": 550000
},
"urban_area_sqkm": {
"2001": 29,
"2006": 36.5,
"2011": 44,
"2016": 53.0,
"2021": 62
},
"land_price_inr_per_sqft": {
"2010": 600,
"2015": 1100,
"2021": 1800
},
"infrastructure": {
"has_railway": true,
"has_airport": true,
"num_national_highways": 2,
"has_university": true,
"has_medical_college": true,
"industry_type": "textile"
},
"scores": {
"infrastructure": 92,
"connectivity": 80,
"economic_activity": 70.2,
"overall": 80.7
},
"growth_triggers": [
"railway_connectivity",
"airport_access",
"national_highway_junction",
"amrut_scheme",
"tier3_emerging_market"
],
"growth_directions": [
"E",
"SE",
"S"
],
"nearest_metro": "Bangalore",
"dist_to_metro_km": 270,
"government_schemes": [
"AMRUT"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "accelerating",
"investment_score": 91.6,
"description": "Cotton and textile hub, central Karnataka"
},
{
"id": "chennai",
"name": "Chennai",
"state": "Tamil Nadu",
"tier": 1,
"lat": 13.0827,
"lng": 80.2707,
"population": {
"2001": 4343645,
"2011": 4646732,
"2021": 7100000
},
"urban_area_sqkm": {
"2001": 390,
"2006": 410.0,
"2011": 430,
"2016": 475.0,
"2021": 520
},
"land_price_inr_per_sqft": {
"2010": 5000,
"2015": 8000,
"2021": 13000
},
"infrastructure": {
"has_railway": true,
"has_airport": true,
"num_national_highways": 5,
"has_university": true,
"has_medical_college": true,
"industry_type": "IT-auto"
},
"scores": {
"infrastructure": 100,
"connectivity": 75,
"economic_activity": 100,
"overall": 91.7
},
"growth_triggers": [
"railway_connectivity",
"airport_access",
"national_highway_junction",
"smart_city_mission",
"amrut_scheme"
],
"growth_directions": [
"N",
"NW",
"W",
"SW"
],
"nearest_metro": "Hyderabad",
"dist_to_metro_km": 625,
"government_schemes": [
"Smart City",
"AMRUT"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "maturing",
"investment_score": 83.2,
"description": "Detroit of India + IT, OMR IT corridor boom"
},
{
"id": "coimbatore",
"name": "Coimbatore",
"state": "Tamil Nadu",
"tier": 1,
"lat": 11.0168,
"lng": 76.9558,
"population": {
"2001": 1456079,
"2011": 1601438,
"2021": 2300000
},
"urban_area_sqkm": {
"2001": 125,
"2006": 150.0,
"2011": 175,
"2016": 212.5,
"2021": 250
},
"land_price_inr_per_sqft": {
"2010": 2500,
"2015": 4000,
"2021": 6500
},
"infrastructure": {
"has_railway": true,
"has_airport": true,
"num_national_highways": 3,
"has_university": true,
"has_medical_college": true,
"industry_type": "textile-IT"
},
"scores": {
"infrastructure": 100,
"connectivity": 83,
"economic_activity": 96.6,
"overall": 93.2
},
"growth_triggers": [
"railway_connectivity",
"airport_access",
"national_highway_junction",
"smart_city_mission",
"amrut_scheme"
],
"growth_directions": [
"N",
"E",
"NE"
],
"nearest_metro": "Chennai",
"dist_to_metro_km": 508,
"government_schemes": [
"Smart City",
"AMRUT"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "accelerating",
"investment_score": 95,
"description": "Manchester of South India, growing IT hub"
},
{
"id": "madurai",
"name": "Madurai",
"state": "Tamil Nadu",
"tier": 2,
"lat": 9.9252,
"lng": 78.1198,
"population": {
"2001": 1194665,
"2011": 1462420,
"2021": 1900000
},
"urban_area_sqkm": {
"2001": 98,
"2006": 124.0,
"2011": 150,
"2016": 182.5,
"2021": 215
},
"land_price_inr_per_sqft": {
"2010": 1500,
"2015": 2600,
"2021": 4200
},
"infrastructure": {
"has_railway": true,
"has_airport": true,
"num_national_highways": 3,
"has_university": true,
"has_medical_college": true,
"industry_type": "textile-tourism"
},
"scores": {
"infrastructure": 100,
"connectivity": 83,
"economic_activity": 71.8,
"overall": 84.9
},
"growth_triggers": [
"railway_connectivity",
"airport_access",
"national_highway_junction",
"smart_city_mission",
"amrut_scheme"
],
"growth_directions": [
"N",
"NE",
"E"
],
"nearest_metro": "Chennai",
"dist_to_metro_km": 456,
"government_schemes": [
"Smart City",
"AMRUT"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "accelerating",
"investment_score": 95,
"description": "Temple city + textile hub, Third largest TN city"
},
{
"id": "tiruchirappalli",
"name": "Tiruchirappalli",
"state": "Tamil Nadu",
"tier": 2,
"lat": 10.7905,
"lng": 78.7047,
"population": {
"2001": 746062,
"2011": 916857,
"2021": 1200000
},
"urban_area_sqkm": {
"2001": 62,
"2006": 78.0,
"2011": 94,
"2016": 113.0,
"2021": 132
},
"land_price_inr_per_sqft": {
"2010": 1200,
"2015": 2000,
"2021": 3300
},
"infrastructure": {
"has_railway": true,
"has_airport": true,
"num_national_highways": 2,
"has_university": true,
"has_medical_college": true,
"industry_type": "industrial"
},
"scores": {
"infrastructure": 92,
"connectivity": 73,
"economic_activity": 90.2,
"overall": 85.1
},
"growth_triggers": [
"railway_connectivity",
"airport_access",
"national_highway_junction",
"smart_city_mission",
"amrut_scheme"
],
"growth_directions": [
"N",
"NE",
"E"
],
"nearest_metro": "Chennai",
"dist_to_metro_km": 332,
"government_schemes": [
"Smart City",
"AMRUT"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "accelerating",
"investment_score": 95,
"description": "BHEL defense industry, central TN hub"
},
{
"id": "salem",
"name": "Salem",
"state": "Tamil Nadu",
"tier": 2,
"lat": 11.6643,
"lng": 78.146,
"population": {
"2001": 693236,
"2011": 831038,
"2021": 1080000
},
"urban_area_sqkm": {
"2001": 56,
"2006": 70.5,
"2011": 85,
"2016": 102.5,
"2021": 120
},
"land_price_inr_per_sqft": {
"2010": 1000,
"2015": 1700,
"2021": 2800
},
"infrastructure": {
"has_railway": true,
"has_airport": true,
"num_national_highways": 2,
"has_university": true,
"has_medical_college": true,
"industry_type": "steel-textile"
},
"scores": {
"infrastructure": 92,
"connectivity": 73,
"economic_activity": 66.2,
"overall": 77.1
},
"growth_triggers": [
"railway_connectivity",
"airport_access",
"national_highway_junction",
"amrut_scheme"
],
"growth_directions": [
"N",
"NW",
"W"
],
"nearest_metro": "Chennai",
"dist_to_metro_km": 340,
"government_schemes": [
"AMRUT"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "accelerating",
"investment_score": 87.4,
"description": "Steel city, expressway to Chennai = land boom"
},
{
"id": "tirunelveli",
"name": "Tirunelveli",
"state": "Tamil Nadu",
"tier": 3,
"lat": 8.7139,
"lng": 77.7567,
"population": {
"2001": 432566,
"2011": 473637,
"2021": 590000
},
"urban_area_sqkm": {
"2001": 35,
"2006": 44.0,
"2011": 53,
"2016": 63.5,
"2021": 74
},
"land_price_inr_per_sqft": {
"2010": 700,
"2015": 1200,
"2021": 2000
},
"infrastructure": {
"has_railway": true,
"has_airport": true,
"num_national_highways": 2,
"has_university": true,
"has_medical_college": true,
"industry_type": "agri-industry"
},
"scores": {
"infrastructure": 92,
"connectivity": 65,
"economic_activity": 60.3,
"overall": 72.4
},
"growth_triggers": [
"railway_connectivity",
"airport_access",
"national_highway_junction",
"amrut_scheme",
"tier3_emerging_market"
],
"growth_directions": [
"N",
"NE",
"E"
],
"nearest_metro": "Chennai",
"dist_to_metro_km": 665,
"government_schemes": [
"AMRUT"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "accelerating",
"investment_score": 81.9,
"description": "Wind energy + agriculture, deep south TN"
},
{
"id": "ahmedabad",
"name": "Ahmedabad",
"state": "Gujarat",
"tier": 1,
"lat": 23.0225,
"lng": 72.5714,
"population": {
"2001": 3520085,
"2011": 5570585,
"2021": 8000000
},
"urban_area_sqkm": {
"2001": 310,
"2006": 395.0,
"2011": 480,
"2016": 590.0,
"2021": 700
},
"land_price_inr_per_sqft": {
"2010": 3500,
"2015": 5500,
"2021": 9000
},
"infrastructure": {
"has_railway": true,
"has_airport": true,
"num_national_highways": 5,
"has_university": true,
"has_medical_college": true,
"industry_type": "industry-IT"
},
"scores": {
"infrastructure": 100,
"connectivity": 83,
"economic_activity": 80,
"overall": 87.7
},
"growth_triggers": [
"railway_connectivity",
"airport_access",
"national_highway_junction",
"smart_city_mission",
"amrut_scheme"
],
"growth_directions": [
"N",
"E",
"S",
"W",
"NE"
],
"nearest_metro": "Mumbai",
"dist_to_metro_km": 555,
"government_schemes": [
"Smart City",
"AMRUT"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "maturing",
"investment_score": 78.2,
"description": "Business capital of Gujarat, GIFT City financial hub"
},
{
"id": "surat",
"name": "Surat",
"state": "Gujarat",
"tier": 1,
"lat": 21.1702,
"lng": 72.8311,
"population": {
"2001": 2433787,
"2011": 4462002,
"2021": 7200000
},
"urban_area_sqkm": {
"2001": 220,
"2006": 305.0,
"2011": 390,
"2016": 515.0,
"2021": 640
},
"land_price_inr_per_sqft": {
"2010": 2500,
"2015": 4000,
"2021": 7000
},
"infrastructure": {
"has_railway": true,
"has_airport": true,
"num_national_highways": 4,
"has_university": true,
"has_medical_college": true,
"industry_type": "textile-diamond"
},
"scores": {
"infrastructure": 100,
"connectivity": 90,
"economic_activity": 80,
"overall": 90.0
},
"growth_triggers": [
"railway_connectivity",
"airport_access",
"national_highway_junction",
"smart_city_mission",
"amrut_scheme"
],
"growth_directions": [
"N",
"NE",
"E",
"S"
],
"nearest_metro": "Ahmedabad",
"dist_to_metro_km": 265,
"government_schemes": [
"Smart City",
"AMRUT"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "maturing",
"investment_score": 80.1,
"description": "Diamond and textile capital, fastest growing Tier-1"
},
{
"id": "vadodara",
"name": "Vadodara",
"state": "Gujarat",
"tier": 2,
"lat": 22.3072,
"lng": 73.1812,
"population": {
"2001": 1306035,
"2011": 1666703,
"2021": 2200000
},
"urban_area_sqkm": {
"2001": 115,
"2006": 142.5,
"2011": 170,
"2016": 205.0,
"2021": 240
},
"land_price_inr_per_sqft": {
"2010": 1800,
"2015": 3000,
"2021": 5000
},
"infrastructure": {
"has_railway": true,
"has_airport": true,
"num_national_highways": 4,
"has_university": true,
"has_medical_college": true,
"industry_type": "industrial"
},
"scores": {
"infrastructure": 100,
"connectivity": 90,
"economic_activity": 91.7,
"overall": 93.9
},
"growth_triggers": [
"railway_connectivity",
"airport_access",
"national_highway_junction",
"smart_city_mission",
"amrut_scheme"
],
"growth_directions": [
"N",
"NE",
"E"
],
"nearest_metro": "Ahmedabad",
"dist_to_metro_km": 113,
"government_schemes": [
"Smart City",
"AMRUT"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "accelerating",
"investment_score": 95,
"description": "Petrochemicals + cultural city, Baroda"
},
{
"id": "rajkot",
"name": "Rajkot",
"state": "Gujarat",
"tier": 2,
"lat": 22.3039,
"lng": 70.8022,
"population": {
"2001": 1002160,
"2011": 1286678,
"2021": 1700000
},
"urban_area_sqkm": {
"2001": 87,
"2006": 108.5,
"2011": 130,
"2016": 157.0,
"2021": 184
},
"land_price_inr_per_sqft": {
"2010": 1500,
"2015": 2500,
"2021": 4000
},
"infrastructure": {
"has_railway": true,
"has_airport": true,
"num_national_highways": 3,
"has_university": true,
"has_medical_college": true,
"industry_type": "industrial"
},
"scores": {
"infrastructure": 100,
"connectivity": 90,
"economic_activity": 91.9,
"overall": 94.0
},
"growth_triggers": [
"railway_connectivity",
"airport_access",
"national_highway_junction",
"smart_city_mission",
"amrut_scheme"
],
"growth_directions": [
"N",
"E",
"SE"
],
"nearest_metro": "Ahmedabad",
"dist_to_metro_km": 220,
"government_schemes": [
"Smart City",
"AMRUT"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "accelerating",
"investment_score": 95,
"description": "Engineering + watch industry, Smart City model"
},
{
"id": "bhavnagar",
"name": "Bhavnagar",
"state": "Gujarat",
"tier": 3,
"lat": 21.7645,
"lng": 72.1519,
"population": {
"2001": 510958,
"2011": 605882,
"2021": 775000
},
"urban_area_sqkm": {
"2001": 42,
"2006": 52.5,
"2011": 63,
"2016": 76.0,
"2021": 89
},
"land_price_inr_per_sqft": {
"2010": 700,
"2015": 1200,
"2021": 2000
},
"infrastructure": {
"has_railway": true,
"has_airport": true,
"num_national_highways": 2,
"has_university": false,
"has_medical_college": true,
"industry_type": "port-ship"
},
"scores": {
"infrastructure": 80,
"connectivity": 80,
"economic_activity": 70.3,
"overall": 76.8
},
"growth_triggers": [
"railway_connectivity",
"airport_access",
"national_highway_junction",
"amrut_scheme",
"tier3_emerging_market"
],
"growth_directions": [
"N",
"NE",
"NW"
],
"nearest_metro": "Ahmedabad",
"dist_to_metro_km": 195,
"government_schemes": [
"AMRUT"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "accelerating",
"investment_score": 87.5,
"description": "Port city, ship-breaking industry Alang"
},
{
"id": "jamnagar",
"name": "Jamnagar",
"state": "Gujarat",
"tier": 3,
"lat": 22.4707,
"lng": 70.0577,
"population": {
"2001": 443518,
"2011": 600943,
"2021": 780000
},
"urban_area_sqkm": {
"2001": 36,
"2006": 45.5,
"2011": 55,
"2016": 66.5,
"2021": 78
},
"land_price_inr_per_sqft": {
"2010": 800,
"2015": 1400,
"2021": 2300
},
"infrastructure": {
"has_railway": true,
"has_airport": true,
"num_national_highways": 2,
"has_university": true,
"has_medical_college": false,
"industry_type": "oil-port"
},
"scores": {
"infrastructure": 83,
"connectivity": 80,
"economic_activity": 88.2,
"overall": 83.7
},
"growth_triggers": [
"railway_connectivity",
"airport_access",
"national_highway_junction",
"amrut_scheme",
"tier3_emerging_market"
],
"growth_directions": [
"N",
"NE",
"E"
],
"nearest_metro": "Ahmedabad",
"dist_to_metro_km": 298,
"government_schemes": [
"AMRUT"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "accelerating",
"investment_score": 95,
"description": "Reliance refinery city, largest refinery complex in world"
},
{
"id": "jaipur",
"name": "Jaipur",
"state": "Rajasthan",
"tier": 1,
"lat": 26.9124,
"lng": 75.7873,
"population": {
"2001": 2322575,
"2011": 3073350,
"2021": 4500000
},
"urban_area_sqkm": {
"2001": 205,
"2006": 252.5,
"2011": 300,
"2016": 362.5,
"2021": 425
},
"land_price_inr_per_sqft": {
"2010": 2500,
"2015": 4500,
"2021": 7500
},
"infrastructure": {
"has_railway": true,
"has_airport": true,
"num_national_highways": 5,
"has_university": true,
"has_medical_college": true,
"industry_type": "tourism-IT"
},
"scores": {
"infrastructure": 100,
"connectivity": 90,
"economic_activity": 100,
"overall": 96.7
},
"growth_triggers": [
"railway_connectivity",
"airport_access",
"national_highway_junction",
"smart_city_mission",
"amrut_scheme"
],
"growth_directions": [
"N",
"E",
"S",
"W",
"NE"
],
"nearest_metro": "Delhi",
"dist_to_metro_km": 268,
"government_schemes": [
"Smart City",
"AMRUT"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "maturing",
"investment_score": 87.3,
"description": "Pink City, tourism + IT boom, Metro expansion"
},
{
"id": "jodhpur",
"name": "Jodhpur",
"state": "Rajasthan",
"tier": 2,
"lat": 26.2389,
"lng": 73.0243,
"population": {
"2001": 851051,
"2011": 1033918,
"2021": 1400000
},
"urban_area_sqkm": {
"2001": 72,
"2006": 90.0,
"2011": 108,
"2016": 131.5,
"2021": 155
},
"land_price_inr_per_sqft": {
"2010": 1200,
"2015": 2200,
"2021": 3800
},
"infrastructure": {
"has_railway": true,
"has_airport": true,
"num_national_highways": 3,
"has_university": true,
"has_medical_college": true,
"industry_type": "tourism-industrial"
},
"scores": {
"infrastructure": 100,
"connectivity": 83,
"economic_activity": 72.9,
"overall": 85.3
},
"growth_triggers": [
"railway_connectivity",
"airport_access",
"national_highway_junction",
"smart_city_mission",
"amrut_scheme"
],
"growth_directions": [
"N",
"NE",
"E"
],
"nearest_metro": "Jaipur",
"dist_to_metro_km": 330,
"government_schemes": [
"Smart City",
"AMRUT"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "accelerating",
"investment_score": 95,
"description": "Blue City + defense air base, AIIMS campus"
},
{
"id": "udaipur",
"name": "Udaipur",
"state": "Rajasthan",
"tier": 2,
"lat": 24.5854,
"lng": 73.7125,
"population": {
"2001": 389317,
"2011": 451100,
"2021": 600000
},
"urban_area_sqkm": {
"2001": 32,
"2006": 40.0,
"2011": 48,
"2016": 58.0,
"2021": 68
},
"land_price_inr_per_sqft": {
"2010": 1500,
"2015": 2500,
"2021": 4200
},
"infrastructure": {
"has_railway": true,
"has_airport": true,
"num_national_highways": 2,
"has_university": true,
"has_medical_college": true,
"industry_type": "tourism"
},
"scores": {
"infrastructure": 92,
"connectivity": 80,
"economic_activity": 78.8,
"overall": 83.6
},
"growth_triggers": [
"railway_connectivity",
"airport_access",
"national_highway_junction",
"smart_city_mission",
"amrut_scheme"
],
"growth_directions": [
"N",
"NE",
"NW"
],
"nearest_metro": "Ahmedabad",
"dist_to_metro_km": 255,
"government_schemes": [
"Smart City",
"AMRUT"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "accelerating",
"investment_score": 95,
"description": "City of Lakes, luxury + heritage tourism"
},
{
"id": "kota",
"name": "Kota",
"state": "Rajasthan",
"tier": 2,
"lat": 25.2138,
"lng": 75.8648,
"population": {
"2001": 696899,
"2011": 1001694,
"2021": 1350000
},
"urban_area_sqkm": {
"2001": 58,
"2006": 73.0,
"2011": 88,
"2016": 106.5,
"2021": 125
},
"land_price_inr_per_sqft": {
"2010": 1200,
"2015": 2100,
"2021": 3500
},
"infrastructure": {
"has_railway": true,
"has_airport": true,
"num_national_highways": 2,
"has_university": true,
"has_medical_college": true,
"industry_type": "education-industrial"
},
"scores": {
"infrastructure": 92,
"connectivity": 80,
"economic_activity": 81.7,
"overall": 84.6
},
"growth_triggers": [
"railway_connectivity",
"airport_access",
"national_highway_junction",
"amrut_scheme"
],
"growth_directions": [
"N",
"E",
"SE"
],
"nearest_metro": "Jaipur",
"dist_to_metro_km": 240,
"government_schemes": [
"AMRUT"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "accelerating",
"investment_score": 95,
"description": "Coaching capital of India + Kota Super Thermal Plant"
},
{
"id": "ajmer",
"name": "Ajmer",
"state": "Rajasthan",
"tier": 3,
"lat": 26.4499,
"lng": 74.6399,
"population": {
"2001": 402700,
"2011": 551360,
"2021": 700000
},
"urban_area_sqkm": {
"2001": 33,
"2006": 42.0,
"2011": 51,
"2016": 61.5,
"2021": 72
},
"land_price_inr_per_sqft": {
"2010": 800,
"2015": 1400,
"2021": 2500
},
"infrastructure": {
"has_railway": true,
"has_airport": true,
"num_national_highways": 2,
"has_university": true,
"has_medical_college": false,
"industry_type": "religious-industrial"
},
"scores": {
"infrastructure": 83,
"connectivity": 80,
"economic_activity": 71.8,
"overall": 78.3
},
"growth_triggers": [
"railway_connectivity",
"airport_access",
"national_highway_junction",
"amrut_scheme",
"tier3_emerging_market"
],
"growth_directions": [
"N",
"NW",
"W"
],
"nearest_metro": "Jaipur",
"dist_to_metro_km": 132,
"government_schemes": [
"AMRUT"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "accelerating",
"investment_score": 89.3,
"description": "Dargah Sharif, NH-8 industrial corridor"
},
{
"id": "bikaner",
"name": "Bikaner",
"state": "Rajasthan",
"tier": 3,
"lat": 28.0229,
"lng": 73.3119,
"population": {
"2001": 416289,
"2011": 644406,
"2021": 840000
},
"urban_area_sqkm": {
"2001": 35,
"2006": 44.0,
"2011": 53,
"2016": 64.5,
"2021": 76
},
"land_price_inr_per_sqft": {
"2010": 600,
"2015": 1100,
"2021": 1900
},
"infrastructure": {
"has_railway": true,
"has_airport": true,
"num_national_highways": 2,
"has_university": true,
"has_medical_college": false,
"industry_type": "tourism-agri"
},
"scores": {
"infrastructure": 83,
"connectivity": 73,
"economic_activity": 70,
"overall": 75.3
},
"growth_triggers": [
"railway_connectivity",
"airport_access",
"national_highway_junction",
"amrut_scheme",
"tier3_emerging_market"
],
"growth_directions": [
"E",
"SE",
"S"
],
"nearest_metro": "Jaipur",
"dist_to_metro_km": 330,
"government_schemes": [
"AMRUT"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "accelerating",
"investment_score": 86.0,
"description": "Desert city, camel fair + Bikaner Expressway"
},
{
"id": "bhopal",
"name": "Bhopal",
"state": "Madhya Pradesh",
"tier": 2,
"lat": 23.2599,
"lng": 77.4126,
"population": {
"2001": 1437354,
"2011": 1795648,
"2021": 2400000
},
"urban_area_sqkm": {
"2001": 125,
"2006": 157.5,
"2011": 190,
"2016": 229.0,
"2021": 268
},
"land_price_inr_per_sqft": {
"2010": 1800,
"2015": 3000,
"2021": 5000
},
"infrastructure": {
"has_railway": true,
"has_airport": true,
"num_national_highways": 4,
"has_university": true,
"has_medical_college": true,
"industry_type": "government-IT"
},
"scores": {
"infrastructure": 100,
"connectivity": 75,
"economic_activity": 93.4,
"overall": 89.5
},
"growth_triggers": [
"railway_connectivity",
"airport_access",
"national_highway_junction",
"smart_city_mission",
"amrut_scheme"
],
"growth_directions": [
"N",
"E",
"NE",
"W"
],
"nearest_metro": "Delhi",
"dist_to_metro_km": 770,
"government_schemes": [
"Smart City",
"AMRUT"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "accelerating",
"investment_score": 95,
"description": "City of Lakes + state capital, IT Park Bhopal"
},
{
"id": "indore",
"name": "Indore",
"state": "Madhya Pradesh",
"tier": 1,
"lat": 22.7196,
"lng": 75.8577,
"population": {
"2001": 1597441,
"2011": 1964086,
"2021": 2900000
},
"urban_area_sqkm": {
"2001": 140,
"2006": 177.5,
"2011": 215,
"2016": 261.5,
"2021": 308
},
"land_price_inr_per_sqft": {
"2010": 2500,
"2015": 4000,
"2021": 7000
},
"infrastructure": {
"has_railway": true,
"has_airport": true,
"num_national_highways": 4,
"has_university": true,
"has_medical_college": true,
"industry_type": "business-IT"
},
"scores": {
"infrastructure": 100,
"connectivity": 75,
"economic_activity": 100,
"overall": 91.7
},
"growth_triggers": [
"railway_connectivity",
"airport_access",
"national_highway_junction",
"smart_city_mission",
"amrut_scheme"
],
"growth_directions": [
"N",
"E",
"S",
"W"
],
"nearest_metro": "Mumbai",
"dist_to_metro_km": 600,
"government_schemes": [
"Smart City",
"AMRUT"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "maturing",
"investment_score": 83.2,
"description": "Cleanest city 6 yrs, commercial capital, Super Corridor"
},
{
"id": "jabalpur",
"name": "Jabalpur",
"state": "Madhya Pradesh",
"tier": 2,
"lat": 23.1815,
"lng": 79.9864,
"population": {
"2001": 1098697,
"2011": 1267564,
"2021": 1650000
},
"urban_area_sqkm": {
"2001": 95,
"2006": 118.5,
"2011": 142,
"2016": 171.0,
"2021": 200
},
"land_price_inr_per_sqft": {
"2010": 900,
"2015": 1600,
"2021": 2700
},
"infrastructure": {
"has_railway": true,
"has_airport": true,
"num_national_highways": 3,
"has_university": true,
"has_medical_college": true,
"industry_type": "defense-industrial"
},
"scores": {
"infrastructure": 100,
"connectivity": 90,
"economic_activity": 80.0,
"overall": 90.0
},
"growth_triggers": [
"railway_connectivity",
"airport_access",
"national_highway_junction",
"amrut_scheme"
],
"growth_directions": [
"N",
"NE",
"E"
],
"nearest_metro": "Bhopal",
"dist_to_metro_km": 290,
"government_schemes": [
"AMRUT"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "accelerating",
"investment_score": 95,
"description": "Ordnance factory + defense hub, Marble rocks city"
},
{
"id": "gwalior",
"name": "Gwalior",
"state": "Madhya Pradesh",
"tier": 2,
"lat": 26.2183,
"lng": 78.1828,
"population": {
"2001": 826919,
"2011": 1069276,
"2021": 1400000
},
"urban_area_sqkm": {
"2001": 72,
"2006": 90.0,
"2011": 108,
"2016": 130.0,
"2021": 152
},
"land_price_inr_per_sqft": {
"2010": 1000,
"2015": 1800,
"2021": 3000
},
"infrastructure": {
"has_railway": true,
"has_airport": true,
"num_national_highways": 3,
"has_university": true,
"has_medical_college": true,
"industry_type": "industrial"
},
"scores": {
"infrastructure": 100,
"connectivity": 83,
"economic_activity": 91.9,
"overall": 91.6
},
"growth_triggers": [
"railway_connectivity",
"airport_access",
"national_highway_junction",
"smart_city_mission",
"amrut_scheme"
],
"growth_directions": [
"N",
"NW",
"W"
],
"nearest_metro": "Delhi",
"dist_to_metro_km": 320,
"government_schemes": [
"Smart City",
"AMRUT"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "accelerating",
"investment_score": 95,
"description": "Historical fort city + MSME industrial hub"
},
{
"id": "ujjain",
"name": "Ujjain",
"state": "Madhya Pradesh",
"tier": 2,
"lat": 23.1765,
"lng": 75.7885,
"population": {
"2001": 430427,
"2011": 515215,
"2021": 680000
},
"urban_area_sqkm": {
"2001": 36,
"2006": 45.0,
"2011": 54,
"2016": 65.0,
"2021": 76
},
"land_price_inr_per_sqft": {
"2010": 700,
"2015": 1200,
"2021": 2100
},
"infrastructure": {
"has_railway": true,
"has_airport": true,
"num_national_highways": 2,
"has_university": true,
"has_medical_college": false,
"industry_type": "religious-industrial"
},
"scores": {
"infrastructure": 83,
"connectivity": 90,
"economic_activity": 68.6,
"overall": 80.5
},
"growth_triggers": [
"railway_connectivity",
"airport_access",
"national_highway_junction",
"amrut_scheme"
],
"growth_directions": [
"N",
"NE",
"E"
],
"nearest_metro": "Indore",
"dist_to_metro_km": 55,
"government_schemes": [
"AMRUT"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "accelerating",
"investment_score": 91.2,
"description": "Kumbh Mela city + Ujjain Corridor industrial zone"
},
{
"id": "sagar",
"name": "Sagar",
"state": "Madhya Pradesh",
"tier": 3,
"lat": 23.8388,
"lng": 78.7378,
"population": {
"2001": 232133,
"2011": 274543,
"2021": 360000
},
"urban_area_sqkm": {
"2001": 19,
"2006": 24.0,
"2011": 29,
"2016": 35.0,
"2021": 41
},
"land_price_inr_per_sqft": {
"2010": 400,
"2015": 700,
"2021": 1200
},
"infrastructure": {
"has_railway": true,
"has_airport": true,
"num_national_highways": 2,
"has_university": true,
"has_medical_college": false,
"industry_type": "agriculture-education"
},
"scores": {
"infrastructure": 83,
"connectivity": 80,
"economic_activity": 56.0,
"overall": 73.0
},
"growth_triggers": [
"railway_connectivity",
"airport_access",
"national_highway_junction",
"amrut_scheme",
"tier3_emerging_market"
],
"growth_directions": [
"N",
"E",
"NE"
],
"nearest_metro": "Bhopal",
"dist_to_metro_km": 185,
"government_schemes": [
"AMRUT"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "emerging",
"investment_score": 95,
"description": "Educational town, Sagar University, agriculture belt"
},
{
"id": "kolkata",
"name": "Kolkata",
"state": "West Bengal",
"tier": 1,
"lat": 22.5726,
"lng": 88.3639,
"population": {
"2001": 4580544,
"2011": 4486679,
"2021": 5200000
},
"urban_area_sqkm": {
"2001": 400,
"2006": 415.0,
"2011": 430,
"2016": 449.0,
"2021": 468
},
"land_price_inr_per_sqft": {
"2010": 3000,
"2015": 5000,
"2021": 8000
},
"infrastructure": {
"has_railway": true,
"has_airport": true,
"num_national_highways": 5,
"has_university": true,
"has_medical_college": true,
"industry_type": "finance-industry"
},
"scores": {
"infrastructure": 100,
"connectivity": 75,
"economic_activity": 62.7,
"overall": 79.2
},
"growth_triggers": [
"railway_connectivity",
"airport_access",
"national_highway_junction",
"smart_city_mission",
"amrut_scheme"
],
"growth_directions": [
"N",
"E",
"S",
"W"
],
"nearest_metro": "Delhi",
"dist_to_metro_km": 1340,
"government_schemes": [
"Smart City",
"AMRUT"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "mature",
"investment_score": 50.4,
"description": "Cultural capital of India, New Town Rajarhat tech hub"
},
{
"id": "durgapur",
"name": "Durgapur",
"state": "West Bengal",
"tier": 2,
"lat": 23.5204,
"lng": 87.3119,
"population": {
"2001": 492734,
"2011": 566517,
"2021": 725000
},
"urban_area_sqkm": {
"2001": 42,
"2006": 52.5,
"2011": 63,
"2016": 76.0,
"2021": 89
},
"land_price_inr_per_sqft": {
"2010": 600,
"2015": 1100,
"2021": 1900
},
"infrastructure": {
"has_railway": true,
"has_airport": true,
"num_national_highways": 3,
"has_university": true,
"has_medical_college": true,
"industry_type": "steel-industrial"
},
"scores": {
"infrastructure": 100,
"connectivity": 90,
"economic_activity": 86.4,
"overall": 92.1
},
"growth_triggers": [
"railway_connectivity",
"airport_access",
"national_highway_junction",
"amrut_scheme"
],
"growth_directions": [
"N",
"NE",
"E"
],
"nearest_metro": "Kolkata",
"dist_to_metro_km": 165,
"government_schemes": [
"AMRUT"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "accelerating",
"investment_score": 95,
"description": "Steel city of India, SAIL + Durgapur IT corridor"
},
{
"id": "asansol",
"name": "Asansol",
"state": "West Bengal",
"tier": 2,
"lat": 23.6836,
"lng": 86.9522,
"population": {
"2001": 564491,
"2011": 563917,
"2021": 720000
},
"urban_area_sqkm": {
"2001": 48,
"2006": 60.0,
"2011": 72,
"2016": 86.5,
"2021": 101
},
"land_price_inr_per_sqft": {
"2010": 500,
"2015": 900,
"2021": 1600
},
"infrastructure": {
"has_railway": true,
"has_airport": true,
"num_national_highways": 2,
"has_university": true,
"has_medical_college": true,
"industry_type": "coal-industrial"
},
"scores": {
"infrastructure": 92,
"connectivity": 80,
"economic_activity": 80.5,
"overall": 84.2
},
"growth_triggers": [
"railway_connectivity",
"airport_access",
"national_highway_junction",
"smart_city_mission",
"amrut_scheme"
],
"growth_directions": [
"N",
"E",
"SE"
],
"nearest_metro": "Kolkata",
"dist_to_metro_km": 200,
"government_schemes": [
"Smart City",
"AMRUT"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "accelerating",
"investment_score": 95,
"description": "Coal and steel industrial center, Raniganj coalfields"
},
{
"id": "siliguri",
"name": "Siliguri",
"state": "West Bengal",
"tier": 2,
"lat": 26.7271,
"lng": 88.3952,
"population": {
"2001": 470275,
"2011": 513264,
"2021": 720000
},
"urban_area_sqkm": {
"2001": 39,
"2006": 49.0,
"2011": 59,
"2016": 71.5,
"2021": 84
},
"land_price_inr_per_sqft": {
"2010": 1000,
"2015": 1800,
"2021": 3000
},
"infrastructure": {
"has_railway": true,
"has_airport": true,
"num_national_highways": 3,
"has_university": true,
"has_medical_college": true,
"industry_type": "trade"
},
"scores": {
"infrastructure": 100,
"connectivity": 75,
"economic_activity": 78.6,
"overall": 84.5
},
"growth_triggers": [
"railway_connectivity",
"airport_access",
"national_highway_junction",
"smart_city_mission",
"amrut_scheme"
],
"growth_directions": [
"N",
"NE",
"E"
],
"nearest_metro": "Kolkata",
"dist_to_metro_km": 600,
"government_schemes": [
"Smart City",
"AMRUT"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "accelerating",
"investment_score": 95,
"description": "Gateway to Northeast + Bhutan, e-commerce hub"
},
{
"id": "kharagpur",
"name": "Kharagpur",
"state": "West Bengal",
"tier": 3,
"lat": 22.346,
"lng": 87.332,
"population": {
"2001": 194795,
"2011": 207986,
"2021": 265000
},
"urban_area_sqkm": {
"2001": 16,
"2006": 20.0,
"2011": 24,
"2016": 29.0,
"2021": 34
},
"land_price_inr_per_sqft": {
"2010": 500,
"2015": 900,
"2021": 1500
},
"infrastructure": {
"has_railway": true,
"has_airport": false,
"num_national_highways": 2,
"has_university": true,
"has_medical_college": false,
"industry_type": "education-industry"
},
"scores": {
"infrastructure": 53,
"connectivity": 55,
"economic_activity": 62.2,
"overall": 56.7
},
"growth_triggers": [
"railway_connectivity",
"national_highway_junction",
"amrut_scheme",
"tier3_emerging_market"
],
"growth_directions": [
"N",
"NE",
"E"
],
"nearest_metro": "Kolkata",
"dist_to_metro_km": 120,
"government_schemes": [
"AMRUT"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "emerging",
"investment_score": 88.2,
"description": "IIT Kharagpur campus city, major railway junction"
},
{
"id": "bardhaman",
"name": "Bardhaman",
"state": "West Bengal",
"tier": 3,
"lat": 23.2324,
"lng": 87.8615,
"population": {
"2001": 285630,
"2011": 314265,
"2021": 405000
},
"urban_area_sqkm": {
"2001": 24,
"2006": 30.0,
"2011": 36,
"2016": 43.5,
"2021": 51
},
"land_price_inr_per_sqft": {
"2010": 500,
"2015": 900,
"2021": 1600
},
"infrastructure": {
"has_railway": true,
"has_airport": true,
"num_national_highways": 2,
"has_university": true,
"has_medical_college": true,
"industry_type": "agriculture-industry"
},
"scores": {
"infrastructure": 92,
"connectivity": 90,
"economic_activity": 63.4,
"overall": 81.8
},
"growth_triggers": [
"railway_connectivity",
"airport_access",
"national_highway_junction",
"amrut_scheme",
"tier3_emerging_market"
],
"growth_directions": [
"N",
"E",
"SE"
],
"nearest_metro": "Kolkata",
"dist_to_metro_km": 95,
"government_schemes": [
"AMRUT"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "emerging",
"investment_score": 95,
"description": "Rice bowl of WB, coal mines + agriculture belt"
},
{
"id": "hyderabad",
"name": "Hyderabad",
"state": "Telangana",
"tier": 1,
"lat": 17.385,
"lng": 78.4867,
"population": {
"2001": 3637483,
"2011": 6731790,
"2021": 10500000
},
"urban_area_sqkm": {
"2001": 320,
"2006": 430.0,
"2011": 540,
"2016": 705.0,
"2021": 870
},
"land_price_inr_per_sqft": {
"2010": 3000,
"2015": 6000,
"2021": 10000
},
"infrastructure": {
"has_railway": true,
"has_airport": true,
"num_national_highways": 5,
"has_university": true,
"has_medical_college": true,
"industry_type": "IT-pharma"
},
"scores": {
"infrastructure": 100,
"connectivity": 83,
"economic_activity": 100,
"overall": 94.3
},
"growth_triggers": [
"railway_connectivity",
"airport_access",
"national_highway_junction",
"smart_city_mission",
"amrut_scheme"
],
"growth_directions": [
"N",
"E",
"S",
"W",
"NE"
],
"nearest_metro": "Bangalore",
"dist_to_metro_km": 570,
"government_schemes": [
"Smart City",
"AMRUT"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "maturing",
"investment_score": 85.4,
"description": "HITEC City + pharma hub, Genome Valley"
},
{
"id": "visakhapatnam",
"name": "Visakhapatnam",
"state": "Andhra Pradesh",
"tier": 1,
"lat": 17.6868,
"lng": 83.2185,
"population": {
"2001": 969608,
"2011": 1730320,
"2021": 2600000
},
"urban_area_sqkm": {
"2001": 84,
"2006": 119.5,
"2011": 155,
"2016": 200.0,
"2021": 245
},
"land_price_inr_per_sqft": {
"2010": 1500,
"2015": 2800,
"2021": 5000
},
"infrastructure": {
"has_railway": true,
"has_airport": true,
"num_national_highways": 4,
"has_university": true,
"has_medical_college": true,
"industry_type": "port-industrial"
},
"scores": {
"infrastructure": 100,
"connectivity": 75,
"economic_activity": 80,
"overall": 85.0
},
"growth_triggers": [
"railway_connectivity",
"airport_access",
"national_highway_junction",
"smart_city_mission",
"amrut_scheme"
],
"growth_directions": [
"N",
"NW",
"W",
"SW"
],
"nearest_metro": "Hyderabad",
"dist_to_metro_km": 625,
"government_schemes": [
"Smart City",
"AMRUT"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "maturing",
"investment_score": 76.0,
"description": "Jewel of East Coast, Vizag Steel + IT corridor"
},
{
"id": "vijayawada",
"name": "Vijayawada",
"state": "Andhra Pradesh",
"tier": 2,
"lat": 16.5062,
"lng": 80.648,
"population": {
"2001": 851282,
"2011": 1048240,
"2021": 1400000
},
"urban_area_sqkm": {
"2001": 72,
"2006": 91.0,
"2011": 110,
"2016": 133.5,
"2021": 157
},
"land_price_inr_per_sqft": {
"2010": 1200,
"2015": 2200,
"2021": 3800
},
"infrastructure": {
"has_railway": true,
"has_airport": true,
"num_national_highways": 3,
"has_university": true,
"has_medical_college": true,
"industry_type": "commercial"
},
"scores": {
"infrastructure": 100,
"connectivity": 90,
"economic_activity": 77.9,
"overall": 89.3
},
"growth_triggers": [
"railway_connectivity",
"airport_access",
"national_highway_junction",
"smart_city_mission",
"amrut_scheme"
],
"growth_directions": [
"N",
"NW",
"W"
],
"nearest_metro": "Hyderabad",
"dist_to_metro_km": 280,
"government_schemes": [
"Smart City",
"AMRUT"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "accelerating",
"investment_score": 95,
"description": "AP commercial capital, Amaravati capital region proximity"
},
{
"id": "guntur",
"name": "Guntur",
"state": "Andhra Pradesh",
"tier": 2,
"lat": 16.3067,
"lng": 80.4365,
"population": {
"2001": 514707,
"2011": 743354,
"2021": 980000
},
"urban_area_sqkm": {
"2001": 43,
"2006": 55.0,
"2011": 67,
"2016": 81.0,
"2021": 95
},
"land_price_inr_per_sqft": {
"2010": 800,
"2015": 1400,
"2021": 2400
},
"infrastructure": {
"has_railway": true,
"has_airport": true,
"num_national_highways": 2,
"has_university": true,
"has_medical_college": true,
"industry_type": "agriculture-commercial"
},
"scores": {
"infrastructure": 92,
"connectivity": 80,
"economic_activity": 71.1,
"overall": 81.0
},
"growth_triggers": [
"railway_connectivity",
"airport_access",
"national_highway_junction",
"amrut_scheme"
],
"growth_directions": [
"N",
"NW",
"W"
],
"nearest_metro": "Hyderabad",
"dist_to_metro_km": 260,
"government_schemes": [
"AMRUT"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "accelerating",
"investment_score": 92.0,
"description": "Chilli + tobacco market, Amaravati adjacency benefit"
},
{
"id": "warangal",
"name": "Warangal",
"state": "Telangana",
"tier": 2,
"lat": 17.9784,
"lng": 79.5941,
"population": {
"2001": 528570,
"2011": 811844,
"2021": 1100000
},
"urban_area_sqkm": {
"2001": 44,
"2006": 58.5,
"2011": 73,
"2016": 88.5,
"2021": 104
},
"land_price_inr_per_sqft": {
"2010": 600,
"2015": 1100,
"2021": 2000
},
"infrastructure": {
"has_railway": true,
"has_airport": true,
"num_national_highways": 2,
"has_university": true,
"has_medical_college": true,
"industry_type": "industrial"
},
"scores": {
"infrastructure": 92,
"connectivity": 80,
"economic_activity": 98,
"overall": 90.0
},
"growth_triggers": [
"railway_connectivity",
"airport_access",
"national_highway_junction",
"smart_city_mission",
"amrut_scheme"
],
"growth_directions": [
"N",
"NE",
"E"
],
"nearest_metro": "Hyderabad",
"dist_to_metro_km": 148,
"government_schemes": [
"Smart City",
"AMRUT"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "accelerating",
"investment_score": 95,
"description": "Granite city + growing IT, 150 km from Hyderabad"
},
{
"id": "tirupati",
"name": "Tirupati",
"state": "Andhra Pradesh",
"tier": 3,
"lat": 13.6288,
"lng": 79.4192,
"population": {
"2001": 228499,
"2011": 374260,
"2021": 520000
},
"urban_area_sqkm": {
"2001": 19,
"2006": 26.5,
"2011": 34,
"2016": 41.0,
"2021": 48
},
"land_price_inr_per_sqft": {
"2010": 800,
"2015": 1500,
"2021": 2700
},
"infrastructure": {
"has_railway": true,
"has_airport": true,
"num_national_highways": 2,
"has_university": false,
"has_medical_college": true,
"industry_type": "religious-IT"
},
"scores": {
"infrastructure": 80,
"connectivity": 80,
"economic_activity": 92,
"overall": 84.0
},
"growth_triggers": [
"railway_connectivity",
"airport_access",
"national_highway_junction",
"smart_city_mission",
"amrut_scheme",
"tier3_emerging_market"
],
"growth_directions": [
"N",
"NW",
"W"
],
"nearest_metro": "Chennai",
"dist_to_metro_km": 135,
"government_schemes": [
"Smart City",
"AMRUT"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "accelerating",
"investment_score": 95,
"description": "Temple city + growing IT, TTD trust economy"
},
{
"id": "chandigarh",
"name": "Chandigarh",
"state": "Chandigarh",
"tier": 1,
"lat": 30.7333,
"lng": 76.7794,
"population": {
"2001": 900635,
"2011": 1025682,
"2021": 1400000
},
"urban_area_sqkm": {
"2001": 80,
"2006": 92.5,
"2011": 105,
"2016": 122.5,
"2021": 140
},
"land_price_inr_per_sqft": {
"2010": 4000,
"2015": 6500,
"2021": 10000
},
"infrastructure": {
"has_railway": true,
"has_airport": true,
"num_national_highways": 4,
"has_university": true,
"has_medical_college": true,
"industry_type": "government-IT"
},
"scores": {
"infrastructure": 100,
"connectivity": 90,
"economic_activity": 91.1,
"overall": 93.7
},
"growth_triggers": [
"railway_connectivity",
"airport_access",
"national_highway_junction",
"smart_city_mission",
"amrut_scheme"
],
"growth_directions": [
"N",
"E",
"S",
"W"
],
"nearest_metro": "Delhi",
"dist_to_metro_km": 250,
"government_schemes": [
"Smart City",
"AMRUT"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "maturing",
"investment_score": 84.1,
"description": "Planned city, tech + startup hub, Aerocity SAS Nagar"
},
{
"id": "ludhiana",
"name": "Ludhiana",
"state": "Punjab",
"tier": 2,
"lat": 30.901,
"lng": 75.8573,
"population": {
"2001": 1398467,
"2011": 1613878,
"2021": 2100000
},
"urban_area_sqkm": {
"2001": 122,
"2006": 150.0,
"2011": 178,
"2016": 216.0,
"2021": 254
},
"land_price_inr_per_sqft": {
"2010": 2000,
"2015": 3500,
"2021": 5800
},
"infrastructure": {
"has_railway": true,
"has_airport": true,
"num_national_highways": 3,
"has_university": true,
"has_medical_college": true,
"industry_type": "textile-bicycle"
},
"scores": {
"infrastructure": 100,
"connectivity": 100,
"economic_activity": 70.0,
"overall": 90.0
},
"growth_triggers": [
"railway_connectivity",
"airport_access",
"national_highway_junction",
"smart_city_mission",
"amrut_scheme"
],
"growth_directions": [
"N",
"E",
"NE"
],
"nearest_metro": "Chandigarh",
"dist_to_metro_km": 95,
"government_schemes": [
"Smart City",
"AMRUT"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "accelerating",
"investment_score": 95,
"description": "Textile + bicycle capital of India"
},
{
"id": "amritsar",
"name": "Amritsar",
"state": "Punjab",
"tier": 2,
"lat": 31.634,
"lng": 74.8723,
"population": {
"2001": 1011327,
"2011": 1132761,
"2021": 1500000
},
"urban_area_sqkm": {
"2001": 88,
"2006": 109.0,
"2011": 130,
"2016": 157.5,
"2021": 185
},
"land_price_inr_per_sqft": {
"2010": 1500,
"2015": 2600,
"2021": 4200
},
"infrastructure": {
"has_railway": true,
"has_airport": true,
"num_national_highways": 3,
"has_university": true,
"has_medical_college": true,
"industry_type": "tourism-trade"
},
"scores": {
"infrastructure": 100,
"connectivity": 90,
"economic_activity": 69.7,
"overall": 86.6
},
"growth_triggers": [
"railway_connectivity",
"airport_access",
"national_highway_junction",
"smart_city_mission",
"amrut_scheme"
],
"growth_directions": [
"N",
"E",
"NE"
],
"nearest_metro": "Chandigarh",
"dist_to_metro_km": 200,
"government_schemes": [
"Smart City",
"AMRUT"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "accelerating",
"investment_score": 95,
"description": "Golden Temple city, border trade hub, Amritsar-Kolkata corridor"
},
{
"id": "gurgaon",
"name": "Gurugram",
"state": "Haryana",
"tier": 1,
"lat": 28.4595,
"lng": 77.0266,
"population": {
"2001": 228831,
"2011": 876969,
"2021": 2200000
},
"urban_area_sqkm": {
"2001": 25,
"2006": 66.5,
"2011": 108,
"2016": 184.0,
"2021": 260
},
"land_price_inr_per_sqft": {
"2010": 4000,
"2015": 8000,
"2021": 14000
},
"infrastructure": {
"has_railway": true,
"has_airport": true,
"num_national_highways": 4,
"has_university": true,
"has_medical_college": true,
"industry_type": "IT-finance"
},
"scores": {
"infrastructure": 100,
"connectivity": 100,
"economic_activity": 100,
"overall": 100.0
},
"growth_triggers": [
"railway_connectivity",
"airport_access",
"national_highway_junction",
"smart_city_mission",
"amrut_scheme"
],
"growth_directions": [
"N",
"NE",
"E",
"S"
],
"nearest_metro": "Delhi",
"dist_to_metro_km": 30,
"government_schemes": [
"Smart City",
"AMRUT"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "maturing",
"investment_score": 90.0,
"description": "Millennium City, Cyber Hub IT + financial district"
},
{
"id": "delhi",
"name": "Delhi",
"state": "Delhi",
"tier": 1,
"lat": 28.6139,
"lng": 77.209,
"population": {
"2001": 12877470,
"2011": 16314838,
"2021": 20000000
},
"urban_area_sqkm": {
"2001": 1083,
"2006": 1154.0,
"2011": 1225,
"2016": 1354.5,
"2021": 1484
},
"land_price_inr_per_sqft": {
"2010": 8000,
"2015": 14000,
"2021": 22000
},
"infrastructure": {
"has_railway": true,
"has_airport": true,
"num_national_highways": 10,
"has_university": true,
"has_medical_college": true,
"industry_type": "government-IT"
},
"scores": {
"infrastructure": 100,
"connectivity": 100,
"economic_activity": 91.1,
"overall": 97.0
},
"growth_triggers": [
"railway_connectivity",
"airport_access",
"national_highway_junction",
"smart_city_mission",
"amrut_scheme"
],
"growth_directions": [
"N",
"E",
"S",
"W",
"NE",
"NW",
"SE",
"SW"
],
"nearest_metro": "Delhi",
"dist_to_metro_km": 0,
"government_schemes": [
"Smart City",
"AMRUT"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "mature",
"investment_score": 62.7,
"description": "National capital, largest urban agglomeration in India"
},
{
"id": "ranchi",
"name": "Ranchi",
"state": "Jharkhand",
"tier": 2,
"lat": 23.3441,
"lng": 85.3096,
"population": {
"2001": 847093,
"2011": 1073440,
"2021": 1450000
},
"urban_area_sqkm": {
"2001": 74,
"2006": 94.0,
"2011": 114,
"2016": 138.0,
"2021": 162
},
"land_price_inr_per_sqft": {
"2010": 900,
"2015": 1600,
"2021": 2800
},
"infrastructure": {
"has_railway": true,
"has_airport": true,
"num_national_highways": 3,
"has_university": true,
"has_medical_college": true,
"industry_type": "government-mining"
},
"scores": {
"infrastructure": 100,
"connectivity": 83,
"economic_activity": 79.2,
"overall": 87.4
},
"growth_triggers": [
"railway_connectivity",
"airport_access",
"national_highway_junction",
"smart_city_mission",
"amrut_scheme"
],
"growth_directions": [
"N",
"E",
"NE"
],
"nearest_metro": "Kolkata",
"dist_to_metro_km": 400,
"government_schemes": [
"Smart City",
"AMRUT"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "accelerating",
"investment_score": 95,
"description": "Capital of Jharkhand, steel + mining hub, AIIMS Ranchi"
},
{
"id": "jamshedpur",
"name": "Jamshedpur",
"state": "Jharkhand",
"tier": 2,
"lat": 22.8046,
"lng": 86.2029,
"population": {
"2001": 1104713,
"2011": 1337131,
"2021": 1750000
},
"urban_area_sqkm": {
"2001": 96,
"2006": 120.5,
"2011": 145,
"2016": 175.0,
"2021": 205
},
"land_price_inr_per_sqft": {
"2010": 1000,
"2015": 1800,
"2021": 3200
},
"infrastructure": {
"has_railway": true,
"has_airport": true,
"num_national_highways": 3,
"has_university": true,
"has_medical_college": true,
"industry_type": "steel-industrial"
},
"scores": {
"infrastructure": 100,
"connectivity": 90,
"economic_activity": 88.7,
"overall": 92.9
},
"growth_triggers": [
"railway_connectivity",
"airport_access",
"national_highway_junction",
"amrut_scheme"
],
"growth_directions": [
"N",
"E",
"NE"
],
"nearest_metro": "Kolkata",
"dist_to_metro_km": 270,
"government_schemes": [
"AMRUT"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "accelerating",
"investment_score": 95,
"description": "Tata Steel city, model planned industrial township"
},
{
"id": "bhubaneswar",
"name": "Bhubaneswar",
"state": "Odisha",
"tier": 2,
"lat": 20.2961,
"lng": 85.8245,
"population": {
"2001": 647302,
"2011": 837737,
"2021": 1200000
},
"urban_area_sqkm": {
"2001": 57,
"2006": 72.0,
"2011": 87,
"2016": 106.0,
"2021": 125
},
"land_price_inr_per_sqft": {
"2010": 1200,
"2015": 2200,
"2021": 3800
},
"infrastructure": {
"has_railway": true,
"has_airport": true,
"num_national_highways": 4,
"has_university": true,
"has_medical_college": true,
"industry_type": "government-IT"
},
"scores": {
"infrastructure": 100,
"connectivity": 83,
"economic_activity": 97.1,
"overall": 93.4
},
"growth_triggers": [
"railway_connectivity",
"airport_access",
"national_highway_junction",
"smart_city_mission",
"amrut_scheme"
],
"growth_directions": [
"N",
"E",
"NE",
"S"
],
"nearest_metro": "Kolkata",
"dist_to_metro_km": 440,
"government_schemes": [
"Smart City",
"AMRUT"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "accelerating",
"investment_score": 95,
"description": "Temple city, growing IT + startup hub, Infocity"
},
{
"id": "cuttack",
"name": "Cuttack",
"state": "Odisha",
"tier": 3,
"lat": 20.4625,
"lng": 85.883,
"population": {
"2001": 535139,
"2011": 606007,
"2021": 780000
},
"urban_area_sqkm": {
"2001": 45,
"2006": 56.0,
"2011": 67,
"2016": 81.5,
"2021": 96
},
"land_price_inr_per_sqft": {
"2010": 600,
"2015": 1100,
"2021": 1900
},
"infrastructure": {
"has_railway": true,
"has_airport": true,
"num_national_highways": 2,
"has_university": true,
"has_medical_college": true,
"industry_type": "commercial"
},
"scores": {
"infrastructure": 92,
"connectivity": 90,
"economic_activity": 69.2,
"overall": 83.7
},
"growth_triggers": [
"railway_connectivity",
"airport_access",
"national_highway_junction",
"amrut_scheme",
"tier3_emerging_market"
],
"growth_directions": [
"N",
"NW",
"W"
],
"nearest_metro": "Bhubaneswar",
"dist_to_metro_km": 26,
"government_schemes": [
"AMRUT"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "accelerating",
"investment_score": 94.6,
"description": "Commercial capital of Odisha, silver filigree craft"
},
{
"id": "guwahati",
"name": "Guwahati",
"state": "Assam",
"tier": 2,
"lat": 26.1445,
"lng": 91.7362,
"population": {
"2001": 808021,
"2011": 957352,
"2021": 1400000
},
"urban_area_sqkm": {
"2001": 70,
"2006": 88.0,
"2011": 106,
"2016": 129.0,
"2021": 152
},
"land_price_inr_per_sqft": {
"2010": 1000,
"2015": 1800,
"2021": 3200
},
"infrastructure": {
"has_railway": true,
"has_airport": true,
"num_national_highways": 3,
"has_university": true,
"has_medical_college": true,
"industry_type": "trade-government"
},
"scores": {
"infrastructure": 100,
"connectivity": 75,
"economic_activity": 79.7,
"overall": 84.9
},
"growth_triggers": [
"railway_connectivity",
"airport_access",
"national_highway_junction",
"smart_city_mission",
"amrut_scheme"
],
"growth_directions": [
"N",
"NE",
"E",
"W"
],
"nearest_metro": "Kolkata",
"dist_to_metro_km": 1000,
"government_schemes": [
"Smart City",
"AMRUT"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "accelerating",
"investment_score": 95,
"description": "Gateway to Northeast India, e-commerce + trade boom"
},
{
"id": "raipur",
"name": "Raipur",
"state": "Chhattisgarh",
"tier": 2,
"lat": 21.2514,
"lng": 81.6296,
"population": {
"2001": 605747,
"2011": 1010433,
"2021": 1450000
},
"urban_area_sqkm": {
"2001": 53,
"2006": 72.5,
"2011": 92,
"2016": 113.0,
"2021": 134
},
"land_price_inr_per_sqft": {
"2010": 900,
"2015": 1600,
"2021": 2800
},
"infrastructure": {
"has_railway": true,
"has_airport": true,
"num_national_highways": 3,
"has_university": true,
"has_medical_college": true,
"industry_type": "government-industrial"
},
"scores": {
"infrastructure": 100,
"connectivity": 83,
"economic_activity": 88,
"overall": 90.3
},
"growth_triggers": [
"railway_connectivity",
"airport_access",
"national_highway_junction",
"smart_city_mission",
"amrut_scheme"
],
"growth_directions": [
"N",
"E",
"NE"
],
"nearest_metro": "Nagpur",
"dist_to_metro_km": 310,
"government_schemes": [
"Smart City",
"AMRUT"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "accelerating",
"investment_score": 95,
"description": "Capital of CG, steel + mining, Naya Raipur greenfield"
},
{
"id": "kochi",
"name": "Kochi",
"state": "Kerala",
"tier": 2,
"lat": 9.9312,
"lng": 76.2673,
"population": {
"2001": 1355972,
"2011": 2117990,
"2021": 2300000
},
"urban_area_sqkm": {
"2001": 180,
"2006": 230.0,
"2011": 280,
"2016": 320.0,
"2021": 360
},
"land_price_inr_per_sqft": {
"2010": 3500,
"2015": 5000,
"2021": 8500
},
"infrastructure": {
"has_railway": true,
"has_airport": true,
"num_national_highways": 3,
"has_university": true,
"has_medical_college": true,
"industry_type": "port-finance"
},
"scores": {
"infrastructure": 100,
"connectivity": 100,
"economic_activity": 100,
"overall": 100.0
},
"growth_triggers": [
"railway_connectivity",
"airport_access",
"national_highway_junction",
"smart_city_mission",
"amrut_scheme"
],
"growth_directions": [
"N",
"E",
"S"
],
"nearest_metro": "Kochi",
"dist_to_metro_km": 0,
"government_schemes": [
"Smart City",
"AMRUT"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "maturing",
"investment_score": 90.0,
"description": "Commercial capital of Kerala, port + IT hub with metro rail"
},
{
"id": "thiruvananthapuram",
"name": "Thiruvananthapuram",
"state": "Kerala",
"tier": 2,
"lat": 8.5241,
"lng": 76.9366,
"population": {
"2001": 744983,
"2011": 957730,
"2021": 1050000
},
"urban_area_sqkm": {
"2001": 90,
"2006": 110.0,
"2011": 130,
"2016": 147.5,
"2021": 165
},
"land_price_inr_per_sqft": {
"2010": 3000,
"2015": 4500,
"2021": 7000
},
"infrastructure": {
"has_railway": true,
"has_airport": true,
"num_national_highways": 2,
"has_university": true,
"has_medical_college": true,
"industry_type": "government-IT"
},
"scores": {
"infrastructure": 92,
"connectivity": 80,
"economic_activity": 88.2,
"overall": 86.7
},
"growth_triggers": [
"railway_connectivity",
"airport_access",
"national_highway_junction",
"smart_city_mission",
"amrut_scheme"
],
"growth_directions": [
"N",
"E",
"NW"
],
"nearest_metro": "Kochi",
"dist_to_metro_km": 200,
"government_schemes": [
"Smart City",
"AMRUT"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "maturing",
"investment_score": 78.2,
"description": "Kerala capital, Technopark IT hub and space research centre"
},
{
"id": "kozhikode",
"name": "Kozhikode",
"state": "Kerala",
"tier": 2,
"lat": 11.2588,
"lng": 75.7804,
"population": {
"2001": 436527,
"2011": 609224,
"2021": 700000
},
"urban_area_sqkm": {
"2001": 60,
"2006": 75.0,
"2011": 90,
"2016": 105.0,
"2021": 120
},
"land_price_inr_per_sqft": {
"2010": 2500,
"2015": 3800,
"2021": 6000
},
"infrastructure": {
"has_railway": true,
"has_airport": true,
"num_national_highways": 2,
"has_university": true,
"has_medical_college": true,
"industry_type": "trade"
},
"scores": {
"infrastructure": 92,
"connectivity": 80,
"economic_activity": 75.1,
"overall": 82.4
},
"growth_triggers": [
"railway_connectivity",
"airport_access",
"national_highway_junction",
"smart_city_mission"
],
"growth_directions": [
"N",
"S",
"E"
],
"nearest_metro": "Kochi",
"dist_to_metro_km": 180,
"government_schemes": [
"Smart City"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "accelerating",
"investment_score": 93.9,
"description": "Historic Malabar trade port, NRI-driven real estate"
},
{
"id": "thrissur",
"name": "Thrissur",
"state": "Kerala",
"tier": 3,
"lat": 10.5276,
"lng": 76.2144,
"population": {
"2001": 317474,
"2011": 315957,
"2021": 360000
},
"urban_area_sqkm": {
"2001": 40,
"2006": 47.5,
"2011": 55,
"2016": 63.5,
"2021": 72
},
"land_price_inr_per_sqft": {
"2010": 2200,
"2015": 3400,
"2021": 5200
},
"infrastructure": {
"has_railway": true,
"has_airport": false,
"num_national_highways": 2,
"has_university": true,
"has_medical_college": true,
"industry_type": "trade"
},
"scores": {
"infrastructure": 62,
"connectivity": 65,
"economic_activity": 65.7,
"overall": 64.2
},
"growth_triggers": [
"railway_connectivity",
"national_highway_junction",
"amrut_scheme",
"tier3_emerging_market"
],
"growth_directions": [
"N",
"E",
"S"
],
"nearest_metro": "Kochi",
"dist_to_metro_km": 75,
"government_schemes": [
"AMRUT"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "accelerating",
"investment_score": 74.0,
"description": "Cultural capital of Kerala, gold and banking hub"
},
{
"id": "dehradun",
"name": "Dehradun",
"state": "Uttarakhand",
"tier": 2,
"lat": 30.3165,
"lng": 78.0322,
"population": {
"2001": 426674,
"2011": 578420,
"2021": 760000
},
"urban_area_sqkm": {
"2001": 60,
"2006": 77.5,
"2011": 95,
"2016": 115.0,
"2021": 135
},
"land_price_inr_per_sqft": {
"2010": 3000,
"2015": 4800,
"2021": 7500
},
"infrastructure": {
"has_railway": true,
"has_airport": true,
"num_national_highways": 2,
"has_university": true,
"has_medical_college": true,
"industry_type": "government-IT"
},
"scores": {
"infrastructure": 92,
"connectivity": 80,
"economic_activity": 95.6,
"overall": 89.2
},
"growth_triggers": [
"railway_connectivity",
"airport_access",
"national_highway_junction",
"smart_city_mission",
"amrut_scheme"
],
"growth_directions": [
"S",
"SE",
"E"
],
"nearest_metro": "Delhi",
"dist_to_metro_km": 240,
"government_schemes": [
"Smart City",
"AMRUT"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "accelerating",
"investment_score": 95,
"description": "Uttarakhand capital, education + IT, Himalayan gateway"
},
{
"id": "haridwar",
"name": "Haridwar",
"state": "Uttarakhand",
"tier": 3,
"lat": 29.9457,
"lng": 78.1642,
"population": {
"2001": 175010,
"2011": 228832,
"2021": 310000
},
"urban_area_sqkm": {
"2001": 28,
"2006": 35.0,
"2011": 42,
"2016": 51.0,
"2021": 60
},
"land_price_inr_per_sqft": {
"2010": 1800,
"2015": 2900,
"2021": 4500
},
"infrastructure": {
"has_railway": true,
"has_airport": false,
"num_national_highways": 1,
"has_university": true,
"has_medical_college": false,
"industry_type": "religious-industrial"
},
"scores": {
"infrastructure": 45,
"connectivity": 55,
"economic_activity": 72.4,
"overall": 57.5
},
"growth_triggers": [
"railway_connectivity",
"amrut_scheme",
"tier3_emerging_market"
],
"growth_directions": [
"S",
"SE"
],
"nearest_metro": "Dehradun",
"dist_to_metro_km": 55,
"government_schemes": [
"AMRUT"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "emerging",
"investment_score": 90.8,
"description": "Pilgrimage city on the Ganga, BHEL industrial belt"
},
{
"id": "rishikesh",
"name": "Rishikesh",
"state": "Uttarakhand",
"tier": 3,
"lat": 30.0869,
"lng": 78.2676,
"population": {
"2001": 59671,
"2011": 70499,
"2021": 110000
},
"urban_area_sqkm": {
"2001": 12,
"2006": 16.0,
"2011": 20,
"2016": 25.0,
"2021": 30
},
"land_price_inr_per_sqft": {
"2010": 2000,
"2015": 3200,
"2021": 5000
},
"infrastructure": {
"has_railway": false,
"has_airport": false,
"num_national_highways": 1,
"has_university": false,
"has_medical_college": false,
"industry_type": "tourism"
},
"scores": {
"infrastructure": 8,
"connectivity": 35,
"economic_activity": 74.9,
"overall": 39.3
},
"growth_triggers": [
"tier3_emerging_market"
],
"growth_directions": [
"S",
"SW"
],
"nearest_metro": "Dehradun",
"dist_to_metro_km": 45,
"government_schemes": [],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "emerging",
"investment_score": 66.0,
"description": "Yoga capital of the world, adventure + wellness tourism"
},
{
"id": "panaji",
"name": "Panaji",
"state": "Goa",
"tier": 3,
"lat": 15.4909,
"lng": 73.8278,
"population": {
"2001": 99677,
"2011": 114405,
"2021": 140000
},
"urban_area_sqkm": {
"2001": 22,
"2006": 27.0,
"2011": 32,
"2016": 38.5,
"2021": 45
},
"land_price_inr_per_sqft": {
"2010": 4000,
"2015": 6500,
"2021": 11000
},
"infrastructure": {
"has_railway": true,
"has_airport": true,
"num_national_highways": 1,
"has_university": true,
"has_medical_college": true,
"industry_type": "tourism"
},
"scores": {
"infrastructure": 84,
"connectivity": 80,
"economic_activity": 71.1,
"overall": 78.4
},
"growth_triggers": [
"railway_connectivity",
"airport_access",
"smart_city_mission",
"tier3_emerging_market"
],
"growth_directions": [
"E",
"NE",
"N"
],
"nearest_metro": "Panaji",
"dist_to_metro_km": 0,
"government_schemes": [
"Smart City"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "maturing",
"investment_score": 69.9,
"description": "Goa capital, tourism and second-home property market"
},
{
"id": "shimla",
"name": "Shimla",
"state": "Himachal Pradesh",
"tier": 3,
"lat": 31.1048,
"lng": 77.1734,
"population": {
"2001": 142161,
"2011": 169578,
"2021": 215000
},
"urban_area_sqkm": {
"2001": 18,
"2006": 22.0,
"2011": 26,
"2016": 30.5,
"2021": 35
},
"land_price_inr_per_sqft": {
"2010": 3500,
"2015": 5200,
"2021": 8000
},
"infrastructure": {
"has_railway": true,
"has_airport": true,
"num_national_highways": 1,
"has_university": true,
"has_medical_college": true,
"industry_type": "tourism"
},
"scores": {
"infrastructure": 84,
"connectivity": 70,
"economic_activity": 73.2,
"overall": 75.7
},
"growth_triggers": [
"railway_connectivity",
"airport_access",
"smart_city_mission",
"tier3_emerging_market"
],
"growth_directions": [
"S",
"SW",
"W"
],
"nearest_metro": "Chandigarh",
"dist_to_metro_km": 115,
"government_schemes": [
"Smart City"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "emerging",
"investment_score": 95,
"description": "Himachal capital, hill-station tourism and education"
},
{
"id": "srinagar",
"name": "Srinagar",
"state": "Jammu & Kashmir",
"tier": 2,
"lat": 34.0837,
"lng": 74.7973,
"population": {
"2001": 898440,
"2011": 1180570,
"2021": 1300000
},
"urban_area_sqkm": {
"2001": 90,
"2006": 110.0,
"2011": 130,
"2016": 150.0,
"2021": 170
},
"land_price_inr_per_sqft": {
"2010": 2500,
"2015": 3800,
"2021": 6000
},
"infrastructure": {
"has_railway": true,
"has_airport": true,
"num_national_highways": 1,
"has_university": true,
"has_medical_college": true,
"industry_type": "tourism"
},
"scores": {
"infrastructure": 84,
"connectivity": 70,
"economic_activity": 76.9,
"overall": 77.0
},
"growth_triggers": [
"railway_connectivity",
"airport_access",
"smart_city_mission",
"amrut_scheme"
],
"growth_directions": [
"N",
"S",
"E"
],
"nearest_metro": "Jammu",
"dist_to_metro_km": 260,
"government_schemes": [
"Smart City",
"AMRUT"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "accelerating",
"investment_score": 88.5,
"description": "Summer capital of J&K, tourism and horticulture hub"
},
{
"id": "jammu",
"name": "Jammu",
"state": "Jammu & Kashmir",
"tier": 2,
"lat": 32.7266,
"lng": 74.857,
"population": {
"2001": 369959,
"2011": 502197,
"2021": 660000
},
"urban_area_sqkm": {
"2001": 55,
"2006": 70.0,
"2011": 85,
"2016": 102.5,
"2021": 120
},
"land_price_inr_per_sqft": {
"2010": 2200,
"2015": 3400,
"2021": 5500
},
"infrastructure": {
"has_railway": true,
"has_airport": true,
"num_national_highways": 2,
"has_university": true,
"has_medical_college": true,
"industry_type": "government"
},
"scores": {
"infrastructure": 92,
"connectivity": 90,
"economic_activity": 85.7,
"overall": 89.2
},
"growth_triggers": [
"railway_connectivity",
"airport_access",
"national_highway_junction",
"smart_city_mission",
"amrut_scheme"
],
"growth_directions": [
"N",
"NE",
"S"
],
"nearest_metro": "Jammu",
"dist_to_metro_km": 0,
"government_schemes": [
"Smart City",
"AMRUT"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "accelerating",
"investment_score": 95,
"description": "Winter capital of J&K, gateway and pilgrimage transit"
},
{
"id": "puducherry",
"name": "Puducherry",
"state": "Puducherry",
"tier": 3,
"lat": 11.9416,
"lng": 79.8083,
"population": {
"2001": 220865,
"2011": 244377,
"2021": 280000
},
"urban_area_sqkm": {
"2001": 30,
"2006": 36.0,
"2011": 42,
"2016": 50.0,
"2021": 58
},
"land_price_inr_per_sqft": {
"2010": 2500,
"2015": 3800,
"2021": 5800
},
"infrastructure": {
"has_railway": true,
"has_airport": false,
"num_national_highways": 1,
"has_university": true,
"has_medical_college": true,
"industry_type": "tourism"
},
"scores": {
"infrastructure": 54,
"connectivity": 45,
"economic_activity": 68.4,
"overall": 55.8
},
"growth_triggers": [
"railway_connectivity",
"smart_city_mission",
"tier3_emerging_market"
],
"growth_directions": [
"N",
"W",
"NW"
],
"nearest_metro": "Chennai",
"dist_to_metro_km": 160,
"government_schemes": [
"Smart City"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "accelerating",
"investment_score": 65.6,
"description": "Former French colony, coastal tourism and education"
},
{
"id": "noida",
"name": "Noida",
"state": "Uttar Pradesh",
"tier": 1,
"lat": 28.5355,
"lng": 77.391,
"population": {
"2001": 305058,
"2011": 642381,
"2021": 950000
},
"urban_area_sqkm": {
"2001": 80,
"2006": 115.0,
"2011": 150,
"2016": 182.5,
"2021": 215
},
"land_price_inr_per_sqft": {
"2010": 6000,
"2015": 9500,
"2021": 16000
},
"infrastructure": {
"has_railway": true,
"has_airport": true,
"num_national_highways": 3,
"has_university": true,
"has_medical_college": true,
"industry_type": "IT"
},
"scores": {
"infrastructure": 100,
"connectivity": 100,
"economic_activity": 100,
"overall": 100.0
},
"growth_triggers": [
"railway_connectivity",
"airport_access",
"national_highway_junction",
"smart_city_mission"
],
"growth_directions": [
"E",
"SE",
"S"
],
"nearest_metro": "Delhi",
"dist_to_metro_km": 20,
"government_schemes": [
"Smart City"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "maturing",
"investment_score": 90.0,
"description": "NCR tech + corporate hub, expressway and metro connected"
},
{
"id": "ghaziabad",
"name": "Ghaziabad",
"state": "Uttar Pradesh",
"tier": 2,
"lat": 28.6692,
"lng": 77.4538,
"population": {
"2001": 968256,
"2011": 1729000,
"2021": 2100000
},
"urban_area_sqkm": {
"2001": 110,
"2006": 145.0,
"2011": 180,
"2016": 210.0,
"2021": 240
},
"land_price_inr_per_sqft": {
"2010": 4500,
"2015": 7000,
"2021": 11000
},
"infrastructure": {
"has_railway": true,
"has_airport": false,
"num_national_highways": 3,
"has_university": true,
"has_medical_college": true,
"industry_type": "industrial"
},
"scores": {
"infrastructure": 70,
"connectivity": 75,
"economic_activity": 98,
"overall": 81.0
},
"growth_triggers": [
"railway_connectivity",
"national_highway_junction",
"smart_city_mission",
"amrut_scheme"
],
"growth_directions": [
"E",
"NE",
"SE"
],
"nearest_metro": "Delhi",
"dist_to_metro_km": 30,
"government_schemes": [
"Smart City",
"AMRUT"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "maturing",
"investment_score": 74.4,
"description": "NCR industrial city, RapidX rail and residential boom"
},
{
"id": "ayodhya",
"name": "Ayodhya",
"state": "Uttar Pradesh",
"tier": 3,
"lat": 26.7922,
"lng": 82.1998,
"population": {
"2001": 49593,
"2011": 55890,
"2021": 120000
},
"urban_area_sqkm": {
"2001": 12,
"2006": 16.0,
"2011": 20,
"2016": 31.0,
"2021": 42
},
"land_price_inr_per_sqft": {
"2010": 1200,
"2015": 2200,
"2021": 5500
},
"infrastructure": {
"has_railway": true,
"has_airport": true,
"num_national_highways": 2,
"has_university": true,
"has_medical_college": false,
"industry_type": "religious-industrial"
},
"scores": {
"infrastructure": 83,
"connectivity": 80,
"economic_activity": 77,
"overall": 80.0
},
"growth_triggers": [
"railway_connectivity",
"airport_access",
"national_highway_junction",
"smart_city_mission",
"tier3_emerging_market"
],
"growth_directions": [
"N",
"E",
"SE"
],
"nearest_metro": "Lucknow",
"dist_to_metro_km": 135,
"government_schemes": [
"Smart City"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "emerging",
"investment_score": 95,
"description": "Ram Mandir pilgrimage boom, new airport and tourism surge"
},
{
"id": "kolhapur",
"name": "Kolhapur",
"state": "Maharashtra",
"tier": 3,
"lat": 16.705,
"lng": 74.2433,
"population": {
"2001": 485183,
"2011": 549236,
"2021": 620000
},
"urban_area_sqkm": {
"2001": 50,
"2006": 59.0,
"2011": 68,
"2016": 78.0,
"2021": 88
},
"land_price_inr_per_sqft": {
"2010": 2200,
"2015": 3400,
"2021": 5200
},
"infrastructure": {
"has_railway": true,
"has_airport": false,
"num_national_highways": 2,
"has_university": true,
"has_medical_college": true,
"industry_type": "agri-industrial"
},
"scores": {
"infrastructure": 62,
"connectivity": 55,
"economic_activity": 60.6,
"overall": 59.2
},
"growth_triggers": [
"railway_connectivity",
"national_highway_junction",
"amrut_scheme",
"tier3_emerging_market"
],
"growth_directions": [
"N",
"E",
"NE"
],
"nearest_metro": "Pune",
"dist_to_metro_km": 230,
"government_schemes": [
"AMRUT"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "emerging",
"investment_score": 91.4,
"description": "Western Maharashtra trade hub, sugar and foundry industry"
},
{
"id": "amravati",
"name": "Amravati",
"state": "Maharashtra",
"tier": 3,
"lat": 20.9374,
"lng": 77.7796,
"population": {
"2001": 549510,
"2011": 647057,
"2021": 720000
},
"urban_area_sqkm": {
"2001": 55,
"2006": 65.0,
"2011": 75,
"2016": 85.0,
"2021": 95
},
"land_price_inr_per_sqft": {
"2010": 1400,
"2015": 2200,
"2021": 3400
},
"infrastructure": {
"has_railway": true,
"has_airport": false,
"num_national_highways": 2,
"has_university": true,
"has_medical_college": true,
"industry_type": "textile"
},
"scores": {
"infrastructure": 62,
"connectivity": 55,
"economic_activity": 66.2,
"overall": 61.1
},
"growth_triggers": [
"railway_connectivity",
"national_highway_junction",
"amrut_scheme",
"tier3_emerging_market"
],
"growth_directions": [
"N",
"W",
"NW"
],
"nearest_metro": "Nagpur",
"dist_to_metro_km": 155,
"government_schemes": [
"AMRUT"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "emerging",
"investment_score": 94.8,
"description": "Cotton belt city, textile park and storage hub"
},
{
"id": "belagavi",
"name": "Belagavi",
"state": "Karnataka",
"tier": 3,
"lat": 15.8497,
"lng": 74.4977,
"population": {
"2001": 399653,
"2011": 488292,
"2021": 560000
},
"urban_area_sqkm": {
"2001": 48,
"2006": 59.0,
"2011": 70,
"2016": 81.0,
"2021": 92
},
"land_price_inr_per_sqft": {
"2010": 1800,
"2015": 2800,
"2021": 4200
},
"infrastructure": {
"has_railway": true,
"has_airport": true,
"num_national_highways": 2,
"has_university": true,
"has_medical_college": true,
"industry_type": "defense-industrial"
},
"scores": {
"infrastructure": 92,
"connectivity": 73,
"economic_activity": 83.0,
"overall": 82.7
},
"growth_triggers": [
"railway_connectivity",
"airport_access",
"national_highway_junction",
"smart_city_mission",
"amrut_scheme",
"tier3_emerging_market"
],
"growth_directions": [
"N",
"NE",
"E"
],
"nearest_metro": "Bangalore",
"dist_to_metro_km": 500,
"government_schemes": [
"Smart City",
"AMRUT"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "accelerating",
"investment_score": 95,
"description": "Border city, foundry cluster and second-capital push"
},
{
"id": "kalaburagi",
"name": "Kalaburagi",
"state": "Karnataka",
"tier": 3,
"lat": 17.3297,
"lng": 76.8343,
"population": {
"2001": 430651,
"2011": 543147,
"2021": 620000
},
"urban_area_sqkm": {
"2001": 45,
"2006": 55.0,
"2011": 65,
"2016": 75.0,
"2021": 85
},
"land_price_inr_per_sqft": {
"2010": 1300,
"2015": 2100,
"2021": 3200
},
"infrastructure": {
"has_railway": true,
"has_airport": true,
"num_national_highways": 2,
"has_university": true,
"has_medical_college": true,
"industry_type": "agri-industrial"
},
"scores": {
"infrastructure": 92,
"connectivity": 80,
"economic_activity": 63.8,
"overall": 78.6
},
"growth_triggers": [
"railway_connectivity",
"airport_access",
"national_highway_junction",
"amrut_scheme",
"tier3_emerging_market"
],
"growth_directions": [
"N",
"NE",
"W"
],
"nearest_metro": "Hyderabad",
"dist_to_metro_km": 220,
"government_schemes": [
"AMRUT"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "emerging",
"investment_score": 95,
"description": "North Karnataka hub, toor dal trade and cement industry"
},
{
"id": "nellore",
"name": "Nellore",
"state": "Andhra Pradesh",
"tier": 3,
"lat": 14.4426,
"lng": 79.9865,
"population": {
"2001": 378947,
"2011": 505258,
"2021": 600000
},
"urban_area_sqkm": {
"2001": 42,
"2006": 51.0,
"2011": 60,
"2016": 70.0,
"2021": 80
},
"land_price_inr_per_sqft": {
"2010": 1500,
"2015": 2400,
"2021": 3800
},
"infrastructure": {
"has_railway": true,
"has_airport": false,
"num_national_highways": 2,
"has_university": true,
"has_medical_college": true,
"industry_type": "agri-industrial"
},
"scores": {
"infrastructure": 62,
"connectivity": 55,
"economic_activity": 66.7,
"overall": 61.2
},
"growth_triggers": [
"railway_connectivity",
"national_highway_junction",
"amrut_scheme",
"tier3_emerging_market"
],
"growth_directions": [
"N",
"E",
"NE"
],
"nearest_metro": "Chennai",
"dist_to_metro_km": 175,
"government_schemes": [
"AMRUT"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "emerging",
"investment_score": 95,
"description": "Aquaculture and solar hub on the Chennai-Vijayawada corridor"
},
{
"id": "kakinada",
"name": "Kakinada",
"state": "Andhra Pradesh",
"tier": 3,
"lat": 16.9891,
"lng": 82.2475,
"population": {
"2001": 296329,
"2011": 312538,
"2021": 380000
},
"urban_area_sqkm": {
"2001": 35,
"2006": 42.5,
"2011": 50,
"2016": 59.0,
"2021": 68
},
"land_price_inr_per_sqft": {
"2010": 1600,
"2015": 2500,
"2021": 3900
},
"infrastructure": {
"has_railway": true,
"has_airport": true,
"num_national_highways": 1,
"has_university": true,
"has_medical_college": true,
"industry_type": "oil-port"
},
"scores": {
"infrastructure": 84,
"connectivity": 70,
"economic_activity": 83.6,
"overall": 79.2
},
"growth_triggers": [
"railway_connectivity",
"airport_access",
"smart_city_mission",
"amrut_scheme",
"tier3_emerging_market"
],
"growth_directions": [
"N",
"W",
"SW"
],
"nearest_metro": "Visakhapatnam",
"dist_to_metro_km": 160,
"government_schemes": [
"Smart City",
"AMRUT"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "accelerating",
"investment_score": 91.6,
"description": "Port and petrochemical hub, fertiliser and SEZ growth"
},
{
"id": "vellore",
"name": "Vellore",
"state": "Tamil Nadu",
"tier": 3,
"lat": 12.9165,
"lng": 79.1325,
"population": {
"2001": 386746,
"2011": 423425,
"2021": 500000
},
"urban_area_sqkm": {
"2001": 40,
"2006": 49.0,
"2011": 58,
"2016": 68.0,
"2021": 78
},
"land_price_inr_per_sqft": {
"2010": 1800,
"2015": 2800,
"2021": 4300
},
"infrastructure": {
"has_railway": true,
"has_airport": false,
"num_national_highways": 2,
"has_university": true,
"has_medical_college": true,
"industry_type": "education-industrial"
},
"scores": {
"infrastructure": 62,
"connectivity": 55,
"economic_activity": 68.9,
"overall": 62.0
},
"growth_triggers": [
"railway_connectivity",
"national_highway_junction",
"amrut_scheme",
"tier3_emerging_market"
],
"growth_directions": [
"E",
"SE",
"S"
],
"nearest_metro": "Chennai",
"dist_to_metro_km": 140,
"government_schemes": [
"AMRUT"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "emerging",
"investment_score": 95,
"description": "Medical and education hub (CMC, VIT), leather industry"
},
{
"id": "erode",
"name": "Erode",
"state": "Tamil Nadu",
"tier": 3,
"lat": 11.341,
"lng": 77.7172,
"population": {
"2001": 151184,
"2011": 498000,
"2021": 560000
},
"urban_area_sqkm": {
"2001": 38,
"2006": 46.5,
"2011": 55,
"2016": 63.5,
"2021": 72
},
"land_price_inr_per_sqft": {
"2010": 1600,
"2015": 2500,
"2021": 3800
},
"infrastructure": {
"has_railway": true,
"has_airport": false,
"num_national_highways": 2,
"has_university": true,
"has_medical_college": false,
"industry_type": "textile"
},
"scores": {
"infrastructure": 53,
"connectivity": 65,
"economic_activity": 80,
"overall": 66.0
},
"growth_triggers": [
"railway_connectivity",
"national_highway_junction",
"amrut_scheme",
"tier3_emerging_market"
],
"growth_directions": [
"E",
"W",
"S"
],
"nearest_metro": "Coimbatore",
"dist_to_metro_km": 90,
"government_schemes": [
"AMRUT"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "emerging",
"investment_score": 95,
"description": "Textile and turmeric trade centre of west Tamil Nadu"
},
{
"id": "sikar",
"name": "Sikar",
"state": "Rajasthan",
"tier": 3,
"lat": 27.6094,
"lng": 75.1399,
"population": {
"2001": 185925,
"2011": 237579,
"2021": 300000
},
"urban_area_sqkm": {
"2001": 28,
"2006": 35.0,
"2011": 42,
"2016": 50.0,
"2021": 58
},
"land_price_inr_per_sqft": {
"2010": 1400,
"2015": 2200,
"2021": 3400
},
"infrastructure": {
"has_railway": true,
"has_airport": false,
"num_national_highways": 2,
"has_university": true,
"has_medical_college": false,
"industry_type": "agriculture-education"
},
"scores": {
"infrastructure": 53,
"connectivity": 55,
"economic_activity": 57.3,
"overall": 55.1
},
"growth_triggers": [
"railway_connectivity",
"national_highway_junction",
"amrut_scheme",
"tier3_emerging_market"
],
"growth_directions": [
"S",
"SE",
"E"
],
"nearest_metro": "Jaipur",
"dist_to_metro_km": 115,
"government_schemes": [
"AMRUT"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "emerging",
"investment_score": 85.2,
"description": "Shekhawati education hub, coaching and agri trade"
},
{
"id": "gandhinagar",
"name": "Gandhinagar",
"state": "Gujarat",
"tier": 2,
"lat": 23.2156,
"lng": 72.6369,
"population": {
"2001": 195891,
"2011": 292797,
"2021": 410000
},
"urban_area_sqkm": {
"2001": 50,
"2006": 65.0,
"2011": 80,
"2016": 100.0,
"2021": 120
},
"land_price_inr_per_sqft": {
"2010": 3000,
"2015": 4800,
"2021": 8000
},
"infrastructure": {
"has_railway": true,
"has_airport": true,
"num_national_highways": 2,
"has_university": true,
"has_medical_college": true,
"industry_type": "government-IT"
},
"scores": {
"infrastructure": 92,
"connectivity": 90,
"economic_activity": 95,
"overall": 92.3
},
"growth_triggers": [
"railway_connectivity",
"airport_access",
"national_highway_junction",
"smart_city_mission"
],
"growth_directions": [
"N",
"NE",
"E"
],
"nearest_metro": "Ahmedabad",
"dist_to_metro_km": 28,
"government_schemes": [
"Smart City"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "accelerating",
"investment_score": 95,
"description": "Gujarat capital, GIFT City fintech SEZ and planned growth"
},
{
"id": "faridabad",
"name": "Faridabad",
"state": "Haryana",
"tier": 2,
"lat": 28.4089,
"lng": 77.3178,
"population": {
"2001": 1054981,
"2011": 1404653,
"2021": 1700000
},
"urban_area_sqkm": {
"2001": 120,
"2006": 147.5,
"2011": 175,
"2016": 202.5,
"2021": 230
},
"land_price_inr_per_sqft": {
"2010": 4000,
"2015": 6500,
"2021": 10000
},
"infrastructure": {
"has_railway": true,
"has_airport": false,
"num_national_highways": 3,
"has_university": true,
"has_medical_college": true,
"industry_type": "industrial"
},
"scores": {
"infrastructure": 70,
"connectivity": 75,
"economic_activity": 90.2,
"overall": 78.4
},
"growth_triggers": [
"railway_connectivity",
"national_highway_junction",
"smart_city_mission",
"amrut_scheme"
],
"growth_directions": [
"S",
"SE",
"E"
],
"nearest_metro": "Delhi",
"dist_to_metro_km": 30,
"government_schemes": [
"Smart City",
"AMRUT"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "maturing",
"investment_score": 71.6,
"description": "NCR industrial belt, metro-connected manufacturing city"
},
{
"id": "panipat",
"name": "Panipat",
"state": "Haryana",
"tier": 3,
"lat": 29.3909,
"lng": 76.9635,
"population": {
"2001": 261740,
"2011": 294292,
"2021": 360000
},
"urban_area_sqkm": {
"2001": 32,
"2006": 40.0,
"2011": 48,
"2016": 57.0,
"2021": 66
},
"land_price_inr_per_sqft": {
"2010": 2500,
"2015": 3800,
"2021": 5800
},
"infrastructure": {
"has_railway": true,
"has_airport": false,
"num_national_highways": 2,
"has_university": true,
"has_medical_college": false,
"industry_type": "textile"
},
"scores": {
"infrastructure": 53,
"connectivity": 65,
"economic_activity": 67.5,
"overall": 61.8
},
"growth_triggers": [
"railway_connectivity",
"national_highway_junction",
"amrut_scheme",
"tier3_emerging_market"
],
"growth_directions": [
"N",
"NW",
"S"
],
"nearest_metro": "Delhi",
"dist_to_metro_km": 90,
"government_schemes": [
"AMRUT"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "emerging",
"investment_score": 95,
"description": "Textile and refinery city on NH-44, handloom export hub"
},
{
"id": "karimnagar",
"name": "Karimnagar",
"state": "Telangana",
"tier": 3,
"lat": 18.4386,
"lng": 79.1288,
"population": {
"2001": 218391,
"2011": 261185,
"2021": 320000
},
"urban_area_sqkm": {
"2001": 30,
"2006": 37.5,
"2011": 45,
"2016": 53.5,
"2021": 62
},
"land_price_inr_per_sqft": {
"2010": 1300,
"2015": 2100,
"2021": 3300
},
"infrastructure": {
"has_railway": true,
"has_airport": false,
"num_national_highways": 2,
"has_university": true,
"has_medical_college": true,
"industry_type": "agri-industrial"
},
"scores": {
"infrastructure": 62,
"connectivity": 55,
"economic_activity": 69.3,
"overall": 62.1
},
"growth_triggers": [
"railway_connectivity",
"national_highway_junction",
"smart_city_mission",
"amrut_scheme",
"tier3_emerging_market"
],
"growth_directions": [
"N",
"NE",
"E"
],
"nearest_metro": "Hyderabad",
"dist_to_metro_km": 165,
"government_schemes": [
"Smart City",
"AMRUT"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "emerging",
"investment_score": 95,
"description": "Granite and agri hub, Smart City in north Telangana"
},
{
"id": "nizamabad",
"name": "Nizamabad",
"state": "Telangana",
"tier": 3,
"lat": 18.6725,
"lng": 78.0941,
"population": {
"2001": 288722,
"2011": 311152,
"2021": 380000
},
"urban_area_sqkm": {
"2001": 32,
"2006": 39.0,
"2011": 46,
"2016": 54.0,
"2021": 62
},
"land_price_inr_per_sqft": {
"2010": 1200,
"2015": 1900,
"2021": 3000
},
"infrastructure": {
"has_railway": true,
"has_airport": false,
"num_national_highways": 2,
"has_university": true,
"has_medical_college": true,
"industry_type": "agriculture"
},
"scores": {
"infrastructure": 62,
"connectivity": 55,
"economic_activity": 53.3,
"overall": 56.8
},
"growth_triggers": [
"railway_connectivity",
"national_highway_junction",
"amrut_scheme",
"tier3_emerging_market"
],
"growth_directions": [
"N",
"NW",
"E"
],
"nearest_metro": "Hyderabad",
"dist_to_metro_km": 175,
"government_schemes": [
"AMRUT"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "emerging",
"investment_score": 86.9,
"description": "Turmeric and maize trade centre of north Telangana"
},
{
"id": "haldia",
"name": "Haldia",
"state": "West Bengal",
"tier": 3,
"lat": 22.0667,
"lng": 88.0698,
"population": {
"2001": 130000,
"2011": 200762,
"2021": 270000
},
"urban_area_sqkm": {
"2001": 30,
"2006": 39.0,
"2011": 48,
"2016": 58.0,
"2021": 68
},
"land_price_inr_per_sqft": {
"2010": 1500,
"2015": 2400,
"2021": 3800
},
"infrastructure": {
"has_railway": true,
"has_airport": false,
"num_national_highways": 2,
"has_university": false,
"has_medical_college": false,
"industry_type": "oil-port"
},
"scores": {
"infrastructure": 41,
"connectivity": 55,
"economic_activity": 93,
"overall": 63.0
},
"growth_triggers": [
"railway_connectivity",
"national_highway_junction",
"amrut_scheme",
"tier3_emerging_market"
],
"growth_directions": [
"N",
"NW",
"W"
],
"nearest_metro": "Kolkata",
"dist_to_metro_km": 120,
"government_schemes": [
"AMRUT"
],
"twin_city_id": null,
"twin_city_lag_years": 0,
"growth_phase": "accelerating",
"investment_score": 75.9,
"description": "Port and petrochemical hub on the Hooghly, industrial zone"
}
]

// ── Helpers (operate on the full backend-shape city objects above) ──────────
const _yrs = (o) => Object.keys(o).map(Number).sort((a, b) => a - b)
const _phaseRank = { emerging: 0, accelerating: 1, maturing: 2, mature: 3 }
const _bearing = { N: [1, 0], S: [-1, 0], E: [0, 1], W: [0, -1], NE: [0.7, 0.7], NW: [0.7, -0.7], SE: [-0.7, 0.7], SW: [-0.7, -0.7] }

function _genPrediction(city) {
  const baseYear = 2021, horizon = 15
  const curArea = city.urban_area_sqkm['2021']
  const curPrice = city.land_price_inr_per_sqft['2021']
  const cagrBase = { emerging: 0.115, accelerating: 0.09, maturing: 0.065, mature: 0.045 }[city.growth_phase] ?? 0.08
  const cagr = Math.min(Math.max(cagrBase + (city.tier === 3 ? 0.012 : 0) - (curPrice > 8000 ? 0.015 : 0), 0.03), 0.15)
  const aCagr = Math.min({ emerging: 0.045, accelerating: 0.032, maturing: 0.022, mature: 0.012 }[city.growth_phase] ?? 0.03, 0.055)
  const years = [], areas = [], prices = []
  for (let i = 0; i <= horizon; i++) {
    years.push(baseYear + i)
    areas.push(Math.round(curArea * Math.pow(1 + aCagr, i) * 100) / 100)
    prices.push(Math.round(curPrice * Math.pow(1 + cagr, i)))
  }
  const area5 = areas[5], area10 = areas[10], price5 = prices[5], price10 = prices[10]
  const dirs = (city.growth_directions && city.growth_directions.length ? city.growth_directions : ['N', 'E']).slice(0, 4)
  const phaseScore = { emerging: 88, accelerating: 72, maturing: 55, mature: 40 }[city.growth_phase] ?? 65
  const coslat = Math.max(Math.cos(city.lat * Math.PI / 180), 0.2)
  const rCur = Math.sqrt(curArea / Math.PI), r5 = Math.sqrt(area5 / Math.PI), r10 = Math.sqrt(area10 / Math.PI)
  const zones = []
  dirs.forEach((d, i) => {
    const [dy, dx] = _bearing[d] || [0, 0]
    const score = Math.min(phaseScore + (4 - i) * 3, 95)
    zones.push({ zone_id: `zone_${d.toLowerCase()}_5yr`, label: `${d} Corridor — 5-Year Zone`, direction: d, horizon_years: 5,
      radius_km: Math.round((r5 - rCur) * 100) / 100,
      center_lat: Math.round((city.lat + dy / 111 * r5 * 0.6) * 1e4) / 1e4,
      center_lng: Math.round((city.lng + dx / (111 * coslat) * r5 * 0.6) * 1e4) / 1e4,
      investment_score: score, expected_price_rise_pct: Math.round(phaseScore * 0.8 + 10),
      risk_level: score > 70 ? 'medium' : 'low', recommendation: score > 75 ? 'Buy Now' : 'Watch' })
    zones.push({ zone_id: `zone_${d.toLowerCase()}_10yr`, label: `${d} Fringe — 10-Year Zone`, direction: d, horizon_years: 10,
      radius_km: Math.round((r10 - r5) * 100) / 100,
      center_lat: Math.round((city.lat + dy / 111 * r10 * 0.7) * 1e4) / 1e4,
      center_lng: Math.round((city.lng + dx / (111 * coslat) * r10 * 0.7) * 1e4) / 1e4,
      investment_score: Math.max(score - 12, 40), expected_price_rise_pct: Math.round(phaseScore * 1.4 + 15),
      risk_level: ['emerging', 'accelerating'].includes(city.growth_phase) ? 'high' : 'medium',
      recommendation: ['emerging', 'accelerating'].includes(city.growth_phase) ? 'Buy Early' : 'Monitor' })
  })
  return {
    base_year: baseYear,
    annual_cagr_price_pct: Math.round(cagr * 1000) / 10,
    model: { type: 'calibrated_bounded_cagr(mock)', area_cagr_pct: Math.round(aCagr * 1000) / 10, price_cagr_pct: Math.round(cagr * 1000) / 10 },
    timeline: { years, urban_area_sqkm: areas, land_price_inr_per_sqft: prices },
    milestones: {
      area_2026_sqkm: area5, area_2031_sqkm: area10,
      price_2026_inr_per_sqft: price5, price_2031_inr_per_sqft: price10,
      price_appreciation_5yr_pct: Math.round((price5 / curPrice - 1) * 1000) / 10,
      price_appreciation_10yr_pct: Math.round((price10 / curPrice - 1) * 1000) / 10,
      confidence_5yr: 0.75, confidence_10yr: 0.5,
    },
    investment_zones: zones,
    growth_phase: city.growth_phase, investment_score: city.investment_score,
    city: { land_price_inr_per_sqft: city.land_price_inr_per_sqft },
  }
}

function _findTwin(city) {
  const cands = MOCK_CITIES.filter(c => c.id !== city.id && (_phaseRank[c.growth_phase] ?? 0) > (_phaseRank[city.growth_phase] ?? 0))
  const pool = (cands.length ? cands : MOCK_CITIES.filter(c => c.id !== city.id)).slice()
  pool.sort((a, b) => (b.state === city.state) - (a.state === city.state) || b.investment_score - a.investment_score)
  return pool[0]
}

export function getMockFullAnalysis(cityId) {
  const city = MOCK_CITIES.find(c => c.id === cityId) || MOCK_CITIES[0]
  const ay = _yrs(city.urban_area_sqkm), py = _yrs(city.land_price_inr_per_sqft)
  const history = { years: ay, urban_area_sqkm: ay.map(y => city.urban_area_sqkm[String(y)]) }
  const price_history = { years: py, values: py.map(y => city.land_price_inr_per_sqft[String(y)]) }
  const prediction = _genPrediction(city)
  const tw = _findTwin(city)
  const twinAy = _yrs(tw.urban_area_sqkm)
  const lag = { emerging: 18, accelerating: 12, maturing: 8, mature: 5 }[city.growth_phase] ?? 12
  const twin = {
    city_id: tw.id, city_name: tw.name, twin_city: tw, lag_years: lag,
    similarity_score: Math.min(95, 70 + Math.round(tw.investment_score * 0.25)),
    match_reason: 'Mock match — more-developed city with a comparable profile',
    twin_current_price: tw.land_price_inr_per_sqft['2021'],
    comparison: {
      city_a: { id: city.id, name: city.name, history: { area_years: ay, area_values: history.urban_area_sqkm } },
      city_b: { id: tw.id, name: tw.name, history: { area_years: twinAy, area_values: twinAy.map(y => tw.urban_area_sqkm[String(y)]) } },
    },
  }
  return { city, history, price_history, prediction, twin }
}

export function getMockSimilarCities(cityId, top = 6) {
  const city = MOCK_CITIES.find(c => c.id === cityId)
  const pool = city
    ? MOCK_CITIES.filter(c => c.id !== cityId)
        .map(c => ({ c, d: Math.abs(c.investment_score - city.investment_score) + (c.tier === city.tier ? 0 : 8) }))
        .sort((a, b) => a.d - b.d).map(x => x.c)
    : MOCK_CITIES
  return pool.slice(0, top).map((c, i) => ({
    city_id: c.id, name: c.name, state: c.state, tier: c.tier,
    growth_phase: c.growth_phase, investment_score: c.investment_score,
    similarity_score: Math.max(60, 94 - i * 5),
  }))
}

// ── Fallbacks for the AI / NLP / CV feature endpoints ───────────────────────
export function getMockMlPrice(cityId, horizon = 10) {
  const city = MOCK_CITIES.find(c => c.id === cityId) || MOCK_CITIES[0]
  const cagrBase = { emerging: 0.15, accelerating: 0.115, maturing: 0.08, mature: 0.055 }[city.growth_phase] ?? 0.10
  const cagr = Math.min(cagrBase + (city.tier === 3 ? 0.015 : 0), 0.30)
  const cur = city.land_price_inr_per_sqft['2021']
  const traj = []
  for (let i = 0; i <= horizon; i++) traj.push({ year: 2021 + i, price_inr_per_sqft: Math.round(cur * Math.pow(1 + cagr, i)) })
  return {
    city_id: city.id, model_backend: 'mock-fallback',
    predicted_annual_cagr_pct: Math.round(cagr * 1000) / 10,
    current_price_inr_per_sqft: cur,
    projected_price_5yr: traj[5]?.price_inr_per_sqft ?? traj[traj.length - 1].price_inr_per_sqft,
    projected_price_10yr: traj[traj.length - 1].price_inr_per_sqft,
    price_trajectory: traj,
    top_feature_contributions: [
      { feature: 'urban_area_cagr_01_21', contribution: 0.01 },
      { feature: 'economic_score', contribution: 0.004 },
      { feature: 'growth_phase_rank', contribution: -0.003 },
    ],
    feature_values: {},
  }
}

export function getMockSignals(cityId, top = 6) {
  const city = MOCK_CITIES.find(c => c.id === cityId) || MOCK_CITIES[0]
  const infra = city.infrastructure || {}
  const raw = []
  if (infra.has_airport) raw.push(['airport', 'operational', 1, `${city.name} has operational airport connectivity.`, 'AAI', 86])
  if ((city.government_schemes || []).some(s => /smart/i.test(s))) raw.push(['smart_city', 'approved', 3, `${city.name} is funded under the Smart City Mission.`, 'Smart City Mission', 70])
  if ((infra.num_national_highways || 0) >= 2) raw.push(['expressway', 'operational', 1, `${city.name} sits at a national highway junction.`, 'NHAI', 78])
  if (infra.has_railway) raw.push(['railway', 'approved', 4, `${city.name} railway station modernisation is underway.`, 'Indian Railways', 64])
  if (city.tier === 3 && city.growth_phase === 'emerging') raw.push(['realty', 'proposed', 6, `${city.name} is an emerging Tier-3 market with rising RERA registrations.`, 'RERA', 55])
  while (raw.length < 3) raw.push(['expressway', 'proposed', 5, `${city.name} regional road upgrades are proposed.`, 'State PWD', 50])
  const signals = raw.slice(0, top).map(([pt, st, lead, head, src, imp], i) => ({
    id: `mock_${city.id}_${i}`, project_type: pt, status: st, lead_time_years: lead,
    impact_score: imp, certainty: 0.7, headline: head, source: src, year: 2024, origin: 'mock',
    entities: { amounts_inr_crore: [], organizations: [src], locations: [city.name] },
  })).sort((a, b) => b.impact_score - a.impact_score)
  return {
    city_id: city.id, city_name: city.name, signal_count: signals.length,
    composite_signal_score: Math.round(signals.reduce((s, x) => s + x.impact_score, 0) / Math.max(signals.length, 1) * 10) / 10,
    soonest_impact_years: signals.length ? Math.min(...signals.map(s => s.lead_time_years)) : null,
    signals,
  }
}

export function getMockCvMetrics(cityId) {
  const city = MOCK_CITIES.find(c => c.id === cityId) || MOCK_CITIES[0]
  const ay = _yrs(city.urban_area_sqkm)
  return {
    city_id: city.id, city_name: city.name,
    grid: { resolution: 200, pixel_km: 0.2, window_km: 20 }, method: 'mock-fallback',
    per_year: ay.map(y => ({ year: y, area_sqkm: city.urban_area_sqkm[String(y)], compactness_polsby_popper: 0.95, fragmentation_components: 1 })),
    dominant_growth_direction: { compass: (city.growth_directions && city.growth_directions[0]) || 'N', bearing_deg: 0, offset_km: 1.5 },
    stated_growth_directions: city.growth_directions || [], sprawl_index: 3.0, raster_png_url: null,
  }
}

export function getMockGeoZones(cityId) {
  const { city } = getMockFullAnalysis(cityId)
  return { type: 'FeatureCollection', city_id: city.id, city_name: city.name, center: [city.lng, city.lat], features: [] }
}

// ── Investment scoring + copilot fallbacks ──────────────────────────────────
const _riskMock = (c) => {
  let s = { emerging: 70, accelerating: 52, maturing: 34, mature: 22 }[c.growth_phase] ?? 50
  if (c.tier === 3) s += 10
  if (c.dist_to_metro_km > 300) s += 8; else if (c.dist_to_metro_km > 120) s += 4
  if (!c.infrastructure?.has_airport) s += 5
  s = Math.max(5, Math.min(s, 95))
  return [s, s >= 62 ? 'high' : s >= 40 ? 'medium' : 'low']
}
const _roiMock = (c) => Math.round(Math.min(({ emerging: 0.115, accelerating: 0.09, maturing: 0.065, mature: 0.045 }[c.growth_phase] ?? 0.08) / 0.15 * 100, 100) * 10) / 10

export function getMockScore(cityId) {
  const c = MOCK_CITIES.find(x => x.id === cityId) || MOCK_CITIES[0]
  const [risk, level] = _riskMock(c)
  const roi = _roiMock(c)
  const demand = Math.round(Math.min((c.population['2021'] / Math.max(c.population['2001'], 1) - 1) * 60, 45) + c.scores.economic_activity * 0.35 + (c.government_schemes || []).length * 4)
  const fdp = Math.min(30 + (c.growth_triggers || []).length * 7 + ({ emerging: 22, accelerating: 16, maturing: 6, mature: 0 }[c.growth_phase] ?? 8), 100)
  const composite = Math.round(roi * 0.26 + demand * 0.18 + fdp * 0.16 + c.scores.infrastructure * 0.12 + c.scores.connectivity * 0.10 + c.scores.economic_activity * 0.10 + (100 - risk) * 0.08)
  return {
    city_id: c.id, city_name: c.name, composite_score: composite, headline_investment_score: c.investment_score,
    sub_scores: { roi_score: roi, risk_score: risk, risk_level: level, liquidity_score: Math.min(60 + { 1: 30, 2: 20, 3: 10 }[c.tier], 100), demand_score: demand, future_development_probability: fdp, infrastructure_score: c.scores.infrastructure, connectivity_score: c.scores.connectivity, economic_score: c.scores.economic_activity },
    rationale: {
      strengths: [c.infrastructure?.has_airport ? 'Airport access widens the catchment.' : 'Rail + road connectivity supports growth.', c.growth_phase === 'emerging' ? 'Early-stage market — most upside.' : `Strong fundamentals (score ${c.investment_score}).`],
      watch_outs: [level === 'high' ? 'High-risk early/peripheral market — verify infra execution.' : 'Standard market risks apply.'],
    },
    model_drivers: null, recommendation: composite >= 75 && level !== 'high' ? 'Buy Now' : composite >= 62 ? 'Buy Early' : composite >= 48 ? 'Watch' : 'Hold',
  }
}

export function getMockCopilot(q, top = 6) {
  const ql = (q || '').toLowerCase()
  let list = MOCK_CITIES.slice()
  const intent = {}
  const mp = ql.match(/([\d,]+)\s*(?:\/|per\s?)?\s?sq/); if (mp) { intent.max_price_per_sqft = +mp[1].replace(/,/g, '') }
  const mb = ql.match(/([\d.]+)\s*(lakhs?|crores?|cr)/); if (mb && !intent.max_price_per_sqft) { const l = mb[2].startsWith('cr') ? +mb[1] * 100 : +mb[1]; intent.budget_lakh = l; intent.max_price_per_sqft = Math.round(l * 100) }
  const mt = ql.match(/tier[- ]?([123])/); if (mt) intent.tier = +mt[1];
  ['emerging', 'accelerating', 'maturing', 'mature'].forEach(p => { if (ql.includes(p)) intent.phase = p })
  MOCK_STATES.forEach(s => { if (ql.includes(s.toLowerCase())) intent.state = s })
  if (/low[- ]?risk|safe|stable/.test(ql)) intent.risk = 'low'
  if (/high[- ]?growth|aggressive|roi|appreciation|return|upside/.test(ql)) intent.sort = 'roi'
  if (/near (a )?metro|close to (a )?metro/.test(ql)) intent.near_metro = true
  if (intent.state) list = list.filter(c => c.state === intent.state)
  if (intent.tier) list = list.filter(c => c.tier === intent.tier)
  if (intent.phase) list = list.filter(c => c.growth_phase === intent.phase)
  if (intent.max_price_per_sqft) list = list.filter(c => c.land_price_inr_per_sqft['2021'] <= intent.max_price_per_sqft)
  if (intent.near_metro) list = list.filter(c => c.dist_to_metro_km <= 120)
  if (intent.risk === 'low') list = list.filter(c => _riskMock(c)[0] < 62)
  let sortBy = 'investment score'
  if (intent.sort === 'roi') { list.sort((a, b) => _roiMock(b) - _roiMock(a)); sortBy = 'modelled ROI' }
  else if (intent.risk === 'low') { list.sort((a, b) => _riskMock(a)[0] - _riskMock(b)[0]); sortBy = 'lowest risk' }
  else if (intent.max_price_per_sqft) { list.sort((a, b) => a.land_price_inr_per_sqft['2021'] - b.land_price_inr_per_sqft['2021']); sortBy = 'affordability' }
  else list.sort((a, b) => b.investment_score - a.investment_score)
  const results = list.slice(0, top).map(c => ({ city_id: c.id, name: c.name, state: c.state, tier: c.tier, growth_phase: c.growth_phase, investment_score: c.investment_score, land_price_2021: c.land_price_inr_per_sqft['2021'], roi_score: _roiMock(c), risk_level: _riskMock(c)[1], dist_to_metro_km: c.dist_to_metro_km, reason: `score ${c.investment_score} · ${c.growth_phase}` }))
  return { query: q, interpretation: intent, summary: `Showing ${results.length} cities, ranked by ${sortBy}.`, sort_by: sortBy, count: results.length, results }
}
