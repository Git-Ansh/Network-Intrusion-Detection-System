// File: /nids-suite/nids-suite/api-gateway/src/types/index.ts

export interface Alert {
    id: string;
    severity: 'low' | 'medium' | 'high';
    message: string;
    timestamp: Date;
}

export interface User {
    id: string;
    username: string;
    role: 'Viewer' | 'Analyst' | 'Admin';
}

export interface Metric {
    name: string;
    value: number;
    timestamp: Date;
}

export interface Sensor {
    id: string;
    name: string;
    status: 'active' | 'inactive';
    lastSeen: Date;
}

export interface Feature {
    flowId: string;
    srcIp: string;
    dstIp: string;
    srcPort: number;
    dstPort: number;
    protocol: string;
    bytes: number;
    packets: number;
    startTime: Date;
    endTime: Date;
}