import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link, useSearchParams } from 'react-router-dom';
import { searchFolders, folderJobs } from '../api/jenkins';

export default function FolderBrowser() {
  const [params] = useSearchParams();
  const selectedFolder = params.get('folder') || '';
  const [pattern, setPattern] = useState('.*');
  const [search, setSearch] = useState('.*');

  const folders = useQuery({
    queryKey: ['folders', search],
    queryFn: () => searchFolders(search),
  });

  const jobs = useQuery({
    queryKey: ['folder-jobs', selectedFolder],
    queryFn: () => folderJobs(selectedFolder),
    enabled: !!selectedFolder,
  });

  return (
    <div className="page">
      <h2>Folders</h2>

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

      {folders.isLoading && <p>Loading...</p>}
      {folders.error && <p className="error">{(folders.error as Error).message}</p>}

      <div className="folder-layout">
        <section className="card folder-list">
          <h3>Folders</h3>
          {folders.data && (
            <ul>
              {folders.data.results.map((folder, i) => (
                <li key={i}>
                  <Link to={`/folders?folder=${encodeURIComponent(folders.data.urls[i])}`}>
                    {String(folder.name || folder.fullName || folders.data.urls[i])}
                  </Link>
                </li>
              ))}
            </ul>
          )}
        </section>

        {selectedFolder && (
          <section className="card folder-detail">
            <h3>Jobs in folder</h3>
            {jobs.isLoading && <p>Loading...</p>}
            {jobs.error && <p className="error">{(jobs.error as Error).message}</p>}
            {jobs.data && (
              <table>
                <thead>
                  <tr><th>Job</th><th>URL</th></tr>
                </thead>
                <tbody>
                  {jobs.data.jobs.map((job, i) => (
                    <tr key={i}>
                      <td>
                        <Link to={`/jobs/detail?job=${encodeURIComponent(jobs.data.urls[i])}`}>
                          {String(job.name || job.fullName || 'Unknown')}
                        </Link>
                      </td>
                      <td className="url-cell">{jobs.data.urls[i]}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </section>
        )}
      </div>
    </div>
  );
}
