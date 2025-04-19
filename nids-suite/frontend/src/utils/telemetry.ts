// File: /nids-suite/nids-suite/frontend/src/utils/telemetry.ts

import { useEffect } from 'react';

const telemetryEndpoint = 'https://your-telemetry-endpoint.com/track';

export const sendTelemetryData = (event: string, data: Record<string, any>) => {
    fetch(telemetryEndpoint, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ event, data }),
    }).catch((error) => {
        console.error('Error sending telemetry data:', error);
    });
};

export const useTelemetry = (event: string, data: Record<string, any>) => {
    useEffect(() => {
        sendTelemetryData(event, data);
    }, [event, data]);
};