import React, { useEffect, useState } from 'react';
import { supabase } from '../../lib/supabase';
import PacketItem from '../components/packets/PacketItem';

const PacketExplorerPage = () => {
    const [packets, setPackets] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchPackets = async () => {
            try {
                const { data, error } = await supabase
                    .from('packets')
                    .select('*')
                    .order('timestamp', { ascending: false });

                if (error) throw error;

                setPackets(data);
            } catch (error) {
                setError(error.message);
            } finally {
                setLoading(false);
            }
        };

        fetchPackets();
    }, []);

    if (loading) return <div>Loading packets...</div>;
    if (error) return <div>Error: {error}</div>;

    return (
        <div className="packet-explorer">
            <h1 className="text-2xl font-bold mb-4">Packet Explorer</h1>
            <div className="packet-list">
                {packets.map(packet => (
                    <PacketItem key={packet.id} packet={packet} />
                ))}
            </div>
        </div>
    );
};

export default PacketExplorerPage;