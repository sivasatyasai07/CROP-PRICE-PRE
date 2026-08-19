import React, { useState } from 'react';
import type { Language } from '../i18n/translations';
import { translations } from '../i18n/translations';
import { ExternalLink, CheckCircle, Award, Landmark, Sparkles } from 'lucide-react';

interface Props {
  language: Language;
}

interface Scheme {
  id: string;
  nameEn: string;
  nameTe: string;
  nameHi: string;
  nameMl: string;
  nameTa: string;
  category: 'central' | 'ap' | 'insurance' | 'credit';
  benefitsEn: string;
  benefitsTe: string;
  benefitsHi: string;
  benefitsMl: string;
  benefitsTa: string;
  eligibilityEn: string;
  eligibilityTe: string;
  eligibilityHi: string;
  eligibilityMl: string;
  eligibilityTa: string;
  officialUrl: string;
  badge: string;
  imageUrl: string;
}

export const GovernmentSchemesTab: React.FC<Props> = ({ language }) => {
  const t = translations[language].schemes;
  const [selectedCategory, setSelectedCategory] = useState<string>('all');

  const schemes: Scheme[] = [
    {
      id: 'pm-kisan',
      nameEn: 'PM-KISAN (Pradhan Mantri Kisan Samman Nidhi)',
      nameTe: 'పీఎం కిసాన్ (సమ్మాన్ నిధి)',
      nameHi: 'पीएम-किसान (प्रधान मंत्री किसान सम्मान निधि)',
      nameMl: 'പിഎം കിസാൻ (പ്രധാനമന്ത്രി കിസാൻ സമ്മാൻ നിധി)',
      nameTa: 'பிஎம்-கிசான் (பிரதான் மந்திரி கிசான் சம்மான் நிதி)',
      category: 'central',
      benefitsEn: '₹6,000 per year direct income support in 3 equal installments of ₹2,000 directly into farmer bank accounts.',
      benefitsTe: 'సంవత్సరానికి ₹6,000ల ఆర్థిక సహాయం 3 సమాన విడతలలో (రూ.2,000 చొప్పున) నేరుగా బ్యాంక్ ఖాతాలో జమ.',
      benefitsHi: 'किसानों के बैंक खातों में सीधी ₹6,000 प्रति वर्ष 3 समान किस्तों में आय सहायता।',
      benefitsMl: 'വർഷത്തിൽ ₹6,000 സാമ്പത്തിക സഹായം കർഷക ബാങ്ക് അക്കൗണ്ടിലേക്ക് നേരിട്ട് നൽകുന്നു.',
      benefitsTa: 'ஆண்டுக்கு ₹6,000 நேரடி உதவித்தொகை 3 தவணைகளாக விவசாயிகளின் வங்கி கணக்கில் பெறலாம்.',
      eligibilityEn: 'Small and marginal farmer families with cultivable landholding up to 2 hectares.',
      eligibilityTe: 'సాగుభూమి ఉన్న చిన్న మరియు సన్నకారు రైతు కుటుంబాలు.',
      eligibilityHi: 'कृषि योग्य भूमि वाले छोटे और सीमांत किसान परिवार।',
      eligibilityMl: 'കൃഷിഭൂമിയുള്ള ചെറുകിട കർഷക കുടുംബങ്ങൾ.',
      eligibilityTa: 'விவசாய நிலம் உள்ள அனைத்து சிறு குறு விவசாயிகள்.',
      officialUrl: 'https://pmkisan.gov.in/',
      badge: 'Central Government • Direct Transfer',
      imageUrl: 'https://images.unsplash.com/photo-1592982537447-7440770cbfc9?auto=format&fit=crop&w=600&q=80'
    },
    {
      id: 'rythu-bharosa',
      nameEn: 'YSR Rythu Bharosa (Andhra Pradesh)',
      nameTe: 'వైఎస్ఆర్ రైతు భరోసా (ఆంధ్రప్రదేశ్)',
      nameHi: 'वाईएसआर रायथू भरोसा (आंध्र प्रदेश)',
      nameMl: 'വൈഎസ്ആർ റൈതു ഭരോസ (ആന്ധ്രപ്രദേശ്)',
      nameTa: 'வொய்எஸ்ஆர் ரைது பரோசா (ஆந்திரப் பிரதேசம்)',
      category: 'ap',
      benefitsEn: 'Financial assistance of ₹13,500 per year per farmer family for crop investment ahead of sowing season.',
      benefitsTe: 'విత్తనాల సీజన్‌కు ముందు ప్రతి రైతు కుటుంబానికి సంవత్సరానికి ₹13,500 పెట్టుబడి సాయం.',
      benefitsHi: 'बुवाई के मौसम से पहले प्रति किसान परिवार ₹13,500 की वार्षिक वित्तीय सहायता।',
      benefitsMl: 'വിത്തു വിതയ്ക്കുന്നതിന് മുൻപായി കർഷക കുടുംബത്തിന് പ്രതിവർഷം ₹13,500 സാമ്പത്തിക സഹായം.',
      benefitsTa: 'ஆண்டுக்கு ₹13,500 முதலீட்டு நிதி உதவி விதைப்பு பருவத்திற்கு முன் வழங்கப்படும்.',
      eligibilityEn: 'All landowning farmers and SC/ST/BC/Minority tenant farmers in Andhra Pradesh.',
      eligibilityTe: 'ఆంధ్రప్రదేశ్‌లోని భూమి ఉన్న రైతులు మరియు కౌలు రైతులు.',
      eligibilityHi: 'आंध्र प्रदेश के सभी भूमिस्वामी एवं पट्टेदार किसान।',
      eligibilityMl: 'ആന്ധ്രപ്രദേശിലെ എല്ലാ കർഷകരും പാട്ടക്കർഷകരും.',
      eligibilityTa: 'ஆந்திராவில் உள்ள நில உரிமையாளர்கள் மற்றும் குத்தகை விவசாயிகள்.',
      officialUrl: 'https://rythubharosa.ap.gov.in/',
      badge: 'Andhra Pradesh State Govt',
      imageUrl: 'https://images.unsplash.com/photo-1625246333195-78d9c38ad449?auto=format&fit=crop&w=600&q=80'
    },
    {
      id: 'pmfby',
      nameEn: 'PM Fasal Bima Yojana (Crop Insurance)',
      nameTe: 'పీఎం ఫసల్ బీమా యోజన (పంట బీమా)',
      nameHi: 'प्रधानमंत्री फसल बीमा योजना',
      nameMl: 'പ്രധാനമന്ത്രി ഫസൽ ബീമ യോജന (വിള ഇൻഷുറൻസ്)',
      nameTa: 'பிரதான் மந்திரி பயிர் காப்பீட்டு திட்டம்',
      category: 'insurance',
      benefitsEn: 'Comprehensive crop insurance against natural calamities, droughts, floods, and pest damage at lowest premium rates (1.5% - 2%).',
      benefitsTe: 'ప్రకృతి వైపరీత్యాలు, కరువు, వరదలు మరియు చీడపీడల వల్ల పంట నష్టానికి అత్యల్ప ప్రీమియం రేటులో సమగ్ర బీమా.',
      benefitsHi: 'प्राकृतिक आपदाओं, सूखे, बाढ़ और कीटों से फसल क्षति के खिलाफ व्यापक बीमा।',
      benefitsMl: 'പ്രകൃതിദുരന്തങ്ങൾ മൂലം വിളനാശം സംഭവിച്ചാൽ ഇൻഷുറൻസ് പരിരക്ഷ.',
      benefitsTa: 'இயற்கை சீற்றங்கள் மற்றும் பூச்சி தாக்குதலால் ஏற்படும் பயிர் இழப்பிற்கு காப்பீடு.',
      eligibilityEn: 'All farmers growing notified crops in notified areas including sharecroppers and tenant farmers.',
      eligibilityTe: 'నోటిఫై చేసిన పంటలు పండించే రైతులు మరియు కౌలు రైతులు అందరూ అర్హులు.',
      eligibilityHi: 'अधिसूचित क्षेत्रों में अधिसूचित फसलें उगाने वाले सभी किसान।',
      eligibilityMl: 'അറിയിപ്പ് ലഭിച്ച വിളകൾ കൃഷി ചെയ്യുന്ന എല്ലാ കർഷകരും.',
      eligibilityTa: 'அறிவிக்கப்பட்ட பயிர்களை பயிரிடும் அனைத்து விவசாயிகளும்.',
      officialUrl: 'https://pmfby.gov.in/',
      badge: 'Crop Risk & Disaster Insurance',
      imageUrl: 'https://images.unsplash.com/photo-1500382017468-9049fed747ef?auto=format&fit=crop&w=600&q=80'
    },
    {
      id: 'enam',
      nameEn: 'e-NAM (National Agriculture Market)',
      nameTe: 'ఈ-నామ్ (జాతీయ వ్యవసాయ మార్కెట్)',
      nameHi: 'ई-नाम (राष्ट्रीय कृषि बाजार)',
      nameMl: 'ഇ-നാം (ദേശീയ കാർഷിക വിപണി)',
      nameTa: 'இ-நாம் (தேசிய விவசாய சந்தை)',
      category: 'central',
      benefitsEn: 'Pan-India electronic trading portal uniting APMC mandis for transparent price discovery and online payment.',
      benefitsTe: 'సులభమైన పంట విక్రయం, పారదర్శక ధరలు మరియు ఆన్‌లైన్ పేమెంట్ కొరకు దేశవ్యాప్త ఎలక్ట్రానిక్ మార్కెట్.',
      benefitsHi: 'पारदर्शी मूल्य खोज और ऑनलाइन भुगतान के लिए अखिल भारतीय इलेक्ट्रॉनिक व्यापार पोर्टल।',
      benefitsMl: 'വിളകൾ ഓൺലൈനായി ലേലം വിളിച്ച് സാമ്പത്തിക സുതാര്യത നൽകുന്നു.',
      benefitsTa: 'வெளிப்படையான ஆன்லைன் விற்பனை மற்றும் கட்டண வசதிக்கான தேசிய மின்னணு சந்தை.',
      eligibilityEn: 'All registered farmers, traders, and APMC market yards across India.',
      eligibilityTe: 'భారతదేశంలోని నమోదు చేసుకున్న రైతులు మరియు వ్యాపారులు అందరూ.',
      eligibilityHi: 'भारत भर के सभी पंजीकृत किसान और व्यापारी।',
      eligibilityMl: 'രജിസ്റ്റർ ചെയ്ത എല്ലാ കർഷകരും വ്യാപാരികളും.',
      eligibilityTa: 'பதிவு செய்த அனைத்து விவசாயிகள் மற்றும் வியாபாரிகள்.',
      officialUrl: 'https://www.enam.gov.in/',
      badge: 'Pan-India Digital Mandi Portal',
      imageUrl: 'https://images.unsplash.com/photo-1586771107445-d3ca888129ff?auto=format&fit=crop&w=600&q=80'
    },
    {
      id: 'kcc',
      nameEn: 'Kisan Credit Card (KCC) Scheme',
      nameTe: 'కిసాన్ క్రెడిట్ కార్డ్ (KCC) పథకం',
      nameHi: 'किसान क्रेडिट कार्ड (KCC) योजना',
      nameMl: 'കിസാൻ ക്രെഡിറ്റ് കാർഡ് (KCC) പദ്ധതി',
      nameTa: 'கிசான் கிரெடிட் கார்டு (KCC) திட்டம்',
      category: 'credit',
      benefitsEn: 'Low-interest short-term credit up to ₹3 Lakhs at 4% effective interest rate for crop seeds, fertilizers & machinery.',
      benefitsTe: 'విత్తనాలు, ఎరువులు మరియు వ్యవసాయ యంత్రాల కోసం 4% వడ్డీకే ₹3 లక్షల వరకు సులభ రుణం.',
      benefitsHi: 'बीज, उर्वरक और मशीनरी के लिए 4% प्रभावी ब्याज दर पर ₹3 लाख तक का कम ब्याज ऋण।',
      benefitsMl: 'വിത്ത്, വളം, യന്ത്രങ്ങൾ എന്നിവ വാങ്ങാൻ കർഷകർക്ക് കുറഞ്ഞ പലിശയിൽ ബാങ്ക് വായ്പ.',
      benefitsTa: 'விதை மற்றும் உரம் வாங்க 4% வட்டி விகிதத்தில் ₹3 லட்சம் வரை கடன் உதவி.',
      eligibilityEn: 'Farmers, individual/joint borrowers, tenant farmers, self-help groups (SHGs).',
      eligibilityTe: 'రైతులు, కౌలు రైతులు మరియు స్వయం సహాయక బృందాలు.',
      eligibilityHi: 'सभी किसान, पट्टेदार किसान और स्वयं सहायता समूह।',
      eligibilityMl: 'എല്ലാ കർഷകരും പാട്ടക്കർഷകരും സ്വയം സഹായ സംഘങ്ങളും.',
      eligibilityTa: 'அனைத்து விவசாயிகள் மற்றும் சுய உதவிக்குழுக்கள்.',
      officialUrl: 'https://www.myscheme.gov.in/schemes/kcc',
      badge: 'Agricultural Credit & Loan Support',
      imageUrl: 'https://images.unsplash.com/photo-1554224155-8d04cb21cd6c?auto=format&fit=crop&w=600&q=80'
    },
    {
      id: 'soil-health',
      nameEn: 'Soil Health Card Scheme',
      nameTe: 'సాయిల్ హెల్త్ కార్డ్ (నేల ఆరోగ్య కార్డ్)',
      nameHi: 'मृदा स्वास्थ्य कार्ड योजना',
      nameMl: 'സോയിൽ ഹെൽത്ത് കാർഡ് (മണ്ണ് പരിശോധന)',
      nameTa: 'மண் வள அட்டை திட்டம்',
      category: 'central',
      benefitsEn: 'Free soil testing report detailing nutrient status (NPK & micronutrients) with tailored crop fertilizer recommendations.',
      benefitsTe: 'భూమి సారాన్ని ఉచితంగా పరీక్షించి ఎరువుల వినియోగానికి సంబంధించిన నివేదిక మరియు సలహాలు.',
      benefitsHi: 'मुफ्त मिट्टी परीक्षण रिपोर्ट, जिसमें उर्वरक सिफारिशों के साथ पोषक तत्वों की स्थिति का विवरण शामिल है।',
      benefitsMl: 'മണ്ണിന്റെ ഫലഭൂയിഷ്ഠത സൗജന്യമായി പരിശോധിച്ച് വളപ്രയോഗത്തിനുള്ള നിർദ്ദേശങ്ങൾ.',
      benefitsTa: 'இலவச மண் பரிசோதனை அறிக்கை மற்றும் உர பயன்பாட்டு பரிந்துரைகள்.',
      eligibilityEn: 'All agricultural landowners and operational farmers in India.',
      eligibilityTe: 'భారతదేశంలోని సాగుభూమి ఉన్న రైతులందరూ.',
      eligibilityHi: 'भारत के सभी कृषि भूमिस्वामी और किसान।',
      eligibilityMl: 'എല്ലാ കർഷകർക്കും സൗജന്യ മണ്ണ് പരിശോധന.',
      eligibilityTa: 'அனைத்து நில உரிமையாளர் விவசாயிகளுக்கும்.',
      officialUrl: 'https://soilhealth.dac.gov.in/',
      badge: 'Soil Nutrient Testing',
      imageUrl: 'https://images.unsplash.com/photo-1464226184884-fa280b87c399?auto=format&fit=crop&w=600&q=80'
    }
  ];

  const filteredSchemes = selectedCategory === 'all' 
    ? schemes 
    : schemes.filter(s => s.category === selectedCategory);

  const getName = (s: Scheme) => {
    switch (language) {
      case 'te': return s.nameTe;
      case 'hi': return s.nameHi;
      case 'ml': return s.nameMl;
      case 'ta': return s.nameTa;
      default: return s.nameEn;
    }
  };

  const getBenefits = (s: Scheme) => {
    switch (language) {
      case 'te': return s.benefitsTe;
      case 'hi': return s.benefitsHi;
      case 'ml': return s.benefitsMl;
      case 'ta': return s.benefitsTa;
      default: return s.benefitsEn;
    }
  };

  const getEligibility = (s: Scheme) => {
    switch (language) {
      case 'te': return s.eligibilityTe;
      case 'hi': return s.eligibilityHi;
      case 'ml': return s.eligibilityMl;
      case 'ta': return s.eligibilityTa;
      default: return s.eligibilityEn;
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      
      {/* Header Banner */}
      <div className="glass-panel" style={{ padding: '2rem', borderRadius: 'var(--radius-lg)', background: 'linear-gradient(135deg, rgba(255,255,255,0.95) 0%, rgba(216,243,220,0.4) 100%)', borderLeft: '6px solid var(--primary)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', color: 'var(--primary)', fontWeight: 700, marginBottom: '0.4rem', fontSize: '0.9rem' }}>
              <Landmark size={20} />
              <span>OFFICIAL WELFARE & FINANCIAL SCHEMES</span>
            </div>
            <h2 style={{ fontSize: '1.75rem', fontWeight: 800, color: 'var(--primary-dark)' }}>
              {t.title}
            </h2>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.95rem', marginTop: '0.3rem', maxWidth: '800px' }}>
              {t.subtitle}
            </p>
          </div>

          <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
            <button
              onClick={() => setSelectedCategory('all')}
              className={selectedCategory === 'all' ? 'btn-primary' : 'btn-secondary'}
              style={{ fontSize: '0.85rem', padding: '0.5rem 1rem' }}
            >
              All Schemes
            </button>
            <button
              onClick={() => setSelectedCategory('central')}
              className={selectedCategory === 'central' ? 'btn-primary' : 'btn-secondary'}
              style={{ fontSize: '0.85rem', padding: '0.5rem 1rem' }}
            >
              Central Govt
            </button>
            <button
              onClick={() => setSelectedCategory('ap')}
              className={selectedCategory === 'ap' ? 'btn-primary' : 'btn-secondary'}
              style={{ fontSize: '0.85rem', padding: '0.5rem 1rem' }}
            >
              Andhra Pradesh
            </button>
            <button
              onClick={() => setSelectedCategory('insurance')}
              className={selectedCategory === 'insurance' ? 'btn-primary' : 'btn-secondary'}
              style={{ fontSize: '0.85rem', padding: '0.5rem 1rem' }}
            >
              Insurance
            </button>
          </div>
        </div>
      </div>

      {/* Grid of Schemes */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))', gap: '1.75rem' }}>
        {filteredSchemes.map((scheme) => (
          <div
            key={scheme.id}
            className="glass-panel"
            style={{
              overflow: 'hidden',
              display: 'flex',
              flexDirection: 'column',
              borderRadius: 'var(--radius-md)',
              border: '1px solid var(--border-color)',
              background: '#ffffff',
            }}
          >
            {/* Cover Image & Badge */}
            <div style={{ position: 'relative', height: '180px', width: '100%', overflow: 'hidden' }}>
              <img
                src={scheme.imageUrl}
                alt={scheme.nameEn}
                style={{ width: '100%', height: '100%', objectFit: 'cover' }}
              />
              <div style={{ position: 'absolute', inset: 0, background: 'linear-gradient(to top, rgba(27,67,50,0.85) 0%, transparent 60%)' }} />
              
              <div style={{ position: 'absolute', top: '1rem', left: '1rem' }}>
                <span className="badge badge-green" style={{ background: '#ffffff', color: 'var(--primary-dark)', boxShadow: 'var(--shadow-sm)' }}>
                  <Award size={14} color="var(--primary)" />
                  {scheme.badge}
                </span>
              </div>

              <h3 style={{ position: 'absolute', bottom: '1rem', left: '1rem', right: '1rem', color: '#ffffff', fontSize: '1.15rem', fontWeight: 800, textShadow: '0 2px 4px rgba(0,0,0,0.5)' }}>
                {getName(scheme)}
              </h3>
            </div>

            {/* Content */}
            <div style={{ padding: '1.5rem', flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'space-between', gap: '1.25rem' }}>
              
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                <div>
                  <div style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--primary)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.3rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                    <Sparkles size={14} />
                    {t.benefits}
                  </div>
                  <p style={{ fontSize: '0.92rem', color: 'var(--text-main)', fontWeight: 500, lineHeight: 1.5 }}>
                    {getBenefits(scheme)}
                  </p>
                </div>

                <div style={{ background: 'var(--bg-primary)', padding: '0.85rem 1rem', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-color)' }}>
                  <div style={{ fontSize: '0.78rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.2rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                    <CheckCircle size={14} color="var(--primary)" />
                    {t.eligibility}
                  </div>
                  <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', lineHeight: 1.4 }}>
                    {getEligibility(scheme)}
                  </p>
                </div>
              </div>

              {/* Action Link */}
              <div style={{ borderTop: '1px solid var(--border-color)', paddingTop: '1rem' }}>
                <a
                  href={scheme.officialUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="btn-primary"
                  style={{ width: '100%', justifyContent: 'center' }}
                >
                  <span>{t.visitOfficialWebsite}</span>
                  <ExternalLink size={16} />
                </a>
              </div>

            </div>
          </div>
        ))}
      </div>

    </div>
  );
};
