// File: /nids-suite/nids-suite/frontend/src/types/index.ts

export interface Alert {
    id: string;
    severity: 'low' | 'medium' | 'high';
    message: string;
    timestamp: string;
}

export interface FlowSummary {
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
}

export interface User {
    id: string;
    email: string;
    role: 'Viewer' | 'Analyst' | 'Admin';
}

export interface Metric {
    name: string;
    value: number;
    timestamp: string;
}

export interface Telemetry {
    url: string;
    status: number;
    duration: number;
    error?: string;
}