import React, { useState } from "react";

const DATA_CLASS_CONFIG = {
  real: {
    badge: "🟢 Real",
    bg: "rgba(5, 150, 105, 0.12)",
    border: "rgba(5, 150, 105, 0.35)",
    text: "#059669",
    label: "Government circle-rate data (GODL-India)",
  },
  heuristic: {
    badge: "🟠 Heuristic",
    bg: "rgba(217, 119, 6, 0.10)",
    border: "rgba(217, 119, 6, 0.25)",
    text: "#d97706",
    label: "Distance-decay formula (circle rate unavailable)",
  },
};

function ProvenanceTooltip({ prov, onClose }) {
  if (!prov) return null;
  return (
    <div className="zone-prov-tooltip" role="tooltip">
      <button className="zone-prov-close" onClick={onClose} aria-label="Close">×</button>
      <div className="zone-prov-title">Data Provenance</div>
      <dl className="zone-prov-list">
        <dt>Source</dt>
        <dd>{prov.source || "—"}</dd>
        <dt>License</dt>
        <dd>{prov.license || "—"}</dd>
        <dt>Effective Date</dt>
        <dd>{prov.effective_date || "—"}</dd>
        <dt>Confidence</dt>
        <dd>{prov.confidence ? `${(prov.confidence * 100).toFixed(0)}%` : "—"}</dd>
        <dt>Basis</dt>
        <dd>{prov.basis || "—"}</dd>
        <dt>Localities matched</dt>
        <dd>{prov.localities_matched ?? "—"}</dd>
        {prov.source_url && (
          <>
            <dt>Source URL</dt>
            <dd>
              <a href={prov.source_url} target="_blank" rel="noopener noreferrer">
                Official portal ↗
              </a>
            </dd>
          </>
        )}
      </dl>
    </div>
  );
}

function ZoneRow({ zone, corePrice, cheapestId, hottestId }) {
  const [showProv, setShowProv] = useState(false);
  const cfg = DATA_CLASS_CONFIG[zone.data_class] || DATA_CLASS_CONFIG.heuristic;
  const isCheapest = zone.zone_id === cheapestId;
  const isHottest  = zone.zone_id === hottestId;

  const fmtPrice = (v) =>
    v != null ? `₹${Number(v).toLocaleString("en-IN")}/sqft` : "—";
  const fmtPct = (v) => (v != null ? `${Number(v).toFixed(1)}%` : "—");

  return (
    <tr
      className={`zone-row ${isCheapest ? "zone-row--cheapest" : ""} ${isHottest ? "zone-row--hottest" : ""}`}
      style={{ "--zone-accent": cfg.text }}
    >
      <td className="zone-name-cell">
        <div className="zone-name">{zone.label}</div>
        <div className="zone-dir">{zone.direction} · {zone.horizon_years}yr</div>
        {isCheapest && <span className="zone-tag zone-tag--cheap">Cheapest entry</span>}
        {isHottest  && <span className="zone-tag zone-tag--hot">Highest CAGR</span>}
      </td>
      <td className="zone-price-cell">
        <span className="zone-price">{fmtPrice(zone.current_price_inr_per_sqft)}</span>
      </td>
      <td className="zone-price-cell zone-price--proj">
        {fmtPrice(zone.projected_price_inr_per_sqft)}
      </td>
      <td className="zone-cagr-cell">
        <span className="zone-cagr">{fmtPct(zone.implied_price_cagr_pct)}</span>
      </td>
      <td className="zone-dc-cell" style={{ position: "relative" }}>
        <button
          className="zone-dc-badge"
          style={{ background: cfg.bg, border: `1px solid ${cfg.border}`, color: cfg.text }}
          onClick={() => zone.data_class === "real" && setShowProv(!showProv)}
          title={cfg.label}
          aria-pressed={showProv}
        >
          {cfg.badge}
          {zone.data_class === "real" && <span className="zone-dc-info">ⓘ</span>}
        </button>
        {showProv && zone.provenance && (
          <ProvenanceTooltip prov={zone.provenance} onClose={() => setShowProv(false)} />
        )}
      </td>
      <td className="zone-score-cell">
        <div
          className="zone-score-bar"
          style={{ width: `${Math.min(zone.investment_score, 100)}%` }}
        />
        <span className="zone-score-num">{zone.investment_score}</span>
      </td>
    </tr>
  );
}

export default function ZonePriceTable({ data, loading, error }) {
  if (loading) {
    return (
      <div className="zone-table-loading">
        <div className="zone-table-skeleton" />
        <div className="zone-table-skeleton zone-table-skeleton--sm" />
      </div>
    );
  }
  if (error) {
    return (
      <div className="zone-table-error">
        <span>⚠</span> Failed to load zone price data
      </div>
    );
  }
  if (!data || !data.zones || data.zones.length === 0) return null;

  const { zones, cheapest_zone_id, highest_appreciation_zone_id, coverage, core_price_inr_per_sqft } = data;
  const realZones    = coverage?.real_zones ?? 0;
  const totalZones   = coverage?.total_zones ?? zones.length;
  const overallClass = realZones > 0 ? "real" : "heuristic";
  const overallCfg   = DATA_CLASS_CONFIG[overallClass];

  return (
    <section className="zone-table-section" aria-label="Zone Price Index">
      {/* ── Header row ── */}
      <div className="zone-table-header">
        <div className="zone-table-title-group">
          <h3 className="zone-table-title">Zone Price Index</h3>
          <span
            className="zone-table-badge"
            style={{ background: overallCfg.bg, border: `1px solid ${overallCfg.border}`, color: overallCfg.text }}
          >
            {overallCfg.badge}
            {realZones > 0 && ` · ${realZones}/${totalZones} zones`}
          </span>
        </div>
        <p className="zone-table-subtitle">
          Core: ₹{Number(core_price_inr_per_sqft).toLocaleString("en-IN")}/sqft ·{" "}
          {realZones > 0
            ? `${realZones} of ${totalZones} zones backed by govt circle-rate data`
            : "All zones derived from distance-decay model — real data unavailable for this city"}
        </p>
      </div>

      {/* ── Table ── */}
      <div className="zone-table-scroll">
        <table className="zone-table" aria-label="Zone price breakdown">
          <thead>
            <tr>
              <th>Zone</th>
              <th>Current Price</th>
              <th>Projected Price</th>
              <th>CAGR</th>
              <th>Data Source</th>
              <th>Score</th>
            </tr>
          </thead>
          <tbody>
            {zones.map((zone) => (
              <ZoneRow
                key={zone.zone_id}
                zone={zone}
                corePrice={core_price_inr_per_sqft}
                cheapestId={cheapest_zone_id}
                hottestId={highest_appreciation_zone_id}
              />
            ))}
          </tbody>
        </table>
      </div>

      {/* ── Honesty footnote ── */}
      <p className="zone-table-footnote">
        🟢 <strong>Real</strong> = government guidance value (GODL-India; click badge for details) ·{" "}
        🟠 <strong>Heuristic</strong> = distance-decay formula off city core.
        All prices in ₹/sqft. Projected over zone's investment horizon.
      </p>
    </section>
  );
}
