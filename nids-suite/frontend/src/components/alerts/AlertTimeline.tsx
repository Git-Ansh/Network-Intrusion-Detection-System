import React from 'react';
import { useAlerts } from '../../../hooks/useAlerts';
import AlertItem from './AlertItem';

const AlertTimeline: React.FC = () => {
    const { alerts, loading, error } = useAlerts();

    if (loading) {
        return <div>Loading alerts...</div>;
    }

    if (error) {
        return <div>Error loading alerts: {error.message}</div>;
    }

    return (
        <div className="alert-timeline">
            <h2 className="text-lg font-semibold">Alert Timeline</h2>
            <ul className="space-y-2">
                {alerts.map(alert => (
                    <AlertItem key={alert.id} alert={alert} />
                ))}
            </ul>
        </div>
    );
};

export default AlertTimeline;