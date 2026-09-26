import { useState } from 'react';

export default function Transactions({ transactions, onCreateTransaction, onRefund, busy }) {
  const [showForm, setShowForm] = useState(false);
  const [amount, setAmount] = useState('');
  const [customerEmail, setCustomerEmail] = useState('');
  const [refundingId, setRefundingId] = useState(null);
  const [refundAmount, setRefundAmount] = useState('');
  const [formError, setFormError] = useState(null);

  async function handleCreate(e) {
    e.preventDefault();
    setFormError(null);
    try {
      await onCreateTransaction({
        amount: parseFloat(amount),
        customer_email: customerEmail || undefined,
        idempotency_key: crypto.randomUUID(),
      });
      setAmount('');
      setCustomerEmail('');
      setShowForm(false);
    } catch (err) {
      setFormError(err.message);
    }
  }

  async function handleRefund(txnId) {
    setFormError(null);
    try {
      await onRefund({ transaction_id: txnId, amount: parseFloat(refundAmount) });
      setRefundingId(null);
      setRefundAmount('');
    } catch (err) {
      setFormError(err.message);
    }
  }

  return (
    <div style={{ padding: '40px 48px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1 style={styles.heading}>Transactions</h1>
        <button style={styles.newButton} onClick={() => setShowForm((v) => !v)}>
          {showForm ? 'Cancel' : '+ New transaction'}
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleCreate} style={styles.form}>
          <div style={styles.formRow}>
            <div>
              <label style={styles.label}>Amount (CAD)</label>
              <input
                style={styles.input}
                type="number"
                step="0.01"
                min="0.01"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                required
              />
            </div>
            <div>
              <label style={styles.label}>Customer email (optional)</label>
              <input
                style={styles.input}
                type="email"
                value={customerEmail}
                onChange={(e) => setCustomerEmail(e.target.value)}
              />
            </div>
            <button style={styles.submitButton} type="submit" disabled={busy}>
              Create
            </button>
          </div>
        </form>
      )}

      {formError && <div style={styles.error}>{formError}</div>}

      <table style={styles.table}>
        <thead>
          <tr>
            <th style={styles.th}>Date</th>
            <th style={styles.th}>Customer</th>
            <th style={{ ...styles.th, textAlign: 'right' }}>Amount</th>
            <th style={styles.th}>Status</th>
            <th style={styles.th}>Fraud</th>
            <th style={styles.th}></th>
          </tr>
        </thead>
        <tbody>
          {transactions.map((t) => (
            <tr key={t.id} style={styles.tr}>
              <td style={styles.td}>{new Date(t.created_at).toLocaleDateString()}</td>
              <td style={{ ...styles.td, color: 'var(--text-dim)' }}>
                {t.customer_email || '—'}
              </td>
              <td style={{ ...styles.td, ...styles.amountCell }}>
                ${t.amount.toLocaleString(undefined, { minimumFractionDigits: 2 })}
              </td>
              <td style={styles.td}>
                <StatusBadge status={t.status} />
              </td>
              <td style={styles.td}>
                {t.is_flagged ? (
                  <span style={styles.fraudBadge}>flagged · {t.fraud_score.toFixed(2)}</span>
                ) : (
                  <span style={{ color: 'var(--text-dim)' }}>—</span>
                )}
              </td>
              <td style={{ ...styles.td, textAlign: 'right' }}>
                {t.status === 'completed' || t.status === 'partially_refunded' ? (
                  refundingId === t.id ? (
                    <span style={{ display: 'inline-flex', gap: 6 }}>
                      <input
                        style={styles.refundInput}
                        type="number"
                        step="0.01"
                        placeholder="0.00"
                        value={refundAmount}
                        onChange={(e) => setRefundAmount(e.target.value)}
                        autoFocus
                      />
                      <button style={styles.linkButton} onClick={() => handleRefund(t.id)}>
                        Confirm
                      </button>
                      <button
                        style={{ ...styles.linkButton, color: 'var(--text-dim)' }}
                        onClick={() => setRefundingId(null)}
                      >
                        Cancel
                      </button>
                    </span>
                  ) : (
                    <button
                      style={styles.linkButton}
                      onClick={() => {
                        setRefundingId(t.id);
                        setRefundAmount('');
                      }}
                    >
                      Refund
                    </button>
                  )
                ) : null}
              </td>
            </tr>
          ))}
          {transactions.length === 0 && (
            <tr>
              <td colSpan={6} style={{ ...styles.td, color: 'var(--text-dim)', padding: '32px 0' }}>
                No transactions yet. Create one to get started.
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}

function StatusBadge({ status }) {
  const colors = {
    completed: 'var(--accent-green)',
    pending: 'var(--accent-gold)',
    failed: 'var(--accent-red)',
    refunded: 'var(--text-dim)',
    partially_refunded: 'var(--accent-gold)',
  };
  return (
    <span style={{ color: colors[status] || 'var(--text)', fontSize: 13 }}>
      {status.replace('_', ' ')}
    </span>
  );
}

const styles = {
  heading: {
    fontSize: 22,
    fontWeight: 600,
    margin: 0,
  },
  newButton: {
    background: 'var(--panel-alt)',
    border: '1px solid var(--border)',
    color: 'var(--text)',
    borderRadius: 6,
    padding: '8px 14px',
    fontSize: 13,
    cursor: 'pointer',
  },
  form: {
    marginTop: 20,
    padding: 20,
    background: 'var(--panel)',
    border: '1px solid var(--border)',
    borderRadius: 8,
  },
  formRow: {
    display: 'flex',
    gap: 16,
    alignItems: 'flex-end',
    flexWrap: 'wrap',
  },
  label: {
    display: 'block',
    fontSize: 12,
    color: 'var(--text-dim)',
    marginBottom: 6,
  },
  input: {
    background: 'var(--panel-alt)',
    border: '1px solid var(--border)',
    borderRadius: 6,
    padding: '9px 11px',
    color: 'var(--text)',
    fontSize: 14,
    width: 220,
  },
  submitButton: {
    background: 'var(--accent-gold)',
    color: '#0e121b',
    border: 'none',
    borderRadius: 6,
    padding: '10px 18px',
    fontSize: 13,
    fontWeight: 600,
    cursor: 'pointer',
  },
  error: {
    marginTop: 12,
    color: 'var(--accent-red)',
    fontSize: 13,
  },
  table: {
    width: '100%',
    borderCollapse: 'collapse',
    marginTop: 28,
  },
  th: {
    textAlign: 'left',
    fontSize: 12,
    color: 'var(--text-dim)',
    fontWeight: 500,
    padding: '0 0 10px 0',
    borderBottom: '1px solid var(--border)',
  },
  tr: {
    borderBottom: '1px solid var(--border)',
  },
  td: {
    padding: '12px 0',
    fontSize: 13.5,
  },
  amountCell: {
    fontFamily: 'var(--font-mono)',
    textAlign: 'right',
  },
  fraudBadge: {
    color: 'var(--accent-red)',
    fontSize: 12,
  },
  linkButton: {
    background: 'none',
    border: 'none',
    color: 'var(--accent-gold)',
    fontSize: 13,
    cursor: 'pointer',
    padding: 0,
  },
  refundInput: {
    width: 70,
    background: 'var(--panel-alt)',
    border: '1px solid var(--border)',
    borderRadius: 4,
    padding: '4px 6px',
    color: 'var(--text)',
    fontSize: 12,
  },
};
