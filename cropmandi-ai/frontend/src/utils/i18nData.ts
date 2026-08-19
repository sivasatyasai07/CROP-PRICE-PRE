import type { Language } from '../i18n/translations';

// Multilingual mapping for all configured commodities
const commodityTranslations: Record<string, Record<Language, string>> = {
  'Ajwan': {
    te: 'వాము (Ajwan)',
    hi: 'अजवाइन (Ajwan)',
    ta: 'ஓமம் (Ajwan)',
    ml: 'അയമോദകം (Ajwan)',
    en: 'Ajwan'
  },
  'Tomato': {
    te: 'టమోటా (Tomato)',
    hi: 'टमाटर (Tomato)',
    ta: 'தக்காளி (Tomato)',
    ml: 'തക്കാളി (Tomato)',
    en: 'Tomato'
  },
  'Onion': {
    te: 'ఉల్లిపాయ (Onion)',
    hi: 'प्याज (Onion)',
    ta: 'வெங்காயம் (Onion)',
    ml: 'സവോള (Onion)',
    en: 'Onion'
  },
  'Potato': {
    te: 'బంగాళాదుంప (Potato)',
    hi: 'आलू (Potato)',
    ta: 'உருளைக்கிழங்கு (Potato)',
    ml: 'ഉരുളക്കിഴങ്ങ് (Potato)',
    en: 'Potato'
  },
  'Lemon': {
    te: 'నిమ్మకాయ (Lemon)',
    hi: 'नींबू (Lemon)',
    ta: 'எலுமிச்சை (Lemon)',
    ml: 'നാരങ്ങ (Lemon)',
    en: 'Lemon'
  },
  'Brinjal': {
    te: 'వంకాయ (Brinjal)',
    hi: 'बैंगन (Brinjal)',
    ta: 'கத்தரிக்காய் (Brinjal)',
    ml: 'വഴുതനങ്ങ (Brinjal)',
    en: 'Brinjal'
  },
  'Cabbage': {
    te: 'క్యాబేజీ (Cabbage)',
    hi: 'पत्तागोभी (Cabbage)',
    ta: 'முட்டைக்கோஸ் (Cabbage)',
    ml: 'കാബേജ് (Cabbage)',
    en: 'Cabbage'
  },
  'Cauliflower': {
    te: 'కాలీఫ్లవర్ (Cauliflower)',
    hi: 'फूलगोभी (Cauliflower)',
    ta: 'காளிபிளவர் (Cauliflower)',
    ml: 'കോളീഫ്ലവർ (Cauliflower)',
    en: 'Cauliflower'
  },
  'Green Chilli': {
    te: 'పచ్చిమిర్చి (Green Chilli)',
    hi: 'हरी मिर्च (Green Chilli)',
    ta: 'பச்சை மிளகாய் (Green Chilli)',
    ml: 'പച്ചമുളക് (Green Chilli)',
    en: 'Green Chilli'
  },
  'Cluster Beans': {
    te: 'గోరుచిక్కుడు (Cluster Beans)',
    hi: 'ग्वार फली (Cluster Beans)',
    ta: 'கொத்தவரங்காய் (Cluster Beans)',
    ml: 'അമരപ്പയർ (Cluster Beans)',
    en: 'Cluster Beans'
  },
  'Ridgeguard': {
    te: 'బీరకాయ (Ridgeguard)',
    hi: 'तोरई (Ridgeguard)',
    ta: 'பீர்க்கங்காய் (Ridgeguard)',
    ml: 'പീച്ചിങ്ങ (Ridgeguard)',
    en: 'Ridgeguard'
  },
  'Ridge Gourd': {
    te: 'బీరకాయ (Ridge Gourd)',
    hi: 'तोरई (Ridge Gourd)',
    ta: 'பீர்க்கங்காய் (Ridge Gourd)',
    ml: 'പീച്ചിങ്ങ (Ridge Gourd)',
    en: 'Ridge Gourd'
  },
  'Paddy': {
    te: 'వరి ధాన్యం (Paddy)',
    hi: 'धान (Paddy)',
    ta: 'நெல் (Paddy)',
    ml: 'നെല്ല് (Paddy)',
    en: 'Paddy'
  },
  'Maize': {
    te: 'మొక్కజొన్న (Maize)',
    hi: 'मक्का (Maize)',
    ta: 'சோளம் (Maize)',
    ml: 'ചോളം (Maize)',
    en: 'Maize'
  },
  'Jowar': {
    te: 'జొన్నలు (Jowar)',
    hi: 'ज्वार (Jowar)',
    ta: 'சோளம் (Jowar)',
    ml: 'യവം (Jowar)',
    en: 'Jowar'
  },
  'Groundnut': {
    te: 'వేరుశెనగ (Groundnut)',
    hi: 'मूंगफली (Groundnut)',
    ta: 'நிலக்கடலை (Groundnut)',
    ml: 'നിലക്കടല (Groundnut)',
    en: 'Groundnut'
  },
  'Castor Seed': {
    te: 'ఆముదాలు (Castor Seed)',
    hi: 'अरंडी (Castor Seed)',
    ta: 'ஆமணக்கு (Castor Seed)',
    ml: 'ആവണക്ക് (Castor Seed)',
    en: 'Castor Seed'
  },
  'Sunflower': {
    te: 'పొద్దుతిరుగుడు (Sunflower)',
    hi: 'सूरजमुखी (Sunflower)',
    ta: 'சூரியகாந்தி (Sunflower)',
    ml: 'സൂര്യകാന്തി (Sunflower)',
    en: 'Sunflower'
  },
  'Bengal Gram': {
    te: 'శనగలు (Bengal Gram)',
    hi: 'चना (Bengal Gram)',
    ta: 'கொண்டைக்கடலை (Bengal Gram)',
    ml: 'കടല (Bengal Gram)',
    en: 'Bengal Gram'
  },
  'Red Gram': {
    te: 'కందులు (Red Gram)',
    hi: 'अरहर (Red Gram)',
    ta: 'துவரை (Red Gram)',
    ml: 'തുവര (Red Gram)',
    en: 'Red Gram'
  },
  'Black Gram': {
    te: 'మినుములు (Black Gram)',
    hi: 'உறद (Black Gram)',
    ta: 'உளுந்து (Black Gram)',
    ml: 'ഉഴുന്ന് (Black Gram)',
    en: 'Black Gram'
  },
  'Dry Chillies': {
    te: 'ఎండుమిర్చి (Dry Chillies)',
    hi: 'सूखी मिर्च (Dry Chillies)',
    ta: 'காய்ந்த மிளகாய் (Dry Chillies)',
    ml: 'ഉണക്കമുളക് (Dry Chillies)',
    en: 'Dry Chillies'
  },
  'Turmeric': {
    te: 'పసుపు (Turmeric)',
    hi: 'हल्दी (Turmeric)',
    ta: 'மஞ்சள் (Turmeric)',
    ml: 'മഞ്ഞൾ (Turmeric)',
    en: 'Turmeric'
  }
};

// Multilingual mapping for all configured APMC Markets
const marketTranslations: Record<string, Record<Language, string>> = {
  'Kurnool APMC': {
    te: 'కర్నూలు APMC (Kurnool)',
    hi: 'कुरनूल मंडी (Kurnool)',
    ta: 'கர்நூல் மண்டி (Kurnool)',
    ml: 'കർനൂൾ മണ്ടി (Kurnool)',
    en: 'Kurnool APMC'
  },
  'Madanapalle APMC': {
    te: 'మదనపల్లె APMC (Madanapalle)',
    hi: 'मदनपल्ले मंडी (Madanapalle)',
    ta: 'மதனபள்ளி மண்டி (Madanapalle)',
    ml: 'മദനപ്പള്ളി മണ്ടി (Madanapalle)',
    en: 'Madanapalle APMC'
  },
  'Madanapalli APMC': {
    te: 'మదనపల్లె APMC (Madanapalli)',
    hi: 'मदनपल्ले मंडी (Madanapalli)',
    ta: 'மதனபள்ளி மண்டி (Madanapalli)',
    ml: 'മദനപ്പള്ളി മണ്ടി (Madanapalli)',
    en: 'Madanapalli APMC'
  },
  'Kalikiri APMC': {
    te: 'కలికిరి APMC (Kalikiri)',
    hi: 'कालिकिरी मंडी (Kalikiri)',
    ta: 'கலிகிரி மண்டி (Kalikiri)',
    ml: 'കലിക്കിരി മണ്ടി (Kalikiri)',
    en: 'Kalikiri APMC'
  },
  'Palamaner APMC': {
    te: 'పలమనేరు APMC (Palamaner)',
    hi: 'पलमनेर मंडी (Palamaner)',
    ta: 'பல்மனேர் மண்டி (Palamaner)',
    ml: 'പലമനേർ മണ്ടി (Palamaner)',
    en: 'Palamaner APMC'
  },
  'Punganur APMC': {
    te: 'పుంగనూరు APMC (Punganur)',
    hi: 'पुंगनूर मंडी (Punganur)',
    ta: 'புங்கனூர் மண்டி (Punganur)',
    ml: 'പുങ്കനൂർ മണ്ടി (Punganur)',
    en: 'Punganur APMC'
  },
  'Ananthapur APMC': {
    te: 'అనంతపురం APMC (Ananthapur)',
    hi: 'अनंतपुर मंडी (Ananthapur)',
    ta: 'அனந்தபூர் மண்டி (Ananthapur)',
    ml: 'അനന്തപൂർ മണ്ടി (Ananthapur)',
    en: 'Ananthapur APMC'
  },
  'Anantapur APMC': {
    te: 'అనంతపురం APMC (Anantapur)',
    hi: 'अनंतपुर मंडी (Anantapur)',
    ta: 'அனந்தபூர் மண்டி (Anantapur)',
    ml: 'അനന്തപൂർ മണ്ടി (Anantapur)',
    en: 'Anantapur APMC'
  },
  'Pattikonda APMC': {
    te: 'పత్తికొండ APMC (Pattikonda)',
    hi: 'पत्तीकोंडा मंडी (Pattikonda)',
    ta: 'பத்திகொண்டா மண்டி (Pattikonda)',
    ml: 'പത്തികൊണ്ട മണ്ടി (Pattikonda)',
    en: 'Pattikonda APMC'
  },
  'Mulakalacheruvu APMC': {
    te: 'ముళకలచెరువు APMC (Mulakalacheruvu)',
    hi: 'मुलकलचेरुवु मंडी (Mulakalacheruvu)',
    ta: 'முளகலசெருவு மண்டி (Mulakalacheruvu)',
    ml: 'മുളകലച്ചെറുവ് മണ്ടി (Mulakalacheruvu)',
    en: 'Mulakalacheruvu APMC'
  },
  'Valmikipuram APMC': {
    te: 'వాల్మీకిపురం APMC (Valmikipuram)',
    hi: 'वाल्मीकिपुरम मंडी (Valmikipuram)',
    ta: 'வால்மீகிபுரம் மண்டி (Valmikipuram)',
    ml: 'വാൽമീകിപുരം മണ്ടി (Valmikipuram)',
    en: 'Valmikipuram APMC'
  },
  'Somala APMC': {
    te: 'సోమల APMC (Somala)',
    hi: 'सोमला मंडी (Somala)',
    ta: 'சோமலா மண்டி (Somala)',
    ml: 'സോമല മണ്ടി (Somala)',
    en: 'Somala APMC'
  },
  'Kuppam APMC': {
    te: 'కుప్పం APMC (Kuppam)',
    hi: 'कुप्पम मंडी (Kuppam)',
    ta: 'குப்பம் மண்டி (Kuppam)',
    ml: 'കുപ്പം മണ്ടി (Kuppam)',
    en: 'Kuppam APMC'
  },
  'Adoni APMC': {
    te: 'ఆదోని APMC (Adoni)',
    hi: 'आदोनी मंडी (Adoni)',
    ta: 'ஆதோனி மண்டி (Adoni)',
    ml: 'ആദോനി മണ്ടി (Adoni)',
    en: 'Adoni APMC'
  },
  'Yerraguntla APMC': {
    te: 'ఎర్రగుంట్ల APMC (Yerraguntla)',
    hi: 'येर्रागुंट्ला मंडी (Yerraguntla)',
    ta: 'எர்ரகுண்ட்லா மண்டி (Yerraguntla)',
    ml: 'യെർറഗുണ്ട്ല മണ്ടി (Yerraguntla)',
    en: 'Yerraguntla APMC'
  },
  'Rajahmundry APMC': {
    te: 'రాజమండ్రి APMC (Rajahmundry)',
    hi: 'राजमुंदरी मंडी (Rajahmundry)',
    ta: 'ராஜமன்றி மண்டி (Rajahmundry)',
    ml: 'രാജമുണ്ട്രി മണ്ടി (Rajahmundry)',
    en: 'Rajahmundry APMC'
  },
  'Tenali APMC': {
    te: 'తెనాలి APMC (Tenali)',
    hi: 'तेनाली मंडी (Tenali)',
    ta: 'தெனாலி மண்டி (Tenali)',
    ml: 'തെനാലി മണ്ടി (Tenali)',
    en: 'Tenali APMC'
  },
  'Gopalapuram APMC': {
    te: 'గోపాలపురం APMC (Gopalapuram)',
    hi: 'गोपालपुरम मंडी (Gopalapuram)',
    ta: 'கோபாலபுரம் மண்டி (Gopalapuram)',
    ml: 'ഗോപാലപുരം മണ്ടി (Gopalapuram)',
    en: 'Gopalapuram APMC'
  },
  'Chintalapudi APMC': {
    te: 'చింతలపూడి APMC (Chintalapudi)',
    hi: 'चिंतालपुडी मंडी (Chintalapudi)',
    ta: 'சிந்தலபூடி மண்டி (Chintalapudi)',
    ml: 'ചിന്തലപൂടി മണ്ടി (Chintalapudi)',
    en: 'Chintalapudi APMC'
  },
  'Eluru APMC': {
    te: 'ఏలూరు APMC (Eluru)',
    hi: 'एलुरु मंडी (Eluru)',
    ta: 'ஏலூர் மண்டி (Eluru)',
    ml: 'ഏലൂര് മണ്ടി (Eluru)',
    en: 'Eluru APMC'
  },
  'Denduluru APMC': {
    te: 'దెందులూరు APMC (Denduluru)',
    hi: 'देंदुलुरु मंडी (Denduluru)',
    ta: 'தெந்துலூரு மண்டி (Denduluru)',
    ml: 'ദെന്ദുലൂരു മണ്ടി (Denduluru)',
    en: 'Denduluru APMC'
  },
  'Parchur APMC': {
    te: 'పర్చూరు APMC (Parchur)',
    hi: 'परचूर मंडी (Parchur)',
    ta: 'பர்ச்சூர் மண்டி (Parchur)',
    ml: 'പർചൂർ മണ്ടി (Parchur)',
    en: 'Parchur APMC'
  },
  'Banaganapalli APMC': {
    te: 'బనగానపల్లె APMC (Banaganapalli)',
    hi: 'बनगानपल्ले मंडी (Banaganapalli)',
    ta: 'பனகானபள்ளி மண்டி (Banaganapalli)',
    ml: 'ബനഗാനപള്ളി മണ്ടി (Banaganapalli)',
    en: 'Banaganapalli APMC'
  },
  'Atmakur (Nandyal District) APMC': {
    te: 'ఆత్మకూరు APMC (Atmakur Nandyal)',
    hi: 'आत्मकूर मंडी (Atmakur Nandyal)',
    ta: 'ஆத்மகூர் மண்டி (Atmakur Nandyal)',
    ml: 'ആത്മകൂർ മണ്ടി (Atmakur Nandyal)',
    en: 'Atmakur (Nandyal District) APMC'
  },
  'Tiruvuru APMC': {
    te: 'తిరువూరు APMC (Tiruvuru)',
    hi: 'तिरुवूरु मंडी (Tiruvuru)',
    ta: 'திருவூரு மண்டி (Tiruvuru)',
    ml: 'തിരുവൂരു മണ്ടി (Tiruvuru)',
    en: 'Tiruvuru APMC'
  },
  'Tanuku APMC': {
    te: 'తణుకు APMC (Tanuku)',
    hi: 'तणुकू मंडी (Tanuku)',
    ta: 'தணுகு மண்டி (Tanuku)',
    ml: 'തണുക്കു മണ്ടി (Tanuku)',
    en: 'Tanuku APMC'
  },
  'Sampara (Kakinada Rural) APMC': {
    te: 'సాంపర APMC (Sampara Kakinada)',
    hi: 'सामपरा मंडी (Sampara Kakinada)',
    ta: 'சம்பரா மண்டி (Sampara Kakinada)',
    ml: 'സാംപര മണ്ടി (Sampara Kakinada)',
    en: 'Sampara (Kakinada Rural) APMC'
  },
  'Nandyal APMC': {
    te: 'నంద్యాల APMC (Nandyal)',
    hi: 'नंद्याल मंडी (Nandyal)',
    ta: 'நந்தியாலா மண்டி (Nandyal)',
    ml: 'നന്ദ്യാൽ മണ്ടി (Nandyal)',
    en: 'Nandyal APMC'
  },
  'Alur APMC': {
    te: 'ఆలూరు APMC (Alur)',
    hi: 'आलूर मंडी (Alur)',
    ta: 'ஆலூர் மண்டி (Alur)',
    ml: 'ആലൂർ മണ്ടി (Alur)',
    en: 'Alur APMC'
  },
  'Kadapa APMC': {
    te: 'కడప APMC (Kadapa)',
    hi: 'कडपा मंडी (Kadapa)',
    ta: 'கடப்பா மண்டி (Kadapa)',
    ml: 'കടപ്പ മണ്ടി (Kadapa)',
    en: 'Kadapa APMC'
  },
  'Yemmiganuru APMC': {
    te: 'ఎమ్మిగనూరు APMC (Yemmiganuru)',
    hi: 'एम्मिगनूर मंडी (Yemmiganuru)',
    ta: 'எம்மிகனூர் மண்டி (Yemmiganuru)',
    ml: 'എമ്മിഗനൂർ മണ്ടി (Yemmiganuru)',
    en: 'Yemmiganuru APMC'
  },
  'Dhone APMC': {
    te: 'డోన్ APMC (Dhone)',
    hi: 'डोण मंडी (Dhone)',
    ta: 'டோன் மண்டி (Dhone)',
    ml: 'ഡോൺ മണ്ടി (Dhone)',
    en: 'Dhone APMC'
  },
  'Guntur APMC': {
    te: 'గుంటూరు APMC (Guntur)',
    hi: 'गुंटूर मंडी (Guntur)',
    ta: 'குண்டூர் மண்டி (Guntur)',
    ml: 'ഗുണ്ടൂർ മണ്ടി (Guntur)',
    en: 'Guntur APMC'
  },
  'Pidugurala (Palnadu) APMC': {
    te: 'పిడుగురాళ్ల APMC (Pidugurala)',
    hi: 'पिडुगुराल्ला मंडी (Pidugurala)',
    ta: 'பிடுகுராள்ளா மண்டி (Pidugurala)',
    ml: 'പിടുഗുരാള്ള മണ്ടി (Pidugurala)',
    en: 'Pidugurala (Palnadu) APMC'
  },
  'Piduguralla (Palnadu) APMC': {
    te: 'పిడుగురాళ్ల APMC (Piduguralla)',
    hi: 'पिडुगुराल्ला मंडी (Piduguralla)',
    ta: 'பிடுகுராள்ளா மண்டி (Piduguralla)',
    ml: 'പിടുഗുരാള്ള മണ്ടി (Piduguralla)',
    en: 'Piduguralla (Palnadu) APMC'
  },
};

// District multilingual mapping for all 26 Andhra Pradesh districts
const districtTranslations: Record<string, Record<Language, string>> = {
  'Anantapur': {
    te: 'అనంతపురం జిల్లా',
    hi: 'अनंतपुर ज़िला',
    ta: 'அனந்தபூர் மாவட்டம்',
    ml: 'അനന്തപൂർ ജില്ല',
    en: 'Anantapur District'
  },
  'Annamayya': {
    te: 'అన్నమయ్య జిల్లా',
    hi: 'अन्नमय्या ज़िला',
    ta: 'அன்னமய்யா மாவட்டம்',
    ml: 'അന്നമയ്യ ജില്ല',
    en: 'Annamayya District'
  },
  'Chittoor': {
    te: 'చిత్తూరు జిల్లా',
    hi: 'चित्तूर ज़िला',
    ta: 'சித்தூர் மாவட்டம்',
    ml: 'ചിറ്റൂർ ജില്ല',
    en: 'Chittoor District'
  },
  'Kurnool': {
    te: 'కర్నూలు జిల్లా',
    hi: 'कुरनूल ज़िला',
    ta: 'கர்நூல் மாவட்டம்',
    ml: 'കർനൂൾ ജില്ല',
    en: 'Kurnool District'
  },
  'Nandyal': {
    te: 'నంద్యాల జిల్లా',
    hi: 'नंद्याल ज़िला',
    ta: 'நந்தியாலா மாவட்டம்',
    ml: 'നന്ദ്യാൽ ജില്ല',
    en: 'Nandyal District'
  },
  'Guntur': {
    te: 'గుంటూరు జిల్లా',
    hi: 'गुंटूर ज़िला',
    ta: 'குண்டூர் மாவட்டம்',
    ml: 'ഗുണ്ടൂർ ജില്ല',
    en: 'Guntur District'
  },
  'Palnadu': {
    te: 'పల్నాడు జిల్లా',
    hi: 'पलनाडु ज़िला',
    ta: 'பல்நாடு மாவட்டம்',
    ml: 'പൽനാട് ജില്ല',
    en: 'Palnadu District'
  },
  'Bapatla': {
    te: 'బాపట్ల జిల్లా',
    hi: 'बापटला ज़िला',
    ta: 'பாபட்லா மாவட்டம்',
    ml: 'ബാപട്‌ല ജില്ല',
    en: 'Bapatla District'
  },
  'Eluru': {
    te: 'ఏలూరు జిల్లా',
    hi: 'एलुरु ज़िला',
    ta: 'ஏலூர் மாவட்டம்',
    ml: 'ഏലൂർ ജില്ല',
    en: 'Eluru District'
  },
  'East Godavari': {
    te: 'తూర్పు గోదావరి జిల్లా',
    hi: 'पूर्वी गोदावरी ज़िला',
    ta: 'கிழக்கு கோதாவரி மாவட்டம்',
    ml: 'കിഴക്കൻ ഗോദാവരി ജില്ല',
    en: 'East Godavari District'
  },
  'West Godavari': {
    te: 'పశ్చిమ గోదావరి జిల్లా',
    hi: 'पश्चिम गोदावरी ज़िला',
    ta: 'மேற்கு கோதாவரி மாவட்டம்',
    ml: 'പടിഞ്ഞാറൻ ഗോദാവരി ജില്ല',
    en: 'West Godavari District'
  },
  'Kakinada': {
    te: 'కాకినాడ జిల్లా',
    hi: 'काकीनाडा ज़िला',
    ta: 'காக்கிநாடா மாவட்டம்',
    ml: 'കാക്കിനട ജില്ല',
    en: 'Kakinada District'
  },
  'NTR': {
    te: 'ఎన్టీఆర్ జిల్లా',
    hi: 'एनटीआर ज़िला',
    ta: 'என்டிஆர் மாவட்டம்',
    ml: 'എൻടിആർ ജില്ല',
    en: 'NTR District'
  },
  'YSR Kadapa': {
    te: 'వైఎస్సార్ కడప జిల్లా',
    hi: 'वाईएसआर कडपा ज़िला',
    ta: 'ஒய்.எஸ்.ஆர் கடப்பா மாவட்டம்',
    ml: 'വൈ.എസ്.ആർ കടപ്പ ജില്ല',
    en: 'YSR Kadapa District'
  },
  'Kadapa': {
    te: 'వైఎస్సార్ కడప జిల్లా',
    hi: 'वाईएसआर कडपा ज़िला',
    ta: 'ஒய்.எஸ்.ஆர் கடப்பா மாவட்டம்',
    ml: 'വൈ.എസ്.ആർ കടപ്പ ജില്ല',
    en: 'YSR Kadapa District'
  },
  'Alluri Sitharama Raju': {
    te: 'అల్లూరి సీతారామరాజు జిల్లా',
    hi: 'अल्लूरी सीताराम राजू ज़िला',
    ta: 'அல்லூரி சீதாராம ராஜு மாவட்டம்',
    ml: 'അല്ലൂരി സീതാരാമ രാജു ജില്ല',
    en: 'Alluri Sitharama Raju District'
  }
};

/**
 * Robust multilingual getter for commodity names with fuzzy & alias resolution.
 */
export const getLocalizedCommodityName = (name: string, lang: Language): string => {
  if (!name) return '';
  if (commodityTranslations[name] && commodityTranslations[name][lang]) {
    return commodityTranslations[name][lang];
  }

  const clean = name.trim().toLowerCase();

  for (const key in commodityTranslations) {
    if (key.toLowerCase() === clean) {
      return commodityTranslations[key][lang] || commodityTranslations[key]['en'];
    }
  }

  if (clean.includes('ajw') || clean.includes('omam')) return commodityTranslations['Ajwan']?.[lang] || 'Ajwan';
  if (clean.includes('tomat')) return commodityTranslations['Tomato']?.[lang] || 'Tomato';
  if (clean.includes('onion') || clean.includes('ulli')) return commodityTranslations['Onion']?.[lang] || 'Onion';
  if (clean.includes('potat') || clean.includes('alu') || clean.includes('bangala')) return commodityTranslations['Potato']?.[lang] || 'Potato';
  if (clean.includes('lemon') || clean.includes('nimma')) return commodityTranslations['Lemon']?.[lang] || 'Lemon';
  if (clean.includes('brinjal') || clean.includes('vankaya') || clean.includes('baingan')) return commodityTranslations['Brinjal']?.[lang] || 'Brinjal';
  if (clean.includes('cabbage')) return commodityTranslations['Cabbage']?.[lang] || 'Cabbage';
  if (clean.includes('cauli')) return commodityTranslations['Cauliflower']?.[lang] || 'Cauliflower';
  if (clean.includes('green ch') || clean.includes('chilli') || clean.includes('mirchi')) return commodityTranslations['Green Chilli']?.[lang] || 'Green Chilli';
  if (clean.includes('cluster') || clean.includes('guar') || clean.includes('goruchikkudu')) return commodityTranslations['Cluster Beans']?.[lang] || 'Cluster Beans';
  if (clean.includes('ridge') || clean.includes('tori') || clean.includes('beerakaya')) return commodityTranslations['Ridgeguard']?.[lang] || 'Ridgeguard';
  if (clean.includes('paddy') || clean.includes('rice') || clean.includes('vari')) return commodityTranslations['Paddy']?.[lang] || 'Paddy';
  if (clean.includes('maize') || clean.includes('corn') || clean.includes('mokkajonna')) return commodityTranslations['Maize']?.[lang] || 'Maize';
  if (clean.includes('jowar') || clean.includes('sorghum') || clean.includes('jonna')) return commodityTranslations['Jowar']?.[lang] || 'Jowar';
  if (clean.includes('groundnut') || clean.includes('peanut') || clean.includes('verusanaga')) return commodityTranslations['Groundnut']?.[lang] || 'Groundnut';
  if (clean.includes('castor') || clean.includes('amudamu')) return commodityTranslations['Castor Seed']?.[lang] || 'Castor Seed';
  if (clean.includes('sunflower') || clean.includes('poddu')) return commodityTranslations['Sunflower']?.[lang] || 'Sunflower';
  if (clean.includes('bengal') || clean.includes('chana') || clean.includes('senaga')) return commodityTranslations['Bengal Gram']?.[lang] || 'Bengal Gram';
  if (clean.includes('red gram') || clean.includes('arhar') || clean.includes('tur') || clean.includes('kandulu')) return commodityTranslations['Red Gram']?.[lang] || 'Red Gram';
  if (clean.includes('black gram') || clean.includes('urad') || clean.includes('minumulu')) return commodityTranslations['Black Gram']?.[lang] || 'Black Gram';
  if (clean.includes('dry chill') || clean.includes('mirchi')) return commodityTranslations['Dry Chillies']?.[lang] || 'Dry Chillies';
  if (clean.includes('turmeric') || clean.includes('pasupu') || clean.includes('haldi')) return commodityTranslations['Turmeric']?.[lang] || 'Turmeric';

  return name;
};

/**
 * Robust multilingual getter for APMC Market names with fuzzy & alias resolution.
 */
export const getLocalizedMarketName = (name: string, lang: Language): string => {
  if (!name) return '';
  if (marketTranslations[name] && marketTranslations[name][lang]) {
    return marketTranslations[name][lang];
  }

  const clean = name.trim().toLowerCase();

  for (const key in marketTranslations) {
    if (key.toLowerCase() === clean) {
      return marketTranslations[key][lang] || marketTranslations[key]['en'];
    }
  }

  if (clean.includes('kurnool')) return marketTranslations['Kurnool APMC']?.[lang] || 'Kurnool APMC';
  if (clean.includes('madanapalle')) return marketTranslations['Madanapalle APMC']?.[lang] || 'Madanapalle APMC';
  if (clean.includes('madanapalli')) return marketTranslations['Madanapalli APMC']?.[lang] || 'Madanapalli APMC';
  if (clean.includes('kalikiri')) return marketTranslations['Kalikiri APMC']?.[lang] || 'Kalikiri APMC';
  if (clean.includes('palamaner')) return marketTranslations['Palamaner APMC']?.[lang] || 'Palamaner APMC';
  if (clean.includes('punganur') || clean.includes('pungunur')) return marketTranslations['Punganur APMC']?.[lang] || 'Punganur APMC';
  if (clean.includes('ananthapur')) return marketTranslations['Ananthapur APMC']?.[lang] || 'Ananthapur APMC';
  if (clean.includes('anantapur')) return marketTranslations['Anantapur APMC']?.[lang] || 'Anantapur APMC';
  if (clean.includes('pattikonda')) return marketTranslations['Pattikonda APMC']?.[lang] || 'Pattikonda APMC';
  if (clean.includes('mulakalacheruvu') || clean.includes('mulakalcheruvu')) return marketTranslations['Mulakalacheruvu APMC']?.[lang] || 'Mulakalacheruvu APMC';
  if (clean.includes('valmikipuram')) return marketTranslations['Valmikipuram APMC']?.[lang] || 'Valmikipuram APMC';
  if (clean.includes('somala')) return marketTranslations['Somala APMC']?.[lang] || 'Somala APMC';
  if (clean.includes('kuppam')) return marketTranslations['Kuppam APMC']?.[lang] || 'Kuppam APMC';
  if (clean.includes('adoni')) return marketTranslations['Adoni APMC']?.[lang] || 'Adoni APMC';
  if (clean.includes('yerraguntla') || clean.includes('yerraguntala')) return marketTranslations['Yerraguntla APMC']?.[lang] || 'Yerraguntla APMC';
  if (clean.includes('rajahmundry') || clean.includes('rajahmundary')) return marketTranslations['Rajahmundry APMC']?.[lang] || 'Rajahmundry APMC';
  if (clean.includes('tenali') || clean.includes('tenalli')) return marketTranslations['Tenali APMC']?.[lang] || 'Tenali APMC';
  if (clean.includes('gopalapuram')) return marketTranslations['Gopalapuram APMC']?.[lang] || 'Gopalapuram APMC';
  if (clean.includes('chintalapudi')) return marketTranslations['Chintalapudi APMC']?.[lang] || 'Chintalapudi APMC';
  if (clean.includes('eluru')) return marketTranslations['Eluru APMC']?.[lang] || 'Eluru APMC';
  if (clean.includes('denduluru')) return marketTranslations['Denduluru APMC']?.[lang] || 'Denduluru APMC';
  if (clean.includes('parchur')) return marketTranslations['Parchur APMC']?.[lang] || 'Parchur APMC';
  if (clean.includes('banaganapalli')) return marketTranslations['Banaganapalli APMC']?.[lang] || 'Banaganapalli APMC';
  if (clean.includes('atmakur')) return marketTranslations['Atmakur (Nandyal District) APMC']?.[lang] || 'Atmakur (Nandyal District) APMC';
  if (clean.includes('tiruvuru')) return marketTranslations['Tiruvuru APMC']?.[lang] || 'Tiruvuru APMC';
  if (clean.includes('tanuku')) return marketTranslations['Tanuku APMC']?.[lang] || 'Tanuku APMC';
  if (clean.includes('sampara')) return marketTranslations['Sampara (Kakinada Rural) APMC']?.[lang] || 'Sampara (Kakinada Rural) APMC';
  if (clean.includes('nandyal')) return marketTranslations['Nandyal APMC']?.[lang] || 'Nandyal APMC';
  if (clean.includes('alur')) return marketTranslations['Alur APMC']?.[lang] || 'Alur APMC';
  if (clean.includes('kadapa')) return marketTranslations['Kadapa APMC']?.[lang] || 'Kadapa APMC';
  if (clean.includes('yemmiganuru')) return marketTranslations['Yemmiganuru APMC']?.[lang] || 'Yemmiganuru APMC';
  if (clean.includes('dhone')) return marketTranslations['Dhone APMC']?.[lang] || 'Dhone APMC';
  if (clean.includes('guntur')) return marketTranslations['Guntur APMC']?.[lang] || 'Guntur APMC';
  if (clean.includes('pidugurala') || clean.includes('piduguralla')) return marketTranslations['Pidugurala (Palnadu) APMC']?.[lang] || 'Pidugurala (Palnadu) APMC';

  return name;
};

/**
 * Robust multilingual getter for Andhra Pradesh district names.
 * Prevents double "District" / "జిల్లా" repetition.
 */
export const getLocalizedDistrictName = (rawDistrict: string, lang: Language): string => {
  if (!rawDistrict) return '';
  const clean = rawDistrict.replace(/district/gi, '').trim();

  for (const key in districtTranslations) {
    if (key.toLowerCase() === clean.toLowerCase() || clean.toLowerCase().includes(key.toLowerCase())) {
      return districtTranslations[key][lang] || districtTranslations[key]['en'];
    }
  }

  if (lang === 'te') return `${clean} జిల్లా`;
  if (lang === 'hi') return `${clean} ज़िला`;
  if (lang === 'ta') return `${clean} மாவட்டம்`;
  if (lang === 'ml') return `${clean} ജില്ല`;
  return `${clean} District`;
};
