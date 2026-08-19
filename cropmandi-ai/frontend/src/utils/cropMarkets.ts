/**
 * Crop to Available Mandi Markets Mapping
 * Restricts markets strictly to verified APMC yards with rich historical and official records.
 */

export const CROP_MARKETS_MAP: Record<string, string[]> = {
  'Ajwan': [
    'Kurnool APMC',
  ],
  'Tomato': [
    'Madanapalle APMC',
    'Kalikiri APMC',
    'Palamaner APMC',
    'Punganur APMC',
    'Ananthapur APMC',
    'Pattikonda APMC',
    'Mulakalacheruvu APMC',
    'Valmikipuram APMC',
    'Somala APMC',
    'Kuppam APMC',
  ],
  'Onion': [
    'Kurnool APMC',
    'Pattikonda APMC',
    'Adoni APMC',
    'Yerraguntla APMC',
    'Rajahmundry APMC',
    'Tenali APMC',
  ],
  'Potato': [
    'Palamaner APMC',
    'Kurnool APMC',
    'Rajahmundry APMC',
    'Tenali APMC',
  ],
  'Lemon': [
    'Tenali APMC',
    'Gopalapuram APMC',
    'Chintalapudi APMC',
    'Eluru APMC',
    'Denduluru APMC',
  ],
  'Brinjal': [
    'Palamaner APMC',
  ],
  'Cabbage': [
    'Palamaner APMC',
  ],
  'Cauliflower': [
    'Palamaner APMC',
  ],
  'Green Chilli': [
    'Palamaner APMC',
    'Parchur APMC',
  ],
  'Cluster Beans': [
    'Palamaner APMC',
  ],
  'Ridgeguard': [
    'Palamaner APMC',
  ],
  'Paddy': [
    'Banaganapalli APMC',
    'Atmakur (Nandyal District) APMC',
    'Rajahmundry APMC',
    'Tiruvuru APMC',
    'Tanuku APMC',
    'Sampara (Kakinada Rural) APMC',
  ],
  'Maize': [
    'Kurnool APMC',
    'Atmakur (Nandyal District) APMC',
    'Tiruvuru APMC',
    'Nandyal APMC',
    'Chintalapudi APMC',
  ],
  'Jowar': [
    'Banaganapalli APMC',
    'Alur APMC',
  ],
  'Groundnut': [
    'Kurnool APMC',
    'Adoni APMC',
    'Kadapa APMC',
    'Yemmiganuru APMC',
  ],
  'Castor Seed': [
    'Kurnool APMC',
    'Adoni APMC',
    'Yemmiganuru APMC',
  ],
  'Sunflower': [
    'Kurnool APMC',
    'Adoni APMC',
  ],
  'Bengal Gram': [
    'Banaganapalli APMC',
    'Kurnool APMC',
  ],
  'Red Gram': [
    'Kurnool APMC',
    'Dhone APMC',
  ],
  'Black Gram': [
    'Kurnool APMC',
  ],
  'Dry Chillies': [
    'Guntur APMC',
    'Kurnool APMC',
    'Pidugurala (Palnadu) APMC',
    'Tiruvuru APMC',
  ],
};

// Aliases for compatibility
CROP_MARKETS_MAP['Ridge Gourd'] = CROP_MARKETS_MAP['Ridgeguard'];

export const MARKET_DISTRICT_MAP: Record<string, string> = {
  'Kurnool APMC': 'Kurnool',
  'Madanapalle APMC': 'Annamayya',
  'Madanapalli APMC': 'Annamayya',
  'Kalikiri APMC': 'Annamayya',
  'Palamaner APMC': 'Chittoor',
  'Punganur APMC': 'Chittoor',
  'Ananthapur APMC': 'Anantapur',
  'Anantapur APMC': 'Anantapur',
  'Pattikonda APMC': 'Kurnool',
  'Mulakalacheruvu APMC': 'Annamayya',
  'Valmikipuram APMC': 'Annamayya',
  'Somala APMC': 'Chittoor',
  'Kuppam APMC': 'Chittoor',
  'Adoni APMC': 'Kurnool',
  'Yerraguntla APMC': 'YSR Kadapa',
  'Rajahmundry APMC': 'East Godavari',
  'Tenali APMC': 'Guntur',
  'Gopalapuram APMC': 'East Godavari',
  'Chintalapudi APMC': 'Eluru',
  'Eluru APMC': 'Eluru',
  'Denduluru APMC': 'Eluru',
  'Parchur APMC': 'Bapatla',
  'Banaganapalli APMC': 'Nandyal',
  'Atmakur (Nandyal District) APMC': 'Nandyal',
  'Tiruvuru APMC': 'NTR',
  'Tanuku APMC': 'West Godavari',
  'Sampara (Kakinada Rural) APMC': 'Kakinada',
  'Nandyal APMC': 'Nandyal',
  'Alur APMC': 'Kurnool',
  'Kadapa APMC': 'YSR Kadapa',
  'Yemmiganuru APMC': 'Kurnool',
  'Dhone APMC': 'Nandyal',
  'Guntur APMC': 'Guntur',
  'Pidugurala (Palnadu) APMC': 'Palnadu',
  'Piduguralla (Palnadu) APMC': 'Palnadu',
};

export const SUPPORTED_CROPS = Object.keys(CROP_MARKETS_MAP).filter(c => c !== 'Ridge Gourd');

/**
 * Returns available markets for a given commodity name, handling case & alias variations.
 */
export function getMarketsForCrop(cropName: string): string[] {
  if (!cropName) {
    return CROP_MARKETS_MAP['Tomato'];
  }
  const clean = cropName.trim().toLowerCase();

  // Exact match first
  for (const [key, markets] of Object.entries(CROP_MARKETS_MAP)) {
    if (key.toLowerCase() === clean) {
      return markets;
    }
  }

  // Alias checks
  if (clean.includes('ajw') || clean.includes('omam')) return CROP_MARKETS_MAP['Ajwan'];
  if (clean.includes('tomat')) return CROP_MARKETS_MAP['Tomato'];
  if (clean.includes('onion') || clean.includes('ulli')) return CROP_MARKETS_MAP['Onion'];
  if (clean.includes('potat') || clean.includes('alu') || clean.includes('bangala')) return CROP_MARKETS_MAP['Potato'];
  if (clean.includes('lemon') || clean.includes('nimma') || clean.includes('lime')) return CROP_MARKETS_MAP['Lemon'];
  if (clean.includes('brinjal') || clean.includes('eggplant') || clean.includes('vankaya')) return CROP_MARKETS_MAP['Brinjal'];
  if (clean.includes('cabbage')) return CROP_MARKETS_MAP['Cabbage'];
  if (clean.includes('cauli')) return CROP_MARKETS_MAP['Cauliflower'];
  if (clean.includes('green ch') || clean.includes('chilli') || clean.includes('mirchi')) return CROP_MARKETS_MAP['Green Chilli'];
  if (clean.includes('cluster') || clean.includes('guar') || clean.includes('goruchikkudu')) return CROP_MARKETS_MAP['Cluster Beans'];
  if (clean.includes('ridge') || clean.includes('tori') || clean.includes('beerakaya')) return CROP_MARKETS_MAP['Ridgeguard'];
  if (clean.includes('paddy') || clean.includes('rice') || clean.includes('vari')) return CROP_MARKETS_MAP['Paddy'];
  if (clean.includes('maize') || clean.includes('corn') || clean.includes('mokkajonna')) return CROP_MARKETS_MAP['Maize'];
  if (clean.includes('jowar') || clean.includes('sorghum') || clean.includes('jonna')) return CROP_MARKETS_MAP['Jowar'];
  if (clean.includes('groundnut') || clean.includes('peanut') || clean.includes('verusanaga')) return CROP_MARKETS_MAP['Groundnut'];
  if (clean.includes('castor') || clean.includes('amudamu')) return CROP_MARKETS_MAP['Castor Seed'];
  if (clean.includes('sunflower') || clean.includes('poddu')) return CROP_MARKETS_MAP['Sunflower'];
  if (clean.includes('bengal') || clean.includes('chana') || clean.includes('senaga')) return CROP_MARKETS_MAP['Bengal Gram'];
  if (clean.includes('red gram') || clean.includes('arhar') || clean.includes('tur') || clean.includes('kandulu')) return CROP_MARKETS_MAP['Red Gram'];
  if (clean.includes('black gram') || clean.includes('urad') || clean.includes('minumulu')) return CROP_MARKETS_MAP['Black Gram'];
  if (clean.includes('dry chill') || clean.includes('mirchi')) return CROP_MARKETS_MAP['Dry Chillies'];

  return CROP_MARKETS_MAP['Tomato'];
}

/**
 * Returns the mapped Andhra Pradesh district for a given market name.
 */
export function getDistrictForMarket(marketName: string): string {
  if (!marketName) return 'Andhra Pradesh';
  return MARKET_DISTRICT_MAP[marketName] || 'Andhra Pradesh';
}
