export default function Rail({ active, onChange, onLogout }) {
  const items = [
    { key: 'overview', label: 'Overview', glyph: '◆' },
    { key: 'transactions', label: 'Transactions', glyph: '≡' },
  ];

  return (
    <nav style={styles.rail}>
      <div style={styles.mark} title="PayFlow">
        P
      </div>
      <div style={styles.items}>
        {items.map((item) => (
          <button
            key={item.key}
            title={item.label}
            onClick={() => onChange(item.key)}
            style={{
              ...styles.item,
              ...(active === item.key ? styles.itemActive : {}),
            }}
          >
            {item.glyph}
          </button>
        ))}
      </div>
      <button title="Sign out" onClick={onLogout} style={styles.logout}>
        ⏻
      </button>
    </nav>
  );
}

const styles = {
  rail: {
    width: 64,
    flexShrink: 0,
    background: 'var(--panel)',
    borderRight: '1px solid var(--border)',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    padding: '18px 0',
  },
  mark: {
    width: 32,
    height: 32,
    borderRadius: 8,
    background: 'var(--accent-gold)',
    color: '#0e121b',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontFamily: 'var(--font-mono)',
    fontWeight: 700,
    fontSize: 15,
  },
  items: {
    marginTop: 40,
    display: 'flex',
    flexDirection: 'column',
    gap: 8,
    flex: 1,
  },
  item: {
    width: 40,
    height: 40,
    background: 'transparent',
    border: 'none',
    borderRadius: 8,
    color: 'var(--text-dim)',
    fontSize: 16,
    cursor: 'pointer',
  },
  itemActive: {
    background: 'var(--panel-alt)',
    color: 'var(--accent-gold)',
  },
  logout: {
    width: 40,
    height: 40,
    background: 'transparent',
    border: 'none',
    borderRadius: 8,
    color: 'var(--text-dim)',
    fontSize: 16,
    cursor: 'pointer',
  },
};
