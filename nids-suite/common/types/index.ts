// File: /nids-suite/nids-suite/common/types/index.ts

export type FlowSummary = {
  flow_id: string;
  src_ip: string;
  dst_ip: string;
  src_port: number;
  dst_port: number;
  protocol: string;
  start_time: number; // timestamp in microseconds
  end_time: number;   // timestamp in microseconds
  bytes: number;
  packets: number;
  state: string;
};

export type Alert = {
  alert_id: string;
  flow_id: string;
  severity: 'low' | 'medium' | 'high';
  message: string;
  timestamp: number; // timestamp in milliseconds
  source: string; // e.g., IP address or hostname
};