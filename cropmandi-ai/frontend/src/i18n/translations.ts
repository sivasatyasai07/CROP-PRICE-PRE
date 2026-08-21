export type Language = 'en' | 'te' | 'hi' | 'ml' | 'ta';

export interface TranslationDictionary {
  appTitle: string;
  appSubtitle: string;
  tabs: {
    forecast: string;
    trends: string;
    disease: string;
    weather: string;
    schemes: string;
  };
  forecast: {
    selectCrop: string;
    selectMarket: string;
    forecastDate: string;
    generateBtn: string;
    latestObserved: string;
    expectedTrend: string;
    advisoryTitle: string;
    disclaimerTitle: string;
    disclaimerText: string;
    day1: string;
    day2: string;
    day3: string;
    confidenceBounds: string;
    predictedPrice: string;
    loadingStages: string[];
    loadingSubtitle: string;
  };
  location: {
    detectLocationBtn: string;
    locationDetected: string;
    nearestMandi: string;
    distanceAway: string;
    permissionDenied: string;
  };
  weather: {
    title: string;
    subtitle: string;
    userLocationWeather: string;
    mandiLocationWeather: string;
    temperature: string;
    rain: string;
    humidity: string;
    wind: string;
    extremeAlert: string;
    historicalWeather: string;
    date: string;
    maxTemp: string;
    minTemp: string;
    heavyRainAlert: string;
    extremeHeatAlert: string;
    district: string;
    detectingLocation: string;
    past14Days: string;
    liveWeather: string;
  };
  schemes: {
    title: string;
    subtitle: string;
    visitOfficialWebsite: string;
    eligibility: string;
    benefits: string;
    howToApply: string;
  };
  disease: {
    tabTitle: string;
    tabSubtitle: string;
    badge: string;
    newAnalysis: string;
    history: string;
    uploadTitle: string;
    uploadSubtitle: string;
    browseFiles: string;
    takePhoto: string;
    maxImagesHint: string;
    analyzeBtn: string;
    analyzingBtn: string;
    loginPrompt: string;
    notesPlaceholder: string;
    notesLabel: string;
    recognizedCrop: string;
    primaryDiagnosis: string;
    confidence: string;
    botanicalEvidence: string;
    immediateAction: string;
    preventiveMeasures: string;
    chemicalControl: string;
    safetyPrecaution: string;
    disclaimerTitle: string;
    disclaimerText: string;
    deleteHistory: string;
    noHistory: string;
  };
  chatbot: {
    title: string;
    subtitle: string;
    placeholder: string;
    send: string;
    welcomeMsg: string;
    quickPrompts: string[];
  };
}

export const translations: Record<Language, TranslationDictionary> = {
  en: {
    appTitle: "Mandi Price Prediction",
    appSubtitle: "AI-Powered 3-Day Farmer Mandi Price Forecast & Advisory • Andhra Pradesh",
    tabs: {
      forecast: "Price Forecast",
      trends: "Trends & Compare",
      disease: "🌿 Crop Disease",
      weather: "Weather",
      schemes: "Govt Schemes",
    },
    forecast: {
      selectCrop: "Select Crop / Commodity",
      selectMarket: "Select AP Mandi Market",
      forecastDate: "Forecast Base Date",
      generateBtn: "Generate 3-Day Forecast",
      latestObserved: "Latest Observed Modal Price",
      expectedTrend: "3-Day Expected Trend",
      advisoryTitle: "Farmer Decision Advisory",
      disclaimerTitle: "Decision Support Advisory Disclaimer",
      disclaimerText: "Predictions are computed using CatBoost machine learning models based on historic APMC market arrivals, prices, and weather trends. Use as decision guidance alongside local market inquiries.",
      day1: "Tomorrow (Day 1)",
      day2: "Day +2",
      day3: "Day +3",
      confidenceBounds: "80% Confidence Interval",
      predictedPrice: "Predicted Modal Price",
      loadingSubtitle: "Executing strict 5-level precedence: Official API (data.gov.in) → master-data.csv → CatBoost ML Prediction → Fallback → Unavailable.",
      loadingStages: [
        "Stage 1 of 5: Querying official data.gov.in API records with filters...",
        "Stage 2 of 5: Checking verified official records across 4-date horizon...",
        "Stage 3 of 5: Checking master-data.csv & building feature vectors...",
        "Stage 4 of 5: Executing CatBoost ML model inference for missing dates...",
        "Stage 5 of 5: Finalizing verified predictions & conformal intervals..."
      ]
    },
    location: {
      detectLocationBtn: "Detect My Location",
      locationDetected: "Your Current Location",
      nearestMandi: "Nearest AP Mandi Market",
      distanceAway: "km away",
      permissionDenied: "Location permission denied. Defaulting to AP central markets.",
    },
    weather: {
      title: "Mandi & Location Weather Service",
      subtitle: "Live satellite & Open-Meteo historical/forecast weather data for crops",
      userLocationWeather: "Your Current Location Weather",
      mandiLocationWeather: "Selected AP Mandi Weather",
      temperature: "Temperature",
      rain: "Precipitation",
      humidity: "Humidity",
      wind: "Wind Speed",
      extremeAlert: "Extreme Weather Alert",
      historicalWeather: "Historical Weather Log",
      date: "Date",
      maxTemp: "Max Temp (°C)",
      minTemp: "Min Temp (°C)",
      heavyRainAlert: "Heavy Rainfall Risk",
      extremeHeatAlert: "Extreme Heat Alert (>40°C)",
      district: "District",
      detectingLocation: "Detecting Location...",
      past14Days: "Past 14 Days",
      liveWeather: "Live Satellite & Open-Meteo Weather"
    },
    schemes: {
      title: "Government Agricultural Schemes",
      subtitle: "Official central & state financial assistance, crop insurance, and market welfare for farmers",
      visitOfficialWebsite: "Visit Official Portal",
      eligibility: "Eligibility Criteria",
      benefits: "Key Benefits",
      howToApply: "How to Apply",
    },
    disease: {
      tabTitle: "Instant Crop Disease & Health Diagnosis",
      tabSubtitle: "Upload or capture a photo of your crop foliage. Gemini AI will automatically recognize the crop species, analyze visible symptoms, and provide localized treatment guidance.",
      badge: "AI-Powered Crop Pathology",
      newAnalysis: "New Analysis",
      history: "Diagnostic History",
      uploadTitle: "Upload or Capture Crop Leaf Photos",
      uploadSubtitle: "Drag & drop leaf images or use camera (Supported: JPG, PNG, WebP up to 10MB)",
      browseFiles: "Browse Files",
      takePhoto: "Take Photo",
      maxImagesHint: "You can upload up to 3 images for comprehensive visual angle evidence",
      analyzeBtn: "Analyze Crop Disease with AI",
      analyzingBtn: "AI Pathology Analysis in Progress...",
      loginPrompt: "Please log in or sign up to analyze crop diseases and maintain diagnostic history.",
      notesPlaceholder: "Add optional observations (e.g., noticed yellow spots 3 days ago, applied urea last week)...",
      notesLabel: "Field Notes & Observations (Optional)",
      recognizedCrop: "Recognized Crop Species",
      primaryDiagnosis: "Primary Pathology Diagnosis",
      confidence: "Confidence Level",
      botanicalEvidence: "Botanical & Visual Evidence",
      immediateAction: "Immediate Treatment Actions",
      preventiveMeasures: "Long-term Preventive Measures",
      chemicalControl: "Chemical & Fungicide Guidance",
      safetyPrecaution: "Safety & Spraying Precautions",
      disclaimerTitle: "Agricultural Pathology Advisory Disclaimer",
      disclaimerText: "This analysis is an AI preliminary diagnostic decision-support tool. Always consult your local agricultural extension officer (AEO) or Krishi Vigyan Kendra (KVK) before applying hazardous chemical sprays.",
      deleteHistory: "Delete Record",
      noHistory: "No prior disease diagnosis records found."
    },
    chatbot: {
      title: "Mandi Mitra AI Chatbot",
      subtitle: "Ask about crop prices, weather advice, or government schemes in your language",
      placeholder: "Ask Mandi Mitra AI a question...",
      send: "Send",
      welcomeMsg: "Namaste! I am Mandi Mitra AI. How can I help you today with mandi price predictions, weather, or farmer schemes?",
      quickPrompts: [
        "What is the 3-day Tomato price forecast?",
        "Which AP mandi gives highest profit for Tomato?",
        "Tell me about PM-KISAN scheme eligibility",
        "How will today's weather affect crop harvesting?"
      ]
    }
  },
  te: {
    appTitle: "మండి ధరల అంచనా",
    appSubtitle: "రైతుల కోసం 3 రోజుల మండి మార్కెట్ ధరల AI అంచనా & సలహాలు • ఆంధ్రప్రదేశ్",
    tabs: {
      forecast: "ధరల అంచనా",
      trends: "ధరల పోలిక",
      disease: "🌿 పంట తెగుళ్ళు",
      weather: "వాతావరణం",
      schemes: "ప్రభుత్వ పథకాలు",
    },
    forecast: {
      selectCrop: "పంటను ఎంచుకోండి",
      selectMarket: "AP మండి మార్కెట్ ఎంచుకోండి",
      forecastDate: "అంచనా తేదీ",
      generateBtn: "3 రోజుల అంచనా పొందండి",
      latestObserved: "ఇటీవలి మార్కెట్ ధర",
      expectedTrend: "3 రోజుల అంచనా మార్పు",
      advisoryTitle: "రైతు నిర్ణయ సలహా",
      disclaimerTitle: "సలహా మార్గదర్శకం",
      disclaimerText: "ఈ అంచనాలు గత APMC మండి ధరలు, రాబడులు మరియు వాతావరణం ఆధారంగా AI మెషిన్ లెర్నింగ్ మోడల్స్ ద్వారా అందించబడ్డాయి. స్థానిక మార్కెట్ సమాచారంతో పాటు దీనిని ఉపయోగించండి.",
      day1: "రేపు (రేపటి ధర)",
      day2: "ఎల్లుండి (2వ రోజు)",
      day3: "3వ రోజు",
      confidenceBounds: "80% నమ్మకమైన పరిధి (అల్ప - అధిక)",
      predictedPrice: "అంచనా వేసిన ధర",
      loadingSubtitle: "అధికారిక API (data.gov.in) → మాస్టర్ డేటా → CatBoost AI అంచనా క్రమంలో ప్రాసెస్ చేయబడుతోంది.",
      loadingStages: [
        "దశ 1/5: data.gov.in అధికారిక API నుండి రికార్డులను శోధిస్తోంది...",
        "దశ 2/5: 4 రోజుల వ్యవధిలో ధృవీకరించబడిన అధికారిక ధరలను తనిఖీ చేస్తోంది...",
        "దశ 3/5: మాస్టర్ డేటా మరియు ఫీచర్ వెక్టర్లను సిద్ధం చేస్తోంది...",
        "దశ 4/5: మిస్సింగ్ తేదీల కోసం CatBoost ML మోడల్ అంచనా వేస్తోంది...",
        "దశ 5/5: ధృవీకరించిన అంచనాలు మరియు విశ్వసనీయ పరిమితులను సిద్ధం చేస్తోంది..."
      ]
    },
    location: {
      detectLocationBtn: "నా స్థానాన్ని గుర్తించు",
      locationDetected: "మీ ప్రస్తుత స్థానం",
      nearestMandi: "సమీప AP మండి మార్కెట్",
      distanceAway: "కిమీ దూరంలో",
      permissionDenied: "స్థాన అనుమతి నిరాకరించబడింది. డిఫాల్ట్ మండి ఎంచుకోబడింది.",
    },
    weather: {
      title: "వాతావరణ సమాచారం",
      subtitle: "లైవ్ శాటిలైట్ మరియు నిజమైన వాతావరణ సమాచారం",
      userLocationWeather: "మీ ప్రస్తుత ప్రాంతపు వాతావరణం",
      mandiLocationWeather: "ఎంచుకున్న మండి వాతావరణం",
      temperature: "ఉష్ణోగ్రత",
      rain: "వర్షపాతం",
      humidity: "తేమ శాతం",
      wind: "గాలి వేగం",
      extremeAlert: "తీవ్రమైన వాతావరణ హెచ్చరిక",
      historicalWeather: "గత వాతావరణ రికార్డులు",
      date: "తేదీ",
      maxTemp: "గరిష్ట ఉష్ణోగ్రత (°C)",
      minTemp: "కనిష్ట ఉష్ణోగ్రత (°C)",
      heavyRainAlert: "భారీ వర్షపాతం ప్రమాదం",
      extremeHeatAlert: "తీవ్రమైన వేడి హెచ్చరిక (>40°C)",
      district: "జిల్లా",
      detectingLocation: "స్థానాన్ని గుర్తిస్తోంది...",
      past14Days: "గత 14 రోజుల వివరాలు",
      liveWeather: "ప్రత్యక్ష శాటిలైట్ వాతావరణ సమాచారం"
    },
    schemes: {
      title: "ప్రభుత్వ వ్యవసాయ పథకాలు",
      subtitle: "కేంద్ర మరియు ఆంధ్రప్రదేశ్ ప్రభుత్వ రైతు సంక్షేమ పథకాలు, బీమా మరియు ఆర్థిక సాయం",
      visitOfficialWebsite: "అధికారిక వెబ్‌సైట్ చూడండి",
      eligibility: "అర్హతలు",
      benefits: "ముఖ్య ప్రయోజనాలు",
      howToApply: "దరఖాస్తు విధానం",
    },
    disease: {
      tabTitle: "పంట తెగుళ్ళు మరియు ఆరోగ్య నిర్ధారణ",
      tabSubtitle: "మీ పంట ఆకుల ఫోటోను అప్‌లోడ్ చేయండి లేదా తీయండి. Gemini AI పంట రకాన్ని గుర్తించి, తెగుళ్ళను విశ్లేషించి, తగిన చికిత్సా మార్గాలను మీ స్థానిక భాషలో అందిస్తుంది.",
      badge: "AI-ఆధారిత పంట రోగ నిర్ధారణ",
      newAnalysis: "కొత్త నిర్ధారణ",
      history: "గత రోగ రికార్డులు",
      uploadTitle: "పంట ఆకుల ఫోటోలను అప్‌లోడ్ చేయండి లేదా తీయండి",
      uploadSubtitle: "ఆకుల ఫోటోలను ఇక్కడ లాగండి లేదా కెమెరా ఉపయోగించండి (JPG, PNG, గరిష్టంగా 10MB)",
      browseFiles: "ఫైళ్ళను ఎంచుకోండి",
      takePhoto: "ఫోటో తీయండి",
      maxImagesHint: "స్పష్టమైన ఫలితాల కోసం గరిష్టంగా 3 విభిన్న కోణాల ఫోటోలను జోడించవచ్చు",
      analyzeBtn: "తెగుళ్ళను AI తో నిర్ధారించండి",
      analyzingBtn: "AI విశ్లేషణ జరుగుతోంది...",
      loginPrompt: "పంట తెగుళ్ళను నిర్ధారించడానికి మరియు రికార్డులు భద్రపరచడానికి దయచేసి లాగిన్ అవ్వండి.",
      notesPlaceholder: "అదనపు వివరాలు రాయండి (ఉదా: 3 రోజుల క్రితం పసుపు మచ్చలు కనిపించాయి)...",
      notesLabel: "రైతు గమనింపులు & గమనికలు (ఐచ్ఛికం)",
      recognizedCrop: "గుర్తించిన పంట రకం",
      primaryDiagnosis: "ప్రధాన తెగులు / వ్యాధి నిర్ధారణ",
      confidence: "నమ్మక స్థాయి",
      botanicalEvidence: "వృక్ష శాస్త్ర & దృశ్య ఆధారాలు",
      immediateAction: "వెంటనే తీసుకోవాల్సిన చర్యలు",
      preventiveMeasures: "దీర్ఘకాలిక నివారణ చర్యలు",
      chemicalControl: "రసాయన & మందుల పిచికారీ మార్గదర్శకాలు",
      safetyPrecaution: "భద్రత & ముందస్తు జాగ్రత్తలు",
      disclaimerTitle: "వ్యవసాయ సలహా మార్గదర్శకం",
      disclaimerText: "ఇది ప్రాథమిక AI సాంకేతిక రోగ నిర్ధారణ సలహా మాత్రమే. రసాయన మందులను పిచికారీ చేసే ముందు స్థానిక వ్యవసాయ అధికారి లేదా కృషి విజ్ఞాన కేంద్రం (KVK) నిపుణులను సంప్రదించండి.",
      deleteHistory: "రికార్డును తొలగించండి",
      noHistory: "గత రోగ నిర్ధారణ రికార్డులు ఏవీ లేవు."
    },
    chatbot: {
      title: "మండి మిత్ర AI చాట్‌బాట్",
      subtitle: "ధరలు, వాతావరణం మరియు ప్రభుత్వ పథకాల గురించి మీ భాషలోనే అడగండి",
      placeholder: "మండి మిత్ర AI ని ఏదైనా అడగండి...",
      send: "పంపించు",
      welcomeMsg: "నమస్కారం! నేను మండి మిత్ర AI. మీకు మండి ధరలు, వాతావరణం లేదా రైతు పథకాల గురించి ఎలా సహాయపడగలను?",
      quickPrompts: [
        "టమోటా 3 రోజుల ధరల అంచనా ఏమిటి?",
        "టమోటాలకు ఏ AP మండిలో ఎక్కువ లాభం వస్తుంది?",
        "PM-KISAN పథకం అర్హతలు ఏమిటి?",
        "ఈరోజు వాతావరణం పంట కోతపై ఎలా ప్రభావం చూపుతుంది?"
      ]
    }
  },
  hi: {
    appTitle: "मंडी भाव पूर्वानुमान",
    appSubtitle: "किसानों के लिए AI 3-दिवसीय मंडी भाव पूर्वानुमान एवं सलाह • आंध्र प्रदेश",
    tabs: {
      forecast: "भाव पूर्वानुमान",
      trends: "मूल्य रुझान",
      disease: "🌿 फसल रोग",
      weather: "मौसम",
      schemes: "सरकारी योजनाएं",
    },
    forecast: {
      selectCrop: "फसल चुनें",
      selectMarket: "आंध्र प्रदेश मंडी चुनें",
      forecastDate: "पूर्वानुमान तिथि",
      generateBtn: "3-दिवसीय पूर्वानुमान प्राप्त करें",
      latestObserved: "नवीनतम दर्ज मंडी भाव",
      expectedTrend: "3-दिवसीय अनुमानित रुझान",
      advisoryTitle: "किसान निर्णय सलाह",
      disclaimerTitle: "निर्णय सहायता अस्वीकरण",
      disclaimerText: "यह पूर्वानुमान ऐतिहासिक मंडी आवक, मूल्यों और मौसम डेटा पर आधारित CatBoost AI मॉडल द्वारा तैयार किया गया है।",
      day1: "कल (दिन 1)",
      day2: "परसों (दिन 2)",
      day3: "दिन 3",
      confidenceBounds: "80% विश्वास अंतराल सीमा",
      predictedPrice: "अनुमानित भाव",
      loadingSubtitle: "आधिकारिक API (data.gov.in) → मास्टर डेटा → CatBoost AI पूर्वानुमान क्रम में निष्पादित हो रहा है।",
      loadingStages: [
        "चरण 1/5: data.gov.in आधिकारिक API से मंडी मूल्य रिकॉर्ड प्राप्त किए जा रहे हैं...",
        "चरण 2/5: 4-दिवसीय अवधि में सत्यापित आधिकारिक डेटा की जांच हो रही है...",
        "चरण 3/5: मास्टर डेटा एवं ML फ़ीचर वैक्टर तैयार किए जा रहे हैं...",
        "चरण 4/5: शेष तिथियों के लिए CatBoost AI मॉडल पूर्वानुमान लगा रहा है...",
        "चरण 5/5: सत्यापित पूर्वानुमान और मूल्य सीमाएं अंतिम रूप दी जा रही हैं..."
      ]
    },
    location: {
      detectLocationBtn: "मेरा स्थान खोजें",
      locationDetected: "आपका वर्तमान स्थान",
      nearestMandi: "निकटतम आंध्र प्रदेश मंडी",
      distanceAway: "किमी दूर",
      permissionDenied: "स्थान की अनुमति अस्वीकृत। डिफ़ॉल्ट मंडी चयनित।",
    },
    weather: {
      title: "मौसम सेवा",
      subtitle: "वास्तविक उपग्रह और Open-Meteo मौसम पूर्वानुमान एवं ऐतिहासिक डेटा",
      userLocationWeather: "आपके वर्तमान स्थान का मौसम",
      mandiLocationWeather: "चयनित मंडी का मौसम",
      temperature: "तापमान",
      rain: "वर्षा",
      humidity: "आर्द्रता",
      wind: "हवा की गति",
      extremeAlert: "खराब मौसम की चेतावनी",
      historicalWeather: "ऐतिहासिक मौसम रिकॉर्ड",
      date: "तारीख",
      maxTemp: "अधिकतम तापमान (°C)",
      minTemp: "न्यूनतम तापमान (°C)",
      heavyRainAlert: "भारी बारिश का खतरा",
      extremeHeatAlert: "अत्यधिक गर्मी की चेतावनी (>40°C)",
      district: "ज़िला",
      detectingLocation: "स्थान खोजा जा रहा है...",
      past14Days: "पिछले 14 दिनों का विवरण",
      liveWeather: "लाइव उपग्रह मौसम डेटा"
    },
    schemes: {
      title: "सरकारी कृषि योजनाएं",
      subtitle: "किसानों के लिए केंद्र और राज्य सरकार की वित्तीय सहायता एवं फसल बीमा योजनाएं",
      visitOfficialWebsite: "आधिकारिक वेबसाइट पर जाएं",
      eligibility: "पात्रता मापदंड",
      benefits: "मुख्य लाभ",
      howToApply: "आवेदन कैसे करें",
    },
    disease: {
      tabTitle: "फसल रोग एवं स्वास्थ्य निदान",
      tabSubtitle: "अपनी फसल की पत्ती की तस्वीर अपलोड करें या खींचें। Gemini AI फसल की पहचान करेगा, लक्षणों का विश्लेषण करेगा और उपचार सलाह प्रदान करेगा।",
      badge: "AI-संचालित फसल रोग निदान",
      newAnalysis: "नया निदान",
      history: "निदान इतिहास",
      uploadTitle: "फसल पत्ती की तस्वीर अपलोड करें या खींचें",
      uploadSubtitle: "पत्तियों की तस्वीर यहां खींचें या कैमरा उपयोग करें (JPG, PNG, 10MB तक)",
      browseFiles: "तस्वीर चुनें",
      takePhoto: "तस्वीर खींचें",
      maxImagesHint: "सटीक परिणाम के लिए आप अधिकतम 3 तस्वीरें जोड़ सकते हैं",
      analyzeBtn: "AI से फसल रोग जांचें",
      analyzingBtn: "AI विश्लेषण जारी है...",
      loginPrompt: "फसल रोग विश्लेषण एवं इतिहास सुरक्षित रखने के लिए कृपया लॉगिन करें।",
      notesPlaceholder: "अतिरिक्त लक्षण या खाद आदि का विवरण लिखें...",
      notesLabel: "खेत की टिप्पणियां एवं लक्षण (वैकल्पिक)",
      recognizedCrop: "पहचानी गई फसल",
      primaryDiagnosis: "मुख्य रोग निदान",
      confidence: "विश्वास स्तर",
      botanicalEvidence: "वानस्पतिक एवं दृश्य साक्ष्य",
      immediateAction: "तत्काल आवश्यक उपचार",
      preventiveMeasures: "दीर्घकालिक रोकथाम उपाय",
      chemicalControl: "कीटनाशक एवं कवकनाशी मार्गदर्शन",
      safetyPrecaution: "छिड़काव सुरक्षा सावधानियां",
      disclaimerTitle: "कृषि रोग परामर्श अस्वीकरण",
      disclaimerText: "यह AI द्वारा दिया गया प्रारंभिक रोग निदान सुझाव है। रासायनिक दवाओं के उपयोग से पहले अपने स्थानीय कृषि विस्तार अधिकारी या कृषि विज्ञान केंद्र (KVK) से परामर्श लें।",
      deleteHistory: "हटाएं",
      noHistory: "कोई पूर्व रोग निदान रिकॉर्ड नहीं मिला।"
    },
    chatbot: {
      title: "मंडी मित्र AI चैटबॉट",
      subtitle: "मंडी भाव, मौसम सलाह या योजनाओं के बारे में अपनी भाषा में पूछें",
      placeholder: "मंडी मित्र AI से कोई प्रश्न पूछें...",
      send: "भेजें",
      welcomeMsg: "नमस्ते! मैं मंडी मित्र AI हूँ। मैं आज आपकी क्या सहायता कर सकता हूँ?",
      quickPrompts: [
        "टमाटर का 3-दिवसीय मूल्य पूर्वानुमान क्या है?",
        "टमाटर के लिए कौन सी मंडी सबसे अधिक लाभ देगी?",
        "PM-KISAN योजना की पात्रता क्या है?",
        "आज का मौसम फसल कटाई को कैसे प्रभावित करेगा?"
      ]
    }
  },
  ml: {
    appTitle: "മണ്ഡി വില പ്രവചനം",
    appSubtitle: "കർഷകർക്കായുള്ള AI 3-ദിവസ മണ്ഡി വില പ്രവചനവും നിർദ്ദേശങ്ങളും • ആന്ധ്രപ്രദേശ്",
    tabs: {
      forecast: "വില പ്രവചനം",
      trends: "വില ട്രെൻഡുകൾ",
      disease: "🌿 വിള രോഗങ്ങൾ",
      weather: "കാലാവസ്ഥ",
      schemes: "സർക്കാർ പദ്ധതികൾ",
    },
    forecast: {
      selectCrop: "വിള തിരഞ്ഞെടുക്കുക",
      selectMarket: "എപി മണ്ഡി മാർക്കറ്റ് തിരഞ്ഞെടുക്കുക",
      forecastDate: "പ്രവചന തീയതി",
      generateBtn: "3-ദിവസ പ്രവചനം നേടുക",
      latestObserved: "ഏറ്റവും പുതിയ മണ്ഡി വില",
      expectedTrend: "3-ദിവസ പ്രതീക്ഷിത ട്രെൻഡ്",
      advisoryTitle: "കർഷക തീരുമാന നിർദ്ദേശം",
      disclaimerTitle: "മാർഗ്ഗനിർദ്ദേശ വിവരണം",
      disclaimerText: "ചരിത്രപരമായ മാർക്കറ്റ് ഡാറ്റയും കാലാവസ്ഥയും അടിസ്ഥാനമാക്കിയുള്ള AI മെഷീൻ ലേണിംഗ് മോഡലുകളാണ് ഈ പ്രവചനങ്ങൾ നൽകുന്നത്.",
      day1: "നാളെ (ദിവസം 1)",
      day2: "മറ്റന്നാൾ (ദിവസം 2)",
      day3: "ദിവസം 3",
      confidenceBounds: "80% വിശ്വാസ്യത പരിധി",
      predictedPrice: "പ്രതീക്ഷിക്കുന്ന വില",
      loadingSubtitle: "ഔദ്യോഗിക API → മാസ്റ്റർ ഡാറ്റ → CatBoost AI പ്രവചനം ക്രമത്തിൽ പ്രോസസ്സ് ചെയ്യുന്നു.",
      loadingStages: [
        "ഘട്ടം 1/5: data.gov.in ഔദ്യോഗിക API റെക്കോർഡുകൾ പരിശോധിക്കുന്നു...",
        "ഘട്ടം 2/5: 4 ദിവസത്തെ ഔദ്യോഗിക നിരക്കുകൾ പരിശോധിക്കുന്നു...",
        "ഘട്ടം 3/5: മാസ്റ്റർ ഡാറ്റയും ഫീച്ചർ വെക്ടറുകളും തയ്യാറാക്കുന്നു...",
        "ഘട്ടം 4/5: കാണാതായ തീയതികൾക്കായി CatBoost AI പ്രവചനം നടത്തുന്നു...",
        "ഘട്ടം 5/5: സ്ഥിരീകരിച്ച പ്രവചനങ്ങളും ശ്രേണികളും അന്തിമമാക്കുന്നു..."
      ]
    },
    location: {
      detectLocationBtn: "എന്റെ സ്ഥാനം കണ്ടെത്തുക",
      locationDetected: "നിങ്ങളുടെ നിലവിലെ സ്ഥാനം",
      nearestMandi: "ഏറ്റവും അടുത്തുള്ള മണ്ഡി",
      distanceAway: "കി.മീ അകലെ",
      permissionDenied: "ലൊക്കേഷൻ അനുമതി നൽകിയിട്ടില്ല.",
    },
    weather: {
      title: "കാലാവസ്ഥ വിവരങ്ങൾ",
      subtitle: "തത്സമയ ഉപഗ്രഹ കാലാവസ്ഥ ഡാറ്റയും ചരിത്ര വിവരങ്ങളും",
      userLocationWeather: "നിങ്ങളുടെ ലൊക്കേഷൻ കാലാവസ്ഥ",
      mandiLocationWeather: "മണ്ഡി ലൊക്കേഷൻ കാലാവസ്ഥ",
      temperature: "താപനില",
      rain: "മഴ ലഭ്യത",
      humidity: "ഈർപ്പം",
      wind: "കാറ്റിന്റെ വേഗത",
      extremeAlert: "മോശം കാലാവസ്ഥ മുന്നറിയിപ്പ്",
      historicalWeather: "ചരിത്രപരമായ കാലാവസ്ഥ",
      date: "തീയതി",
      maxTemp: "പരമാവധി താപനില (°C)",
      minTemp: "കുറഞ്ഞ താപനില (°C)",
      heavyRainAlert: "കനത്ത മഴ മുന്നറിയിപ്പ്",
      extremeHeatAlert: "കഠിനമായ ചൂട് മുന്നറിയിപ്പ് (>40°C)",
      district: "ജില്ല",
      detectingLocation: "സ്ഥാനം കണ്ടെത്തുന്നു...",
      past14Days: "കഴിഞ്ഞ 14 ദിവസങ്ങളിലെ വിവരങ്ങൾ",
      liveWeather: "തത്സമയ ഉപഗ്രഹ കാലാവസ്ഥ"
    },
    schemes: {
      title: "സർക്കാർ കാർഷിക പദ്ധതികൾ",
      subtitle: "കർഷകർക്കുള്ള സാമ്പത്തിക സഹായങ്ങളും ഇൻഷുറൻസ് പദ്ധതികളും",
      visitOfficialWebsite: "ഔദ്യോഗിക വെബ്സൈറ്റ് സന്ദർശിക്കുക",
      eligibility: "അർഹത മാനദണ്ഡങ്ങൾ",
      benefits: "പ്രധാന നേട്ടങ്ങൾ",
      howToApply: "അപേക്ഷിക്കേണ്ടവിധം",
    },
    disease: {
      tabTitle: "വിള രോഗനിർണയവും ആരോഗ്യ പരിശോധനയും",
      tabSubtitle: "വിളകളുടെ ഇലകളുടെ ഫോട്ടോ അപ്‌ലോഡ് ചെയ്യുക അല്ലെങ്കിൽ പകർത്തുക. Gemini AI വിള തിരിച്ചറിഞ്ഞ് ചികിത്സാ മാർഗ്ഗങ്ങൾ നൽകും.",
      badge: "AI വിള രോഗനിർണ്ണയം",
      newAnalysis: "പുതിയ പരിശോധന",
      history: "ചരിത്രം",
      uploadTitle: "വിളകളുടെ ചിത്രങ്ങൾ അപ്‌ലോഡ് ചെയ്യുക",
      uploadSubtitle: "ഫോട്ടോ ഡ്രാഗ് ചെയ്യുക അല്ലെങ്കിൽ ക്യാമറ ഉപയോഗിക്കുക",
      browseFiles: "ഫയലുകൾ തിരഞ്ഞെടുക്കുക",
      takePhoto: "ഫോട്ടോ എടുക്കുക",
      maxImagesHint: "പരമാവധി 3 ചിത്രങ്ങൾ വരെ അപ്‌ലോഡ് ചെയ്യാം",
      analyzeBtn: "AI ഉപയോഗിച്ച് രോഗം പരിശോധിക്കുക",
      analyzingBtn: "പരിശോധന പുരോഗമിക്കുന്നു...",
      loginPrompt: "വിള രോഗനിർണയത്തിനായി ലോഗിൻ ചെയ്യുക.",
      notesPlaceholder: "അധിക വിവരങ്ങൾ ചേർക്കുക...",
      notesLabel: "കുറിപ്പുകൾ (ഓപ്ഷണൽ)",
      recognizedCrop: "തിരിച്ചറിഞ്ഞ വിള",
      primaryDiagnosis: "പ്രധാന രോഗനിർണയം",
      confidence: "വിശ്വാസ്യത",
      botanicalEvidence: "ദൃശ്യ തെളിവുകൾ",
      immediateAction: "ഉടൻ സ്വീകരിക്കേണ്ട നടപടികൾ",
      preventiveMeasures: "പ്രതിരോധ മാർഗ്ഗങ്ങൾ",
      chemicalControl: "കീടനാശിനി പ്രയോഗ നിർദ്ദേശങ്ങൾ",
      safetyPrecaution: "സുരക്ഷാ മുൻകരുതലുകൾ",
      disclaimerTitle: "മാർഗ്ഗനിർദ്ദേശ വിവരണം",
      disclaimerText: "ഇതൊരു പ്രാഥമിക AI രോഗനിർണയ ഉപകരണം മാത്രമാണ്. രാസവസ്തുക്കൾ പ്രയോഗിക്കുന്നതിന് മുൻപ് കൃഷി ഓഫീസറുമായി ബന്ധപ്പെടുക.",
      deleteHistory: "നീക്കം ചെയ്യുക",
      noHistory: "മുൻകാല രേഖകളൊന്നുമില്ല."
    },
    chatbot: {
      title: "മണ്ഡി മിത്ര AI ചാറ്റ്ബോട്ട്",
      subtitle: "മാർക്കറ്റ് വിലയും പദ്ധതികളും നിങ്ങളുടെ ഭാഷയിൽ ചോദിച്ചറിയൂ",
      placeholder: "മണ്ഡി മിത്രയോട് ചോദിക്കൂ...",
      send: "അയക്കുക",
      welcomeMsg: "നമസ്കാരം! ഞാൻ മണ്ഡി മിത്ര AI. ഇന്ന് ഞാൻ നിങ്ങളെ എങ്ങനെ സഹായിക്കണം?",
      quickPrompts: [
        "തക്കാളിയുടെ 3 ദിവസത്തെ വില പ്രവചനം എന്താണ്?",
        "ഏറ്റവും ഉയർന്ന ലാഭം നൽകുന്ന മണ്ഡി ഏതാണ്?",
        "പിഎം കിസാൻ പദ്ധതിയുടെ അർഹത എന്താണ്?",
        "ഇന്നത്തെ കാലാവസ്ഥ വിളവെടുപ്പിനെ എങ്ങനെ ബാധിക്കും?"
      ]
    }
  },
  ta: {
    appTitle: "மண்டி விலை கணிப்பு",
    appSubtitle: "விவசாயிகளுக்கான AI 3-நாள் மண்டி சந்தை விலை கணிப்பு & ஆலோசனைகள் • ஆந்திரப் பிரதேசம்",
    tabs: {
      forecast: "விலை கணிப்பு",
      trends: "விலை ஒப்பீடு",
      disease: "🌿 பயிர் நோய்",
      weather: "வானிலை",
      schemes: "அரசு திட்டங்கள்",
    },
    forecast: {
      selectCrop: "பயிரைத் தேர்ந்தெடுக்கவும்",
      selectMarket: "ஆந்திர மண்டி சந்தையைத் தேர்ந்தெடுக்கவும்",
      forecastDate: "கணிப்பு தேதி",
      generateBtn: "3-நாள் கணிப்பைப் பெறுக",
      latestObserved: "சமீபத்திய மண்டி விலை",
      expectedTrend: "3-நாள் எதிர்பார்க்கப்படும் மாற்றம்",
      advisoryTitle: "விவசாயி முடிவு ஆலோசனை",
      disclaimerTitle: "ஆலோசனை வழிகாட்டுதல்",
      disclaimerText: "இந்த கணிப்புகள் வரலாற்று மண்டி தரவு மற்றும் வானிலை ఆధారமாக AI மெஷின் லேர்னிங் மூலம் வழங்கப்படுகின்றன.",
      day1: "நாளை (நாள் 1)",
      day2: "நாளை மறுநாள் (நாள் 2)",
      day3: "நாள் 3",
      confidenceBounds: "80% நம்பிக்கை எல்லை",
      predictedPrice: "கணிக்கப்பட்ட விலை",
      loadingSubtitle: "அதிகாரப்பூர்வ API → மாஸ்டர் தரவு → CatBoost AI கணிப்பு வரிசையில் செயல்படுத்தப்படுகிறது.",
      loadingStages: [
        "நிலை 1/5: data.gov.in அதிகாரப்பூர்வ API பதிவுகளை சரிபார்க்கிறது...",
        "நிலை 2/5: 4-நாள் காலத்திற்கான அதிகாரப்பூர்வ விலைகளை சரிபார்க்கிறது...",
        "நிலை 3/5: மாஸ்டர் தரவு மற்றும் மாதிரி அம்சங்களை உருவாக்குகிறது...",
        "நிலை 4/5: விடுபட்ட தேதிகளுக்கு CatBoost AI மாதிரி கணிப்பை இயக்குகிறது...",
        "நிலை 5/5: சரிபார்க்கப்பட்ட கணிப்புகள் மற்றும் இடைவெளிகளை இறுதி செய்கிறது..."
      ]
    },
    location: {
      detectLocationBtn: "என் இருப்பிடத்தைக் கண்டுபிடி",
      locationDetected: "உங்கள் தற்போதைய இருப்பிடம்",
      nearestMandi: "அருகிலுள்ள ஆந்திர மண்டி",
      distanceAway: "கி.மீ தூரத்தில்",
      permissionDenied: "இருப்பிட அனுமதி மறுக்கப்பட்டது.",
    },
    weather: {
      title: "வானிலை சேவை",
      subtitle: "நேரடி செயற்கைக்கோள் மற்றும் வரலாற்று வானிலை தரவு",
      userLocationWeather: "உங்கள் இருப்பிட வானிலை",
      mandiLocationWeather: "தேர்ந்தெடுக்கப்பட்ட மண்டி வானிலை",
      temperature: "வெப்பநிலை",
      rain: "மழைப்பொழிவு",
      humidity: "ஈரப்பதம்",
      wind: "காற்றின் வேகம்",
      extremeAlert: "கடுமையான வானிலை எச்சரிக்கை",
      historicalWeather: "வரலாற்று வானிலை பதிவு",
      date: "தேதி",
      maxTemp: "அதிகபட்ச வெப்பநிலை (°C)",
      minTemp: "குறைந்தபட்ச வெப்பநிலை (°C)",
      heavyRainAlert: "கனமழை எச்சரிக்கை",
      extremeHeatAlert: "கடும் வெப்ப எச்சரிக்கை (>40°C)",
      district: "மாவட்டம்",
      detectingLocation: "இருப்பிடம் கண்டறியப்படுகிறது...",
      past14Days: "கடந்த 14 நாட்கள் பதிவு",
      liveWeather: "நேரடி செயற்கைக்கோள் வானிலை"
    },
    schemes: {
      title: "அரசு விவசாய திட்டங்கள்",
      subtitle: "மத்திய மற்றும் மாநில அரசு நிதியுதவி மற்றும் பயிர் காப்பீட்டு திட்டங்கள்",
      visitOfficialWebsite: "அதிகாரப்பூர்வ இணையதளத்தைப் பார்வையிடவும்",
      eligibility: "தகுதி வரம்புகள்",
      benefits: "முக்கிய நன்மைகள்",
      howToApply: "விண்ணப்பிக்கும் முறை",
    },
    disease: {
      tabTitle: "பயிர் நோய் மற்றும் சுகாதார கண்டறிதல்",
      tabSubtitle: "உங்கள் பயிர் இலையின் புகைப்படத்தை பதிவேற்றவும் அல்லது படம் எடுக்கவும். Gemini AI பயிரை அடையாளம் கண்டு சிகிச்சை ஆலோசனைகளை வழங்கும்.",
      badge: "AI-இயங்கும் பயிர் நோயியல்",
      newAnalysis: "புதிய ஆய்வு",
      history: "வரலாறு",
      uploadTitle: "பயிர் இலை புகைப்படங்களை பதிவேற்றவும்",
      uploadSubtitle: "படங்களை இங்கே இழுக்கவும் அல்லது கேமராவை பயன்படுத்தவும்",
      browseFiles: "கோப்புகளை தேர்வு செய்க",
      takePhoto: "படம் எடு",
      maxImagesHint: "துல்லியமான முடிவுகளுக்கு 3 படங்கள் வரை சேர்க்கலாம்",
      analyzeBtn: "AI மூலம் பயிர் நோயை கண்டறியவும்",
      analyzingBtn: "AI பகுப்பாய்வு நடக்கிறது...",
      loginPrompt: "பயிர் நோய் ஆய்வு செய்ய உள்நுழையவும்.",
      notesPlaceholder: "கூடுதல் குறிப்புகளை இங்கே எழுதவும்...",
      notesLabel: "குறிப்புகள் (விருப்பத்தேர்வு)",
      recognizedCrop: "கண்டறியப்பட்ட பயிர்",
      primaryDiagnosis: "முதன்மை நோய் கண்டறிதல்",
      confidence: "நம்பகத்தன்மை",
      botanicalEvidence: "காட்சி சான்றுகள்",
      immediateAction: "உடனடி நடவடிக்கை",
      preventiveMeasures: "தடுப்பு முறைகள்",
      chemicalControl: "மருந்து தெளிப்பு வழிகாட்டுதல்",
      safetyPrecaution: "பாதுகாப்பு முன்னெச்சரிக்கைகள்",
      disclaimerTitle: "வழிகாட்டுதல் அறிக்கை",
      disclaimerText: "இது ஒரு ஆரம்பநிலை AI தொழில்நுட்ப ஆலோசனை மட்டுமே. ரசாயன மருந்துகளை தெளிப்பதற்கு முன் உள்ளூர் வேளாண்மை அதிகாரியை அணுகவும்.",
      deleteHistory: "அழிக்கவும்",
      noHistory: "முந்தைய பதிவுகள் எதுவும் இல்லை."
    },
    chatbot: {
      title: "மண்டி மித்ரா AI சேட்பாட்",
      subtitle: "சந்தை விலை மற்றும் அரசு திட்டங்கள் குறித்து உங்கள் மொழியில் கேளுங்கள்",
      placeholder: "மண்டி மித்ராவிடம் கேளுங்கள்...",
      send: "அனுப்பு",
      welcomeMsg: "வணக்கம்! நான் மண்டி மித்ரா AI. இன்று உங்களுக்கு எவ்வாறு உதவ முடியும்?",
      quickPrompts: [
        "தக்காளி 3-நாள் விலை கணிப்பு என்ன?",
        "தக்காளிக்கு அதிக லாபம் தரும் மண்டி எது?",
        "PM-KISAN திட்ட தகுதிகள் என்ன?",
        "இன்றைய வானிலை அறுவடைகளை எவ்வாறு பாதிக்கும்?"
      ]
    }
  }
};
