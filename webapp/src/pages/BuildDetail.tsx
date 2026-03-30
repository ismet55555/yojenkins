import { useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { buildInfo, buildLogs, buildStages } from '../api/jenkins';
import { useWebSocket } from '../api/useWebSocket';
import StatusBadge from '../components/StatusBadge';

export default function BuildDetail() {
  const [params] = useSearchParams();
  const buildUrl = params.get('url') || '';
  const [monitoring, setMonitoring] = useState(false);

  const info = useQuery({
    queryKey: ['build-info', buildUrl],
    queryFn: () => buildInfo(buildUrl),
    enabled: !!buildUrl,
  });

  const stages = useQuery({
    queryKey: ['build-stages', buildUrl],
    queryFn: () => buildStages(buildUrl),
    enabled: !!buildUrl,
  });

  const logs = useQuery({
    queryKey: ['build-logs', buildUrl],
    queryFn: () => buildLogs(buildUrl),
    enabled: !!buildUrl,
  });

  const ws = useWebSocket(monitoring ? buildUrl : null);

  const displayInfo = ws.data?.info || info.data;
  const displayStages = ws.data?.stages || stages.data?.stages;

  if (!buildUrl) return <p className="error">No build URL specified</p>;

  return (
    <div className="page">
      <h2>Build Detail</h2>

      <div className="actions">
        <button
          onClick={() => setMonitoring(!monitoring)}
          className={monitoring ? 'btn-danger' : 'btn-primary'}
        >
          {monitoring ? 'Stop Monitoring' : 'Live Monitor'}
        </button>
        {ws.connected && <span className="live-indicator">LIVE</span>}
      </div>

      <section className="card">
        <h3>Info</h3>
        {info.isLoading && <p>Loading...</p>}
        {info.error && <p className="error">{(info.error as Error).message}</p>}
        {displayInfo && (
          <dl className="info-grid">
            <dt>Number</dt>
            <dd>{String(displayInfo.number ?? 'N/A')}</dd>
            <dt>Result</dt>
            <dd><StatusBadge status={String(displayInfo.result || displayInfo.resultText || '')} /></dd>
            <dt>Duration</dt>
            <dd>{formatDuration(displayInfo.duration as number)}</dd>
            <dt>Timestamp</dt>
            <dd>{displayInfo.timestamp ? new Date(displayInfo.timestamp as number).toLocaleString() : 'N/A'}</dd>
          </dl>
        )}
      </section>

      <section className="card">
        <h3>Stages</h3>
        {stages.isLoading && <p>Loading...</p>}
        {displayStages && displayStages.length > 0 ? (
          <table>
            <thead>
              <tr><th>Stage</th><th>Status</th><th>Duration</th></tr>
            </thead>
            <tbody>
              {displayStages.map((stage, i) => (
                <tr key={i}>
                  <td>{String(stage.name ?? `Stage ${i + 1}`)}</td>
                  <td><StatusBadge status={String(stage.status || '')} /></td>
                  <td>{formatDuration(stage.durationMillis as number)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p className="muted">No stages available</p>
        )}
      </section>

      <section className="card">
        <h3>Console Output</h3>
        {logs.isLoading && <p>Loading...</p>}
        {logs.error && <p className="error">{(logs.error as Error).message}</p>}
        {logs.data && (
          <pre className="console-output">{logs.data.logs || 'No output'}</pre>
        )}
      </section>
    </div>
  );
}

function formatDuration(ms: number | undefined | null): string {
  if (!ms) return 'N/A';
  const seconds = Math.floor(ms / 1000);
  if (seconds < 60) return `${seconds}s`;
  const minutes = Math.floor(seconds / 60);
  const remaining = seconds % 60;
  return `${minutes}m ${remaining}s`;
}
