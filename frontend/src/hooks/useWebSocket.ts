import { useState, useEffect, useRef } from 'react';
import { CampaignMetrics, CampaignStatus } from '../types';

interface WebSocketData {
  status: CampaignStatus;
  metrics: CampaignMetrics;
  error_message: string | null;
}

export function useWebSocket(campaignId: string | null) {
  const [data, setData] = useState<WebSocketData | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    if (!campaignId) return;

    const wsUrl = `ws://localhost:8000/api/campaigns/ws/${campaignId}`;
    let isClosed = false;

    const connect = () => {
      wsRef.current = new WebSocket(wsUrl);

      wsRef.current.onmessage = (event) => {
        try {
          const parsed = JSON.parse(event.data);
          setData(parsed);
        } catch (e) {
          console.error('Failed to parse websocket message', e);
        }
      };

      wsRef.current.onclose = () => {
        if (isClosed) return; // Don't reconnect if intentionally closed on unmount
        // Auto-reconnect after 3s
        reconnectTimerRef.current = setTimeout(() => connect(), 3000);
      };
    };

    connect();

    return () => {
      isClosed = true;
      // Clear any pending reconnect timer
      if (reconnectTimerRef.current !== null) {
        clearTimeout(reconnectTimerRef.current);
        reconnectTimerRef.current = null;
      }
      if (wsRef.current) {
        wsRef.current.onclose = null; // Prevent reconnect callback
        wsRef.current.close();
      }
    };
  }, [campaignId]);

  return data;
}
