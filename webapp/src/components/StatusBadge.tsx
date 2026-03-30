const STATUS_COLORS: Record<string, string> = {
  SUCCESS: '#22c55e',
  FAILURE: '#ef4444',
  ABORTED: '#a855f7',
  UNSTABLE: '#f97316',
  RUNNING: '#06b6d4',
  IN_PROGRESS: '#06b6d4',
  NOT_BUILT: '#6b7280',
};

interface Props {
  status: string;
}

export default function StatusBadge({ status }: Props) {
  const color = STATUS_COLORS[status?.toUpperCase()] || '#6b7280';
  return (
    <span
      className="status-badge"
      style={{ backgroundColor: color }}
    >
      {status || 'UNKNOWN'}
    </span>
  );
}
