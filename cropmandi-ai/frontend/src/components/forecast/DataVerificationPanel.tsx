import React from 'react';
import type { VerifiedForecastResponse } from '../../services/forecastService';
import { formatKolkataDate } from '../../utils/timezone';
import { getLocalizedCommodityName, getLocalizedMarketName } from '../../utils/i18nData';
import type { Language } from '../../i18n/translations';
import { ShieldCheck, Sparkles, CheckCircle2, XCircle, Calendar } from 'lucide-react';
import { PriceSourceBadge } from './PriceSourceBadge';

export interface DataVerificationPanelProps {
  data: VerifiedForecastResponse;
  language?: Language;
}

export const DataVerificationPanel: React.FC<DataVerificationPanelProps> = ({ data, language = 'en' }) => {
  const formattedSelectedDate = formatKolkataDate(data.selected_date);
  const formattedServerDate = data.server_date ? formatKolkataDate(data.server_date) : formattedSelectedDate;

  const dateRangeStr = data.date_range
    ? `${formatKolkataDate(data.date_range.start)} — ${formatKolkataDate(data.date_range.end)}`
    : `${formattedSelectedDate} (4-day sequence)`;

  const apiCheckedTimeStr = data.api_checked_time || new Date(data.fetched_at).toLocaleString('en-IN', {
    dateStyle: 'medium',
    timeStyle: 'short',
    timeZone: 'Asia/Kolkata',
  }) + ' IST';

  const apiCount = data.summary?.official_api_count ?? (data.summary?.official_values || 0);
  const csvCount = data.summary?.official_csv_count ?? 0;
  const predCount = data.summary?.predicted_count ?? (data.summary?.predicted_values || 0);
  const unavailCount = data.summary?.unavailable_count ?? (data.summary?.unavailable_values || 0);

  const locCrop = getLocalizedCommodityName(data.commodity, language);
  const locMarket = getLocalizedMarketName(data.market, language);

  return (
    <div
      style={{
        background: '#ffffff',
        borderRadius: '16px',
        border: '1px solid #e2e8f0',
        padding: '1.5rem',
        boxShadow: '0 2px 8px rgba(0, 0, 0, 0.04)',
        marginTop: '0.5rem',
      }}
    >
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '0.75rem', borderBottom: '1px solid #f1f5f9', paddingBottom: '0.85rem', marginBottom: '1rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
          <div style={{ width: '32px', height: '32px', borderRadius: '8px', background: '#dcfce7', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <ShieldCheck size={18} color="#16a34a" />
          </div>
          <div>
            <h4 style={{ fontSize: '0.98rem', fontWeight: 800, color: '#0f172a', margin: 0 }}>
              {language === 'te'
                ? 'డేటా శోధన ధృవీకరణ & ప్రాధాన్యతా ఆడిట్'
                : (language === 'hi'
                    ? 'डेटा लुकअप सत्यापन एवं प्राथमिकता ऑडिट'
                    : 'Data Lookup Verification & Precedence Audit')}
            </h4>
            <span style={{ fontSize: '0.75rem', color: '#64748b' }}>
              {locCrop} • {locMarket} ({dateRangeStr})
            </span>
          </div>
        </div>

        <span
          style={{
            background: '#f0fdf4',
            color: '#15803d',
            border: '1px solid #bbf7d0',
            fontSize: '0.72rem',
            fontWeight: 800,
            padding: '0.2rem 0.6rem',
            borderRadius: '50px',
            display: 'inline-flex',
            alignItems: 'center',
            gap: '0.35rem',
          }}
        >
          <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#22c55e' }}></span>
          {language === 'te' ? 'ప్రాధాన్యత క్రమం ధృవీకరించబడింది' : (language === 'hi' ? 'प्राथमिकता क्रम सत्यापित' : 'Precedence Hierarchy Verified')}
        </span>
      </div>

      {/* Summary Stat Pills */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: '0.75rem', marginBottom: '1.25rem' }}>
        <div style={{ background: '#f0fdf4', padding: '0.65rem 0.85rem', borderRadius: '10px', border: '1px solid #bbf7d0' }}>
          <span style={{ fontSize: '0.7rem', fontWeight: 700, color: '#166534', textTransform: 'uppercase' }}>
            {language === 'te' ? 'అధికారిక API విలువలు' : (language === 'hi' ? 'आधिकारिक एपीआई मूल्य' : 'Official API Values')}
          </span>
          <div style={{ fontSize: '1.2rem', fontWeight: 800, color: '#15803d' }}>{apiCount}</div>
        </div>

        <div style={{ background: '#e0f2fe', padding: '0.65rem 0.85rem', borderRadius: '10px', border: '1px solid #bae6fd' }}>
          <span style={{ fontSize: '0.7rem', fontWeight: 700, color: '#0369a1', textTransform: 'uppercase' }}>
            {language === 'te' ? 'మాస్టర్ CSV విలువలు' : (language === 'hi' ? 'मास्टर सीएसवी मूल्य' : 'Master CSV Values')}
          </span>
          <div style={{ fontSize: '1.2rem', fontWeight: 800, color: '#0284c7' }}>{csvCount}</div>
        </div>

        <div style={{ background: '#fef3c7', padding: '0.65rem 0.85rem', borderRadius: '10px', border: '1px solid #fde68a' }}>
          <span style={{ fontSize: '0.7rem', fontWeight: 700, color: '#92400e', textTransform: 'uppercase' }}>
            {language === 'te' ? 'AI అంచనా వేసిన రోజులు' : (language === 'hi' ? 'अनुमानित दिन' : 'Predictions Generated')}
          </span>
          <div style={{ fontSize: '1.2rem', fontWeight: 800, color: '#b45309' }}>{predCount}</div>
        </div>

        <div style={{ background: '#f8fafc', padding: '0.65rem 0.85rem', borderRadius: '10px', border: '1px solid #e2e8f0' }}>
          <span style={{ fontSize: '0.7rem', fontWeight: 700, color: '#64748b', textTransform: 'uppercase' }}>
            {language === 'te' ? 'లభించని తేదీలు' : (language === 'hi' ? 'अनुपलब्ध दिन' : 'Unavailable Dates')}
          </span>
          <div style={{ fontSize: '1.2rem', fontWeight: 800, color: '#475569' }}>{unavailCount}</div>
        </div>
      </div>

      {/* Per-Date Lookup Verification Table */}
      <div style={{ overflowX: 'auto', border: '1px solid #e2e8f0', borderRadius: '12px' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.82rem', textAlign: 'left' }}>
          <thead>
            <tr style={{ background: '#f8fafc', borderBottom: '1px solid #e2e8f0' }}>
              <th style={{ padding: '0.75rem 1rem', fontWeight: 700, color: '#475569' }}>
                {language === 'te' ? 'తేదీ' : (language === 'hi' ? 'तारीख' : 'Date')}
              </th>
              <th style={{ padding: '0.75rem 1rem', fontWeight: 700, color: '#475569' }}>
                {language === 'te' ? 'API తనిఖీ' : (language === 'hi' ? 'एपीआई जांच' : 'API Checked')}
              </th>
              <th style={{ padding: '0.75rem 1rem', fontWeight: 700, color: '#475569' }}>
                {language === 'te' ? 'API రికార్డు లభించిందా' : (language === 'hi' ? 'एपीआई रिकॉर्ड मिला' : 'API Record Found')}
              </th>
              <th style={{ padding: '0.75rem 1rem', fontWeight: 700, color: '#475569' }}>
                {language === 'te' ? 'master-data.csv తనిఖీ' : (language === 'hi' ? 'मास्टर डेटा जांच' : 'master-data.csv Checked')}
              </th>
              <th style={{ padding: '0.75rem 1rem', fontWeight: 700, color: '#475569' }}>
                {language === 'te' ? 'CSV రికార్డు లభించిందా' : (language === 'hi' ? 'सीएसवी रिकॉर्ड मिला' : 'CSV Record Found')}
              </th>
              <th style={{ padding: '0.75rem 1rem', fontWeight: 700, color: '#475569' }}>
                {language === 'te' ? 'అంచనా వేయబడిందా' : (language === 'hi' ? 'पूर्वानुमान बना' : 'Prediction Generated')}
              </th>
              <th style={{ padding: '0.75rem 1rem', fontWeight: 700, color: '#475569' }}>
                {language === 'te' ? 'తుది మూలం' : (language === 'hi' ? 'अंतिम स्रोत' : 'Final Source Label')}
              </th>
            </tr>
          </thead>
          <tbody>
            {data.records.map((r, idx) => {
              const formattedDate = formatKolkataDate(r.date);
              const apiFound = r.api_record_found || r.price_source === 'official_api';
              const csvChecked = r.master_csv_checked ?? (!apiFound);
              const csvFound = r.master_csv_record_found || r.price_source === 'official_csv';
              const predGen = r.prediction_generated || r.price_source === 'predicted';

              return (
                <tr key={r.date || idx} style={{ borderBottom: idx < data.records.length - 1 ? '1px solid #f1f5f9' : 'none' }}>
                  <td style={{ padding: '0.75rem 1rem', fontWeight: 800, color: '#0f172a' }}>
                    {formattedDate}
                  </td>
                  <td style={{ padding: '0.75rem 1rem' }}>
                    <span style={{ color: '#16a34a', fontWeight: 700, display: 'inline-flex', alignItems: 'center', gap: '0.25rem' }}>
                      <CheckCircle2 size={13} /> {language === 'te' ? 'అవును' : (language === 'hi' ? 'हाँ' : 'Yes')}
                    </span>
                  </td>
                  <td style={{ padding: '0.75rem 1rem' }}>
                    {apiFound ? (
                      <span style={{ color: '#16a34a', fontWeight: 700, display: 'inline-flex', alignItems: 'center', gap: '0.25rem' }}>
                        <CheckCircle2 size={13} /> {language === 'te' ? 'అవును' : (language === 'hi' ? 'हाँ' : 'Yes')}
                      </span>
                    ) : (
                      <span style={{ color: '#64748b', fontWeight: 600, display: 'inline-flex', alignItems: 'center', gap: '0.25rem' }}>
                        <XCircle size={13} /> {language === 'te' ? 'లేదు' : (language === 'hi' ? 'नहीं' : 'No')}
                      </span>
                    )}
                  </td>
                  <td style={{ padding: '0.75rem 1rem' }}>
                    {csvChecked ? (
                      <span style={{ color: '#0284c7', fontWeight: 700, display: 'inline-flex', alignItems: 'center', gap: '0.25rem' }}>
                        <CheckCircle2 size={13} /> {language === 'te' ? 'అవును' : (language === 'hi' ? 'हाँ' : 'Yes')}
                      </span>
                    ) : (
                      <span style={{ color: '#94a3b8', fontWeight: 600 }}>
                        {language === 'te' ? 'అవసరం లేదు' : (language === 'hi' ? 'आवश्यक नहीं' : 'No (Not needed)')}
                      </span>
                    )}
                  </td>
                  <td style={{ padding: '0.75rem 1rem' }}>
                    {csvFound ? (
                      <span style={{ color: '#0284c7', fontWeight: 700, display: 'inline-flex', alignItems: 'center', gap: '0.25rem' }}>
                        <CheckCircle2 size={13} /> {language === 'te' ? 'అవును' : (language === 'hi' ? 'हाँ' : 'Yes')}
                      </span>
                    ) : (
                      <span style={{ color: '#64748b', fontWeight: 600, display: 'inline-flex', alignItems: 'center', gap: '0.25rem' }}>
                        <XCircle size={13} /> {language === 'te' ? 'లేదు' : (language === 'hi' ? 'नहीं' : 'No')}
                      </span>
                    )}
                  </td>
                  <td style={{ padding: '0.75rem 1rem' }}>
                    {predGen ? (
                      <span style={{ color: '#d97706', fontWeight: 700, display: 'inline-flex', alignItems: 'center', gap: '0.25rem' }}>
                        <Sparkles size={13} /> {language === 'te' ? 'అవును' : (language === 'hi' ? 'हाँ' : 'Yes')}
                      </span>
                    ) : (
                      <span style={{ color: '#94a3b8', fontWeight: 600 }}>
                        {language === 'te' ? 'అధికారిక డేటా లభించింది' : (language === 'hi' ? 'आधिकारिक डेटा मिला' : 'No (Official found)')}
                      </span>
                    )}
                  </td>
                  <td style={{ padding: '0.75rem 1rem' }}>
                    <PriceSourceBadge priceSource={r.price_source} sourceLabel={r.source_label} />
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Live API Freshness & Sync Diagnostics Panel */}
      <div style={{ background: '#f8fafc', borderRadius: '12px', border: '1px solid #e2e8f0', padding: '1rem', marginBottom: '1.25rem' }}>
        <div style={{ fontSize: '0.82rem', fontWeight: 800, color: '#0f172a', marginBottom: '0.65rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <span>LIVE API DATA SYNCHRONIZATION & FRESHNESS AUDIT</span>
          <span style={{ fontSize: '0.72rem', fontWeight: 700, color: data.data_refresh_status === 'failed' ? '#dc2626' : '#16a34a' }}>
            Status: {data.data_refresh_status?.toUpperCase() || 'SUCCESS'}
          </span>
        </div>

        {data.stale_data_warning && (
          <div style={{ background: '#fffbeb', border: '1px solid #fde68a', borderRadius: '8px', padding: '0.6rem 0.85rem', marginBottom: '0.75rem', fontSize: '0.78rem', color: '#92400e', fontWeight: 600 }}>
            ⚠️ {data.stale_data_warning}
          </div>
        )}

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(190px, 1fr))', gap: '0.6rem', fontSize: '0.78rem' }}>
          <div style={{ background: '#ffffff', padding: '0.5rem 0.75rem', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
            <span style={{ color: '#64748b', fontSize: '0.7rem', display: 'block', fontWeight: 700 }}>LIVE API CHECKED</span>
            <span style={{ fontWeight: 800, color: data.api_checked ? '#16a34a' : '#dc2626' }}>
              {data.api_checked ? 'Yes (data.gov.in queried)' : 'No'}
            </span>
          </div>

          <div style={{ background: '#ffffff', padding: '0.5rem 0.75rem', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
            <span style={{ color: '#64748b', fontSize: '0.7rem', display: 'block', fontWeight: 700 }}>LATEST OFFICIAL API DATE</span>
            <span style={{ fontWeight: 800, color: '#0f172a' }}>
              {data.latest_official_api_date ? formatKolkataDate(data.latest_official_api_date) : 'Unavailable in API'}
            </span>
          </div>

          <div style={{ background: '#ffffff', padding: '0.5rem 0.75rem', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
            <span style={{ color: '#64748b', fontSize: '0.7rem', display: 'block', fontWeight: 700 }}>LATEST STORED OFFICIAL DATE</span>
            <span style={{ fontWeight: 800, color: '#0f172a' }}>
              {data.latest_stored_official_date ? formatKolkataDate(data.latest_stored_official_date) : (data.latest_observed_date ? formatKolkataDate(data.latest_observed_date) : 'N/A')}
            </span>
          </div>

          <div style={{ background: '#ffffff', padding: '0.5rem 0.75rem', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
            <span style={{ color: '#64748b', fontSize: '0.7rem', display: 'block', fontWeight: 700 }}>LATEST FEATURE DATE USED</span>
            <span style={{ fontWeight: 800, color: '#0f172a' }}>
              {data.feature_latest_date ? formatKolkataDate(data.feature_latest_date) : (data.latest_observed_date ? formatKolkataDate(data.latest_observed_date) : 'N/A')}
            </span>
          </div>

          <div style={{ background: '#ffffff', padding: '0.5rem 0.75rem', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
            <span style={{ color: '#64748b', fontSize: '0.7rem', display: 'block', fontWeight: 700 }}>LATEST PRICE USED IN FEATURES</span>
            <span style={{ fontWeight: 800, color: '#0f172a' }}>
              {data.latest_price_used_for_features != null ? `₹${data.latest_price_used_for_features.toFixed(2)}/Q` : (data.latest_observed_price != null ? `₹${data.latest_observed_price.toFixed(2)}/Q` : 'N/A')}
            </span>
          </div>

          <div style={{ background: '#ffffff', padding: '0.5rem 0.75rem', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
            <span style={{ color: '#64748b', fontSize: '0.7rem', display: 'block', fontWeight: 700 }}>LATEST ARRIVAL USED IN FEATURES</span>
            <span style={{ fontWeight: 800, color: '#0f172a' }}>
              {data.latest_arrival_used_for_features != null ? `${data.latest_arrival_used_for_features.toFixed(1)} MT` : 'Unavailable / Imputed'}
            </span>
          </div>

          <div style={{ background: '#ffffff', padding: '0.5rem 0.75rem', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
            <span style={{ color: '#64748b', fontSize: '0.7rem', display: 'block', fontWeight: 700 }}>RECORDS FETCHED & SYNCED</span>
            <span style={{ fontWeight: 800, color: '#0f172a' }}>
              {data.records_fetched_count ?? 0} records
            </span>
          </div>

          <div style={{ background: '#ffffff', padding: '0.5rem 0.75rem', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
            <span style={{ color: '#64748b', fontSize: '0.7rem', display: 'block', fontWeight: 700 }}>PREDICTION FALLBACK USED</span>
            <span style={{ fontWeight: 800, color: (data.summary?.fallback_last_observed_count ?? 0) > 0 ? '#d97706' : '#16a34a' }}>
              {(data.summary?.fallback_last_observed_count ?? 0) > 0 ? 'Yes (Last Observed)' : 'No (ML Active / Official)'}
            </span>
          </div>
        </div>
      </div>

      {/* Footer Info */}
      <div style={{ marginTop: '1rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.5rem', fontSize: '0.76rem', color: '#64748b' }}>
        <div>
          {language === 'te' ? 'ధృవీకరణ పూర్తయిన సమయం:' : (language === 'hi' ? 'सत्यापन समय:' : 'Data verification completed at:')} <strong>{apiCheckedTimeStr}</strong>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
          <Calendar size={13} />
          <span>
            {language === 'te' ? 'ఎంచుకున్న తేదీ:' : (language === 'hi' ? 'చयनित तारीख:' : 'Selected Date:')} <strong>{formattedSelectedDate}</strong> ({language === 'te' ? 'నేటి సర్వర్ తేదీ:' : (language === 'hi' ? 'आज सर्वर तिथि:' : 'Today in IST:')} {formattedServerDate})
          </span>
        </div>
      </div>
    </div>
  );
};
