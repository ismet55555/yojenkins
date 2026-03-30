import { useSearchParams, Link } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { jobInfo, jobBuilds, triggerBuild } from '../api/jenkins';
import StatusBadge from '../components/StatusBadge';

export default function JobDetail() {
  const [params] = useSearchParams();
  const jobName = params.get('job') || '';
  const queryClient = useQueryClient();

  const info = useQuery({
    queryKey: ['job-info', jobName],
    queryFn: () => jobInfo(jobName),
    enabled: !!jobName,
  });

  const builds = useQuery({
    queryKey: ['job-builds', jobName],
    queryFn: () => jobBuilds(jobName),
    enabled: !!jobName,
  });

  const trigger = useMutation({
    mutationFn: () => triggerBuild(jobName),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['job-builds', jobName] });
    },
  });

  if (!jobName) return <p className="error">No job specified</p>;

  return (
    <div className="page">
      <h2>Job: {jobName}</h2>

      <button
        onClick={() => trigger.mutate()}
        disabled={trigger.isPending}
        className="btn-primary"
      >
        {trigger.isPending ? 'Triggering...' : 'Trigger Build'}
      </button>
      {trigger.isSuccess && <span className="success"> Build triggered!</span>}
      {trigger.isError && <span className="error"> {(trigger.error as Error).message}</span>}

      <section className="card">
        <h3>Info</h3>
        {info.isLoading && <p>Loading...</p>}
        {info.error && <p className="error">{(info.error as Error).message}</p>}
        {info.data && (
          <dl className="info-grid">
            <dt>Full Name</dt>
            <dd>{String(info.data.fullName ?? info.data.name ?? 'N/A')}</dd>
            <dt>Buildable</dt>
            <dd>{String(info.data.buildable ?? 'N/A')}</dd>
            <dt>Color</dt>
            <dd><StatusBadge status={String(info.data.color || '')} /></dd>
            <dt>Health</dt>
            <dd>{String((info.data.healthReport as Array<Record<string, unknown>>)?.[0]?.description ?? 'N/A')}</dd>
          </dl>
        )}
      </section>

      <section className="card">
        <h3>Build History</h3>
        {builds.isLoading && <p>Loading...</p>}
        {builds.error && <p className="error">{(builds.error as Error).message}</p>}
        {builds.data && (
          <table>
            <thead>
              <tr><th>#</th><th>Status</th><th>URL</th></tr>
            </thead>
            <tbody>
              {builds.data.builds.map((build, i) => (
                <tr key={i}>
                  <td>
                    <Link to={`/builds/detail?url=${encodeURIComponent(builds.data.urls[i])}`}>
                      #{String(build.number ?? i + 1)}
                    </Link>
                  </td>
                  <td><StatusBadge status={String(build.result || build.status || '')} /></td>
                  <td className="url-cell">{builds.data.urls[i]}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>
    </div>
  );
}
