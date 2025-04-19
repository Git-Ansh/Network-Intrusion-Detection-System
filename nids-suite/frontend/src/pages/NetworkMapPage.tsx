import React, { useEffect, useState } from 'react';
import NetworkMap from '../components/network/NetworkMap';
import { useWebSocket } from '../hooks/useWebSocket';

const NetworkMapPage: React.FC = () => {
    const [connections, setConnections] = useState([]);
    const { socket } = useWebSocket();

    useEffect(() => {
        if (socket) {
            socket.on('updateConnections', (data) => {
                setConnections(data);
            });
        }

        return () => {
            if (socket) {
                socket.off('updateConnections');
            }
        };
    }, [socket]);

    return (
        <div className="network-map-page">
            <h1 className="text-2xl font-bold mb-4">Network Map</h1>
            <NetworkMap connections={connections} />
        </div>
    );
};

export default NetworkMapPage;