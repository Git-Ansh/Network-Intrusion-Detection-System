// File: /nids-suite/nids-suite/frontend/src/components/packets/PacketExplorer.tsx

import React, { useEffect, useState } from 'react';
import { fetchPacketData } from '../../lib/supabase';
import PacketTable from './PacketTable';

const PacketExplorer: React.FC = () => {
    const [packets, setPackets] = useState<any[]>([]);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const loadData = async () => {
            try {
                const data = await fetchPacketData();
                setPackets(data);
            } catch (err) {
                setError('Failed to load packet data');
            } finally {
                setLoading(false);
            }
        };

        loadData();
    }, []);

    if (loading) {
        return <div>Loading...</div>;
    }

    if (error) {
        return <div>{error}</div>;
    }

    return (
        <div className="packet-explorer">
            <h2 className="text-2xl font-bold mb-4">Packet Explorer</h2>
            <PacketTable packets={packets} />
        </div>
    );
};

export default PacketExplorer;