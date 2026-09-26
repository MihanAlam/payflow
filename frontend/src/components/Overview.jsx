import RevenueChart from './RevenueChart.jsx';

export default function Overview({ summary }) {
  if (!summary) return null;

  const stats = [
    { label: 'transactions', value: summary.total_transactions },
    { label: 'refunded', value: `$${summary.total_refunded.toLocaleString()}` },
    { label: 'refunds issued', value: summary.refund_count },
    { label: 'fraud flagged', value: summary.flagged_count, alert: summary.flagged_count > 0 },
    { label: 'webhooks pending', value: summary.pending_webhooks },
  ];

  return (
    <div style={{ padding: '40px 48px' }}>
      <div style={{ display: 'flex', alignItems: 'flex-end', gap: 40, flexWrap: 'wrap' }}>
        <div>
          <div style={styles.heroLabel}>total revenue · last 30 days</div>
          <div style={styles.hero}>
            ${summary.total_revenue.toLocaleString(undefined, { minimumFractionDigits: 2 })}
          </div>
        </div>
        <div style={{ flex: 1, minWidth: 240, maxWidth: 480 }}>
          <RevenueChart data={summary.revenue_by_day} />
        </div>
      </div>

      <div style={styles.statStrip}>
        {stats.map((s) => (
          <div key={s.label} style={styles.stat}>
            <div
              style={{
                ...styles.statValue,
                color: s.alert ? 'var(--accent-red)' : 'var(--text)',
              }}
            >
              {s.value}
            </div>
            <div style={styles.statLabel}>{s.label}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

const styles = {
  heroLabel: {
    fontSize: 13,
    color: 'var(--text-dim)',
    marginBottom: 6,
  },
  hero: {
    fontFamily: 'var(--font-mono)',
    fontSize: 52,
    fontWeight: 600,
    color: 'var(--accent-green)',
    lineHeight: 1,
    letterSpacing: '-0.02em',
  },
  statStrip: {
    display: 'flex',
    gap: 0,
    marginTop: 48,
    borderTop: '1px solid var(--border)',
    borderBottom: '1px solid var(--border)',
  },
  stat: {
    flex: 1,
    padding: '18px 24px 18px 0',
    borderRight: '1px solid var(--border)',
  },
  statValue: {
    fontFamily: 'var(--font-mono)',
    fontSize: 22,
    fontWeight: 600,
  },
  statLabel: {
    fontSize: 12,
    color: 'var(--text-dim)',
    marginTop: 4,
  },
};
