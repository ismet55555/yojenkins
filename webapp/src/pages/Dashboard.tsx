import { useQuery } from '@tanstack/react-query';
import { serverInfo, serverQueue } from '../api/jenkins';
import StatusBadge from '../components/StatusBadge';

export default function Dashboard() {
  const info = useQuery({ queryKey: ['server-info'], queryFn: serverInfo });
  const queue = useQuery({ queryKey: ['server-queue'], queryFn: serverQueue, refetchInterval: 10000 });

  return (
    <div className="page">
      <h2>Dashboard</h2>

      <section className="card">
        <h3>Server Info</h3>
        {info.isLoading && <p>Loading...</p>}
        {info.error && <p className="error">{(info.error as Error).message}</p>}
        {info.data && (
          <dl className="info-grid">
            <dt>Version</dt>
            <dd>{String(info.data.version ?? info.data.hudson ?? 'N/A')}</dd>
            <dt>Mode</dt>
            <dd>{String(info.data.mode ?? 'N/A')}</dd>
            <dt>URL</dt>
            <dd>{String(info.data.url ?? info.data.primaryView ?? 'N/A')}</dd>
            <dt>Executors</dt>
            <dd>{String(info.data.numExecutors ?? 'N/A')}</dd>
          </dl>
        )}
      </section>

      <section className="card">
        <h3>Build Queue</h3>
        {queue.isLoading && <p>Loading...</p>}
        {queue.error && <p className="error">{(queue.error as Error).message}</p>}
        {queue.data && (
          queue.data.items.length === 0 ? (
            <p className="muted">Queue is empty</p>
          ) : (
            <table>
              <thead>
                <tr><th>Task</th><th>Status</th><th>Why</th></tr>
              </thead>
              <tbody>
                {queue.data.items.map((item, i) => (
                  <tr key={i}>
                    <td>{String((item.task as Record<string, unknown>)?.name ?? 'Unknown')}</td>
                    <td><StatusBadge status="IN_PROGRESS" /></td>
                    <td>{String(item.why ?? '')}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )
        )}
      </section>
    </div>
  );
}
