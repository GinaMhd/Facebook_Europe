import json
from pathlib import Path

import pandas as pd
import geopandas as gpd
import plotly.express as px
import streamlit as st
from shapely.geometry import box

st.set_page_config(page_title="EU Regional Demographic Map", layout="wide")

# =========================================================
# SETTINGS
# =========================================================
DATA_PATH = "Combined.csv"
REGION_GEOJSON_DIR = Path("geojson_regions")

EU_COUNTRY_CODES = [
    "AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR",
    "DE", "GR", "HU", "IE", "IT", "LV", "LT", "LU", "MT", "NL",
    "PL", "PT", "RO", "SK", "SI", "ES", "SE"
]

COUNTRY_NAME_MAP = {
    "AT": "Austria",
    "BE": "Belgium",
    "BG": "Bulgaria",
    "HR": "Croatia",
    "CY": "Cyprus",
    "CZ": "Czechia",
    "DK": "Denmark",
    "EE": "Estonia",
    "FI": "Finland",
    "FR": "France",
    "DE": "Germany",
    "GR": "Greece",
    "HU": "Hungary",
    "IE": "Ireland",
    "IT": "Italy",
    "LV": "Latvia",
    "LT": "Lithuania",
    "LU": "Luxembourg",
    "MT": "Malta",
    "NL": "Netherlands",
    "PL": "Poland",
    "PT": "Portugal",
    "RO": "Romania",
    "SK": "Slovakia",
    "SI": "Slovenia",
    "ES": "Spain",
    "SE": "Sweden",
}

# ---------------------------------------------------------
# IMPORTANT:
# For each country's GeoJSON, specify the column that has the
# region name matching your CSV's location_name.
# Adjust these if needed after checking each GeoJSON.
# ---------------------------------------------------------
#REGION_NAME_PROPERTY_MAP = {}

# ---------------------------------------------------------
# Optional country-specific region-name fixes
# Add more later if names do not match exactly
# ---------------------------------------------------------
REGION_NAME_FIXES = {
    "IT": {
        "Valle d'Aosta/Vallée d'Aoste": "Valle d'Aosta", # The first one belongs to geojson file and the second is combined (FB marketing annotation)
        "Piemonte": "Piedmont",
        "Lombardia": "Lombardy",
        "Toscana": "Tuscany",
        "Sardegna": "Sardinia",
    },
    "AT": {
        "Burgenland": "Burgenland",
        "Tyrol": "Tirol",
        "Vorarlberg": "Vorarlberg",
        "Lower Austria": "Niederösterreich",
        "Vienna": "Wien",
        "Carinthia": "Kärnten",
        "Styria": "Steiermark",
        "Upper Austria": "Oberösterreich",
        "Salzburg": "Salzburg"
        },
    "BE": {
    "Wallonia": "Région wallonne",
    "Brussels": "Région de Bruxelles-Capitale/Brussels Hoofdstedelijk Gewest",
    "Flemish Region": "Vlaams Gewest"
    },
    
    "HR": 
        {
    "Brod-Posavina County": "Brodsko-posavska županija",
    "Koprivnica-Križevci County": "Koprivničko-križevačka županija",
    "Primorje-Gorski Kotar County": "Primorsko-goranska županija",
    "Sisak-Moslavina County": "Sisačko-moslavačka županija",
    "Lika-Senj County": "Ličko-senjska županija",
    "Zadar County": "Zadarska županija",
    "Požega-Slavonia County": "Požeško-slavonska županija",
    "Zagreb County": "Zagrebačka županija",
    "Split-Dalmatia County": "Splitsko-dalmatinska županija",
    "Varaždin County": "Varaždinska županija",
    "Virovitica-Podravina County": "Virovitičko-podravska županija",
    "Šibenik-Knin County": "Šibensko-kninska županija",
    "Osijek-Baranja County": "Osječko-baranjska županija",
    "Istria County": "Istarska županija",
    "Karlovac County": "Karlovačka županija",
    "Dubrovnik-Neretva County": "Dubrovačko-neretvanska županija",
    "Vukovar-Syrmia County": "Vukovarsko-srijemska županija",
    "Krapina-Zagorje County": "Krapinsko-zagorska županija",
    "Bjelovar-Bilogora County": "Bjelovarsko-bilogorska županija",
    "Međimurje County": "Međimurska županija",
    "Zagreb": "Grad Zagreb"
    },
        
    "BG" : {
    "Silistra Province": "Silistra",
    "Lovech Province": "Lovech",
    "Plovdiv Province": "Plovdiv",
    "Haskovo Province": "Haskovo",
    "Sofia Province": "Sofia",
    "Yambol Province": "Yambol",
    "Sofia City Province": "Sofia (stolitsa)",
    "Kardzhali Province": "Kardzhali",
    "Montana Province": "Montana",
    "Pernik Province": "Pernik",
    "Blagoevgrad Province": "Blagoevgrad",
    "Pazardzhik Province": "Pazardzhik",
    "Varna Province": "Varna",
    "Vratsa Province": "Vratsa",
    "Targovishte Province": "Targovishte",
    "Stara Zagora Province": "Stara Zagora",
    "Burgas Province": "Burgas",
    "Ruse Province": "Ruse",
    "Shumen Province": "Shumen",
    "Sliven Province": "Sliven",
    "Vidin Province": "Vidin",
    "Smolyan Province": "Smolyan",
    "Veliko Tarnovo Province": "Veliko Tarnovo",
    "Kyustendil Province": "Kyustendil",
    "Dobrich Province": "Dobrich",
    "Gabrovo Province": "Gabrovo",
    "Pleven Province": "Pleven",
    "Razgrad Province": "Razgrad"
    },
    
    "CZ": {
    "Plzeň Region": "Plzeňský kraj",
    "South Moravia": "Jihomoravský kraj",
    "Prague": "Hlavní město Praha",
    "Central Bohemia": "Středočeský kraj",
    "Ústí nad Labem": "Ústecký kraj",
    "South Bohemia": "Jihočeský kraj",
    "Hradec Králové": "Královéhradecký kraj",
    "Vysočina Region": "Kraj Vysočina",
    "Olomouc": "Olomoucký kraj",
    "Moravian-Silesian Region": "Moravskoslezský kraj",
    "Liberec": "Liberecký kraj",
    "Zlín": "Zlínský kraj",
    "Karlovy Vary": "Karlovarský kraj",
    "Pardubice": "Pardubický kraj"
    },
    
    "DE": {
    "Saxony-Anhalt": "Sachsen-Anhalt",
    "Rhineland-Palatinate": "Rheinland-Pfalz",
    "Saxony": "Sachsen",
    "Lower Saxony": "Niedersachsen",
    "North Rhine-Westphalia": "Nordrhein-Westfalen"
    },
    
    "DK": {
    "Capital Region of Denmark": "Hovedstaden",
    "Central Denmark Region": "Midtjylland",
    "North Denmark Region": "Nordjylland",
    "Region Zealand": "Sjælland",
    "Region of Southern Denmark": "Syddanmark"
    },
    
    "FR": {
    "Provence-Alpes-Cote d'Azur": "Provence-Alpes-Côte d’Azur",
    "Franche-Comte": "Franche-Comté",
    "Nord-Pas-de-Calais": "Nord-Pas de Calais",
    "Centre": 'Centre — Val de Loire',
    "Midi-Pyrenees": "Midi-Pyrénées",
    },
    
    "FI": {
    "North Karelia": "Pohjois-Karjala",
    "Tavastia Proper": "Kanta-Häme",
    "Southwest Finland": "Varsinais-Suomi",
    "South Karelia": "Etelä-Karjala",
    "Uusimaa": "Helsinki-Uusimaa",
    "Central Finland": "Keski-Suomi",
    "Northern Ostrobothnia": "Pohjois-Pohjanmaa",
    "Ostrobothnia": "Pohjanmaa",
    "Lapland": "Lappi",
    "Central Ostrobothnia": "Keski-Pohjanmaa",
    "Southern Ostrobothnia": "Etelä-Pohjanmaa",
    "Åland Islands": "Åland"
    },
    
    "HU": {
    "Borsod-Abaúj-Zemplén County": "Borsod-Abaúj-Zemplén",
    "Győr-Moson-Sopron County": "Győr-Moson-Sopron",
    "Csongrád County": "Csongrád-Csanád",
    "Komárom-Esztergom County": "Komárom-Esztergom",
    "Nógrád County": "Nógrád",
    "Somogy County": "Somogy",
    "Pest County": "Pest",
    "Zala County": "Zala",
    "Szabolcs-Szatmár-Bereg County": "Szabolcs-Szatmár-Bereg",
    "Baranya County": "Baranya",
    "Veszprém County": "Veszprém",
    "Hajdú-Bihar County": "Hajdú-Bihar",
    "Heves County": "Heves",
    "Tolna County": "Tolna",
    "Vas County": "Vas",
    "Bács-Kiskun County": "Bács-Kiskun",
    "Fejér County": "Fejér",
    "Békés County": "Békés",
    "Jász-Nagykun-Szolnok County": "Jász-Nagykun-Szolnok"
    },
    "IE": {
    "County Westmeath": "Midland",
    "County Laois": "Midland",
    "County Longford": "Midland",
    "County Offaly": "Midland",

    "County Louth": "Border",
    "County Leitrim": "Border",
    "Cavan": "Border",
    "Donegal": "Border",
    "County Monaghan": "Border",
    "County Sligo": "Border",

    "County Galway": "West",
    "County Mayo": "West",
    "Roscommon": "West",

    "County Clare": "Mid-West",
    "County Limerick": "Mid-West",
    "County Tipperary": "Mid-West",

    "County Kilkenny": "South-East",
    "County Wexford": "South-East",
    "County Waterford": "South-East",
    "County Carlow": "South-East",

    "County Cork": "South-West",
    "Kerry": "South-West",

    "County Dublin": "Dublin",

    "County Meath": "Mid-East",
    "County Kildare": "Mid-East",
    "County Wicklow": "Mid-East",
},
    "LT": {
    "Marijampolė County": "Marijampolės apskritis",
    "Utena County": "Utenos apskritis",
    "Telšiai County": "Telšių apskritis",
    "Tauragė County": "Tauragės apskritis",
    "Panevėžys County": "Panevėžio apskritis",
    "Kaunas County": "Kauno apskritis",
    "Alytus County": "Alytaus apskritis",
    "Šiauliai County": "Šiaulių apskritis",
    "Vilnius County": "Vilniaus apskritis",
    "Klaipėda County": "Klaipėdos apskritis"
},
    "LV": {
    "Riga Planning Region": "Rīga",
    "Semigallia": "Zemgale",
    "Kurzeme Planning Region": "Kurzeme"
},
    "NL": {
    "Friesland": "Friesland (NL)",
    "Limburg": "Limburg (NL)",
    "North Holland": "Noord-Holland",
    "North Brabant": "Noord-Brabant"
},
    "PL": {
    "Lesser Poland Voivodeship": "Małopolskie",
    "Lublin Voivodeship": "Lubelskie",
    "Warmian-Masurian Voivodeship": "Warmińsko-mazurskie",
    "Silesian Voivodeship": "Śląskie",
    "Pomeranian Voivodeship": "Pomorskie",
    "Łódź Voivodeship": "Łódzkie",
    "Podlaskie Voivodeship": "Podlaskie",
    "Lower Silesian Voivodeship": "Dolnośląskie",
    "West Pomeranian Voivodeship": "Zachodniopomorskie",
    "Opole Voivodeship": "Opolskie",
    "Greater Poland Voivodeship": "Wielkopolskie",
    "Świętokrzyskie Voivodeship": "Świętokrzyskie",
    "Podkarpackie Voivodeship": "Podkarpackie",
    "Kuyavian-Pomeranian Voivodeship": "Kujawsko-pomorskie",
    "Lubusz Voivodeship": "Lubuskie",
    "Warszawski stołeczny": "Masovian Voivodeship", # the smaller one
    "Mazowiecki regionalny": "Masovian Voivodeship" # the bigger region
},
    
    "PT": {
    "Vila Real District": "Norte",
    "Guarda District": "Centro (PT)",
    "Aveiro District": "Centro (PT)",
    "Évora District": "Alentejo",
    "Setúbal District": "Península de Setúbal",
    "Madeira": "Região Autónoma da Madeira",
    "Coimbra District": "Centro (PT)",
    "Porto District": "Norte",
    "Viana do Castelo District": "Norte",
    "Beja District": "Alentejo",
    "Lisbon District": "Grande Lisboa",
    "Faro District": "Algarve",
    "Santarém District": "Oeste e Vale do Tejo",
    "Leiria District": "Centro (PT)",
    "Viseu District": "Centro (PT)",
    "Bragança District": "Norte",
    "Portalegre District": "Alentejo",
    "Braga District": "Norte",
    "Castelo Branco District": "Centro (PT)",
    "Azores": "Região Autónoma dos Açores"
},
        
        
    "ES":{
    "Castile and León": "Castilla y León",
    "Navarre": "Comunidad Foral de Navarra",
    "Community of Madrid": "Comunidad de Madrid",
    "Catalonia": "Cataluña",
    "Canary Islands": "Canarias",
    "Andalusia": "Andalucía",
    "Region of Murcia": "Región de Murcia",
    "Basque Autonomous Country": "País Vasco",
    "Aragon": "Aragón",
    "Principality of Asturias": "Principado de Asturias",
    "Comunidad Valenciana": "Comunitat Valenciana",
    "Balearic Islands": "Illes Balears"
},
    "RO": {
    "Neamț County": "Neamţ",
    "Arges": "Argeş",
    "Mureș County": "Mureş",
    "Bucharest": "Bucureşti",
    "Olt County": "Olt",
    "Dolj County": "Dolj",
    "Giurgiu County": "Giurgiu",
    "Bihor County": "Bihor",
    "Teleorman County": "Teleorman",
    "Vrancea County": "Vrancea",
    "Timiș County": "Timiş",
    "Mehedinți County": "Mehedinţi",
    "Iași County": "Iaşi",
    "Vaslui County": "Vaslui",
    "Harghita County": "Harghita",
    "Braila": "Brăila",
    "Cluj County": "Cluj",
    "Vâlcea County": "Vâlcea",
    "Brașov County": "Braşov",
    "Alba County": "Alba",
    "Tulcea County": "Tulcea",
    "Maramureș County": "Maramureş",
    "Prahova County": "Prahova",
    "Ilfov County": "Ilfov",
    "Hunedoara County": "Hunedoara",
    "Dâmbovița County": "Dâmboviţa",
    "Arad County": "Arad",
    "Bistrița-Năsăud County": "Bistriţa-Năsăud",
    "Constanța County": "Constanţa",
    "Sibiu County": "Sibiu",
    "Covasna County": "Covasna",
    "Sălaj County": "Sălaj",
    "Buzău County": "Buzău",
    "Gorj County": "Gorj",
    "Caraș-Severin County": "Caraş-Severin",
    "Satu Mare County": "Satu Mare",
    "Suceava County": "Suceava",
    "Călărași County": "Călăraşi",
    "Ialomița County": "Ialomiţa",
    "Galați County": "Galaţi",
    "Bacău County": "Bacău",
    "Botoșani County": "Botoşani"
},
    "SE": {
    "Västmanland County": "Västmanlands län",
    "Dalarna County": "Dalarnas län",
    "Stockholm County": "Stockholms län",
    "Gotland County": "Gotlands län",
    "Östergötland County": "Östergötlands län",
    "Västerbotten County": "Västerbottens län",
    "Skåne County": "Skåne län",
    "Gävleborg County": "Gävleborgs län",
    "Norrbotten County": "Norrbottens län",
    "Jönköping County": "Jönköpings län",
    "Västernorrland County": "Västernorrlands län",
    "Kalmar County": "Kalmar län",
    "Södermanland County": "Södermanlands län",
    "Västra Götaland County": "Västra Götalands län",
    "Uppsala County": "Uppsala län",
    "Blekinge County": "Blekinge län",
    "Örebro County": "Örebro län",
    "Jämtland County": "Jämtlands län",
    "Värmland County": "Värmlands län",
    "Halland County": "Hallands län",
    "Kronoberg County": "Kronobergs län"
},
    "SI": {
    "Savinja Statistical Region": "Savinjska",
    "Carinthia Statistical Region": "Koroška",
    "Southeast Slovenia Statistical Region": "Jugovzhodna Slovenija",
    "Central Sava Statistical Region": "Zasavska",
    "Lower Sava Statistical Region": "Posavska",
    "Upper Carniola Statistical Region": "Gorenjska",
    "Drava Statistical Region": "Podravska",
    "Central Slovenia Statistical Region": "Osrednjeslovenska",
    "Mura Statistical Region": "Pomurska",
    "Coastal–Karst Statistical Region": "Obalno-kraška",
    "Littoral–Inner Carniola Statistical Region": "Primorsko-notranjska"
},
    "SK": {
    "Prešov Region": "Prešovský kraj",
    "Žilina Region": "Žilinský kraj",
    "Nitra Region": "Nitriansky kraj",
    "Košice Region": "Košický kraj",
    "Banská Bystrica Region": "Banskobystrický kraj",
    "Trenčín Region": "Trenčiansky kraj",
    "Trnava Region": "Trnavský kraj",
    "Bratislava Region": "Bratislavský kraj"
},
    "CY": {
    "Lefkoşa District": "Nicosia",
    "Nicosia District": "Nicosia",
    "Limassol District": "Limassol",
    "Paphos District": "Paphos",
    "Famagusta District": "Famagusta",
    "Kyrenia District": "Kerynia",
    "Larnaca District": "Larnaca"
},
    "MT": {
    "Central Region": "Malta",
    "Southern Region": "Malta",
    "Northern Region": "Malta",
    "South Eastern Region": "Malta",
    "Gozo": "Gozo and Comino/Għawdex u Kemmuna", # the smaller one
},
    "EE": {
    "Harju County": "Põhja-Eesti",

    "Ida-Viru County": "Kirde-Eesti",
    "Lääne-Viru County": "Kirde-Eesti",

    "Pärnu County": "Lääne-Eesti",
    "Saare County": "Lääne-Eesti",
    "Hiiu County": "Lääne-Eesti",
    "Lääne County": "Lääne-Eesti",

    "Jõgeva County": "Kesk-Eesti",
    "Rapla County": "Kesk-Eesti",
    "Järva County": "Kesk-Eesti",

    "Tartu County": "Lõuna-Eesti",
    "Võru County": "Lõuna-Eesti",
    "Valga County": "Lõuna-Eesti",
    "Põlva County": "Lõuna-Eesti",
    "Viljandi County": "Lõuna-Eesti"
},
   # "EE": {},
}

# =========================================================
# HELPERS
# =========================================================
def format_int(x):
    if pd.isna(x):
        return "-"
    return f"{int(round(x)):,}"


def get_country_label(country_code):
    return COUNTRY_NAME_MAP.get(country_code, country_code)


def load_data(path):
    df = pd.read_csv(path)

    if "Unnamed: 0" in df.columns:
        df = df.drop(columns=["Unnamed: 0"])

    expected_cols = [
        "category",
        "indicator_name",
        "location_name",
        "gender",
        "age_min",
        "age_max",
        "estimate_dau",
        "estimate_mau_lower_bound",
        "estimate_mau_upper_bound",
        "month",
        "month_name",
        "year",
        "country_code",
    ]

    missing = [c for c in expected_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    numeric_cols = [
        "age_min",
        "age_max",
        "estimate_dau",
        "estimate_mau_lower_bound",
        "estimate_mau_upper_bound",
        "month",
        "year",
    ]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    text_cols = [
        "category",
        "indicator_name",
        "location_name",
        "gender",
        "month_name",
        "country_code",
    ]
    for col in text_cols:
        df[col] = df[col].astype(str).str.strip()

    df["country_code"] = df["country_code"].str.upper()

    # Apply region-name fixes to dataset
    for country_code, fix_map in REGION_NAME_FIXES.items():
        mask = df["country_code"] == country_code
        if mask.any() and fix_map:
            df.loc[mask, "location_name"] = df.loc[mask, "location_name"].replace(fix_map)

    df["country_name"] = df["country_code"].map(COUNTRY_NAME_MAP).fillna(df["country_code"])

    return df


@st.cache_data
def load_europe_geojson():
    world = gpd.read_file(
        "https://gisco-services.ec.europa.eu/distribution/v2/countries/geojson/CNTR_RG_03M_2024_4326.geojson"
    )
    eu_map = world[world["CNTR_ID"].isin(EU_COUNTRY_CODES)].copy()
    
    eu_map = eu_map.to_crs(4326)
    europe_bbox = box(-25, 34, 45, 72)
    eu_map = gpd.clip(eu_map, europe_bbox)
    
    return json.loads(eu_map.to_json())


    
    

@st.cache_data
@st.cache_data

def load_country_region_geojson(country_code):
    geojson_path = REGION_GEOJSON_DIR / f"{country_code}.geojson"

    if not geojson_path.exists():
        return None, None

    gdf = gpd.read_file(geojson_path)

    region_col = "NAME_LATN"

    if region_col not in gdf.columns:
        st.error(
            f"{country_code}.geojson does not contain '{region_col}'. "
            f"Available columns: {list(gdf.columns)}"
        )
        return None, None

    gdf[region_col] = gdf[region_col].astype(str).str.strip()

    fixes = REGION_NAME_FIXES.get(country_code, {})
    if fixes:
        for original_name, cleaned_name in fixes.items():
            gdf[region_col] = gdf[region_col].str.replace(
                original_name, cleaned_name, regex=False
            )

    return json.loads(gdf.to_json()), "properties.NAME_LATN"



def build_europe_map(filtered_df, europe_geojson, metric):
    country_df = (
        filtered_df.groupby(["country_code", "country_name"], as_index=False)[
            ["estimate_dau", "estimate_mau_lower_bound", "estimate_mau_upper_bound"]
        ]
        .sum()
    )

    fig = px.choropleth(
        country_df,
        geojson=europe_geojson,
        locations="country_code",
        featureidkey="properties.CNTR_ID",
        color=metric,
        hover_name="country_name",
        hover_data={
            "country_code": True,
            "estimate_dau": ":,.0f",
            "estimate_mau_lower_bound": ":,.0f",
            "estimate_mau_upper_bound": ":,.0f",
        },
        color_continuous_scale="Reds",
    )

    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(
        title="Europe overview — click a country",
        margin=dict(l=0, r=0, t=60, b=0),
        height=700,
    )

    return fig, country_df


def build_region_map(country_df, country_geojson, feature_path, metric, title):
    region_df = (
        country_df.groupby("location_name", as_index=False)[
            ["estimate_dau", "estimate_mau_lower_bound", "estimate_mau_upper_bound"]
        ]
        .sum()
    )

    fig = px.choropleth(
        region_df,
        geojson=country_geojson,
        locations="location_name",
        featureidkey=feature_path,
        color=metric,
        hover_name="location_name",
        hover_data={
            "estimate_dau": ":,.0f",
            "estimate_mau_lower_bound": ":,.0f",
            "estimate_mau_upper_bound": ":,.0f",
        },
        color_continuous_scale="Reds",
    )

    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(
        title=title,
        margin=dict(l=0, r=0, t=60, b=0),
        height=750,
    )

    return fig, region_df


# =========================================================
# APP
# =========================================================
st.title("EU Regional Demographic Estimates")
st.caption("Click a country on Europe to open its regional map.")

try:
    df = load_data(DATA_PATH)
    europe_geojson = load_europe_geojson()
except Exception as e:
    st.error("Error while loading data or Europe map.")
    st.exception(e)
    st.stop()

if "selected_country_code" not in st.session_state:
    st.session_state.selected_country_code = None

# =========================================================
# SIDEBAR FILTERS
# =========================================================
st.sidebar.header("Filters")

year_options = sorted(df["year"].dropna().astype(int).unique().tolist())
selected_year = st.sidebar.selectbox("Year", year_options, index=len(year_options) - 1)

year_df = df[df["year"] == selected_year].copy()

month_df = year_df[["month", "month_name"]].drop_duplicates().sort_values("month")
month_options = month_df["month"].tolist()
month_name_map = dict(zip(month_df["month"], month_df["month_name"]))

selected_month = st.sidebar.selectbox(
    "Month",
    month_options,
    format_func=lambda m: f"{int(m)} - {month_name_map.get(m, str(m))}"
)

time_df = year_df[year_df["month"] == selected_month].copy()

category_options = sorted(time_df["category"].dropna().unique().tolist())
selected_category = st.sidebar.selectbox("Category", category_options)

category_df = time_df[time_df["category"] == selected_category].copy()

indicator_options = sorted(category_df["indicator_name"].dropna().unique().tolist())
selected_indicator = st.sidebar.selectbox("Indicator", indicator_options)

indicator_df = category_df[category_df["indicator_name"] == selected_indicator].copy()

#gender_options = sorted(indicator_df["gender"].dropna().unique().tolist())
#selected_gender = st.sidebar.selectbox("Gender", gender_options)

age_min_val = int(time_df["age_min"].min())
age_max_val = int(time_df["age_max"].max())

selected_age = st.sidebar.slider(
    "Age range",
    min_value=age_min_val,
    max_value=age_max_val,
    value=(age_min_val, age_max_val),
)

metric_label_map = {
    "estimate_dau": "Estimate DAU",
    "estimate_mau_lower_bound": "Lower bound",
    "estimate_mau_upper_bound": "Upper bound",
}
selected_metric = st.sidebar.radio(
    "Map metric",
    options=list(metric_label_map.keys()),
    format_func=lambda x: metric_label_map[x],
)

filtered_df = time_df[
    (time_df["category"] == selected_category)
    & (time_df["indicator_name"] == selected_indicator)
   # & (time_df["gender"] == selected_gender)
    & (time_df["age_min"] >= selected_age[0])
    & (time_df["age_max"] <= selected_age[1])
    & (time_df["country_code"].isin(EU_COUNTRY_CODES))
].copy()

selected_month_name = month_name_map.get(selected_month, str(selected_month))
st.subheader(f"{selected_category} → {selected_indicator} | {selected_month_name} {selected_year}")

if filtered_df.empty:
    st.warning("No rows match the selected filters.")
    st.stop()

# =========================================================
# VIEW SWITCHING
# =========================================================
if st.session_state.selected_country_code is None:
    # -----------------------------------------
    # EUROPE VIEW
    # -----------------------------------------
    europe_fig, country_summary_df = build_europe_map(
        filtered_df, europe_geojson, selected_metric
    )

    event = st.plotly_chart(
        europe_fig,
        use_container_width=True,
        key="eu_country_map",
        on_select="rerun",
        selection_mode="points",
    )

    if event and event.selection and event.selection.points:
        selected_point = event.selection.points[0]
        point_index = selected_point["point_index"]
        clicked_country_code = country_summary_df.iloc[point_index]["country_code"]
        st.session_state.selected_country_code = clicked_country_code
        st.rerun()

else:
    # -----------------------------------------
    # COUNTRY VIEW
    # -----------------------------------------
    active_country_code = st.session_state.selected_country_code
    active_country_name = get_country_label(active_country_code)

    country_filtered_df = filtered_df[
        filtered_df["country_code"] == active_country_code
    ].copy()

    top_left, top_right = st.columns([1, 5])
    with top_left:
        if st.button("← Back to Europe"):
            st.session_state.selected_country_code = None
            st.rerun()

    if country_filtered_df.empty:
        st.warning("No rows for the selected country under the current filters.")
        st.stop()

    st.markdown(f"## {active_country_name} regional view")

    country_geojson, feature_path = load_country_region_geojson(active_country_code)

    if country_geojson is None or feature_path is None:
        st.error(
            f"No regional GeoJSON configured for {active_country_name} ({active_country_code}). "
            f"Expected file: {REGION_GEOJSON_DIR / f'{active_country_code}.geojson'}"
        )
        st.stop()

    region_fig, region_df = build_region_map(
        country_filtered_df,
        country_geojson,
        feature_path,
        selected_metric,
        title=f"{active_country_name}: estimated audience by region",
    )

    st.plotly_chart(region_fig, use_container_width=True)

    total_dau = country_filtered_df["estimate_dau"].sum()
    total_lower = country_filtered_df["estimate_mau_lower_bound"].sum()
    total_upper = country_filtered_df["estimate_mau_upper_bound"].sum()

    c1, c2, c3 = st.columns(3)
    c1.metric("Estimate DAU", format_int(total_dau))
    c2.metric("Lower bound", format_int(total_lower))
    c3.metric("Upper bound", format_int(total_upper))

    st.markdown("### Regional values")
    st.dataframe(
        region_df.sort_values(selected_metric, ascending=False).reset_index(drop=True),
        use_container_width=True,
    )
