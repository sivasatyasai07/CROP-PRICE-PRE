import type { Language } from '../i18n/translations';

export interface DiseaseI18nLabels {
  badge: string;
  tabTitle: string;
  tabSubtitle: string;
  uploadTitle: string;
  uploadSubtitle: string;
  loginPrompt: string;
  analyzeBtn: string;
  noHistory: string;
  noHistoryDesc: string;
  recognizedCrop: string;
  botanicalEvidence: string;

  statusHealthy: string;
  statusDisease: string;
  statusPest: string;
  statusNutrient: string;
  statusUnclear: string;
  statusNonPlant: string;

  identIdentified: string;
  identProbable: string;
  identLowConfidence: string;
  identUnidentified: string;

  plantParts: Record<string, string>;

  primaryDiagnosis: string;
  confidenceTitle: string;
  geminiReportedConfidence: string;
  botanicalFeatures: string;
  leafMargin: string;
  leafVenation: string;
  symptomsObserved: string;
  immediateActions: string;
  preventiveMeasures: string;
  chemicalControl: string;
  safetyPrecautions: string;
  alternativePossibilities: string;
  additionalAngleNeeded: string;
  cropCandidates: string;
  candidateCropRank: string;
  candidateProbability: string;
  showDetails: string;
  hideDetails: string;
  showAllCrops: string;
  hideAllCrops: string;
  disclaimerTitle: string;
  disclaimerText: string;
  openSetLabel: string;
  analyzingFoliage: string;
  loadingStepBotanical: string;
  loadingStepSymptoms: string;
  loadingStepDiagnosis: string;
  loadingStepTreatment: string;
  fieldNotesLabel: string;
  fieldNotesPlaceholder: string;
  browseFiles: string;
  takePhoto: string;
  dragDropText: string;
  supportedFormatsText: string;
  maxFilesWarning: string;
  noHistoryFound: string;
  deleteConfirmTitle: string;
  deleteConfirmText: string;
  cancel: string;
  confirmDelete: string;
  filterByCrop: string;
  allCrops: string;
  historyTitle: string;
  newAnalysisBtn: string;
  analyzeAnotherBtn: string;
}

export const diseaseI18nMap: Record<Language, DiseaseI18nLabels> = {
  en: {
    badge: "AI-Powered Crop Pathology",
    tabTitle: "Instant Crop Disease & Health Diagnosis",
    tabSubtitle: "Upload or capture a photo of your crop foliage. Gemini AI will automatically recognize the crop species, analyze visible symptoms, and provide localized treatment guidance.",
    uploadTitle: "Upload Crop Foliage Photo",
    uploadSubtitle: "Take a clear, well-lit photo of the affected leaf or crop plant. No manual crop selection required — the AI identifies the crop automatically.",
    loginPrompt: "Please log in or sign up to analyze crop diseases.",
    analyzeBtn: "Analyze Crop Disease",
    noHistory: "No Analysis Records Found",
    noHistoryDesc: "You have not performed any crop disease analyses yet. Upload a leaf photo in the New Analysis tab to get started.",
    recognizedCrop: "Open-Set Crop Recognition",
    botanicalEvidence: "Observed Botanical Evidence",

    statusHealthy: "Healthy Plant",
    statusDisease: "Plant Disease Detected",
    statusPest: "Pest Infestation",
    statusNutrient: "Nutrient Deficiency",
    statusUnclear: "Unclear / Inconclusive Image",
    statusNonPlant: "Non-Plant Image",

    identIdentified: "Identified",
    identProbable: "Probable",
    identLowConfidence: "Low Confidence",
    identUnidentified: "Unidentified",

    plantParts: {
      Leaf: "Leaf",
      Stem: "Stem",
      Fruit: "Fruit",
      Root: "Root",
      Flower: "Flower",
      "Whole plant": "Whole Plant",
      "Multiple parts": "Multiple Parts",
      Unknown: "Plant Part"
    },

    primaryDiagnosis: "Primary Pathology Diagnosis",
    confidenceTitle: "Confidence Level",
    geminiReportedConfidence: "AI-Reported Confidence",
    botanicalFeatures: "Botanical & Visual Leaf Features",
    leafMargin: "Leaf Margin Structure",
    leafVenation: "Leaf Venation Pattern",
    symptomsObserved: "Observed Symptoms & Diagnostic Signs",
    immediateActions: "Immediate Treatment Actions",
    preventiveMeasures: "Long-Term Preventive Measures",
    chemicalControl: "Chemical & Fungicide Spray Guidelines",
    safetyPrecautions: "Safety & Spraying Precautions",
    alternativePossibilities: "Alternative Diagnostic Possibilities",
    additionalAngleNeeded: "Additional Image Angle Recommended",
    cropCandidates: "Ranked Candidate Crop Species",
    candidateCropRank: "Candidate",
    candidateProbability: "Probability",
    showDetails: "View Detailed Botanical Features",
    hideDetails: "Hide Botanical Features",
    showAllCrops: "Show All Candidate Species",
    hideAllCrops: "Hide Candidate Species",
    disclaimerTitle: "Agricultural Pathology Advisory Disclaimer",
    disclaimerText: "This analysis is an AI preliminary diagnostic decision-support tool. Always consult your local agricultural extension officer (AEO) or Krishi Vigyan Kendra (KVK) before applying hazardous chemical sprays.",
    openSetLabel: "Open-Set Agricultural Recognition",
    analyzingFoliage: "AI Pathology Analysis in Progress...",
    loadingStepBotanical: "Extracting leaf morphology and botanical characteristics...",
    loadingStepSymptoms: "Detecting visible foliar lesions, spots, and color changes...",
    loadingStepDiagnosis: "Consulting agricultural pathology reasoning engine...",
    loadingStepTreatment: "Formulating localized treatment & chemical dosage guidelines...",
    fieldNotesLabel: "Field Notes & Observations (Optional)",
    fieldNotesPlaceholder: "Optional context (e.g. soil condition, days since symptom appearance)...",
    browseFiles: "Browse Files",
    takePhoto: "Take Photo",
    dragDropText: "Drag & drop leaf photos here or use your camera",
    supportedFormatsText: "Supported: JPG, PNG, WebP up to 10MB per photo (Max 3 photos)",
    maxFilesWarning: "Maximum 3 images allowed per analysis.",
    noHistoryFound: "No prior disease diagnosis records found.",
    deleteConfirmTitle: "Delete Diagnostic Record?",
    deleteConfirmText: "Are you sure you want to delete this diagnosis record? This action cannot be undone.",
    cancel: "Cancel",
    confirmDelete: "Delete",
    filterByCrop: "Filter by Crop",
    allCrops: "All Crops",
    historyTitle: "Diagnostic History",
    newAnalysisBtn: "New Analysis",
    analyzeAnotherBtn: "Analyze Another Crop Image"
  },

  te: {
    badge: "AI పంట తెగుళ్ళ నిపుణుడు",
    tabTitle: "తక్షణ పంట తెగుళ్ళు & ఆరోగ్య నిర్ధారణ",
    tabSubtitle: "మీ పంట ఆకుల ఫోటోను అప్‌లోడ్ చేయండి. Gemini AI పంట రకాన్ని గుర్తించి, తెగుళ్ళను విశ్లేషించి, స్థానిక తెలుగు భాషలో నివారణ పద్ధతులను అందిస్తుంది.",
    uploadTitle: "పంట ఆకుల ఫోటోను అప్‌లోడ్ చేయండి",
    uploadSubtitle: "పంటను మాన్యువల్‌గా ఎంచుకోవలసిన అవసరం లేదు — AI స్వయంగా పంటను గుర్తిస్తుంది.",
    loginPrompt: "పంట తెగుళ్ళను విశ్లేషించడానికి దయచేసి లాగిన్ అవ్వండి.",
    analyzeBtn: "పంట తెగులును విశ్లేషించండి",
    noHistory: "గత విశ్లేషణ రికార్డులు ఏవీ లేవు",
    noHistoryDesc: "మీరు ఇంకా ఎటువంటి పంట వ్యాధి విశ్లేషణలు చేయలేదు. ప్రారంభించడానికి ఆకు ఫోటోను అప్‌లోడ్ చేయండి.",
    recognizedCrop: "గుర్తించబడిన పంట",
    botanicalEvidence: "గమనించిన వృక్ష శాస్త్ర ఆనవాళ్ళు",

    statusHealthy: "ఆరోగ్యకరమైన మొక్క",
    statusDisease: "పంట తెగులు గుర్తించబడింది",
    statusPest: "పురుగు / కీటకాల నష్టం",
    statusNutrient: "పోషకాల లోపం",
    statusUnclear: "అస్పష్టమైన ఫోటో",
    statusNonPlant: "మొక్క లేని ఫోటో",

    identIdentified: "ఖచ్చితంగా గుర్తించబడింది",
    identProbable: "సంభావ్య పంట",
    identLowConfidence: "తక్కువ ఖచ్చితత్వం",
    identUnidentified: "గుర్తించబడలేదు",

    plantParts: {
      Leaf: "ఆకు",
      Stem: "కాండం",
      Fruit: "కాయ / పండు",
      Root: "వేరు",
      Flower: "పువ్వు",
      "Whole plant": "మొత్తం మొక్క",
      "Multiple parts": "వివిధ భాగాలు",
      Unknown: "మొక్క భాగం"
    },

    primaryDiagnosis: "ప్రధాన తెగులు / వ్యాధి నిర్ధారణ",
    confidenceTitle: "నమ్మక స్థాయి",
    geminiReportedConfidence: "AI నివేదించిన ఖచ్చితత్వం",
    botanicalFeatures: "వృక్ష శాస్త్ర లక్షణాలు (ఆకుల నిర్మాణం & అంచులు)",
    leafMargin: "ఆకు అంచుల అమరిక",
    leafVenation: "ఈనెల అమరిక",
    symptomsObserved: "గమనించిన లక్షణాలు & వ్యాధి ఆనవాళ్ళు",
    immediateActions: "వెంటనే తీసుకోవాల్సిన చికిత్సా చర్యలు",
    preventiveMeasures: "దీర్ఘకాలిక నివారణ పద్ధతులు",
    chemicalControl: "రసాయన & మందుల పిచికారీ మార్గదర్శకాలు",
    safetyPrecautions: "భద్రత & పిచికారీ జాగ్రత్తలు",
    alternativePossibilities: "ఇతర ప్రత్యామ్నాయ కారణాలు",
    additionalAngleNeeded: "మరింత స్పష్టత కోసం అదనపు ఫోటో సిఫార్సు చేయబడింది",
    cropCandidates: "గుర్తించబడిన ఇతర సంభావ్య పంట రకాలు",
    candidateCropRank: "సంభావ్య పంట",
    candidateProbability: "సంభావ్యత",
    showDetails: "వృక్ష శాస్త్ర వివరాలు చూడండి",
    hideDetails: "వివరాలు దాచండి",
    showAllCrops: "అన్ని సంభావ్య పంటలను చూపించు",
    hideAllCrops: "పంటల జాబితాను దాచండి",
    disclaimerTitle: "వ్యవసాయ సలహా మార్గదర్శకం",
    disclaimerText: "ఇది ప్రాథమిక AI సాంకేతిక రోగ నిర్ధారణ సలహా మాత్రమే. రసాయన మందులను పిచికారీ చేసే ముందు స్థానిక వ్యవసాయ అధికారి లేదా కృషి విజ్ఞాన కేంద్రం (KVK) నిపుణులను సంప్రదించండి.",
    openSetLabel: "విస్తృత వ్యవసాయ పంట గుర్తింపు",
    analyzingFoliage: "AI పంట తెగుళ్ళ విశ్లేషణ జరుగుతోంది...",
    loadingStepBotanical: "ఆకుల ఆకారం మరియు వృక్ష శాస్త్ర లక్షణాలను విశ్లేషిస్తోంది...",
    loadingStepSymptoms: "ఆకులపై మచ్చలు, రంగు మార్పులు మరియు తెగుళ్ళను గుర్తిస్తోంది...",
    loadingStepDiagnosis: "వ్యవసాయ పాథాలజీ ఇంజిన్ ద్వారా వ్యాధిని నిర్ధారిస్తోంది...",
    loadingStepTreatment: "స్థానిక భాషలో నివారణ చర్యలు మరియు మందుల మోతాదులను సిద్ధం చేస్తోంది...",
    fieldNotesLabel: "రైతు గమనింపులు & గమనికలు (ఐచ్ఛికం)",
    fieldNotesPlaceholder: "అదనపు సమాచారం (ఉదా: 3 రోజుల క్రితం పసుపు మచ్చలు కనిపించాయి, యూరియా వాడాము)...",
    browseFiles: "ఫైళ్ళను ఎంచుకోండి",
    takePhoto: "ఫోటో తీయండి",
    dragDropText: "ఆకుల ఫోటోలను ఇక్కడ లాగండి లేదా కెమెరా ఉపయోగించండి",
    supportedFormatsText: "JPG, PNG, WebP గరిష్టంగా 10MB (గరిష్టంగా 3 ఫోటోలు)",
    maxFilesWarning: "గరిష్టంగా 3 ఫోటోలను మాత్రమే అనుమతిస్తారు.",
    noHistoryFound: "గత రోగ నిర్ధారణ రికార్డులు ఏవీ లేవు.",
    deleteConfirmTitle: "ఈ రికార్డును తొలగించాలా?",
    deleteConfirmText: "మీరు ఖచ్చితంగా ఈ రోగ నిర్ధారణ రికార్డును తొలగించాలనుకుంటున్నారా? ఈ చర్యను రద్దు చేయలేము.",
    cancel: "రద్దు చేయండి",
    confirmDelete: "తొలగించండి",
    filterByCrop: "పంట ప్రకారం వడపోత",
    allCrops: "అన్ని పంటలు",
    historyTitle: "గత రోగ రికార్డులు",
    newAnalysisBtn: "కొత్త నిర్ధారణ",
    analyzeAnotherBtn: "మరొక ఫోటోను పరీక్షించండి"
  },

  hi: {
    badge: "AI-संचालित फसल रोग निदान",
    tabTitle: "त्वरित फसल रोग एवं स्वास्थ्य निदान",
    tabSubtitle: "फसल की पत्तियों की तस्वीर अपलोड करें। Gemini AI स्वचालित रूप से फसल को पहचानकर बीमारी का विश्लेषण करेगा और हिंदी में उपचार बताएगा।",
    uploadTitle: "फसल की पत्तियों की तस्वीर अपलोड करें",
    uploadSubtitle: "फसल का मैन्युअल चयन करने की आवश्यकता नहीं है — AI स्वयं फसल की पहचान करता है।",
    loginPrompt: "फसल रोगों का विश्लेषण करने के लिए कृपया लॉग इन करें।",
    analyzeBtn: "फसल रोग का विश्लेषण करें",
    noHistory: "कोई निदान रिकॉर्ड नहीं मिला",
    noHistoryDesc: "आपने अभी तक कोई फसल रोग विश्लेषण नहीं किया है। शुरू करने के लिए तस्वीर अपलोड करें।",
    recognizedCrop: "पहचानी गई फसल",
    botanicalEvidence: "देखे गए वानस्पतिक प्रमाण",

    statusHealthy: "स्वस्थ पौधा",
    statusDisease: "फसल रोग का पता चला",
    statusPest: "कीट प्रकोप",
    statusNutrient: "पोषक तत्वों की कमी",
    statusUnclear: "अस्पष्ट चित्र",
    statusNonPlant: "पौधा नहीं है",

    identIdentified: "सटीक पहचान",
    identProbable: "संभावित फसल",
    identLowConfidence: "कम विश्वास",
    identUnidentified: "अज्ञात",

    plantParts: {
      Leaf: "पत्ती",
      Stem: "तना",
      Fruit: "फल",
      Root: "जड़",
      Flower: "फूल",
      "Whole plant": "संपूर्ण पौधा",
      "Multiple parts": "विभिन्न भाग",
      Unknown: "पौधे का भाग"
    },

    primaryDiagnosis: "मुख्य रोग निदान",
    confidenceTitle: "विश्वास स्तर",
    geminiReportedConfidence: "AI रिपोर्ट किया गया विश्वास",
    botanicalFeatures: "वानस्पतिक एवं दृश्य लक्षण",
    leafMargin: "पत्ती के किनारे की संरचना",
    leafVenation: "पत्ती की शिरा विन्यास",
    symptomsObserved: "देखे गए लक्षण एवं रोग संकेत",
    immediateActions: "तत्काल आवश्यक उपचार",
    preventiveMeasures: "दीर्घकालिक रोकथाम उपाय",
    chemicalControl: "कीटनाशक एवं कवकनाशी मार्गदर्शन",
    safetyPrecautions: "छिड़काव सुरक्षा सावधानियां",
    alternativePossibilities: "अन्य संभावित कारण",
    additionalAngleNeeded: "अतिरिक्त कोण की तस्वीर अनुशंसित",
    cropCandidates: "संभावित फसल प्रजातियां",
    candidateCropRank: "संभावित फसल",
    candidateProbability: "संभावना",
    showDetails: "वानस्पतिक विवरण देखें",
    hideDetails: "विवरण छिपाएं",
    showAllCrops: "सभी संभावित फसलें दिखाएं",
    hideAllCrops: "फसलें छिपाएं",
    disclaimerTitle: "कृषि रोग परामर्श अस्वीकरण",
    disclaimerText: "यह AI द्वारा दिया गया प्रारंभिक रोग निदान सुझाव है। रासायनिक दवाओं के उपयोग से पहले अपने स्थानीय कृषि विस्तार अधिकारी या कृषि विज्ञान केंद्र (KVK) से परामर्श लें।",
    openSetLabel: "विस्तृत कृषि फसल पहचान",
    analyzingFoliage: "AI फसल रोग विश्लेषण जारी है...",
    loadingStepBotanical: "पत्तियों के आकार एवं वानस्पतिक लक्षणों का विश्लेषण...",
    loadingStepSymptoms: "पत्तियों पर धब्बे एवं रोग के लक्षणों की पहचान...",
    loadingStepDiagnosis: "कृषि रोग विशेषज्ञ मॉडल से रोग निदान...",
    loadingStepTreatment: "स्थानीय भाषा में उपचार एवं कीटनाशक खुराक तैयार की जा रही है...",
    fieldNotesLabel: "खेत की टिप्पणियां एवं लक्षण (वैकल्पिक)",
    fieldNotesPlaceholder: "अतिरिक्त लक्षण या खाद आदि का विवरण लिखें...",
    browseFiles: "तस्वीर चुनें",
    takePhoto: "तस्वीर खींचें",
    dragDropText: "पत्तियों की तस्वीर यहां खींचें या कैमरा उपयोग करें",
    supportedFormatsText: "JPG, PNG, WebP अधिकतम 10MB (अधिकतम 3 तस्वीरें)",
    maxFilesWarning: "अधिकतम 3 तस्वीरें जोड़ी जा सकती हैं।",
    noHistoryFound: "कोई पूर्व रोग निदान रिकॉर्ड नहीं मिला।",
    deleteConfirmTitle: "रिकॉर्ड हटाएं?",
    deleteConfirmText: "क्या आप वाकई इस निदान रिकॉर्ड को हटाना चाहते हैं?",
    cancel: "रद्द करें",
    confirmDelete: "हटाएं",
    filterByCrop: "फसल अनुसार फ़िल्टर",
    allCrops: "सभी फसलें",
    historyTitle: "निदान इतिहास",
    newAnalysisBtn: "नया निदान",
    analyzeAnotherBtn: "अन्य फसल तस्वीर जांचें"
  },

  ml: {
    badge: "AI വിള രോഗനിർണയം",
    tabTitle: "തത്സമയ വിള രോഗനിർണയം & ആരോഗ്യ പരിശോധന",
    tabSubtitle: "വിളയുടെ ഇലകളുടെ ചിത്രം നൽകുക. Gemini AI വിളയെ തിരിച്ചറിഞ്ഞ് രോഗവിവരങ്ങളും ചികിത്സാരീതികളും നിർദ്ദേശിക്കുന്നു.",
    uploadTitle: "വിളയുടെ ഇലകളുടെ ചിത്രം അപ്‌ലോഡ് ചെയ്യുക",
    uploadSubtitle: "വിള സ്വമേധയാ തിരഞ്ഞെടുക്കേണ്ടതില്ല — AI വിളയെ സ്വയം തിരിച്ചറിയും.",
    loginPrompt: "വിള രോഗങ്ങൾ പരിശോധിക്കാൻ ദയവായി ലോഗിൻ ചെയ്യുക.",
    analyzeBtn: "വിള രോഗം പരിശോധിക്കുക",
    noHistory: "പരിശോധനാ രേഖകൾ ലഭ്യമല്ല",
    noHistoryDesc: "നിങ്ങൾ ഇതുവരെ പരിശോധനകളൊന്നും നടത്തിയിട്ടില്ല. ആരംഭിക്കാൻ ചിത്രം അപ്‌ലോഡ് ചെയ്യുക.",
    recognizedCrop: "തിരിച്ചറിഞ്ഞ വിള",
    botanicalEvidence: "നിരീക്ഷിച്ച സവിശേഷതകൾ",

    statusHealthy: "ആരോഗ്യമുള്ള ചെടി",
    statusDisease: "വിള രോഗം കണ്ടെത്തി",
    statusPest: "കീടബാധ",
    statusNutrient: "പോഷക കുറവ്",
    statusUnclear: "വ്യക്തതയില്ലാത്ത ചിത്രം",
    statusNonPlant: "ചെടിയുടെ ചിത്രമല്ല",

    identIdentified: "തിരിച്ചറിഞ്ഞു",
    identProbable: "സാധ്യതയുള്ള വിള",
    identLowConfidence: "കുറഞ്ഞ വിശ്വാസ്യത",
    identUnidentified: "തിരിച്ചറിയാത്തത്",

    plantParts: {
      Leaf: "ഇല",
      Stem: "തണ്ട്",
      Fruit: "കായ് / പഴം",
      Root: "വേര്",
      Flower: "പൂവ്",
      "Whole plant": "പൂർണ്ണ ചെടി",
      "Multiple parts": "പല ഭാഗങ്ങൾ",
      Unknown: "ചെടിയുടെ ഭാഗം"
    },

    primaryDiagnosis: "പ്രധാന രോഗനിർണയം",
    confidenceTitle: "വിശ്വാസ്യത",
    geminiReportedConfidence: "AI റിപ്പോർട്ട് ചെയ്ത വിശ്വാസ്യത",
    botanicalFeatures: "സസ്യശാസ്ത്ര സവിശേഷതകൾ",
    leafMargin: "ഇലയുടെ അരികുകൾ",
    leafVenation: "ഇല ഞരമ്പുകൾ",
    symptomsObserved: "കണ്ടെത്തിയ ലക്ഷണങ്ങൾ",
    immediateActions: "ഉടൻ സ്വീകരിക്കേണ്ട നടപടികൾ",
    preventiveMeasures: "പ്രതിരോധ മാർഗ്ഗങ്ങൾ",
    chemicalControl: "കീടനാശിനി പ്രയോഗ നിർദ്ദേശങ്ങൾ",
    safetyPrecautions: "സുരക്ഷാ മുൻകരുതലുകൾ",
    alternativePossibilities: "മറ്റ് സാധ്യതകൾ",
    additionalAngleNeeded: "കൂടുതൽ ചിത്രം ആവശ്യമാണ്",
    cropCandidates: "സാധ്യതയുള്ള വിളകൾ",
    candidateCropRank: "സാധ്യതയുള്ള വിള",
    candidateProbability: "സാധ്യത",
    showDetails: "വിശദാംശങ്ങൾ കാണുക",
    hideDetails: "വിശദാംശങ്ങൾ മറയ്ക്കുക",
    showAllCrops: "എല്ലാ വിളകളും കാണിക്കുക",
    hideAllCrops: "വിളകൾ മറയ്ക്കുക",
    disclaimerTitle: "മാർഗ്ഗനിർദ്ദേശ വിവരണം",
    disclaimerText: "ഇതൊരു പ്രാഥമിക AI രോഗനിർണയ ഉപകരണം മാത്രമാണ്. രാസവസ്തുക്കൾ പ്രയോഗിക്കുന്നതിന് മുൻപ് കൃഷി ഓഫീസറുമായി ബന്ധപ്പെടുക.",
    openSetLabel: "വിള തിരിച്ചറിയൽ",
    analyzingFoliage: "പരിശോധന പുരോഗമിക്കുന്നു...",
    loadingStepBotanical: "സസ്യ സവിശേഷതകൾ പരിശോധിക്കുന്നു...",
    loadingStepSymptoms: "ലക്ഷണങ്ങൾ കണ്ടെത്തുന്നു...",
    loadingStepDiagnosis: "രോഗനിർണയം നടത്തുന്നു...",
    loadingStepTreatment: "ചികിത്സാ നിർദ്ദേശങ്ങൾ തയ്യാറാക്കുന്നു...",
    fieldNotesLabel: "കുറിപ്പുകൾ (ഓപ്ഷണൽ)",
    fieldNotesPlaceholder: "അധിക വിവരങ്ങൾ ചേർക്കുക...",
    browseFiles: "ഫയലുകൾ തിരഞ്ഞെടുക്കുക",
    takePhoto: "ഫോട്ടോ എടുക്കുക",
    dragDropText: "ചിത്രങ്ങൾ ഇവിടെ ഡ്രാഗ് ചെയ്യുക",
    supportedFormatsText: "JPG, PNG, WebP (പരമാവധി 3 ചിത്രങ്ങൾ)",
    maxFilesWarning: "പരമാവധി 3 ചിത്രങ്ങൾ വരെ മാത്രം.",
    noHistoryFound: "മുൻകാല രേഖകളൊന്നുമില്ല.",
    deleteConfirmTitle: "നീക്കം ചെയ്യണോ?",
    deleteConfirmText: "ഈ രേഖ തീർച്ചയായും നീക്കം ചെയ്യണോ?",
    cancel: "റദ്ദാക്കുക",
    confirmDelete: "നീക്കം ചെയ്യുക",
    filterByCrop: "വിള പ്രകാരം ഫിൽട്ടർ ചെയ്യുക",
    allCrops: "എല്ലാ വിളകളും",
    historyTitle: "ചരിത്രം",
    newAnalysisBtn: "പുതിയ പരിശോധന",
    analyzeAnotherBtn: "മറ്റൊരു ചിത്രം പരിശോധിക്കുക"
  },

  ta: {
    badge: "AI பயிர் நோய் கண்டறிதல்",
    tabTitle: "உடனடி பயிர் நோய் & ஆரோக்கிய பரிசோதனை",
    tabSubtitle: "பயிர் இலைகளின் புகைப்படத்தை பதிவேற்றவும். Gemini AI பயிரை கண்டறிந்து நோய்களை பகுப்பாய்வு செய்து தமிழில் சிகிச்சை வழிகாட்டும்.",
    uploadTitle: "பயிர் இலை புகைப்படத்தை பதிவேற்றவும்",
    uploadSubtitle: "பயிரை கைமுறையாக தேர்ந்தெடுக்க வேண்டியதில்லை — AI தானாகவே பயிரை கண்டறியும்.",
    loginPrompt: "பயிர் நோய்களை பகுப்பாய்வு செய்ய உள்நுழையவும்.",
    analyzeBtn: "பயிர் நோயை பகுப்பாய்வு செய்",
    noHistory: "பதிவுகள் எதுவும் இல்லை",
    noHistoryDesc: "நீங்கள் இதுவரை எந்த பயிர் நோய் பகுப்பாய்வையும் செய்யவில்லை. தொடங்க புகைப்படத்தை பதிவேற்றவும்.",
    recognizedCrop: "கண்டறியப்பட்ட பயிர்",
    botanicalEvidence: "கண்டறியப்பட்ட சான்றுகள்",

    statusHealthy: "ஆரோக்கியமான பயிர்",
    statusDisease: "பயிர் நோய் கண்டறியப்பட்டது",
    statusPest: "பூச்சி தாக்குதல்",
    statusNutrient: "ஊட்டச்சத்து குறைபாடு",
    statusUnclear: "தெளிவற்ற படம்",
    statusNonPlant: "பயிர் அல்லாத படம்",

    identIdentified: "அடையாளம் காணப்பட்டது",
    identProbable: "சாத்தியமான பயிர்",
    identLowConfidence: "குறைந்த நம்பிக்கை",
    identUnidentified: "அடையாளம் தெரியவில்லை",

    plantParts: {
      Leaf: "இலை",
      Stem: "தண்டு",
      Fruit: "காய் / பழம்",
      Root: "வேர்",
      Flower: "மலர்",
      "Whole plant": "முழு பயிர்",
      "Multiple parts": "பல பகுதிகள்",
      Unknown: "பயிர் பகுதி"
    },

    primaryDiagnosis: "முதன்மை நோய் கண்டறிதல்",
    confidenceTitle: "நம்பகத்தன்மை",
    geminiReportedConfidence: "AI வழங்கிய நம்பகத்தன்மை",
    botanicalFeatures: "தாவரவியல் அம்சங்கள்",
    leafMargin: "இலை விளிம்பு அமைப்பு",
    leafVenation: "இலை நரம்பு அமைப்பு",
    symptomsObserved: "கண்டறியப்பட்ட அறிகுறிகள்",
    immediateActions: "உடனடி சிகிச்சை முறைகள்",
    preventiveMeasures: "நீண்டகால தடுப்பு முறைகள்",
    chemicalControl: "மருந்து தெளிப்பு வழிகாட்டுதல்",
    safetyPrecautions: "பாதுகாப்பு முன்னெச்சரிக்கைகள்",
    alternativePossibilities: "மாற்று சாத்தியக்கூறுகள்",
    additionalAngleNeeded: "கூடுதல் படம் பரிந்துரைக்கப்படுகிறது",
    cropCandidates: "சாத்தியமான பயிர்கள்",
    candidateCropRank: "சாத்தியமான பயிர்",
    candidateProbability: "சாத்தியக்கூறு",
    showDetails: "விவரங்களை பார்க்க",
    hideDetails: "விவரங்களை மறைக்க",
    showAllCrops: "அனைத்து பயிர்களையும் காட்டு",
    hideAllCrops: "பயிர்களை மறை",
    disclaimerTitle: "வழிகாட்டுதல் அறிக்கை",
    disclaimerText: "இது ஒரு ஆரம்பநிலை AI தொழில்நுட்ப ஆலோசனை மட்டுமே. ரசாயன மருந்துகளை தெளிப்பதற்கு முன் உள்ளூர் வேளாண்மை அதிகாரியை அணுகவும்.",
    openSetLabel: "விவசாய பயிர் அடையாளம் காணல்",
    analyzingFoliage: "AI பகுப்பாய்வு நடக்கிறது...",
    loadingStepBotanical: "தாவரவியல் அம்சங்கள் ஆய்வு செய்யப்படுகிறது...",
    loadingStepSymptoms: "இலை அறிகுறிகள் கண்டறியப்படுகிறது...",
    loadingStepDiagnosis: "நோய் கண்டறிதல் மேற்கொள்ளப்படுகிறது...",
    loadingStepTreatment: "மருந்து தெளிப்பு வழிகாட்டல்கள் தயாரிக்கப்படுகிறது...",
    fieldNotesLabel: "குறிப்புகள் (விருப்பத்தேர்வு)",
    fieldNotesPlaceholder: "கூடுதல் குறிப்புகளை இங்கே எழுதவும்...",
    browseFiles: "கோப்புகளை தேர்வு செய்க",
    takePhoto: "படம் எடு",
    dragDropText: "படங்களை இங்கே இழுக்கவும் அல்லது கேமராவை பயன்படுத்தவும்",
    supportedFormatsText: "JPG, PNG, WebP (அதிகபட்சம் 3 படங்கள்)",
    maxFilesWarning: "அதிகபட்சம் 3 படங்கள் மட்டுமே.",
    noHistoryFound: "முந்தைய பதிவுகள் எதுவும் இல்லை.",
    deleteConfirmTitle: "அழிக்கவா?",
    deleteConfirmText: "இந்த பதிவை நிச்சயமாக நீக்க விரும்புகிறீர்களா?",
    cancel: "ரத்து செய்",
    confirmDelete: "அழிக்கவும்",
    filterByCrop: "பயிர் வாரியாக வடிகட்டவும்",
    allCrops: "அனைத்து பயிர்கள்",
    historyTitle: "வரலாறு",
    newAnalysisBtn: "புதிய ஆய்வு",
    analyzeAnotherBtn: "மற்றொரு படத்தை ஆய்வு செய்"
  }
};

export function getDiseaseI18n(lang: Language = 'en'): DiseaseI18nLabels {
  return diseaseI18nMap[lang] || diseaseI18nMap.en;
}

