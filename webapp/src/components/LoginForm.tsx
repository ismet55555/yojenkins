import { type FormEvent, useState } from 'react';
import { login } from '../api/auth';

interface Props {
  onSuccess: () => void;
}

export default function LoginForm({ onSuccess }: Props) {
  const [jenkinsUrl, setJenkinsUrl] = useState('');
  const [username, setUsername] = useState('');
  const [apiToken, setApiToken] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await login({ jenkins_url: jenkinsUrl, username, api_token: apiToken });
      onSuccess();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="login-container">
      <h1>yojenkins</h1>
      <p className="subtitle">Connect to your Jenkins server</p>
      <form onSubmit={handleSubmit} className="login-form">
        <label>
          Jenkins URL
          <input
            type="url"
            value={jenkinsUrl}
            onChange={(e) => setJenkinsUrl(e.target.value)}
            placeholder="https://jenkins.example.com"
            required
          />
        </label>
        <label>
          Username
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="admin"
            required
          />
        </label>
        <label>
          API Token
          <input
            type="password"
            value={apiToken}
            onChange={(e) => setApiToken(e.target.value)}
            placeholder="Your Jenkins API token"
            required
          />
        </label>
        {error && <div className="error">{error}</div>}
        <button type="submit" disabled={loading}>
          {loading ? 'Connecting...' : 'Connect'}
        </button>
      </form>
    </div>
  );
}
