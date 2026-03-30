import { api } from './client';

// Server
export const serverInfo = () => api.get<Record<string, unknown>>('/server/info');
export const serverPeople = () => api.get<{ users: Record<string, unknown>[] }>('/server/people');
export const serverQueue = () => api.get<{ items: Record<string, unknown>[] }>('/server/queue');

// Jobs
export const searchJobs = (pattern = '.*', folder = '', depth = 4) =>
  api.get<{ results: Record<string, unknown>[]; urls: string[] }>(
    `/jobs/search?pattern=${encodeURIComponent(pattern)}&folder=${encodeURIComponent(folder)}&depth=${depth}`
  );

export const jobInfo = (job: string) =>
  api.get<Record<string, unknown>>(`/jobs/info?job=${encodeURIComponent(job)}`);

export const jobBuilds = (job: string) =>
  api.get<{ builds: Record<string, unknown>[]; urls: string[] }>(
    `/jobs/builds?job=${encodeURIComponent(job)}`
  );

export const triggerBuild = (job: string) =>
  api.post<{ message: string; queue_url: string }>(`/jobs/build?job=${encodeURIComponent(job)}`);

// Builds
export const buildInfo = (url: string) =>
  api.get<Record<string, unknown>>(`/builds/info?url=${encodeURIComponent(url)}`);

export const buildLogs = (url: string) =>
  api.get<{ logs: string }>(`/builds/logs?url=${encodeURIComponent(url)}`);

export const buildStages = (url: string) =>
  api.get<{ stages: Record<string, unknown>[]; stage_names: string[] }>(
    `/builds/stages?url=${encodeURIComponent(url)}`
  );

// Folders
export const searchFolders = (pattern = '.*', depth = 4) =>
  api.get<{ results: Record<string, unknown>[]; urls: string[] }>(
    `/folders/search?pattern=${encodeURIComponent(pattern)}&depth=${depth}`
  );

export const folderInfo = (folder: string) =>
  api.get<Record<string, unknown>>(`/folders/info?folder=${encodeURIComponent(folder)}`);

export const folderJobs = (folder: string) =>
  api.get<{ jobs: Record<string, unknown>[]; urls: string[] }>(
    `/folders/jobs?folder=${encodeURIComponent(folder)}`
  );
