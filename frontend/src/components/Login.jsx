import { useState } from 'react';
import { login, ApiError } from '../api.js';

export default function Login({ onLoggedIn }) {
  const [email, setEmail] = useState('demo@payflow.dev');
  const [password, setPassword] = useState('demopassword123');
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const { access_token } = await login(email, password);
      onLoggedIn(access_token);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Could not reach the server');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={styles.page}>
      <form style={styles.card} onSubmit={handleSubmit}>
        <div style={styles.wordmark}>PayFlow</div>
        <p style={styles.sub}>Sign in to your merchant ledger</p>

        <label style={styles.label} htmlFor="email">
          Email
        </label>
        <input
          id="email"
          style={styles.input}
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          autoComplete="username"
          required
        />

        <label style={styles.label} htmlFor="password">
          Password
        </label>
        <input
          id="password"
          style={styles.input}
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          autoComplete="current-password"
          required
        />

        {error && <div style={styles.error}>{error}</div>}

        <button style={styles.button} type="submit" disabled={loading}>
          {loading ? 'Signing in…' : 'Sign in'}
        </button>

        <p style={styles.hint}>demo@payflow.dev / demopassword123 (seeded demo account)</p>
      </form>
    </div>
  );
}

const styles = {
  page: {
    height: '100%',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 24,
  },
  card: {
    width: '100%',
    maxWidth: 360,
    background: 'var(--panel)',
    border: '1px solid var(--border)',
    borderRadius: 10,
    padding: '36px 32px',
  },
  wordmark: {
    fontFamily: 'var(--font-mono)',
    fontSize: 22,
    fontWeight: 600,
    letterSpacing: '-0.02em',
  },
  sub: {
    color: 'var(--text-dim)',
    fontSize: 14,
    marginTop: 6,
    marginBottom: 28,
  },
  label: {
    display: 'block',
    fontSize: 13,
    color: 'var(--text-dim)',
    marginBottom: 6,
    marginTop: 16,
  },
  input: {
    width: '100%',
    background: 'var(--panel-alt)',
    border: '1px solid var(--border)',
    borderRadius: 6,
    padding: '10px 12px',
    color: 'var(--text)',
    fontSize: 14,
  },
  error: {
    marginTop: 16,
    color: 'var(--accent-red)',
    fontSize: 13,
  },
  button: {
    width: '100%',
    marginTop: 24,
    padding: '11px 0',
    background: 'var(--accent-gold)',
    color: '#0e121b',
    border: 'none',
    borderRadius: 6,
    fontSize: 14,
    fontWeight: 600,
    cursor: 'pointer',
  },
  hint: {
    marginTop: 18,
    fontSize: 12,
    color: 'var(--text-dim)',
    textAlign: 'center',
  },
};
