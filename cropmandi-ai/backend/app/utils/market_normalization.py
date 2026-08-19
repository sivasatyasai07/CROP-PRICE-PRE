import json
import os
from typing import Tuple, Dict, Any, Optional

DEFAULT_MARKET_ALIASES: Dict[str, Any] = {
    "Kurnool APMC": {"aliases": ["kurnool", "kurnool apmc", "kurnool mandi", "kurnool market", "కర్నూలు"], "district": "Kurnool", "state": "Andhra Pradesh", "latitude": 15.8281, "longitude": 78.0373},
    "Madanapalle APMC": {"aliases": ["madanapalle", "madanapalli", "madanapalle apmc", "madanapalli apmc", "మదనపల్లె"], "district": "Annamayya", "state": "Andhra Pradesh", "latitude": 13.5500, "longitude": 78.5000},
    "Madanapalli APMC": {"aliases": ["madanapalli", "madanapalle", "madanapalli apmc", "madanapalle apmc", "మదనపల్లె"], "district": "Annamayya", "state": "Andhra Pradesh", "latitude": 13.5500, "longitude": 78.5000},
    "Kalikiri APMC": {"aliases": ["kalikiri", "kalikiri apmc", "కలికిరి"], "district": "Annamayya", "state": "Andhra Pradesh", "latitude": 13.6833, "longitude": 78.7833},
    "Palamaner APMC": {"aliases": ["palamaner", "palamaneru", "palamaner apmc", "పలమనేరు"], "district": "Chittoor", "state": "Andhra Pradesh", "latitude": 13.2000, "longitude": 78.7500},
    "Punganur APMC": {"aliases": ["punganur", "pungunur", "punganur apmc", "పుంగనూరు"], "district": "Chittoor", "state": "Andhra Pradesh", "latitude": 13.3667, "longitude": 78.5833},
    "Ananthapur APMC": {"aliases": ["ananthapur", "anantapur", "ananthapur apmc", "anantapur apmc", "అనంతపురం"], "district": "Anantapur", "state": "Andhra Pradesh", "latitude": 14.6819, "longitude": 77.6006},
    "Anantapur APMC": {"aliases": ["anantapur", "ananthapur", "anantapur apmc", "ananthapur apmc", "అనంతపురం"], "district": "Anantapur", "state": "Andhra Pradesh", "latitude": 14.6819, "longitude": 77.6006},
    "Pattikonda APMC": {"aliases": ["pattikonda", "pattikonda apmc", "పత్తికొండ"], "district": "Kurnool", "state": "Andhra Pradesh", "latitude": 15.4000, "longitude": 77.5000},
    "Mulakalacheruvu APMC": {"aliases": ["mulakalacheruvu", "mulakalcheruvu", "mulakalacheruvu apmc", "ముళకలచెరువు"], "district": "Annamayya", "state": "Andhra Pradesh", "latitude": 13.7833, "longitude": 78.3333},
    "Valmikipuram APMC": {"aliases": ["valmikipuram", "vayalpadoor", "valmikipuram apmc", "వాల్మీకిపురం"], "district": "Annamayya", "state": "Andhra Pradesh", "latitude": 13.6500, "longitude": 78.6333},
    "Somala APMC": {"aliases": ["somala", "somala apmc", "సోమల"], "district": "Chittoor", "state": "Andhra Pradesh", "latitude": 13.4333, "longitude": 78.8500},
    "Kuppam APMC": {"aliases": ["kuppam", "kuppam apmc", "కుప్పం"], "district": "Chittoor", "state": "Andhra Pradesh", "latitude": 12.7500, "longitude": 78.3667},
    "Adoni APMC": {"aliases": ["adoni", "adoni apmc", "ఆదోని"], "district": "Kurnool", "state": "Andhra Pradesh", "latitude": 15.6322, "longitude": 77.2728},
    "Yerraguntla APMC": {"aliases": ["yerraguntla", "yerraguntala", "yerraguntla apmc", "ఎర్రగుంట్ల"], "district": "YSR Kadapa", "state": "Andhra Pradesh", "latitude": 14.6333, "longitude": 78.5333},
    "Rajahmundry APMC": {"aliases": ["rajahmundry", "rajahmundary", "rajamahendravaram", "rajahmundry apmc", "రాజమండ్రి"], "district": "East Godavari", "state": "Andhra Pradesh", "latitude": 17.0005, "longitude": 81.8040},
    "Tenali APMC": {"aliases": ["tenali", "tenalli", "tenali apmc", "తెనాలి"], "district": "Guntur", "state": "Andhra Pradesh", "latitude": 16.2437, "longitude": 80.6400},
    "Gopalapuram APMC": {"aliases": ["gopalapuram", "gopalapuram apmc", "గోపాలపురం"], "district": "East Godavari", "state": "Andhra Pradesh", "latitude": 17.1000, "longitude": 81.5333},
    "Chintalapudi APMC": {"aliases": ["chintalapudi", "chintalapudi apmc", "చింతలపూడి"], "district": "Eluru", "state": "Andhra Pradesh", "latitude": 17.0667, "longitude": 80.9833},
    "Eluru APMC": {"aliases": ["eluru", "eluru apmc", "ఏలూరు"], "district": "Eluru", "state": "Andhra Pradesh", "latitude": 16.7107, "longitude": 81.0952},
    "Denduluru APMC": {"aliases": ["denduluru", "denduluru apmc", "దెందులూరు"], "district": "Eluru", "state": "Andhra Pradesh", "latitude": 16.7500, "longitude": 81.1667},
    "Parchur APMC": {"aliases": ["parchur", "parchur apmc", "పర్చూరు"], "district": "Bapatla", "state": "Andhra Pradesh", "latitude": 15.9667, "longitude": 80.2667},
    "Banaganapalli APMC": {"aliases": ["banaganapalli", "banaganapalle", "banaganapalli apmc", "బనగానపల్లె"], "district": "Nandyal", "state": "Andhra Pradesh", "latitude": 15.3167, "longitude": 78.2333},
    "Atmakur (Nandyal District) APMC": {"aliases": ["atmakur", "atmakur nandyal", "atmakur apmc", "atmakur (nandyal district) apmc", "ఆత్మకూరు"], "district": "Nandyal", "state": "Andhra Pradesh", "latitude": 15.8833, "longitude": 78.5833},
    "Tiruvuru APMC": {"aliases": ["tiruvuru", "tiruvur", "tiruvuru apmc", "తిరువూరు"], "district": "NTR", "state": "Andhra Pradesh", "latitude": 17.1167, "longitude": 80.6167},
    "Tanuku APMC": {"aliases": ["tanuku", "tanuku apmc", "తణుకు"], "district": "West Godavari", "state": "Andhra Pradesh", "latitude": 16.7547, "longitude": 81.6811},
    "Sampara (Kakinada Rural) APMC": {"aliases": ["sampara", "sampara kakinada", "sampara apmc", "sampara (kakinada rural) apmc", "సాంపర"], "district": "Kakinada", "state": "Andhra Pradesh", "latitude": 16.9833, "longitude": 82.2333},
    "Nandyal APMC": {"aliases": ["nandyal", "nandyala", "nandyal apmc", "నంద్యాల"], "district": "Nandyal", "state": "Andhra Pradesh", "latitude": 15.4886, "longitude": 78.4832},
    "Alur APMC": {"aliases": ["alur", "aluru", "alur apmc", "ఆలూరు"], "district": "Kurnool", "state": "Andhra Pradesh", "latitude": 15.3333, "longitude": 77.2333},
    "Kadapa APMC": {"aliases": ["kadapa", "cuddapah", "kadapa apmc", "కడప"], "district": "YSR Kadapa", "state": "Andhra Pradesh", "latitude": 14.4673, "longitude": 78.8242},
    "Yemmiganuru APMC": {"aliases": ["yemmiganuru", "yemmiganur", "yemmiganuru apmc", "ఎమ్మిగనూరు"], "district": "Kurnool", "state": "Andhra Pradesh", "latitude": 15.7333, "longitude": 77.4833},
    "Dhone APMC": {"aliases": ["dhone", "dronachalam", "dhone apmc", "డోన్"], "district": "Nandyal", "state": "Andhra Pradesh", "latitude": 15.4167, "longitude": 77.8667},
    "Guntur APMC": {"aliases": ["guntur", "guntur apmc", "గుంటూరు"], "district": "Guntur", "state": "Andhra Pradesh", "latitude": 16.3067, "longitude": 80.4365},
    "Pidugurala (Palnadu) APMC": {"aliases": ["pidugurala", "piduguralla", "pidugurala apmc", "piduguralla apmc", "pidugurala (palnadu) apmc", "piduguralla (palnadu) apmc", "పిడుగురాళ్ల"], "district": "Palnadu", "state": "Andhra Pradesh", "latitude": 16.4833, "longitude": 79.8833},
    "Piduguralla (Palnadu) APMC": {"aliases": ["piduguralla", "pidugurala", "pidugurala apmc", "piduguralla apmc", "piduguralla (palnadu) apmc", "పిడుగురాళ్ల"], "district": "Palnadu", "state": "Andhra Pradesh", "latitude": 16.4833, "longitude": 79.8833},
}

DEFAULT_COMMODITY_ALIASES: Dict[str, str] = {
    "ajwan": "Ajwan",
    "ajwain": "Ajwan",
    "omam": "Ajwan",
    "వాము": "Ajwan",
    "tomato": "Tomato",
    "tamatar": "Tomato",
    "టమోటా": "Tomato",
    "onion": "Onion",
    "pyaz": "Onion",
    "ulli": "Onion",
    "ఉల్లిపాయ": "Onion",
    "potato": "Potato",
    "alu": "Potato",
    "aaloo": "Potato",
    "బంగాళాదుంప": "Potato",
    "lemon": "Lemon",
    "nimbu": "Lemon",
    "nimma": "Lemon",
    "నిమ్మకాయ": "Lemon",
    "brinjal": "Brinjal",
    "eggplant": "Brinjal",
    "baingan": "Brinjal",
    "వంకాయ": "Brinjal",
    "cabbage": "Cabbage",
    "patta gobhi": "Cabbage",
    "క్యాబేజీ": "Cabbage",
    "cauliflower": "Cauliflower",
    "phool gobhi": "Cauliflower",
    "కాలీఫ్లవర్": "Cauliflower",
    "green chilli": "Green Chilli",
    "green chili": "Green Chilli",
    "hari mirch": "Green Chilli",
    "పచ్చిమిర్చి": "Green Chilli",
    "cluster beans": "Cluster Beans",
    "cluster bean": "Cluster Beans",
    "gawar phali": "Cluster Beans",
    "గోరుచిక్కుడు": "Cluster Beans",
    "ridgeguard": "Ridgeguard",
    "ridge guard": "Ridgeguard",
    "ridge gourd": "Ridgeguard",
    "ridgeguard(tori)": "Ridgeguard",
    "torai": "Ridgeguard",
    "బీరకాయ": "Ridgeguard",
    "paddy": "Paddy",
    "dhan": "Paddy",
    "rice": "Paddy",
    "వరి": "Paddy",
    "maize": "Maize",
    "makka": "Maize",
    "corn": "Maize",
    "మొక్కజొన్న": "Maize",
    "jowar": "Jowar",
    "jowari": "Jowar",
    "sorghum": "Jowar",
    "జొన్నలు": "Jowar",
    "groundnut": "Groundnut",
    "moongfali": "Groundnut",
    "peanut": "Groundnut",
    "వేరుశెనగ": "Groundnut",
    "castor seed": "Castor Seed",
    "castor": "Castor Seed",
    "arandi": "Castor Seed",
    "ఆముదాలు": "Castor Seed",
    "sunflower": "Sunflower",
    "surajmukhi": "Sunflower",
    "పొద్దుతిరుగుడు": "Sunflower",
    "bengal gram": "Bengal Gram",
    "chana": "Bengal Gram",
    "chickpea": "Bengal Gram",
    "శనగలు": "Bengal Gram",
    "red gram": "Red Gram",
    "arhar": "Red Gram",
    "tur": "Red Gram",
    "toor": "Red Gram",
    "కందులు": "Red Gram",
    "black gram": "Black Gram",
    "urad": "Black Gram",
    "మినుములు": "Black Gram",
    "dry chillies": "Dry Chillies",
    "dry chilli": "Dry Chillies",
    "red chilli": "Dry Chillies",
    "sukhi mirch": "Dry Chillies",
    "ఎండుమిర్చి": "Dry Chillies",
    "turmeric": "Turmeric",
    "haldi": "Turmeric",
    "పసుపు": "Turmeric",
}

class MarketNormalizer:
    def __init__(self):
        self.markets_config = DEFAULT_MARKET_ALIASES
        self.commodity_aliases = DEFAULT_COMMODITY_ALIASES
        self.alias_to_canonical = {}

        for canonical, info in self.markets_config.items():
            for alias in info.get("aliases", []):
                self.alias_to_canonical[alias.strip().lower()] = canonical
            self.alias_to_canonical[canonical.strip().lower()] = canonical

    def normalize_market(self, raw_market: str) -> Tuple[str, Optional[Dict[str, Any]]]:
        if not raw_market:
            return "Unknown Market", None
        
        cleaned = raw_market.strip()
        cleaned_lower = cleaned.lower()

        if cleaned_lower in self.alias_to_canonical:
            canonical = self.alias_to_canonical[cleaned_lower]
            return canonical, self.markets_config.get(canonical)

        # Partial matching check
        for canonical, info in self.markets_config.items():
            c_low = canonical.lower()
            if c_low in cleaned_lower or cleaned_lower in c_low:
                return canonical, info
            for alias in info.get("aliases", []):
                if alias.lower() in cleaned_lower or cleaned_lower in alias.lower():
                    return canonical, info

        return cleaned, None

    def normalize_district(self, raw_district: str) -> str:
        if not raw_district:
            return "Unknown"
        return raw_district.strip()

    def normalize_commodity(self, raw_commodity: str) -> str:
        if not raw_commodity:
            return "Unknown"
        cleaned = raw_commodity.strip().lower()
        if cleaned in self.commodity_aliases:
            return self.commodity_aliases[cleaned]
        for k, v in self.commodity_aliases.items():
            if k in cleaned or cleaned in k:
                return v
        return raw_commodity.strip().capitalize()

normalizer = MarketNormalizer()

def normalize_market_name(raw_market: str) -> str:
    res, _ = normalizer.normalize_market(raw_market)
    return res

def normalize_commodity_name(raw_commodity: str) -> str:
    return normalizer.normalize_commodity(raw_commodity)
