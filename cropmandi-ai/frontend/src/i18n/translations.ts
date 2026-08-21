export type Language = 'en' | 'te' | 'hi' | 'ml' | 'ta';

export interface TranslationDictionary {
  common: {
    appTitle: string;
    appSubtitle: string;
    login: string;
    signUp: string;
    logout: string;
    loading: string;
    retry: string;
    today: string;
    selectCrop: string;
    selectDistrict: string;
    selectMarket: string;
    unitQuintal: string;
    location: string;
    andhraPradesh: string;
    allMarkets: string;
    back: string;
    close: string;
    save: string;
    refresh: string;
    verified: string;
  };
  tabs: {
    forecast: string;
    trends: string;
    disease: string;
    weather: string;
    schemes: string;
  };
  forecast: {
    title: string;
    subtitle: string;
    selectCrop: string;
    selectMarket: string;
    baseDate: string;
    targetDate: string;
    observationDate: string;
    forecastOrigin: string;
    forecastDate: string;
    generateBtn: string;
    generate: string;
    generating: string;
    fetchingOfficialData: string;
    updatingRecords: string;
    rebuildingFeatures: string;
    preparingPredictions: string;
    latestModalPrice: string;
    latestOfficialValue: string;
    latestOfficialDate: string;
    dataAge: string;
    currentOneDayTrend: string;
    expectedTrend: string;
    threeDayForecast: string;
    officialApiValue: string;
    officialDatabaseValue: string;
    officialCsvValue: string;
    predictedModelValue: string;
    fallbackValue: string;
    priceUnavailable: string;
    confidenceInterval: string;
    low: string;
    high: string;
    sell: string;
    hold: string;
    buy: string;
    sellOrHold: string;
    sellNow: string;
    holdCrop: string;
    stableTrend: string;
    upwardTrend: string;
    downwardTrend: string;
    trendUnavailable: string;
    todayOfficialUnavailable: string;
    showingLatestOfficialValue: string;
    staleDataWarning: string;
    dataVerification: string;
    apiChecked: string;
    csvChecked: string;
    predictionGenerated: string;
    source: string;
    modelVersion: string;
    advisoryTitle: string;
    disclaimerTitle: string;
    disclaimerText: string;
    day1: string;
    day2: string;
    day3: string;
    confidenceBounds: string;
    predictedPrice: string;
    currentPriceCardTitle: string;
    currentPriceCardSubtitle: string;
    historyPriceCardTitle: string;
    historyPriceCardSubtitle: string;
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
  trends: {
    title: string;
    subtitle: string;
    noRecentData: string;
    officialOnly: string;
    selectCrop: string;
    selectMarket: string;
    timeframe: string;
    last30Days: string;
    modalPrice: string;
    arrivalQuantity: string;
    minMaxRange: string;
    recordedPrices: string;
    gapsExplanation: string;
  };
  comparison: {
    title: string;
    subtitle: string;
    noRecentOfficialData: string;
    selectCrop: string;
    highestPrice: string;
    lowestPrice: string;
    averagePrice: string;
    distance: string;
    priceDiff: string;
    bestMandi: string;
    compareBtn: string;
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
    unavailable: string;
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
  auth: {
    loginTitle: string;
    signUpTitle: string;
    emailLabel: string;
    passwordLabel: string;
    fullNameLabel: string;
    roleLabel: string;
    farmerRole: string;
    traderRole: string;
    adminRole: string;
    loginBtn: string;
    signUpBtn: string;
    dontHaveAccount: string;
    alreadyHaveAccount: string;
  };
  validation: {
    requiredField: string;
    invalidEmail: string;
    passwordTooShort: string;
    futureDateNotAllowed: string;
    selectBothCropAndMarket: string;
  };
  errors: {
    apiUnavailable: string;
    futureDateNotAllowed: string;
    noData: string;
    modelUnavailable: string;
    serverError: string;
    networkError: string;
  };
  warnings: {
    predictionIsEstimate: string;
    dataMayBeStale: string;
    noOfficialValueForToday: string;
    fallbackUsed: string;
  };
  chatbot: {
    title: string;
    subtitle: string;
    placeholder: string;
    send: string;
    welcomeMsg: string;
    quickPrompts: string[];
  };
  
  // Backward-compatibility shortcuts
  appTitle?: string;
  appSubtitle?: string;
}

export const translations: Record<Language, TranslationDictionary> = {
  en: {
    common: {
      appTitle: "Mandi Price Prediction",
      appSubtitle: "AI-Powered Mandi Price Forecast & Advisory • Andhra Pradesh",
      login: "Log In",
      signUp: "Sign Up",
      logout: "Log Out",
      loading: "Loading...",
      retry: "Retry",
      today: "Today",
      selectCrop: "Select Crop / Commodity",
      selectDistrict: "Select District",
      selectMarket: "Select AP Mandi Market",
      unitQuintal: "₹/Quintal",
      location: "Location",
      andhraPradesh: "Andhra Pradesh",
      allMarkets: "All Mandis",
      back: "Back",
      close: "Close",
      save: "Save",
      refresh: "Refresh",
      verified: "Verified"
    },
    tabs: {
      forecast: "Price Forecast",
      trends: "Trends & Compare",
      disease: "🌿 Crop Disease",
      weather: "Weather",
      schemes: "Govt Schemes"
    },
    forecast: {
      title: "Mandi Price Forecast",
      subtitle: "Official data-driven price intelligence and machine learning forecast for Andhra Pradesh mandis",
      selectCrop: "Select Crop / Commodity",
      selectMarket: "Select AP Mandi Market",
      baseDate: "Forecast Base Date",
      targetDate: "Target Date",
      observationDate: "Observation Date",
      forecastOrigin: "Forecast Origin",
      forecastDate: "Forecast Base Date",
      generateBtn: "Generate 3-Day Forecast",
      generate: "Generate Forecast",
      generating: "Generating...",
      fetchingOfficialData: "Fetching official data...",
      updatingRecords: "Updating official records...",
      rebuildingFeatures: "Rebuilding features...",
      preparingPredictions: "Preparing predictions...",
      latestModalPrice: "Latest Observed Modal Price",
      latestOfficialValue: "Latest Official Value",
      latestOfficialDate: "Observation Date",
      dataAge: "Data Age",
      currentOneDayTrend: "1-Day Expected Trend",
      expectedTrend: "Expected Trend",
      threeDayForecast: "3-Day Price Forecast",
      officialApiValue: "Official API Value",
      officialDatabaseValue: "Official Database Record",
      officialCsvValue: "Official Master CSV Value",
      predictedModelValue: "Predicted Model Value",
      fallbackValue: "Fallback Baseline Value",
      priceUnavailable: "Price Unavailable",
      confidenceInterval: "Prediction Interval",
      low: "Low",
      high: "High",
      sell: "SELL",
      hold: "HOLD",
      buy: "BUY",
      sellOrHold: "SELL OR HOLD",
      sellNow: "SELL NOW",
      holdCrop: "HOLD CROP",
      stableTrend: "Stable Trend",
      upwardTrend: "Upward Trend",
      downwardTrend: "Downward Trend",
      trendUnavailable: "Trend Unavailable",
      todayOfficialUnavailable: "Today's official mandi arrival value is not yet published.",
      showingLatestOfficialValue: "Showing latest verified official observation.",
      staleDataWarning: "Official data is older than 2 days. data.gov.in has not published newer records.",
      dataVerification: "Data Verification & Trace",
      apiChecked: "Official API Checked",
      csvChecked: "Master CSV Checked",
      predictionGenerated: "Prediction Generated",
      source: "Price Source",
      modelVersion: "Model Version",
      advisoryTitle: "Farmer Decision Advisory",
      disclaimerTitle: "Decision Support Advisory Disclaimer",
      disclaimerText: "Predictions are computed using CatBoost machine learning models based on historic APMC market arrivals, prices, and weather trends. Use as decision guidance alongside local market inquiries.",
      day1: "Tomorrow (Day 1)",
      day2: "Day +2",
      day3: "Day +3",
      confidenceBounds: "Prediction Interval",
      predictedPrice: "Predicted Modal Price",
      currentPriceCardTitle: "Official Today Modal Price",
      currentPriceCardSubtitle: "Genuine recorded official observation from APMC Mandi",
      historyPriceCardTitle: "Historical Official Price",
      historyPriceCardSubtitle: "Recorded official observation for the selected date",
      loadingSubtitle: "Executing strict 5-level precedence: Official API (data.gov.in) → master-data.csv → Database → CatBoost ML Prediction → Fallback → Unavailable.",
      loadingStages: [
        "Stage 1 of 5: Querying official data.gov.in API records with filters...",
        "Stage 2 of 5: Checking verified official records across horizon...",
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
      permissionDenied: "Location permission denied. Defaulting to AP central markets."
    },
    trends: {
      title: "Price Trends & History",
      subtitle: "Authentic historical mandi prices exclusively from official observations over the last 30 days",
      noRecentData: "No official price observations found in the last 30 days for the selected crop and market.",
      officialOnly: "Exclusively Official Observed Records (No ML Predictions / Synthetic Data)",
      selectCrop: "Filter by Crop",
      selectMarket: "Filter by Mandi",
      timeframe: "Timeframe",
      last30Days: "Last 30 Days",
      modalPrice: "Modal Price (₹/Quintal)",
      arrivalQuantity: "Arrival Quantity (MT)",
      minMaxRange: "Min - Max Price Range",
      recordedPrices: "Recorded Mandi Prices",
      gapsExplanation: "Data gaps indicate market holidays or dates when no official trade was recorded."
    },
    comparison: {
      title: "Mandi Price Comparison",
      subtitle: "Compare latest official mandi prices across Andhra Pradesh APMC yards",
      noRecentOfficialData: "No recent official price observations available for comparison.",
      selectCrop: "Select Crop to Compare",
      highestPrice: "Highest Modal Price",
      lowestPrice: "Lowest Modal Price",
      averagePrice: "Average Mandi Price",
      distance: "Distance",
      priceDiff: "Price Difference",
      bestMandi: "Best Value Mandi",
      compareBtn: "Compare Mandis"
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
      liveWeather: "Live Satellite & Open-Meteo Weather",
      unavailable: "Weather data unavailable for this market"
    },
    schemes: {
      title: "Government Agricultural Schemes",
      subtitle: "Official central & state financial assistance, crop insurance, and market welfare for farmers",
      visitOfficialWebsite: "Visit Official Portal",
      eligibility: "Eligibility Criteria",
      benefits: "Key Benefits",
      howToApply: "How to Apply"
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
      disclaimerTitle: "Pathology Advisory Disclaimer",
      disclaimerText: "Diagnosis is generated using computer vision AI. Consult your local Mandal Agricultural Officer (MAO) before large-scale pesticide application.",
      deleteHistory: "Delete Record",
      noHistory: "No prior diagnostic records found."
    },
    auth: {
      loginTitle: "Log In to CropMandi AI",
      signUpTitle: "Create Your CropMandi Account",
      emailLabel: "Email Address",
      passwordLabel: "Password",
      fullNameLabel: "Full Name",
      roleLabel: "Role",
      farmerRole: "Farmer / Grower",
      traderRole: "Trader / Buyer",
      adminRole: "Agricultural Officer / Admin",
      loginBtn: "Log In",
      signUpBtn: "Create Account",
      dontHaveAccount: "Don't have an account? Sign up",
      alreadyHaveAccount: "Already have an account? Log in"
    },
    validation: {
      requiredField: "This field is required.",
      invalidEmail: "Please enter a valid email address.",
      passwordTooShort: "Password must be at least 6 characters long.",
      futureDateNotAllowed: "Forecast base date cannot be in the future.",
      selectBothCropAndMarket: "Please select both a crop and a market."
    },
    errors: {
      apiUnavailable: "Official data.gov.in API is temporarily unreachable.",
      futureDateNotAllowed: "Selected date cannot be in the future.",
      noData: "No price records found for this selection.",
      modelUnavailable: "Machine learning prediction model is currently unavailable.",
      serverError: "An unexpected server error occurred. Please try again.",
      networkError: "Network connection failed. Please check your internet."
    },
    warnings: {
      predictionIsEstimate: "Predictions are estimates based on historical machine learning models.",
      dataMayBeStale: "Official mandi data has not been updated in the last 2 days.",
      noOfficialValueForToday: "Official mandi price for today has not yet been published.",
      fallbackUsed: "A fallback baseline estimate was used because model inference was unavailable."
    },
    chatbot: {
      title: "CropMandi AI Farmer Assistant",
      subtitle: "Ask in English, Telugu, Hindi, Malayalam, or Tamil about market rates, crop diseases, and schemes",
      placeholder: "Ask a question about prices, mandi trends, diseases...",
      send: "Send",
      welcomeMsg: "Namaste! I am your CropMandi AI Assistant. How can I help you today?",
      quickPrompts: [
        "What is the latest tomato price in Madanapalle?",
        "Should I sell or hold my chili harvest?",
        "How to prevent leaf spot disease in cotton?",
        "Tell me about PM-KISAN scheme eligibility."
      ]
    }
  },

  te: {
    common: {
      appTitle: "మార్కెట్ ధరల అంచనా",
      appSubtitle: "ఆంధ్రప్రదేశ్ రైతుల కోసం AI ఆధారిత మార్కెట్ ధరల అంచనా & సలహా",
      login: "లాగిన్",
      signUp: "సైన్ అప్",
      logout: "లాగ్ అవుట్",
      loading: "లోడ్ అవుతోంది...",
      retry: "మళ్ళీ ప్రయత్నించండి",
      today: "ఈరోజు",
      selectCrop: "పంటను ఎంచుకోండి",
      selectDistrict: "జిల్లాను ఎంచుకోండి",
      selectMarket: "మార్కెట్ యార్డ్ ఎంచుకోండి",
      unitQuintal: "₹/క్వింటాల్",
      location: "ప్రాంతం",
      andhraPradesh: "ఆంధ్రప్రదేశ్",
      allMarkets: "అన్ని మార్కెట్లు",
      back: "వెనుకకు",
      close: "మూసివేయి",
      save: "సేవ్ చేయి",
      refresh: "తాజాకరించు",
      verified: "ధృవీకరించబడింది"
    },
    tabs: {
      forecast: "ధరల అంచనా",
      trends: "ట్రెండ్స్ & పోలిక",
      disease: "🌿 పంట తెగుళ్లు",
      weather: "వాతావరణం",
      schemes: "ప్రభుత్వ పథకాలు"
    },
    forecast: {
      title: "మార్కెట్ ధరల అంచనా",
      subtitle: "ఆంధ్రప్రదేశ్ మార్కెట్ల కోసం అధికారిక డేటా మరియు మెషిన్ లెర్నింగ్ ధరల అంచనా",
      selectCrop: "పంటను ఎంచుకోండి",
      selectMarket: "మార్కెట్ యార్డ్ ఎంచుకోండి",
      baseDate: "అంచనా తేదీ",
      targetDate: "లక్ష్య తేదీ",
      observationDate: "రికార్డు తేదీ",
      forecastOrigin: "అంచనా మూలం",
      forecastDate: "అంచనా తేదీ",
      generateBtn: "ధరల అంచనా పొందండి",
      generate: "అంచనా పొందండి",
      generating: "అంచనా వేస్తోంది...",
      fetchingOfficialData: "అధికారిక డేటాను తెస్తోంది...",
      updatingRecords: "రికార్డులను నవీకరిస్తోంది...",
      rebuildingFeatures: "ఫీచర్లను పునర్నిర్మిస్తోంది...",
      preparingPredictions: "అంచనాలను సిద్ధం చేస్తోంది...",
      latestModalPrice: "తాజా మోడల్ ధర",
      latestOfficialValue: "తాజా అధికారిక ధర",
      latestOfficialDate: "రికార్డు తేదీ",
      dataAge: "డేటా వయస్సు",
      currentOneDayTrend: "1-రోజు ట్రెండ్",
      expectedTrend: "ఆశించిన ట్రెండ్",
      threeDayForecast: "3 రోజుల ధరల అంచనా",
      officialApiValue: "అధికారిక API విలువ",
      officialDatabaseValue: "డేటాబేస్ అధికారిక రికార్డు",
      officialCsvValue: "అధికారిక CSV రికార్డు",
      predictedModelValue: "మోడల్ అంచనా వేసిన ధర",
      fallbackValue: "బేస్‌లైన్ ధర",
      priceUnavailable: "ధర అందుబాటులో లేదు",
      confidenceInterval: "ధర అంచనా పరిధి",
      low: "కనిష్ట",
      high: "గరిష్ట",
      sell: "అమ్మండి",
      hold: "నిల్వ ఉంచండి",
      buy: "కొనండి",
      sellOrHold: "అమ్మండి లేదా నిల్వ ఉంచండి",
      sellNow: "వెంటనే అమ్మండి",
      holdCrop: "పంటను నిల్వ ఉంచండి",
      stableTrend: "స్థిరమైన ట్రెండ్",
      upwardTrend: "పెరుగుతున్న ట్రెండ్",
      downwardTrend: "తగ్గుతున్న ట్రెండ్",
      trendUnavailable: "ట్రెండ్ అందుబాటులో లేదు",
      todayOfficialUnavailable: "ఈరోజు అధికారిక మార్కెట్ ధర ఇంకా ప్రచురించబడలేదు.",
      showingLatestOfficialValue: "లభించిన తాజా అధికారిక రికార్డును చూపుతోంది.",
      staleDataWarning: "అధికారిక డేటా 2 రోజుల కంటే పాతది. data.gov.in లో కొత్త డేటా రాలేదు.",
      dataVerification: "డేటా ధృవీకరణ వివరాలు",
      apiChecked: "అధికారిక API తనిఖీ చేయబడింది",
      csvChecked: "మాస్టర్ CSV తనిఖీ చేయబడింది",
      predictionGenerated: "అంచనా రూపొందించబడింది",
      source: "ధర మూలం",
      modelVersion: "మోడల్ వెర్షన్",
      advisoryTitle: "రైతు నిర్ణయ సలహా",
      disclaimerTitle: "సలహాదారు నిరాకరణ",
      disclaimerText: "గత APMC మార్కెట్ రాకలు, ధరలు మరియు వాతావరణ ట్రెండ్‌ల ఆధారంగా CatBoost మెషిన్ లెర్నింగ్ మోడల్‌లను ఉపయోగించి అంచనాలు లెక్కించబడతాయి.",
      day1: "రేపు (మొదటి రోజు)",
      day2: "2వ రోజు",
      day3: "3వ రోజు",
      confidenceBounds: "ధర అంచనా పరిధి",
      predictedPrice: "అంచనా వేసిన మోడల్ ధర",
      currentPriceCardTitle: "ఈనాటి అధికారిక మోడల్ ధర",
      currentPriceCardSubtitle: "APMC మార్కెట్ యార్డ్ నుండి ధృవీకరించబడిన తాజా రికార్డు",
      historyPriceCardTitle: "చారిత్రక అధికారిక ధర",
      historyPriceCardSubtitle: "ఎంచుకున్న తేదీకి మార్కెట్ యార్డ్ అధికారిక రికార్డు",
      loadingSubtitle: "ఖచ్చితమైన 5-స్థాయి ప్రాధాన్యతను అమలు చేస్తోంది: అధికారిక API → CSV → డేటాబేస్ → ML అంచనా → ఫాల్‌బ్యాక్.",
      loadingStages: [
        "దశ 1/5: data.gov.in అధికారిక API నుండి రికార్డులను శోధిస్తోంది...",
        "దశ 2/5: అధికారిక రికార్డులను ధృవీకరిస్తోంది...",
        "దశ 3/5: మాస్టర్ డేటాను తనిఖీ చేసి ఫీచర్లను సిద్ధం చేస్తోంది...",
        "దశ 4/5: మిగిలిన తేదీలకు CatBoost ML మోడల్ ద్వారా అంచనా వేస్తోంది...",
        "దశ 5/5: తుది ధరల అంచనా మరియు పరిధులను సిద్ధం చేస్తోంది..."
      ]
    },
    location: {
      detectLocationBtn: "నా స్థానాన్ని గుర్తించు",
      locationDetected: "మీ ప్రస్తుత స్థానం",
      nearestMandi: "సమీప మార్కెట్ యార్డ్",
      distanceAway: "కి.మీ దూరం",
      permissionDenied: "లొకేషన్ అనుమతి నిరాకరించబడింది."
    },
    trends: {
      title: "ధరల ట్రెండ్స్ & చరిత్ర",
      subtitle: "గత 30 రోజుల్లో అధికారిక మార్కెట్ రికార్డుల ఆధారంగా ధరల విశ్లేషణ",
      noRecentData: "గత 30 రోజుల్లో ఈ పంట మరియు మార్కెట్‌కు అధికారిక రికార్డులు లేవు.",
      officialOnly: "కేవలం అధికారిక రికార్డులు మాత్రమే (అంచనాలు లేవు)",
      selectCrop: "పంటను ఎంచుకోండి",
      selectMarket: "మార్కెట్‌ను ఎంచుకోండి",
      timeframe: "సమయం",
      last30Days: "గత 30 రోజులు",
      modalPrice: "మోడల్ ధర (₹/క్వింటాల్)",
      arrivalQuantity: "రాక పరిమాణం (టన్నులు)",
      minMaxRange: "కనిష్ట - గరిష్ట ధరల పరిధి",
      recordedPrices: "రికార్డ్ చేయబడిన ధరలు",
      gapsExplanation: "డేటా లేని తేదీలు మార్కెట్ సెలవులను సూచిస్తాయి."
    },
    comparison: {
      title: "మార్కెట్ ధరల పోలిక",
      subtitle: "ఆంధ్రప్రదేశ్ మార్కెట్ యార్డుల మధ్య తాజా అధికారిక ధరలను పోల్చండి",
      noRecentOfficialData: "పోలికకు తాజా అధికారిక ధరలు అందుబాటులో లేవు.",
      selectCrop: "పోల్చడానికి పంటను ఎంచుకోండి",
      highestPrice: "అత్యధిక మోడల్ ధర",
      lowestPrice: "అత్యల్ప మోడల్ ధర",
      averagePrice: "సగటు ధర",
      distance: "దూరం",
      priceDiff: "ధర వ్యత్యాసం",
      bestMandi: "ఉత్తమ మార్కెట్",
      compareBtn: "పోల్చండి"
    },
    weather: {
      title: "వాతావరణ సమాచారం",
      subtitle: "లైవ్ శాటిలైట్ మరియు పంటల వాతావరణ సమాచారం",
      userLocationWeather: "మీ ప్రాంత వాతావరణం",
      mandiLocationWeather: "మార్కెట్ యార్డ్ వాతావరణం",
      temperature: "ఉష్ణోగ్రత",
      rain: "వర్షపాతం",
      humidity: "తేమ",
      wind: "గాలి వేగం",
      extremeAlert: "తీవ్ర వాతావరణ హెచ్చరిక",
      historicalWeather: "గత వాతావరణ వివరాలు",
      date: "తేదీ",
      maxTemp: "గరిష్ట ఉష్ణోగ్రత (°C)",
      minTemp: "కనిష్ట ఉష్ణోగ్రత (°C)",
      heavyRainAlert: "భారీ వర్షపాతం ప్రమాదం",
      extremeHeatAlert: "తీవ్ర ఎండ హెచ్చరిక (>40°C)",
      district: "జిల్లా",
      detectingLocation: "స్థానాన్ని గుర్తిస్తోంది...",
      past14Days: "గత 14 రోజులు",
      liveWeather: "లైవ్ వాతావరణం",
      unavailable: "ఈ మార్కెట్‌కు వాతావరణ డేటా అందుబాటులో లేదు"
    },
    schemes: {
      title: "ప్రభుత్వ వ్యవసాయ పథకాలు",
      subtitle: "రైతుల కోసం కేంద్ర మరియు రాష్ట్ర ప్రభుత్వ ఆర్థిక సహాయం, పంట బీమా పథకాలు",
      visitOfficialWebsite: "అధికారిక వెబ్‌సైట్ చూడండి",
      eligibility: "అర్హత నిబంధనలు",
      benefits: "ప్రయోజనాలు",
      howToApply: "దరఖాస్తు విధానం"
    },
    disease: {
      tabTitle: "పంట తెగుళ్లు & వ్యాధి నిర్ధారణ",
      tabSubtitle: "పంట ఆకుల ఫోటోను అప్‌లోడ్ చేయండి. Gemini AI తెగులును గుర్తించి చికిత్స సలహాలను అందిస్తుంది.",
      badge: "AI పంట రక్షణ",
      newAnalysis: "కొత్త విశ్లేషణ",
      history: "గత రికార్డులు",
      uploadTitle: "ఆకుల ఫోటోను అప్‌లోడ్ చేయండి",
      uploadSubtitle: "ఫోటోను డ్రాగ్ చేయండి లేదా కెమెరా ఉపయోగించండి",
      browseFiles: "ఫైల్‌లను ఎంచుకోండి",
      takePhoto: "ఫోటో తీయండి",
      maxImagesHint: "3 ఫోటోల వరకు అప్‌లోడ్ చేయవచ్చు",
      analyzeBtn: "తెగులును విశ్లేషించండి",
      analyzingBtn: "AI విశ్లేషణ చేస్తోంది...",
      loginPrompt: "తెగుళ్ల నిర్ధారణ కోసం దయచేసి లాగిన్ అవ్వండి.",
      notesPlaceholder: "మీ పరిశీలనలను రాయండి...",
      notesLabel: "రైతు పరిశీలనలు (ఐచ్ఛికం)",
      recognizedCrop: "గుర్తించిన పంట",
      primaryDiagnosis: "వ్యాధి నిర్ధారణ",
      confidence: "ఖచ్చితత్వం",
      botanicalEvidence: "లక్షణాలు & ఆధారాలు",
      immediateAction: "వెంటనే చేయవలసిన పనులు",
      preventiveMeasures: "నివారణ చర్యలు",
      chemicalControl: "రసాయన మందుల వాడకం",
      safetyPrecaution: "జాగ్రత్తలు",
      disclaimerTitle: "సలహా నిరాకరణ",
      disclaimerText: "ఇది కంప్యూటర్ విజన్ AI ద్వారా ఇవ్వబడిన సలహా. మందులు వాడే ముందు వ్యవసాయ అధికారిని సంప్రదించండి.",
      deleteHistory: "తొలగించు",
      noHistory: "గత రికార్డులు ఏవీ లేవు."
    },
    auth: {
      loginTitle: "లాగిన్ అవ్వండి",
      signUpTitle: "ఖాతా సృష్టించండి",
      emailLabel: "ఈమెయిల్ చిరునామా",
      passwordLabel: "పాస్‌వర్డ్",
      fullNameLabel: "పూర్తి పేరు",
      roleLabel: "పాత్ర",
      farmerRole: "రైతు",
      traderRole: "వ్యాపారి",
      adminRole: "అధికారి / అడ్మిన్",
      loginBtn: "లాగిన్",
      signUpBtn: "ఖాతా తెరవండి",
      dontHaveAccount: "ఖాతా లేదా? సైన్ అప్ చేయండి",
      alreadyHaveAccount: "ఖాతా ఉందా? లాగిన్ అవ్వండి"
    },
    validation: {
      requiredField: "ఈ వివరాలు అవసరం.",
      invalidEmail: "సరైన ఈమెయిల్ చిరునామాను నమోదు చేయండి.",
      passwordTooShort: "పాస్‌వర్డ్ కనీసం 6 అక్షరాలు ఉండాలి.",
      futureDateNotAllowed: "భవిష్యత్ తేదీని ఎంచుకోలేరు.",
      selectBothCropAndMarket: "దయచేసి పంట మరియు మార్కెట్ రెండింటినీ ఎంచుకోండి."
    },
    errors: {
      apiUnavailable: "అధికారిక API అందుబాటులో లేదు.",
      futureDateNotAllowed: "ఎంచుకున్న తేదీ భవిష్యత్తులో ఉండకూడదు.",
      noData: "ఈ ఎంపికకు ధరల వివరాలు లేవు.",
      modelUnavailable: "AI అంచనా మోడల్ ప్రస్తుతం అందుబాటులో లేదు.",
      serverError: "సర్వర్ లోపం ఏర్పడింది. దయచేసి మళ్ళీ ప్రయత్నించండి.",
      networkError: "ఇంటర్నెట్ కనెక్షన్ విఫలమైంది."
    },
    warnings: {
      predictionIsEstimate: "ధరల అంచనాలు మెషిన్ లెర్నింగ్ ద్వారా రూపొందించబడినవి.",
      dataMayBeStale: "గత 2 రోజులుగా మార్కెట్ డేటా అప్‌డేట్ కాలేదు.",
      noOfficialValueForToday: "ఈరోజు అధికారిక మార్కెట్ ధర ఇంకా రాలేదు.",
      fallbackUsed: "మోడల్ అందుబాటులో లేనందున బేస్‌లైన్ ధర ఉపయోగించబడింది."
    },
    chatbot: {
      title: "రైతు సహాయక AI చాట్‌బాట్",
      subtitle: "మార్కెట్ ధరలు, పంట తెగుళ్లు మరియు ప్రభుత్వ పథకాల గురించి తెలుగులో అడగండి",
      placeholder: "ధరలు లేదా పంటల గురించి ఏదైనా అడగండి...",
      send: "పంపు",
      welcomeMsg: "నమస్కారం! నేను మీ CropMandi AI సహాయకుడిని. ఈరోజు మీకు ఎలా సహాయపడగలను?",
      quickPrompts: [
        "మదనపల్లెలో తాజా టమోటా ధర ఎంత?",
        "మిరప పంటను ఇప్పుడు అమ్మాలా లేదా నిల్వ చేయాలా?",
        "పత్తిలో ఆకుమచ్చ తెగులు నివారణ ఎలా?",
        "పీఎం కిసాన్ పథకం అర్హతలు ఏమిటి?"
      ]
    }
  },

  hi: {
    common: {
      appTitle: "मंडी मूल्य भविष्यवाणी",
      appSubtitle: "आंध्र प्रदेश के किसानों के लिए AI-आधारित मंडी मूल्य पूर्वानुमान और सलाह",
      login: "लॉग इन",
      signUp: "साइन अप",
      logout: "लॉग आउट",
      loading: "लोड हो रहा है...",
      retry: "पुनः प्रयास करें",
      today: "आज",
      selectCrop: "फसल / कमोडिटी चुनें",
      selectDistrict: "ज़िला चुनें",
      selectMarket: "मंडी चुनें",
      unitQuintal: "₹/क्विंटल",
      location: "स्थान",
      andhraPradesh: "आंध्र प्रदेश",
      allMarkets: "सभी मंडियां",
      back: "पीछे",
      close: "बंद करें",
      save: "सहेजें",
      refresh: "ताज़ा करें",
      verified: "सत्यापित"
    },
    tabs: {
      forecast: "मूल्य पूर्वानुमान",
      trends: "रुझान और तुलना",
      disease: "🌿 फसल रोग",
      weather: "मौसम",
      schemes: "सरकारी योजनाएं"
    },
    forecast: {
      title: "मंडी मूल्य पूर्वानुमान",
      subtitle: "आधिकारिक डेटा और मशीन लर्निंग पर आधारित 3-दिवसीय मूल्य पूर्वानुमान",
      selectCrop: "फसल / कमोडिटी चुनें",
      selectMarket: "मंडी चुनें",
      baseDate: "पूर्वानुमान आधार तिथि",
      targetDate: "लक्षित तिथि",
      observationDate: "निरीक्षण तिथि",
      forecastOrigin: "पूर्वानुमान मूल",
      forecastDate: "पूर्वानुमान तिथि",
      generateBtn: "3-दिवसीय पूर्वानुमान प्राप्त करें",
      generate: "पूर्वानुमान प्राप्त करें",
      generating: "पूर्वानुमान बन रहा है...",
      fetchingOfficialData: "आधिकारिक डेटा प्राप्त किया जा रहा है...",
      updatingRecords: "रिकॉर्ड अपडेट हो रहे हैं...",
      rebuildingFeatures: "फ़ीचर्स तैयार हो रहे हैं...",
      preparingPredictions: "अनुमान तैयार हो रहे हैं...",
      latestModalPrice: "नवीनतम मॉडल मूल्य",
      latestOfficialValue: "नवीनतम आधिकारिक मूल्य",
      latestOfficialDate: "निरीक्षण तिथि",
      dataAge: "डेटा की आयु",
      currentOneDayTrend: "1-दिवसीय रुझान",
      expectedTrend: "अपेक्षित रुझान",
      threeDayForecast: "3-दिवसीय मूल्य पूर्वानुमान",
      officialApiValue: "आधिकारिक API मूल्य",
      officialDatabaseValue: "डेटाबेस आधिकारिक रिकॉर्ड",
      officialCsvValue: "आधिकारिक CSV रिकॉर्ड",
      predictedModelValue: "मॉडल द्वारा अनुमानित मूल्य",
      fallbackValue: "बेसलाइन मूल्य",
      priceUnavailable: "मूल्य अनुपलब्ध",
      confidenceInterval: "मूल्य अनुमान सीमा",
      low: "न्यूनतम",
      high: "अधिकतम",
      sell: "बेचें",
      hold: "रोकें (HOLD)",
      buy: "खरीदें",
      sellOrHold: "बेचें या रोकें",
      sellNow: "अभी बेचें",
      holdCrop: "फसल रोकें",
      stableTrend: "स्थिर रुझान",
      upwardTrend: "बढ़ता रुझान",
      downwardTrend: "घटता रुझान",
      trendUnavailable: "रुझान अनुपलब्ध",
      todayOfficialUnavailable: "आज का आधिकारिक मंडी भाव अभी प्रकाशित नहीं हुआ है।",
      showingLatestOfficialValue: "उपलब्ध नवीनतम सत्यापित आधिकारिक अवलोकन दिखाया जा रहा है।",
      staleDataWarning: "आधिकारिक डेटा 2 दिन से अधिक पुराना है।",
      dataVerification: "डेटा सत्यापन और ट्रेस",
      apiChecked: "आधिकारिक API जांची गई",
      csvChecked: "मास्टर CSV जांची गई",
      predictionGenerated: "पूर्वानुमान जनरेट हुआ",
      source: "मूल्य स्रोत",
      modelVersion: "मॉडल संस्करण",
      advisoryTitle: "किसान निर्णय सलाह",
      disclaimerTitle: "सलाह अस्वीकरण",
      disclaimerText: "पूर्वानुमान ऐतिहासिक APMC मंडी आवक, मूल्यों और मौसम के रुझानों पर CatBoost मशीन लर्निंग मॉडल द्वारा तैयार किए जाते हैं।",
      day1: "कल (दिन 1)",
      day2: "दिन +2",
      day3: "दिन +3",
      confidenceBounds: "अनुमान सीमा",
      predictedPrice: "अनुमानित मॉडल मूल्य",
      currentPriceCardTitle: "आज का आधिकारिक मॉडल मूल्य",
      currentPriceCardSubtitle: "APMC मंडी से सत्यापित वास्तविक आधिकारिक रिकॉर्ड",
      historyPriceCardTitle: "ऐतिहासिक आधिकारिक मूल्य",
      historyPriceCardSubtitle: "चयनित तिथि के लिए आधिकारिक रिकॉर्ड",
      loadingSubtitle: "सख्त 5-स्तरीय प्राथमिकता: आधिकारिक API → CSV → डेटाबेस → CatBoost ML → फॉलबैक।",
      loadingStages: [
        "चरण 1/5: data.gov.in आधिकारिक API से मंडी मूल्य रिकॉर्ड प्राप्त किए जा रहे हैं...",
        "चरण 2/5: 4-दिवसीय क्षितिज पर सत्यापित आधिकारिक रिकॉर्ड की जांच हो रही है...",
        "चरण 3/5: मास्टर डेटा की जांच और फ़ीचर वेक्टर्स का निर्माण...",
        "चरण 4/5: शेष तिथियों के लिए CatBoost ML मॉडल इंफ़रेंस निष्पादित किया जा रहा है...",
        "चरण 5/5: सत्यापित पूर्वानुमान और कॉन्फ़ॉर्मल इंटरवल्स को अंतिम रूप दिया जा रहा है..."
      ]
    },
    location: {
      detectLocationBtn: "मेरा स्थान पहचानें",
      locationDetected: "आपका वर्तमान स्थान",
      nearestMandi: "निकटतम AP मंडी",
      distanceAway: "किमी दूर",
      permissionDenied: "स्थान अनुमति अस्वीकृत।"
    },
    trends: {
      title: "मूल्य रुझान और इतिहास",
      subtitle: "पिछले 30 दिनों में केवल आधिकारिक अवलोकनों से प्राप्त वास्तविक मंडी भाव",
      noRecentData: "पिछले 30 दिनों में इस फसल और मंडी के लिए कोई आधिकारिक रिकॉर्ड नहीं मिला।",
      officialOnly: "केवल आधिकारिक रिकॉर्ड (कोई अनुमान नहीं)",
      selectCrop: "फसल चुनें",
      selectMarket: "मंडी चुनें",
      timeframe: "समय सीमा",
      last30Days: "पिछले 30 दिन",
      modalPrice: "मॉडल मूल्य (₹/क्विंटल)",
      arrivalQuantity: "आवक मात्रा (टन)",
      minMaxRange: "न्यूनतम - अधिकतम मूल्य सीमा",
      recordedPrices: "रिकॉर्ड किए गए मूल्य",
      gapsExplanation: "खाली तिथियां मंडी अवकाश या बिना व्यापार वाले दिन दर्शाती हैं।"
    },
    comparison: {
      title: "मंडी मूल्य तुलना",
      subtitle: "आंध्र प्रदेश की विभिन्न मंडियों में नवीनतम आधिकारिक मूल्यों की तुलना करें",
      noRecentOfficialData: "तुलना के लिए कोई हालिया आधिकारिक डेटा उपलब्ध नहीं है।",
      selectCrop: "तुलना हेतु फसल चुनें",
      highestPrice: "उच्चतम मॉडल मूल्य",
      lowestPrice: "न्यूनतम मॉडल मूल्य",
      averagePrice: "औसत मूल्य",
      distance: "दूरी",
      priceDiff: "मूल्य अंतर",
      bestMandi: "सर्वोत्तम मंडी",
      compareBtn: "तुलना करें"
    },
    weather: {
      title: "मंडी और स्थानीय मौसम सेवा",
      subtitle: "लाइव सैटेलाइट और Open-Meteo मौसम डेटा",
      userLocationWeather: "आपके स्थान का मौसम",
      mandiLocationWeather: "मंडी का मौसम",
      temperature: "तापमान",
      rain: "वर्षा",
      humidity: "आर्द्रता",
      wind: "हवा की गति",
      extremeAlert: "गंभीर मौसम चेतावनी",
      historicalWeather: "मौसम इतिहास",
      date: "तिथि",
      maxTemp: "अधिकतम तापमान (°C)",
      minTemp: "न्यूनतम तापमान (°C)",
      heavyRainAlert: "भारी वर्षा का जोखिम",
      extremeHeatAlert: "अत्यधिक गर्मी चेतावनी (>40°C)",
      district: "ज़िला",
      detectingLocation: "स्थान पहचाना जा रहा है...",
      past14Days: "पिछले 14 दिन",
      liveWeather: "लाइव मौसम",
      unavailable: "इस मंडी के लिए मौसम डेटा उपलब्ध नहीं है"
    },
    schemes: {
      title: "सरकारी कृषि योजनाएं",
      subtitle: "किसानों के लिए आधिकारिक केंद्रीय और राज्य वित्तीय सहायता एवं फसल बीमा योजनाएं",
      visitOfficialWebsite: "आधिकारिक पोर्टल पर जाएं",
      eligibility: "पात्रता मानदंड",
      benefits: "मुख्य लाभ",
      howToApply: "आवेदन कैसे करें"
    },
    disease: {
      tabTitle: "फसल रोग निदान",
      tabSubtitle: "पत्ती की तस्वीर अपलोड करें। Gemini AI रोग की पहचान कर उपचार सलाह देगा।",
      badge: "AI फसल सुरक्षा",
      newAnalysis: "नया विश्लेषण",
      history: "निदान इतिहास",
      uploadTitle: "पत्तियों की फोटो अपलोड करें",
      uploadSubtitle: "फोटो खींचें या फाइल चुनें",
      browseFiles: "फाइलें चुनें",
      takePhoto: "फोटो लें",
      maxImagesHint: "अधिकतम 3 फोटो अपलोड कर सकते हैं",
      analyzeBtn: "रोग का विश्लेषण करें",
      analyzingBtn: "AI विश्लेषण जारी है...",
      loginPrompt: "रोग निदान के लिए कृपया लॉग इन करें।",
      notesPlaceholder: "अपने अवलोकन लिखें...",
      notesLabel: "अवलोकन (वैकल्पिक)",
      recognizedCrop: "पहचानी गई फसल",
      primaryDiagnosis: "रोग का निदान",
      confidence: "सटीकता",
      botanicalEvidence: "लक्षण और साक्ष्य",
      immediateAction: "तत्काल उपचार",
      preventiveMeasures: "रोकथाम के उपाय",
      chemicalControl: "दवा और कवकनाशी सलाह",
      safetyPrecaution: "सावधानियां",
      disclaimerTitle: "सलाह अस्वीकरण",
      disclaimerText: "यह AI द्वारा तैयार की गई सलाह है। कीटनाशक प्रयोग से पहले कृषि अधिकारी से परामर्श करें।",
      deleteHistory: "हटाएं",
      noHistory: "कोई पूर्व रिकॉर्ड नहीं मिला।"
    },
    auth: {
      loginTitle: "लॉग इन करें",
      signUpTitle: "खाता बनाएं",
      emailLabel: "ईमेल पता",
      passwordLabel: "पासवर्ड",
      fullNameLabel: "पूरा नाम",
      roleLabel: "भूमिका",
      farmerRole: "किसान",
      traderRole: "व्यापारी",
      adminRole: "कृषि अधिकारी / व्यवस्थापक",
      loginBtn: "लॉग इन",
      signUpBtn: "खाता बनाएं",
      dontHaveAccount: "खाता नहीं है? साइन अप करें",
      alreadyHaveAccount: "पहले से खाता है? लॉग इन करें"
    },
    validation: {
      requiredField: "यह फ़ील्ड आवश्यक है।",
      invalidEmail: "कृपया मान्य ईमेल पता दर्ज करें।",
      passwordTooShort: "पासवर्ड कम से कम 6 अक्षरों का होना चाहिए।",
      futureDateNotAllowed: "भविष्य की तिथि नहीं चुन सकते।",
      selectBothCropAndMarket: "कृपया फसल और मंडी दोनों चुनें।"
    },
    errors: {
      apiUnavailable: "आधिकारिक API अनुपलब्ध है।",
      futureDateNotAllowed: "तिथि भविष्य में नहीं हो सकती।",
      noData: "कोई मूल्य रिकॉर्ड नहीं मिला।",
      modelUnavailable: "AI मॉडल वर्तमान में उपलब्ध नहीं है।",
      serverError: "सर्वर त्रुटि। कृपया पुनः प्रयास करें।",
      networkError: "इंटरनेट कनेक्शन विफल।"
    },
    warnings: {
      predictionIsEstimate: "पूर्वानुमान केवल अनुमान हैं।",
      dataMayBeStale: "डेटा 2 दिन से अपडेट नहीं हुआ है।",
      noOfficialValueForToday: "आज का आधिकारिक भाव अभी नहीं आया है।",
      fallbackUsed: "मॉडल उपलब्ध न होने पर बेसलाइन मूल्य उपयोग किया गया।"
    },
    chatbot: {
      title: "किसान सहायक AI चैटबॉट",
      subtitle: "मंडी भाव, फसल रोग और सरकारी योजनाओं के बारे में हिंदी में पूछें",
      placeholder: "भाव, रुझान या रोग के बारे में पूछें...",
      send: "भेजें",
      welcomeMsg: "नमस्ते! मैं आपका CropMandi AI सहायक हूँ। आज मैं आपकी क्या मदद कर सकता हूँ?",
      quickPrompts: [
        "मदनापल्ले में टमाटर का ताज़ा भाव क्या है?",
        "क्या मुझे मिर्च बेचनी चाहिए या रोकनी चाहिए?",
        "कपास में पत्ती धब्बा रोग कैसे रोकें?",
        "पीएम-किसान योजना की पात्रता क्या है?"
      ]
    }
  },

  ml: {
    common: {
      appTitle: "വിപണി വില പ്രവചനം",
      appSubtitle: "ആന്ധ്രാപ്രദേശ് കർഷകർക്കായി AI അധിഷ്ഠിത മാർക്കറ്റ് വില പ്രവചനവും ഉപദേശവും",
      login: "ലോഗിൻ",
      signUp: "സൈൻ അപ്പ്",
      logout: "ലോഗ് ഔട്ട്",
      loading: "ലോഡ് ചെയ്യുന്നു...",
      retry: "വീണ്ടും ശ്രമിക്കുക",
      today: "ഇന്ന്",
      selectCrop: "വിള തിരഞ്ഞെടുക്കുക",
      selectDistrict: "ജില്ല തിരഞ്ഞെടുക്കുക",
      selectMarket: "മാർക്കറ്റ് തിരഞ്ഞെടുക്കുക",
      unitQuintal: "₹/ക്വിന്റൽ",
      location: "സ്ഥലം",
      andhraPradesh: "ആന്ധ്രാപ്രദേശ്",
      allMarkets: "എല്ലാ മാർക്കറ്റുകളും",
      back: "പുറകോട്ട്",
      close: "അടയ്ക്കുക",
      save: "സൂക്ഷിക്കുക",
      refresh: "പുതുക്കുക",
      verified: "പരിശോധിച്ചുറപ്പിച്ചത്"
    },
    tabs: {
      forecast: "വില പ്രവചനം",
      trends: "ട്രെൻഡുകൾ & താരതമ്യം",
      disease: "🌿 സസ്യ രോഗങ്ങൾ",
      weather: "കാലാവസ്ഥ",
      schemes: "സർക്കാർ പദ്ധതികൾ"
    },
    forecast: {
      title: "മാർക്കറ്റ് വില പ്രവചനം",
      subtitle: "ഔദ്യോഗിക ഡാറ്റയും മെഷീൻ ലേണിംഗും അടിസ്ഥാനമാക്കിയുള്ള 3 ദിവസത്തെ വില പ്രവചനം",
      selectCrop: "വിള തിരഞ്ഞെടുക്കുക",
      selectMarket: "മാർക്കറ്റ് തിരഞ്ഞെടുക്കുക",
      baseDate: "അടിസ്ഥാന തീയതി",
      targetDate: "ലക്ഷ്യ തീയതി",
      observationDate: "രേഖപ്പെടുത്തിയ തീയതി",
      forecastOrigin: "പ്രവചന ഉത്ഭവം",
      forecastDate: "പ്രവചന തീയതി",
      generateBtn: "പ്രവചനം നേടുക",
      generate: "പ്രവചനം നേടുക",
      generating: "തയ്യാറാക്കുന്നു...",
      fetchingOfficialData: "ഔദ്യോഗിക ഡാറ്റ ശേഖരിക്കുന്നു...",
      updatingRecords: "രേഖകൾ പുതുക്കുന്നു...",
      rebuildingFeatures: "ഫീച്ചറുകൾ നിർമ്മിക്കുന്നു...",
      preparingPredictions: "പ്രവചനങ്ങൾ തയ്യാറാക്കുന്നു...",
      latestModalPrice: "ഏറ്റവും പുതിയ മോഡൽ വില",
      latestOfficialValue: "ഏറ്റവും പുതിയ ഔദ്യോഗിക വില",
      latestOfficialDate: "രേഖപ്പെടുത്തിയ തീയതി",
      dataAge: "ഡാറ്റയുടെ പഴക്കം",
      currentOneDayTrend: "1-ദിവസത്തെ ട്രെൻഡ്",
      expectedTrend: "പ്രതീക്ഷിക്കുന്ന ട്രെൻഡ്",
      threeDayForecast: "3 ദിവസത്തെ വില പ്രവചനം",
      officialApiValue: "ഔദ്യോഗിക API വില",
      officialDatabaseValue: "ഡാറ്റാബേസ് രേഖ",
      officialCsvValue: "ഔദ്യോഗിക CSV രേഖ",
      predictedModelValue: "മോഡൽ പ്രവചിച്ച വില",
      fallbackValue: "ബേസ്‌ലൈൻ വില",
      priceUnavailable: "വില ലഭ്യമല്ല",
      confidenceInterval: "വില പരിധി",
      low: "കുറഞ്ഞത്",
      high: "കൂടിയത്",
      sell: "വിൽക്കുക",
      hold: "സൂക്ഷിക്കുക (HOLD)",
      buy: "വാങ്ങുക",
      sellOrHold: "വിൽക്കുകയോ സൂക്ഷിക്കുകയോ ചെയ്യുക",
      sellNow: "ഇപ്പോൾ വിൽക്കുക",
      holdCrop: "വിള സൂക്ഷിക്കുക",
      stableTrend: "സ്ഥിരതയുള്ള ട്രെൻഡ്",
      upwardTrend: "വർദ്ധിക്കുന്ന ട്രെൻഡ്",
      downwardTrend: "കുറയുന്ന ട്രെൻഡ്",
      trendUnavailable: "ലഭ്യമല്ല",
      todayOfficialUnavailable: "ഇന്നത്തെ ഔദ്യോഗിക വിപണി വില ഇതുവരെ പ്രസിദ്ധീകരിച്ചിട്ടില്ല.",
      showingLatestOfficialValue: "ലഭ്യമായ ഏറ്റവും പുതിയ ഔദ്യോഗിക വിവരങ്ങൾ കാണിക്കുന്നു.",
      staleDataWarning: "ഔദ്യോഗിക ഡാറ്റ 2 ദിവസത്തിൽ കൂടുതൽ പഴക്കമുള്ളതാണ്.",
      dataVerification: "ഡാറ്റാ പരിശോധനാ വിവരങ്ങൾ",
      apiChecked: "ഔദ്യോഗിക API പരിശോധിച്ചു",
      csvChecked: "മാസ്റ്റർ CSV പരിശോധിച്ചു",
      predictionGenerated: "പ്രവചനം തയ്യാറാക്കി",
      source: "വിലയുടെ ഉറവിടം",
      modelVersion: "മോഡൽ പതിപ്പ്",
      advisoryTitle: "കർഷക തീരുമാന ഉപദേശം",
      disclaimerTitle: "ഉപദേശ നിരാകരണം",
      disclaimerText: "ചരിത്രപരമായ മാർക്കറ്റ് വരവ്, വിലകൾ, കാലാവസ്ഥാ പ്രവണതകൾ എന്നിവയെ അടിസ്ഥാനമാക്കി CatBoost മെഷീൻ ലേണിംഗ് മോഡലുകൾ ഉപയോഗിച്ചാണ് പ്രവചനങ്ങൾ കണക്കാക്കുന്നത്.",
      day1: "നാളെ (ദിവസം 1)",
      day2: "ദിവസം +2",
      day3: "ദിവസം +3",
      confidenceBounds: "വില പരിധി",
      predictedPrice: "പ്രവചിച്ച മോഡൽ വില",
      currentPriceCardTitle: "ഇന്നത്തെ ഔദ്യോഗിക മോഡൽ വില",
      currentPriceCardSubtitle: "മാർക്കറ്റിൽ നിന്ന് ലഭിച്ച ഔദ്യോഗിക വില",
      historyPriceCardTitle: "ചരിത്രപരമായ ഔദ്യോഗിക വില",
      historyPriceCardSubtitle: "തിരഞ്ഞെടുത്ത തീയതിയിലെ ഔദ്യോഗിക വില",
      loadingSubtitle: "കർശനമായ മുൻഗണനാ ക്രമം: ഔദ്യോഗിക API → CSV → ഡാറ്റാബേസ് → CatBoost ML → ഫോൾബാക്ക്.",
      loadingStages: [
        "ഘട്ടം 1/5: data.gov.in ഔദ്യോഗിക API റെക്കോർഡുകൾ പരിശോധിക്കുന്നു...",
        "ഘട്ടം 2/5: 4 ദിവസത്തെ ഔദ്യോഗിക രേഖകൾ പരിശോധിക്കുന്നു...",
        "ഘട്ടം 3/5: മാസ്റ്റർ ഡാറ്റ പരിശോധിച്ച് ഫീച്ചറുകൾ നിർമ്മിക്കുന്നു...",
        "ഘട്ടം 4/5: ബാക്കിയുള്ള തീയതികളിലേക്ക് CatBoost ML വഴി പ്രവചിക്കുന്നു...",
        "ഘട്ടം 5/5: അന്തിമ വില പ്രവചനങ്ങളും പരിധികളും തയ്യാറാക്കുന്നു..."
      ]
    },
    location: {
      detectLocationBtn: "എന്റെ സ്ഥാനം കണ്ടെത്തുക",
      locationDetected: "നിങ്ങളുടെ സ്ഥാനം",
      nearestMandi: "ഏറ്റവും അടുത്തുള്ള മാർക്കറ്റ്",
      distanceAway: "കി.മീ ദൂരം",
      permissionDenied: "ലൊക്കേഷൻ അനുമതി നിഷേധിച്ചു."
    },
    trends: {
      title: "വില പ്രവണതകളും ചരിത്രവും",
      subtitle: "കഴിഞ്ഞ 30 ദിവസങ്ങളിലെ ഔദ്യോഗിക വിപണി വിലകൾ മാത്രം",
      noRecentData: "കഴിഞ്ഞ 30 ദിവസങ്ങളിൽ ഔദ്യോഗിക രേഖകൾ ഒന്നും ലഭ്യമല്ല.",
      officialOnly: "ഔദ്യോഗിക രേഖകൾ മാത്രം",
      selectCrop: "വിള തിരഞ്ഞെടുക്കുക",
      selectMarket: "മാർക്കറ്റ് തിരഞ്ഞെടുക്കുക",
      timeframe: "കാലയളവ്",
      last30Days: "കഴിഞ്ഞ 30 ദിവസങ്ങൾ",
      modalPrice: "മോഡൽ വില (₹/ക്വിന്റൽ)",
      arrivalQuantity: "വരവ് (ടൺ)",
      minMaxRange: "വില പരിധി",
      recordedPrices: "രേഖപ്പെടുത്തിയ വിലകൾ",
      gapsExplanation: "ഡാറ്റ ഇല്ലാത്ത ദിവസങ്ങൾ മാർക്കറ്റ് അവധികളെ സൂചിപ്പിക്കുന്നു."
    },
    comparison: {
      title: "മാർക്കറ്റ് വില താരതമ്യം",
      subtitle: "വിവിധ മാർക്കറ്റുകളിലെ ഏറ്റവും പുതിയ ഔദ്യോഗിക വിലകൾ താരതമ്യം ചെയ്യുക",
      noRecentOfficialData: "താരതമ്യത്തിനായി സമീപകാല ഡാറ്റ ലഭ്യമല്ല.",
      selectCrop: "വിള തിരഞ്ഞെടുക്കുക",
      highestPrice: "ഏറ്റവും ഉയർന്ന വില",
      lowestPrice: "ഏറ്റവും കുറഞ്ഞ വില",
      averagePrice: "ശരാശരി വില",
      distance: "ദൂരം",
      priceDiff: "വില വ്യത്യാസം",
      bestMandi: "മികച്ച മാർക്കറ്റ്",
      compareBtn: "താരതമ്യം ചെയ്യുക"
    },
    weather: {
      title: "കാലാവസ്ഥാ സേവനം",
      subtitle: "തത്സമയ കാലാവസ്ഥാ വിവരങ്ങൾ",
      userLocationWeather: "നിങ്ങളുടെ പ്രദേശത്തെ കാലാവസ്ഥ",
      mandiLocationWeather: "മാർക്കറ്റിലെ കാലാവസ്ഥ",
      temperature: "താപനില",
      rain: "മഴ",
      humidity: "ഈർപ്പം",
      wind: "കാറ്റിന്റെ വേഗത",
      extremeAlert: "തീവ്ര കാലാവസ്ഥാ മുന്നറിയിപ്പ്",
      historicalWeather: "കാലാവസ്ഥാ ചരിത്രം",
      date: "തീയതി",
      maxTemp: "കൂടിയ താപനില (°C)",
      minTemp: "കുറഞ്ഞ താപനില (°C)",
      heavyRainAlert: "കനത്ത മഴ സാധ്യത",
      extremeHeatAlert: "കഠിനമായ ചൂട് മുന്നറിയിപ്പ് (>40°C)",
      district: "ജില്ല",
      detectingLocation: "സ്ഥാനം കണ്ടെത്തുന്നു...",
      past14Days: "കഴിഞ്ഞ 14 ദിവസങ്ങൾ",
      liveWeather: "തത്സമയ കാലാവസ്ഥ",
      unavailable: "കാലാവസ്ഥാ വിവരങ്ങൾ ലഭ്യമല്ല"
    },
    schemes: {
      title: "സർക്കാർ കാർഷിക പദ്ധതികൾ",
      subtitle: "കർഷകർക്കായുള്ള കേന്ദ്ര-സംസ്ഥാന സാമ്പത്തിക സഹായങ്ങളും ഇൻഷുറൻസും",
      visitOfficialWebsite: "ഔദ്യോഗിക പോർട്ടൽ സന്ദർശിക്കുക",
      eligibility: "യോഗ്യത",
      benefits: "പ്രയോജനങ്ങൾ",
      howToApply: "എങ്ങനെ അപേക്ഷിക്കാം"
    },
    disease: {
      tabTitle: "സസ്യ രോഗനിർണയം",
      tabSubtitle: "ഇലയുടെ ഫോട്ടോ അപ്‌ലോഡ് ചെയ്യുക. Gemini AI രോഗം നിർണ്ണയിച്ച് പ്രതിവിധി നൽകും.",
      badge: "AI വിള സംരക്ഷണം",
      newAnalysis: "പുതിയ പരിശോധന",
      history: "ചരിത്രം",
      uploadTitle: "ഫോട്ടോ അപ്‌ലോഡ് ചെയ്യുക",
      uploadSubtitle: "ക്യാമറ ഉപയോഗിക്കുകയോ ഫയൽ തിരഞ്ഞെടുക്കുകയോ ചെയ്യുക",
      browseFiles: "ഫയലുകൾ തിരഞ്ഞെടുക്കുക",
      takePhoto: "ഫോട്ടോ എടുക്കുക",
      maxImagesHint: "3 ഫോട്ടോകൾ വരെ നൽകാം",
      analyzeBtn: "പരിശോധിക്കുക",
      analyzingBtn: "പരിശോധിക്കുന്നു...",
      loginPrompt: "രോഗനിർണയത്തിനായി ദയവായി ലോഗിൻ ചെയ്യുക.",
      notesPlaceholder: "നിരീക്ഷണങ്ങൾ എഴുതുക...",
      notesLabel: "കുറിപ്പുകൾ (ഓപ്ഷണൽ)",
      recognizedCrop: "തിരിച്ചറിഞ്ഞ വിള",
      primaryDiagnosis: "രോഗനിർണയം",
      confidence: "കൃത്യത",
      botanicalEvidence: "ലക്ഷണങ്ങൾ",
      immediateAction: "ഉടൻ ചെയ്യേണ്ട കാര്യങ്ങൾ",
      preventiveMeasures: "പ്രതിരോധ നടപടികൾ",
      chemicalControl: "രാസവള നിർദ്ദേശങ്ങൾ",
      safetyPrecaution: "മുൻകരുതലുകൾ",
      disclaimerTitle: "നിരാകരണം",
      disclaimerText: "ഇത് AI നൽകുന്ന ഉപദേശമാണ്. കീടനാശിനി പ്രയോഗത്തിന് മുൻപ് കൃഷി ഓഫീസറെ കാണുക.",
      deleteHistory: "നീക്കം ചെയ്യുക",
      noHistory: "രേഖകൾ ഒന്നും ലഭ്യമല്ല."
    },
    auth: {
      loginTitle: "ലോഗിൻ ചെയ്യുക",
      signUpTitle: "അക്കൗണ്ട് സൃഷ്ടിക്കുക",
      emailLabel: "ഇമെയിൽ വിലാസം",
      passwordLabel: "പാസ്‌വേഡ്",
      fullNameLabel: "പൂർണ്ണ നാമം",
      roleLabel: "തസ്തിക",
      farmerRole: "കർഷകൻ",
      traderRole: "വ്യാപാരി",
      adminRole: "കൃഷി ഓഫീസർ / അഡ്മിൻ",
      loginBtn: "ലോഗിൻ",
      signUpBtn: "അക്കൗണ്ട് സൃഷ്ടിക്കുക",
      dontHaveAccount: "അക്കൗണ്ട് ഇല്ലേ? സൈൻ അപ്പ് ചെയ്യുക",
      alreadyHaveAccount: "അക്കൗണ്ട് ഉണ്ടോ? ലോഗിൻ ചെയ്യുക"
    },
    validation: {
      requiredField: "ഈ വിവരം ആവശ്യമാണ്.",
      invalidEmail: "ശരിയായ ഇമെയിൽ നൽകുക.",
      passwordTooShort: "പാസ്‌വേഡിൽ കുറഞ്ഞത് 6 അക്ഷരങ്ങൾ വേണം.",
      futureDateNotAllowed: "ഭാവി തീയതി തിരഞ്ഞെടുക്കരുത്.",
      selectBothCropAndMarket: "വിളയും മാർക്കറ്റും തിരഞ്ഞെടുക്കുക."
    },
    errors: {
      apiUnavailable: "ഔദ്യോഗിക API ലഭ്യമല്ല.",
      futureDateNotAllowed: "തീയതി ഭാവിയിലാകരുത്.",
      noData: "വിവരങ്ങൾ ലഭ്യമല്ല.",
      modelUnavailable: "AI മോഡൽ ലഭ്യമല്ല.",
      serverError: "സെർവർ തകരാർ. വീണ്ടും ശ്രമിക്കുക.",
      networkError: "ഇന്റർനെറ്റ് കണക്ഷൻ ലഭ്യമല്ല."
    },
    warnings: {
      predictionIsEstimate: "വിലകൾ ഏകദേശ കണക്കുകളാണ്.",
      dataMayBeStale: "കഴിഞ്ഞ 2 ദിവസമായി ഡാറ്റ അപ്‌ഡേറ്റ് ചെയ്തിട്ടില്ല.",
      noOfficialValueForToday: "ഇന്നത്തെ ഔദ്യോഗിക വില പ്രസിദ്ധീകരിച്ചിട്ടില്ല.",
      fallbackUsed: "ബേസ്‌ലൈൻ വില ഉപയോഗിച്ചു."
    },
    chatbot: {
      title: "കർഷക സഹായി AI ചാറ്റ്ബോട്ട്",
      subtitle: "മാർക്കറ്റ് വിലകളെയും രോഗങ്ങളെയും കുറിച്ച് ചോദിക്കുക",
      placeholder: "ചോദ്യങ്ങൾ ചോദിക്കുക...",
      send: "അയക്കുക",
      welcomeMsg: "നമസ്കാരം! ഞാൻ നിങ്ങളുടെ CropMandi AI സഹായിയാണ്. എനിക്ക് എങ്ങനെ സഹായിക്കാനാകും?",
      quickPrompts: [
        "മദനപ്പള്ളിയിലെ തക്കാളി വില എത്ര?",
        "മുളക് ഇപ്പോൾ വിൽക്കണമോ?",
        "പരുത്തിയിലെ ഇലപ്പുള്ളി രോഗം എങ്ങനെ തടയാം?",
        "പിഎം കിസാൻ യോഗ്യതകൾ എന്തൊക്കെയാണ്?"
      ]
    }
  },

  ta: {
    common: {
      appTitle: "மண்டி விலை கணிப்பு",
      appSubtitle: "ஆந்திரப் பிரதேச விவசாயிகளுக்கான AI அடிப்படையிலான மண்டி விலை கணிப்பு மற்றும் ஆலோசனை",
      login: "உள்நுழை",
      signUp: "பதிவு செய்",
      logout: "வெளியேறு",
      loading: "ஏற்றுகிறது...",
      retry: "மீண்டும் முயற்சி செய்",
      today: "இன்று",
      selectCrop: "பயிரைத் தேர்ந்தெடுக்கவும்",
      selectDistrict: "மாவட்டத்தைத் தேர்ந்தெடுக்கவும்",
      selectMarket: "மண்டியைத் தேர்ந்தெடுக்கவும்",
      unitQuintal: "₹/குவிண்டால்",
      location: "இடம்",
      andhraPradesh: "ஆந்திரப் பிரதேசம்",
      allMarkets: "அனைத்து மண்டிகள்",
      back: "பின்னால்",
      close: "மூடு",
      save: "சேமி",
      refresh: "புதுப்பி",
      verified: "சரிபார்க்கப்பட்டது"
    },
    tabs: {
      forecast: "விலை கணிப்பு",
      trends: "போக்கு & ஒப்பீடு",
      disease: "🌿 பயிர் நோய்",
      weather: "வானிலை",
      schemes: "அரசு திட்டங்கள்"
    },
    forecast: {
      title: "மண்டி விலை கணிப்பு",
      subtitle: "அதிகாரப்பூர்வ தரவு மற்றும் இயந்திர கற்றல் அடிப்படையிலான 3 நாள் விலை கணிப்பு",
      selectCrop: "பயிரைத் தேர்ந்தெடுக்கவும்",
      selectMarket: "மண்டியைத் தேர்ந்தெடுக்கவும்",
      baseDate: "கணிப்பு தொடக்க தேதி",
      targetDate: "இலக்கு தேதி",
      observationDate: "பதிவு செய்யப்பட்ட தேதி",
      forecastOrigin: "கணிப்பு தோற்றம்",
      forecastDate: "கணிப்பு தேதி",
      generateBtn: "விலை கணிப்பைப் பெறுங்கள்",
      generate: "கணிப்பைப் பெறுங்கள்",
      generating: "கணிக்கிறது...",
      fetchingOfficialData: "அதிகாரப்பூர்வ தரவை எடுக்கிறது...",
      updatingRecords: "பதிவுகளை புதுப்பிக்கிறது...",
      rebuildingFeatures: "அம்சங்களை உருவாக்குகிறது...",
      preparingPredictions: "கணிப்புகளை தயார் செய்கிறது...",
      latestModalPrice: "சமீபத்திய மாதிரி விலை",
      latestOfficialValue: "சமீபத்திய அதிகாரப்பூர்வ விலை",
      latestOfficialDate: "பதிவு செய்யப்பட்ட தேதி",
      dataAge: "தரவு வயது",
      currentOneDayTrend: "1-நாள் போக்கு",
      expectedTrend: "எதிர்பார்க்கப்படும் போக்கு",
      threeDayForecast: "3 நாள் விலை கணிப்பு",
      officialApiValue: "அதிகாரப்பூர்வ API விலை",
      officialDatabaseValue: "தரவுத்தள அதிகாரப்பூர்வ பதிவு",
      officialCsvValue: "அதிகாரப்பூர்வ CSV பதிவு",
      predictedModelValue: "மாதிரி கணித்த விலை",
      fallbackValue: "அடிப்படை விலை",
      priceUnavailable: "விலை கிடைக்கவில்லை",
      confidenceInterval: "விலை கணிப்பு வரம்பு",
      low: "குறைந்தபட்சம்",
      high: "அதிகபட்சம்",
      sell: "விற்கவும்",
      hold: "வைத்திருக்கவும் (HOLD)",
      buy: "வாங்கவும்",
      sellOrHold: "விற்கவும் அல்லது வைத்திருக்கவும்",
      sellNow: "உடனே விற்கவும்",
      holdCrop: "பயிரை வைத்திருக்கவும்",
      stableTrend: "நிலையான போக்கு",
      upwardTrend: "அதிகரிக்கும் போக்கு",
      downwardTrend: "குறையும் போக்கு",
      trendUnavailable: "போக்கு கிடைக்கவில்லை",
      todayOfficialUnavailable: "இன்றைய அதிகாரப்பூர்வ மண்டி விலை இன்னும் வெளியிடப்படவில்லை.",
      showingLatestOfficialValue: "கிடைக்கக்கூடிய சமீபத்திய அதிகாரப்பூர்வ பதிவு காட்டப்படுகிறது.",
      staleDataWarning: "அதிகாரப்பூர்வ தரவு 2 நாட்களுக்கு மேல் பழமையானது.",
      dataVerification: "தரவு சரிபார்ப்பு விவரங்கள்",
      apiChecked: "அதிகாரப்பூர்வ API சரிபார்க்கப்பட்டது",
      csvChecked: "முதன்மை CSV சரிபார்க்கப்பட்டது",
      predictionGenerated: "கணிப்பு உருவாக்கப்பட்டது",
      source: "விலை ஆதாரம்",
      modelVersion: "மாதிரி பதிப்பு",
      advisoryTitle: "விவசாயி முடிவு ஆலோசனை",
      disclaimerTitle: "ஆலோசனை மறுப்பு",
      disclaimerText: "வரலாற்று APMC மண்டி வரத்துக்கள், விலைகள் மற்றும் வானிலை போக்குகளின் அடிப்படையில் CatBoost இயந்திர கற்றல் மாதிரிகளைப் பயன்படுத்தி கணிப்புகள் கணக்கிடப்படுகின்றன.",
      day1: "நாளை (நாள் 1)",
      day2: "நாள் +2",
      day3: "நாள் +3",
      confidenceBounds: "விலை வரம்பு",
      predictedPrice: "கணிக்கப்பட்ட மாதிரி விலை",
      currentPriceCardTitle: "இன்றைய அதிகாரப்பூர்வ மாதிரி விலை",
      currentPriceCardSubtitle: "APMC மண்டியின் உண்மையான அதிகாரப்பூர்வ பதிவு",
      historyPriceCardTitle: "வரலாற்று அதிகாரப்பூர்வ விலை",
      historyPriceCardSubtitle: "தேர்ந்தெடுக்கப்பட்ட தேதிக்கான அதிகாரப்பூர்வ பதிவு",
      loadingSubtitle: "துல்லியமான 5-நிலை முன்னுரிமை: அதிகாரப்பூர்வ API → CSV → தரவுத்தளம் → CatBoost ML → ஃபால்பேக்.",
      loadingStages: [
        "நிலை 1/5: data.gov.in அதிகாரப்பூர்வ API பதிவுகளை சரிபார்க்கிறது...",
        "நிலை 2/5: 4-நாள் அதிகாரப்பூர்வ பதிவுகளை சரிபார்க்கிறது...",
        "நிலை 3/5: முதன்மைத் தரவை சரிபார்த்து அம்சங்களை உருவாக்குகிறது...",
        "நிலை 4/5: மீதமுள்ள தேதிகளுக்கு CatBoost ML மூலம் கணிக்கிறது...",
        "நிலை 5/5: இறுதி விலை கணிப்புகள் மற்றும் வரம்புகளை தயார் செய்கிறது..."
      ]
    },
    location: {
      detectLocationBtn: "என் இருப்பிடத்தைக் கண்டறி",
      locationDetected: "உங்கள் தற்போதைய இடம்",
      nearestMandi: "அருகிலுள்ள மண்டி",
      distanceAway: "கி.மீ தூரம்",
      permissionDenied: "இருப்பிட அனுமதி மறுக்கப்பட்டது."
    },
    trends: {
      title: "விலை போக்குகள் & வரலாறு",
      subtitle: "கடந்த 30 நாட்களில் அதிகாரப்பூர்வ பதிவுகளின் அடிப்படையிலான விலை பகுப்பாய்வு",
      noRecentData: "கடந்த 30 நாட்களில் இந்த பயிர் மற்றும் மண்டிக்கு அதிகாரப்பூர்வ பதிவுகள் எதுவும் இல்லை.",
      officialOnly: "அதிகாரப்பூர்வ பதிவுகள் மட்டுமே (கணிப்புகள் இல்லை)",
      selectCrop: "பயிரைத் தேர்ந்தெடுக்கவும்",
      selectMarket: "மண்டியைத் தேர்ந்தெடுக்கவும்",
      timeframe: "கால அளவு",
      last30Days: "கடந்த 30 நாட்கள்",
      modalPrice: "மாதிரி விலை (₹/குவிண்டால்)",
      arrivalQuantity: "வரத்து அளவு (டன்)",
      minMaxRange: "குறைந்தபட்ச - அதிகபட்ச விலை வரம்பு",
      recordedPrices: "பதிவு செய்யப்பட்ட விலைகள்",
      gapsExplanation: "தரவு இல்லாத தேதிகள் மண்டி விடுமுறை நாட்களைக் குறிக்கின்றன."
    },
    comparison: {
      title: "மண்டி விலை ஒப்பீடு",
      subtitle: "ஆந்திரப் பிரதேசத்தின் பல்வேறு மண்டிகளில் சமீபத்திய அதிகாரப்பூர்வ விலைகளை ஒப்பிடவும்",
      noRecentOfficialData: "ஒப்பீட்டிற்கு சமீபத்திய அதிகாரப்பூர்வ தரவு எதுவும் கிடைக்கவில்லை.",
      selectCrop: "பயிரைத் தேர்ந்தெடுக்கவும்",
      highestPrice: "அதிகபட்ச மாதிரி விலை",
      lowestPrice: "குறைந்தபட்ச மாதிரி விலை",
      averagePrice: "சராசரி விலை",
      distance: "தூரம்",
      priceDiff: "விலை வேறுபாடு",
      bestMandi: "சிறந்த மண்டி",
      compareBtn: "ஒப்பிடவும்"
    },
    weather: {
      title: "வானிலை சேவை",
      subtitle: "நேரடி செயற்கைக்கோள் வானிலை தகவல்",
      userLocationWeather: "உங்கள் பகுதியின் வானிலை",
      mandiLocationWeather: "மண்டியின் வானிலை",
      temperature: "வெப்பநிலை",
      rain: "மழைப்பொழிவு",
      humidity: "ஈரப்பதம்",
      wind: "காற்றின் வேகம்",
      extremeAlert: "தீவிர வானிலை எச்சரிக்கை",
      historicalWeather: "வானிலை வரலாறு",
      date: "தேதி",
      maxTemp: "அதிகபட்ச வெப்பநிலை (°C)",
      minTemp: "குறைந்தபட்ச வெப்பநிலை (°C)",
      heavyRainAlert: "கனமழை ஆபத்து",
      extremeHeatAlert: "கடும் வெப்ப எச்சரிக்கை (>40°C)",
      district: "மாவட்டம்",
      detectingLocation: "இடம் கண்டறியப்படுகிறது...",
      past14Days: "கடந்த 14 நாட்கள்",
      liveWeather: "நேரடி வானிலை",
      unavailable: "வானிலை தரவு கிடைக்கவில்லை"
    },
    schemes: {
      title: "அரசு விவசாய திட்டங்கள்",
      subtitle: "விவசாயிகளுக்கான மத்திய மற்றும் மாநில அரசு நிதி உதவிகள் மற்றும் பயிர் காப்பீட்டுத் திட்டங்கள்",
      visitOfficialWebsite: "அதிகாரப்பூர்வ தளத்தைப் பார்வையிடவும்",
      eligibility: "தகுதி வரம்புகள்",
      benefits: "நன்மைகள்",
      howToApply: "விண்ணப்பிப்பது எப்படி"
    },
    disease: {
      tabTitle: "பயிர் நோய் கண்டறிதல்",
      tabSubtitle: "இலையின் புகைப்படத்தை பதிவேற்றவும். Gemini AI நோயைக் கண்டறிந்து சிகிச்சை ஆலோசனையை வழங்கும்.",
      badge: "AI பயிர் பாதுகாப்பு",
      newAnalysis: "புதிய பகுப்பாய்வு",
      history: "வரலாறு",
      uploadTitle: "இலை புகைப்படத்தைப் பதிவேற்றவும்",
      uploadSubtitle: "புகைப்படம் எடுக்கவும் அல்லது கோப்பைத் தேர்ந்தெடுக்கவும்",
      browseFiles: "கோப்புகளைத் தேர்ந்தெடுக்கவும்",
      takePhoto: "புகைப்படம் எடு",
      maxImagesHint: "அதிகபட்சம் 3 படங்கள் வரை பதிவேற்றலாம்",
      analyzeBtn: "நோயை பகுப்பாய்வு செய்",
      analyzingBtn: "AI பகுப்பாய்வு செய்கிறது...",
      loginPrompt: "நோய் கண்டறிதலுக்கு தயவுசெய்து உள்நுழையவும்.",
      notesPlaceholder: "உங்கள் அவதானிப்புகளை எழுதவும்...",
      notesLabel: "குறிப்புகள் (விருப்பத்தேர்வு)",
      recognizedCrop: "அடையாளம் காணப்பட்ட பயிர்",
      primaryDiagnosis: "நோய் கண்டறிதல்",
      confidence: "துல்லியம்",
      botanicalEvidence: "அறிகுறிகள்",
      immediateAction: "உடனடி சிகிச்சை",
      preventiveMeasures: "தடுப்பு நடவடிக்கைகள்",
      chemicalControl: "மருந்து பயன்பாட்டு வழிகாட்டுதல்",
      safetyPrecaution: "பாதுகாப்பு முன்னெச்சரிக்கைகள்",
      disclaimerTitle: "ஆலோசனை மறுப்பு",
      disclaimerText: "இது AI உருவாக்கிய ஆலோசனை. பூச்சிக்கொல்லி பயன்படுத்துவதற்கு முன் வேளாண் அதிகாரியை அணுகவும்.",
      deleteHistory: "நீக்கு",
      noHistory: "பதிவுகள் எதுவும் இல்லை."
    },
    auth: {
      loginTitle: "உள்நுழையவும்",
      signUpTitle: "கணக்கை உருவாக்கவும்",
      emailLabel: "மின்னஞ்சல் முகவரி",
      passwordLabel: "கடவுச்சொல்",
      fullNameLabel: "முழு பெயர்",
      roleLabel: "பங்கு",
      farmerRole: "விவசாயி",
      traderRole: "வியாபாரி",
      adminRole: "வேளாண் அலுவலர் / நிர்வாகி",
      loginBtn: "உள்நுழை",
      signUpBtn: "கணக்கை உருவாக்கு",
      dontHaveAccount: "கணக்கு இல்லையா? பதிவு செய்",
      alreadyHaveAccount: "கணக்கு உள்ளதா? உள்நுழை"
    },
    validation: {
      requiredField: "இந்த தகவல் தேவை.",
      invalidEmail: "சரியான மின்னஞ்சலை உள்ளிடவும்.",
      passwordTooShort: "கடவுச்சொல் குறைந்தது 6 எழுத்துகள் இருக்க வேண்டும்.",
      futureDateNotAllowed: "எதிர்கால தேதியைத் தேர்ந்தெடுக்க முடியாது.",
      selectBothCropAndMarket: "பயிர் மற்றும் மண்டி இரண்டையும் தேர்ந்தெடுக்கவும்."
    },
    errors: {
      apiUnavailable: "அதிகாரப்பூர்வ API கிடைக்கவில்லை.",
      futureDateNotAllowed: "தேதி எதிர்காலத்தில் இருக்கக்கூடாது.",
      noData: "விலை விவரங்கள் இல்லை.",
      modelUnavailable: "AI மாதிரி தற்போது கிடைக்கவில்லை.",
      serverError: "சேவையக பிழை. மீண்டும் முயற்சிக்கவும்.",
      networkError: "இணைய இணைப்பு தோல்வியடைந்தது."
    },
    warnings: {
      predictionIsEstimate: "விலை கணிப்புகள் மதிப்பீடுகள் மட்டுமே.",
      dataMayBeStale: "கடந்த 2 நாட்களாக தரவு புதுப்பிக்கப்படவில்லை.",
      noOfficialValueForToday: "இன்றைய அதிகாரப்பூர்வ விலை இன்னும் வரவில்லை.",
      fallbackUsed: "அடிப்படை விலை பயன்படுத்தப்பட்டது."
    },
    chatbot: {
      title: "விவசாயி உதவியாளர் AI சாட்பாட்",
      subtitle: "மண்டி விலைகள், நோய்கள் மற்றும் திட்டங்கள் குறித்து தமிழில் கேளுங்கள்",
      placeholder: "விலைகள் அல்லது பயிர்கள் பற்றி கேளுங்கள்...",
      send: "அனுப்பு",
      welcomeMsg: "வணக்கம்! நான் உங்கள் CropMandi AI உதவியாளர். இன்று நான் உங்களுக்கு எவ்வாறு உதவ முடியும்?",
      quickPrompts: [
        "மதனப்பள்ளியில் தக்காளி விலை என்ன?",
        "மிளகாயை இப்போது விற்க வேண்டுமா?",
        "பருத்தியில் இலைப்புள்ளி நோயை எவ்வாறு தடுப்பது?",
        "பிஎம்-கிசான் திட்டத்தின் தகுதிகள் என்ன?"
      ]
    }
  }
};

// Top-level backward compatibility properties
for (const lang of Object.keys(translations) as Language[]) {
  const dict = translations[lang];
  dict.appTitle = dict.common.appTitle;
  dict.appSubtitle = dict.common.appSubtitle;
}

/**
 * Universal dynamic translation helper with parameter interpolation and English fallback.
 * Usage: t('forecast.title', {}, 'te') or t('forecast.latestOfficialValue')
 */
export function t(key: string, params?: Record<string, string | number>, lang: Language = 'en'): string {
  const dict = translations[lang] || translations.en;
  const enDict = translations.en;

  const parts = key.split('.');
  let val: any = dict;
  let enVal: any = enDict;

  for (const p of parts) {
    if (val && typeof val === 'object' && p in val) {
      val = val[p];
    } else {
      val = undefined;
    }
    if (enVal && typeof enVal === 'object' && p in enVal) {
      enVal = enVal[p];
    } else {
      enVal = undefined;
    }
  }

  let text = typeof val === 'string' ? val : (typeof enVal === 'string' ? enVal : key);

  if (params && typeof text === 'string') {
    for (const [k, v] of Object.entries(params)) {
      text = text.replace(new RegExp(`\\{${k}\\}`, 'g'), String(v));
    }
  }

  return text;
}

/**
 * Returns true if language requires right-to-left layout direction.
 */
export function isRTL(_lang: Language): boolean {
  return false; // Arabic / Urdu / Hebrew can be added here if needed
}
