import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { searchJobs } from '../api/jenkins';
import StatusBadge from '../components/StatusBadge';

export default function JobList() {
  const [pattern, setPattern] = useState('.*');
  const [search, setSearch] = useState('.*');

  const { data, isLoading, error } = useQuery({
    queryKey: ['jobs', search],
    queryFn: () => searchJobs(search),
  });

  return (
    <div className="page">
      <h2>Jobs</h2>

      <div className="search-bar">
        <input
          type="text"
          value={pattern}
          onChange={(e) => setPattern(e.target.value)}
          placeholder="Search pattern (regex)"
          onKeyDown={(e) => e.key === 'Enter' && setSearch(pattern)}
        />
        <button onClick={() => setSearch(pattern)}>Search</button>
      </div>

      {isLoading && <p>Loading...</p>}
      {error && <p className="error">{(error as Error).message}</p>}

      {data && (
        <table>
          <thead>
            <tr><th>Name</th><th>Status</th><th>URL</th></tr>
          </thead>
          <tbody>
            {data.results.map((job, i) => (
              <tr key={i}>
                <td>
                  <Link to={`/jobs/detail?job=${encodeURIComponent(String(job.fullName || job.name || data.urls[i]))}`}>
                    {String(job.fullName || job.name || 'Unknown')}
                  </Link>
                </td>
                <td><StatusBadge status={String(job.color || '')} /></td>
                <td className="url-cell">{data.urls[i]}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
