import { useEffect, useState, useCallback } from 'react';
import Login from './components/Login.jsx';
import Rail from './components/Rail.jsx';
import Overview from './components/Overview.jsx';
import Transactions from './components/Transactions.jsx';
import { api } from './api.js';

const TOKEN_KEY = 'payflow_token';

export default function App() {
  const [token, setToken] = useState(() => localStorage.getItem(TOKEN_KEY));
  const [view, setView] = useState('overview');
  const [summary, setSummary] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [busy, setBusy] = useState(false);
  const [loadError, setLoadError] = useState(null);

  const loadAll = useCallback(async (activeToken) => {
    setLoading(true);
    setLoadError(null);
    try {
      const [summaryData, txnData] = await Promise.all([
        api.dashboardSummary(activeToken),
        api.listTransactions(activeToken, { limit: 100 }),
      ]);
      setSummary(summaryData);
      setTransactions(txnData);
    } catch (err) {
      if (err.status === 401) {
        handleLogout();
      } else {
        setLoadError(err.message);
      }
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (token) loadAll(token);
  }, [token, loadAll]);

  function handleLoggedIn(newToken) {
    localStorage.setItem(TOKEN_KEY, newToken);
    setToken(newToken);
  }

  function handleLogout() {
    localStorage.removeItem(TOKEN_KEY);
    setToken(null);
    setSummary(null);
    setTransactions([]);
  }

  async function handleCreateTransaction(payload) {
    setBusy(true);
    try {
      await api.createTransaction(token, payload);
      await loadAll(token);
    } finally {
      setBusy(false);
    }
  }

  async function handleRefund(payload) {
    setBusy(true);
    try {
      await api.createRefund(token, payload);
      await loadAll(token);
    } finally {
      setBusy(false);
    }
  }

  if (!token) {
    return <Login onLoggedIn={handleLoggedIn} />;
  }

  return (
    <div style={{ display: 'flex', height: '100%' }}>
      <Rail active={view} onChange={setView} onLogout={handleLogout} />
      <main style={{ flex: 1, overflow: 'auto' }}>
        {loading && !summary ? (
          <div style={{ padding: 48, color: 'var(--text-dim)' }}>Loading…</div>
        ) : loadError ? (
          <div style={{ padding: 48, color: 'var(--accent-red)' }}>{loadError}</div>
        ) : view === 'overview' ? (
          <Overview summary={summary} />
        ) : (
          <Transactions
            transactions={transactions}
            onCreateTransaction={handleCreateTransaction}
            onRefund={handleRefund}
            busy={busy}
          />
        )}
      </main>
    </div>
  );
}
