import React from 'react';
import type { FlaggedConflict } from '../types';

interface ConflictAlertBannerProps {
  conflicts: FlaggedConflict[];
}

export const ConflictAlertBanner: React.FC<ConflictAlertBannerProps> = ({ conflicts }) => {
  if (!conflicts || conflicts.length === 0) return null;

  return (
    <div className="pgx-conflict-banner">
      <div className="pgx-conflict-icon">⚠️</div>
      <div style={{ flex: 1 }}>
        <h4 className="pgx-conflict-title">
          Clinical Review Gate Triggered ({conflicts.length} Alert{conflicts.length > 1 ? 's' : ''})
        </h4>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginTop: '6px' }}>
          {conflicts.map((c, i) => (
            <div key={i} style={{ borderLeft: '2px solid rgba(239, 68, 68, 0.5)', paddingLeft: '8px' }}>
              <p className="pgx-conflict-desc">
                <strong>[{c.drug} × {c.gene}]</strong> {c.message}
              </p>
              <div className="pgx-conflict-action">
                <span>🛡️ Recommended Action:</span> {c.action}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
