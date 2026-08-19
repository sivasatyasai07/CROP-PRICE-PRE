import React from 'react';
import type { VerifiedForecastResponse, ForecastRecord } from '../../services/forecastService';
import type { Language } from '../../i18n/translations';
import { Check, TrendingUp, TrendingDown, Minus } from 'lucide-react';

export interface ForecastResultProps {
  data: VerifiedForecastResponse;
  language?: Language;
}

export const ForecastResult: React.FC<ForecastResultProps> = ({ data, language: _language = 'en' }) => {
  if (!data || !data.records || data.records.length === 0) {
    return null;
  }

  const allRecords = data.records;
  // Exclude the base record (Day 0) so only the 3 forecast days are displayed
  const displayRecords: ForecastRecord[] = allRecords.length >= 4 ? allRecords.slice(1, 4) : allRecords;

  const baseRecord = allRecords[0];
  const basePrice = (data.latest_observed_price !== undefined && data.latest_observed_price !== null)
    ? data.latest_observed_price
    : (baseRecord?.modal_price ?? 0);

  const baseDateStr = data.latest_observed_date || (baseRecord?.target_date || baseRecord?.date ? String(baseRecord.target_date || baseRecord.date) : String(data.selected_date));

  // Determine overall expected trend from response metadata or calculation
  const lastRecord = displayRecords[displayRecords.length - 1];
  const lastPrice = lastRecord?.modal_price ?? basePrice;
  const overallDiff = (lastPrice !== null && basePrice !== null) ? lastPrice - basePrice : 0;
  const overallPct = (basePrice && basePrice > 0) ? (overallDiff / basePrice) * 100 : 0;

  let trendLabel = 'Stable Trend';
  let trendColor = '#334155';
  let TrendIcon = Minus;

  if (data.trend_direction === 'upward' || overallPct > 1.0) {
    trendLabel = 'Upward Trend';
    trendColor = '#15803d';
    TrendIcon = TrendingUp;
  } else if (data.trend_direction === 'downward' || overallPct < -1.0) {
    trendLabel = 'Downward Trend';
    trendColor = '#dc2626';
    TrendIcon = TrendingDown;
  } else if (data.trend_direction === null || basePrice === null || lastPrice === null) {
    trendLabel = 'Trend Unavailable';
    trendColor = '#64748b';
    TrendIcon = Minus;
  }

  // 2-Day Sell or Hold Recommendation Logic
  const day2Record = displayRecords.length >= 2 ? displayRecords[1] : displayRecords[0];
  const day3Record = displayRecords.length >= 3 ? displayRecords[2] : day2Record;
  const targetFuturePrice = day2Record?.modal_price ?? day3Record?.modal_price ?? basePrice;
  const twoDayDiff = (targetFuturePrice !== null && basePrice !== null) ? targetFuturePrice - basePrice : 0;
  const twoDayPct = (basePrice && basePrice > 0) ? (twoDayDiff / basePrice) * 100 : 0;

  let recTitle = 'HOLD CROP (Wait 2 Days for Higher Price)';
  let recDescription = `Prices are projected to increase by ₹${Math.abs(twoDayDiff).toFixed(2)}/quintal (+${Math.abs(twoDayPct).toFixed(1)}%) over the next 2 days. Holding your harvest is recommended to get higher profits.`;
  let recBadgeText = '📈 RECOMMENDATION: HOLD';
  let recColor = '#15803d';
  let recBg = '#f0fdf4';
  let recBorder = '#86efac';
  let recIconBg = '#dcfce7';
  let recBadgeBg = '#dcfce7';
  let RecIcon = TrendingUp;

  if (twoDayDiff < -10 || twoDayPct < -1.0) {
    recTitle = 'SELL NOW (Avoid Potential Price Drop)';
    recDescription = `Prices are projected to decline by ₹${Math.abs(twoDayDiff).toFixed(2)}/quintal (-${Math.abs(twoDayPct).toFixed(1)}%) over the next 2 days. Selling at today's modal price is advised to avoid losses.`;
    recBadgeText = '📉 RECOMMENDATION: SELL NOW';
    recColor = '#b91c1c';
    recBg = '#fef2f2';
    recBorder = '#fca5a5';
    recIconBg = '#fee2e2';
    recBadgeBg = '#fee2e2';
    RecIcon = TrendingDown;
  } else if (Math.abs(twoDayDiff) <= 10) {
    recTitle = 'SELL OR HOLD (Stable Mandi Prices)';
    recDescription = `Prices are expected to remain steady around ₹${(basePrice ?? 0).toFixed(2)}/quintal over the next 2 days. You may sell now or hold based on your storage and logistics convenience.`;
    recBadgeText = '⚖️ RECOMMENDATION: SELL OR HOLD';
    recColor = '#0369a1';
    recBg = '#f0f9ff';
    recBorder = '#7dd3fc';
    recIconBg = '#e0f2fe';
    recBadgeBg = '#e0f2fe';
    RecIcon = Minus;
  }

  // Multi-language translation for recommendation
  if (_language === 'te') {
    if (twoDayDiff > 10 || twoDayPct > 1.0) {
      recTitle = 'పంటను నిల్వ ఉంచండి (2 రోజులు వేచి ఉండండి)';
      recDescription = `రాబోయే 2 రోజుల్లో ధర క్వింటాలుకు ₹${Math.abs(twoDayDiff).toFixed(2)} పెరిగే అవకాశం ఉంది. అధిక లాభం కోసం నిల్వ ఉంచడం మంచిది.`;
      recBadgeText = '📈 సిఫార్సు: నిల్వ ఉంచండి (HOLD)';
    } else if (twoDayDiff < -10 || twoDayPct < -1.0) {
      recTitle = 'వెంటనే అమ్మండి (ధర తగ్గే అవకాశం)';
      recDescription = `రాబోయే 2 రోజుల్లో ధర క్వింటాలుకు ₹${Math.abs(twoDayDiff).toFixed(2)} తగ్గే అవకాశం ఉంది. నేటి ధర వద్ద వెంటనే అమ్మడం మంచిది.`;
      recBadgeText = '📉 సిఫార్సు: అమ్మండి (SELL NOW)';
    } else {
      recTitle = 'అమ్మండి లేదా నిల్వ ఉంచండి (స్థిరమైన ధరలు)';
      recDescription = `రాబోయే 2 రోజుల్లో ధరలు స్థిరంగా ఉండే అవకాశం ఉంది. మీ వీలును బట్టి నిర్ణయం తీసుకోండి.`;
      recBadgeText = '⚖️ సిఫార్సు: అమ్మండి లేదా నిల్వ ఉంచండి';
    }
  }

  const topBorderAccents = ['#10b981', '#f59e0b', '#3b82f6'];
  const dayPills = ['Tomorrow (Day 1)', 'Day +2', 'Day +3'];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem', marginTop: '0.25rem' }}>
      
      {/* 1. Hero Card */}
      <div
        style={{
          background: '#ffffff',
          borderRadius: '16px',
          border: '1px solid #e2e8f0',
          padding: '1.25rem 1.75rem',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '1.25rem',
          boxShadow: '0 2px 8px rgba(0, 0, 0, 0.04)',
        }}
      >
        {/* Left Side: Check Circle + Latest Observed Price */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '1.15rem' }}>
          <div
            style={{
              width: '46px',
              height: '46px',
              borderRadius: '50%',
              background: '#dcfce7',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              flexShrink: 0,
            }}
          >
            <Check size={24} color="#16a34a" strokeWidth={2.8} />
          </div>

          <div>
            <div style={{ fontSize: '0.78rem', fontWeight: 700, color: '#475569', textTransform: 'uppercase', letterSpacing: '0.3px' }}>
              LATEST OBSERVED MODAL PRICE ({baseDateStr})
            </div>
            <div style={{ fontSize: '2.1rem', fontWeight: 800, color: '#000000', lineHeight: 1.15, marginTop: '0.15rem' }}>
              {basePrice !== null && basePrice > 0 ? (
                <>
                  ₹{basePrice.toFixed(2)}
                  <span style={{ fontSize: '1.05rem', fontWeight: 500, color: '#64748b', marginLeft: '0.35rem' }}>/ quintal</span>
                </>
              ) : (
                <span style={{ fontSize: '1.2rem', color: '#94a3b8' }}>Unavailable</span>
              )}
            </div>
          </div>
        </div>

        {/* Right Side: 3-Day Expected Trend Box */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.85rem',
            background: '#f1f5f9',
            border: '1px solid #e2e8f0',
            padding: '0.75rem 1.4rem',
            borderRadius: '12px',
          }}
        >
          <TrendIcon size={24} color={trendColor} strokeWidth={2.5} />
          <div>
            <div style={{ fontSize: '0.7rem', fontWeight: 700, color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.3px' }}>
              3–DAY EXPECTED TREND
            </div>
            <div style={{ fontSize: '1.15rem', fontWeight: 800, color: '#0f172a' }}>
              {trendLabel}
            </div>
          </div>
        </div>
      </div>

      {/* 2. Farmer 2-Day Sell vs Hold Recommendation Card */}
      {basePrice !== null && basePrice > 0 && (
        <div
          style={{
            background: recBg,
            border: `1.5px solid ${recBorder}`,
            borderRadius: '16px',
            padding: '1.25rem 1.75rem',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            flexWrap: 'wrap',
            gap: '1rem',
            boxShadow: '0 2px 8px rgba(0, 0, 0, 0.04)',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <div
              style={{
                width: '44px',
                height: '44px',
                borderRadius: '50%',
                background: recIconBg,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                flexShrink: 0,
              }}
            >
              <RecIcon size={22} color={recColor} strokeWidth={2.5} />
            </div>
            <div>
              <div style={{ fontSize: '0.75rem', fontWeight: 800, color: recColor, textTransform: 'uppercase', letterSpacing: '0.4px' }}>
                {_language === 'te' ? 'రైతు మార్కెట్ సలహా (2 రోజుల నిర్ణయం)' : 'FARMER MARKET ADVISORY (2-DAY DECISION)'}
              </div>
              <div style={{ fontSize: '1.2rem', fontWeight: 800, color: '#0f172a', marginTop: '0.1rem' }}>
                {recTitle}
              </div>
              <p style={{ fontSize: '0.85rem', color: '#334155', fontWeight: 500, margin: '0.2rem 0 0 0' }}>
                {recDescription}
              </p>
            </div>
          </div>

          <div
            style={{
              padding: '0.5rem 1.15rem',
              borderRadius: '50px',
              fontWeight: 800,
              fontSize: '0.88rem',
              background: recBadgeBg,
              color: recColor,
              border: `1.5px solid ${recBorder}`,
            }}
          >
            {recBadgeText}
          </div>
        </div>
      )}

      {/* 3. 3 Cards Side-by-Side */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
          gap: '1.15rem',
        }}
      >
        {displayRecords.map((record, index) => {
          const targetDateStr = record.target_date || record.date ? String(record.target_date || record.date) : '';
          const currentPrice = record.modal_price;
          
          const isOfficialApi = record.price_source === 'official_api';
          const isOfficialCsv = record.price_source === 'official_csv';
          const isObserved = isOfficialApi || isOfficialCsv || (record.is_observed && !record.is_predicted);
          
          const isTrainedModel = (
            record.price_source === 'predicted_model' &&
            record.prediction_method === 'trained_model' &&
            record.prediction_executed === true &&
            record.model_predict_called === true
          );

          const isFallback = (
            record.price_source === 'fallback_last_observed' ||
            record.price_source === 'fallback_rolling_average' ||
            record.prediction_method === 'fallback'
          );

          const isUnavailable = record.price_source === 'unavailable' || currentPrice === null;

          // Price difference relative to base today
          let diffFromBase = 0;
          let isDiffZero = true;
          let isDiffPositive = false;

          if (currentPrice !== null && basePrice !== null) {
            diffFromBase = currentPrice - basePrice;
            isDiffZero = Math.abs(diffFromBase) < 0.01;
            isDiffPositive = diffFromBase > 0;
          }

          // Header title & badge styles based on exact source verification
          let cardHeaderTitle = 'PREDICTED PRICE';
          let cardHeaderSub = '(AI MODEL)';
          let cardBadgeText = 'CATBOOST ML';
          let cardHeaderColor = '#0284c7';
          let cardBadgeBg = '#e0f2fe';
          let cardBadgeColor = '#0369a1';

          if (isOfficialApi) {
            cardHeaderTitle = 'ACTUAL PRICE';
            cardHeaderSub = '(RECORDED)';
            cardBadgeText = 'DATA.GOV.IN API';
            cardHeaderColor = '#15803d';
            cardBadgeBg = '#dcfce7';
            cardBadgeColor = '#166534';
          } else if (isOfficialCsv) {
            cardHeaderTitle = 'ACTUAL PRICE';
            cardHeaderSub = '(RECORDED)';
            cardBadgeText = 'MASTER DATA CSV';
            cardHeaderColor = '#15803d';
            cardBadgeBg = '#dcfce7';
            cardBadgeColor = '#166534';
          } else if (isTrainedModel) {
            cardHeaderTitle = 'PREDICTED PRICE';
            cardHeaderSub = '(AI MODEL)';
            cardBadgeText = 'CATBOOST ML';
            cardHeaderColor = '#0284c7';
            cardBadgeBg = '#e0f2fe';
            cardBadgeColor = '#0369a1';
          } else if (isFallback) {
            cardHeaderTitle = 'FALLBACK ESTIMATE';
            cardHeaderSub = '(LAST OBSERVED)';
            cardBadgeText = 'LAST OBSERVED FALLBACK';
            cardHeaderColor = '#c2410c';
            cardBadgeBg = '#ffedd5';
            cardBadgeColor = '#9a3412';
          } else if (isUnavailable) {
            cardHeaderTitle = 'PRICE UNAVAILABLE';
            cardHeaderSub = '(NO DATA)';
            cardBadgeText = 'UNAVAILABLE';
            cardHeaderColor = '#b91c1c';
            cardBadgeBg = '#fee2e2';
            cardBadgeColor = '#991b1b';
          }

          return (
            <div
              key={`card-${index}-${targetDateStr}`}
              style={{
                background: '#ffffff',
                borderRadius: '16px',
                border: '1px solid #e2e8f0',
                borderTop: `4px solid ${topBorderAccents[index % 3]}`,
                padding: '1.25rem 1.15rem',
                boxShadow: '0 2px 8px rgba(0, 0, 0, 0.03)',
                display: 'flex',
                flexDirection: 'column',
                gap: '0.85rem',
              }}
            >
              {/* Header: Day Pill & Target Date */}
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span
                  style={{
                    background: isObserved ? '#dcfce7' : (isTrainedModel ? '#e0f2fe' : (isFallback ? '#ffedd5' : '#fee2e2')),
                    color: isObserved ? '#166534' : (isTrainedModel ? '#0369a1' : (isFallback ? '#9a3412' : '#991b1b')),
                    fontSize: '0.72rem',
                    fontWeight: 700,
                    padding: '0.2rem 0.65rem',
                    borderRadius: '9999px',
                  }}
                >
                  {dayPills[index % 3]}
                </span>
                <span style={{ color: '#0f172a', fontWeight: 700, fontSize: '0.82rem' }}>
                  {targetDateStr}
                </span>
              </div>

              {/* Sub-header Badges */}
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.35rem' }}>
                <div style={{ fontSize: '0.72rem', fontWeight: 800, color: cardHeaderColor, textTransform: 'uppercase' }}>
                  {cardHeaderTitle} <br /><span style={{ fontWeight: 700 }}>{cardHeaderSub}</span>
                </div>
                <span
                  style={{
                    background: cardBadgeBg,
                    color: cardBadgeColor,
                    fontSize: '0.68rem',
                    fontWeight: 700,
                    padding: '0.2rem 0.55rem',
                    borderRadius: '9999px',
                    textTransform: 'uppercase',
                    letterSpacing: '0.2px',
                  }}
                >
                  {cardBadgeText}
                </span>
              </div>

              {/* Price Row */}
              <div>
                <div style={{ display: 'flex', alignItems: 'baseline', gap: '0.25rem' }}>
                  {currentPrice !== null ? (
                    <>
                      <span style={{ fontSize: '1.95rem', fontWeight: 800, color: '#000000', lineHeight: 1 }}>
                        ₹{currentPrice % 1 === 0 ? currentPrice : currentPrice.toFixed(2)}
                      </span>
                      <span style={{ fontSize: '0.88rem', fontWeight: 500, color: '#64748b' }}>
                        /qtl
                      </span>
                    </>
                  ) : (
                    <span style={{ fontSize: '1.35rem', fontWeight: 800, color: '#94a3b8' }}>
                      Unavailable
                    </span>
                  )}
                </div>

                {/* Price Difference from Base Date */}
                {currentPrice !== null && basePrice !== null ? (
                  <div style={{ marginTop: '0.45rem', fontSize: '0.8rem', fontWeight: 700 }}>
                    {isDiffZero ? (
                      <span style={{ color: '#475569' }}>
                        — 0.00 ₹/qtl from today
                      </span>
                    ) : isDiffPositive ? (
                      <span style={{ color: '#16a34a' }}>
                        ↗ +{diffFromBase.toFixed(2)} ₹/qtl from today
                      </span>
                    ) : (
                      <span style={{ color: '#dc2626' }}>
                        ↘ {diffFromBase.toFixed(2)} ₹/qtl from today
                      </span>
                    )}
                  </div>
                ) : null}
              </div>

              {/* Bottom Box: 80% Confidence Interval or Verification State */}
              <div
                style={{
                  background: '#f8fafc',
                  border: '1px solid #e2e8f0',
                  borderRadius: '10px',
                  padding: '0.75rem 0.85rem',
                  marginTop: 'auto',
                }}
              >
                {record.interval_available && record.lower_bound != null && record.upper_bound != null ? (
                  <>
                    <div style={{ fontSize: '0.68rem', fontWeight: 800, color: '#475569', textTransform: 'uppercase', letterSpacing: '0.3px', marginBottom: '0.35rem' }}>
                      80% CONFIDENCE INTERVAL (CONFORMAL)
                    </div>
                    <div style={{ fontSize: '0.82rem', fontWeight: 800, color: '#000000', display: 'flex', gap: '0.85rem', flexWrap: 'wrap' }}>
                      <span>Low: ₹{record.lower_bound.toFixed(2)}</span>
                      <span>High: ₹{record.upper_bound.toFixed(2)}</span>
                    </div>
                  </>
                ) : isObserved ? (
                  <>
                    <div style={{ fontSize: '0.68rem', fontWeight: 800, color: '#166534', textTransform: 'uppercase', letterSpacing: '0.3px', marginBottom: '0.35rem' }}>
                      ACTUAL OBSERVED PRICE
                    </div>
                    <div style={{ fontSize: '0.75rem', fontWeight: 600, color: '#475569' }}>
                      Recorded observation (exact value)
                    </div>
                  </>
                ) : isFallback ? (
                  <>
                    <div style={{ fontSize: '0.68rem', fontWeight: 800, color: '#9a3412', textTransform: 'uppercase', letterSpacing: '0.3px', marginBottom: '0.35rem' }}>
                      FALLBACK ESTIMATE
                    </div>
                    <div style={{ fontSize: '0.72rem', fontWeight: 600, color: '#64748b' }}>
                      {record.fallback_reason || 'Last observed mandi price'}
                    </div>
                  </>
                ) : (
                  <>
                    <div style={{ fontSize: '0.68rem', fontWeight: 800, color: '#991b1b', textTransform: 'uppercase', letterSpacing: '0.3px', marginBottom: '0.35rem' }}>
                      INTERVAL UNAVAILABLE
                    </div>
                    <div style={{ fontSize: '0.72rem', fontWeight: 600, color: '#64748b' }}>
                      Calibration metadata unavailable
                    </div>
                  </>
                )}
              </div>

            </div>
          );
        })}
      </div>

    </div>
  );
};

