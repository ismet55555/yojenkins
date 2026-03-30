import { useCallback, useEffect, useRef, useState } from 'react';
import { getToken } from './client';

interface BuildUpdate {
  type: 'build_update' | 'build_complete';
  info: Record<string, unknown>;
  stages?: Record<string, unknown>[];
  stage_names?: string[];
}

export function useWebSocket(buildUrl: string | null) {
  const [data, setData] = useState<BuildUpdate | null>(null);
  const [connected, setConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);

  const disconnect = useCallback(() => {
    wsRef.current?.close();
    wsRef.current = null;
    setConnected(false);
  }, []);

  useEffect(() => {
    if (!buildUrl) return;

    const token = getToken();
    if (!token) return;

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/api/ws/build-monitor?build_url=${encodeURIComponent(buildUrl)}&token=${encodeURIComponent(token)}`;

    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => setConnected(true);
    ws.onclose = () => setConnected(false);
    ws.onerror = () => setConnected(false);
    ws.onmessage = (event) => {
      const parsed: BuildUpdate = JSON.parse(event.data);
      setData(parsed);
      if (parsed.type === 'build_complete') {
        ws.close();
      }
    };

    return () => {
      ws.close();
    };
  }, [buildUrl]);

  return { data, connected, disconnect };
}
