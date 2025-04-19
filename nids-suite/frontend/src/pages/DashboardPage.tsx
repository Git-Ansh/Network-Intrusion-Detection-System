import React, { useEffect, useState } from 'react';
import { useAlerts } from '../hooks/useAlerts';
import { OverviewPanel } from '../components/dashboard/OverviewPanel';
import { AlertTimeline } from '../components/alerts/AlertTimeline';
import { NetworkMap } from '../components/network/NetworkMap';
import { PacketExplorer } from '../components/packets/PacketExplorer';
import { DashboardLayout } from '../components/dashboard/DashboardLayout';

const DashboardPage: React.FC = () => {
    const { alerts, fetchAlerts } = useAlerts();
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const loadAlerts = async () => {
            await fetchAlerts();
            setLoading(false);
        };

        loadAlerts();
    }, [fetchAlerts]);

    if (loading) {
        return <div>Loading...</div>;
    }

    return (
        <DashboardLayout>
            <OverviewPanel />
            <AlertTimeline alerts={alerts} />
            <NetworkMap />
            <PacketExplorer />
        </DashboardLayout>
    );
};

export default DashboardPage;