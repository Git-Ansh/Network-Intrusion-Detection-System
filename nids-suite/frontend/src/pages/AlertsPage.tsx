import React, { useEffect, useState } from 'react';
import { supabase } from '../../lib/supabase';
import AlertItem from '../components/alerts/AlertItem';
import AlertTimeline from '../components/alerts/AlertTimeline';

const AlertsPage = () => {
    const [alerts, setAlerts] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchAlerts = async () => {
            const { data, error } = await supabase
                .from('alerts')
                .select('*')
                .order('created_at', { ascending: false });

            if (error) {
                console.error('Error fetching alerts:', error);
            } else {
                setAlerts(data);
            }
            setLoading(false);
        };

        fetchAlerts();
    }, []);

    if (loading) {
        return <div>Loading alerts...</div>;
    }

    return (
        <div className="alerts-page">
            <h1 className="text-2xl font-bold mb-4">Alerts</h1>
            <AlertTimeline alerts={alerts} />
            <div className="alert-list">
                {alerts.map(alert => (
                    <AlertItem key={alert.id} alert={alert} />
                ))}
            </div>
        </div>
    );
};

export default AlertsPage;