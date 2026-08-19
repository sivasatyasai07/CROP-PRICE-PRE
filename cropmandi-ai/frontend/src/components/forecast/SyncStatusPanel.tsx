import React from 'react';
import type { SyncStatusResponse } from '../../services/forecastService';

export interface SyncStatusPanelProps {
  syncStatus: SyncStatusResponse | null;
}

export const SyncStatusPanel: React.FC<SyncStatusPanelProps> = ({ syncStatus }) => {
  if (!syncStatus) return null;

  const getStatusBadge = () => {
    switch (syncStatus.status) {
      case 'success':
        return <span className="px-2 py-0.5 rounded text-xs font-bold bg-emerald-100 text-emerald-800 border border-emerald-300">Synchronized</span>;
      case 'in_progress':
        return <span className="px-2 py-0.5 rounded text-xs font-bold bg-blue-100 text-blue-800 border border-blue-300 animate-pulse">Syncing...</span>;
      case 'failed':
        return <span className="px-2 py-0.5 rounded text-xs font-bold bg-red-100 text-red-800 border border-red-300">Sync Error</span>;
      default:
        return <span className="px-2 py-0.5 rounded text-xs font-bold bg-slate-100 text-slate-800 border border-slate-300">Idle</span>;
    }
  };

  return (
    <div className="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl p-3 text-xs flex items-center justify-between shadow-sm">
      <div className="flex items-center space-x-2">
        <span className="font-semibold text-slate-700 dark:text-slate-200">Daily Mandi Sync Status:</span>
        {getStatusBadge()}
      </div>
      <div className="text-slate-500 dark:text-slate-400">
        <span>Accepted: </span>
        <span className="font-bold text-slate-700 dark:text-slate-200">{syncStatus.records_accepted}</span>
        {syncStatus.predictions_replaced > 0 && (
          <span className="ml-2 text-emerald-600 dark:text-emerald-400">
            ({syncStatus.predictions_replaced} predictions replaced)
          </span>
        )}
      </div>
    </div>
  );
};
