// File: /nids-suite/nids-suite/frontend/src/hooks/useAlerts.ts

import { useEffect, useState } from 'react';
import { supabase } from '../lib/supabase';
import { Alert } from '../types';

const useAlerts = () => {
    const [alerts, setAlerts] = useState<Alert[]>([]);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchAlerts = async () => {
            try {
                setLoading(true);
                const { data, error } = await supabase
                    .from('alerts')
                    .select('*')
                    .order('created_at', { ascending: false });

                if (error) throw error;

                setAlerts(data);
            } catch (err) {
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };

        fetchAlerts();

        const alertSubscription = supabase
            .from('alerts')
            .on('INSERT', (payload) => {
                setAlerts((prevAlerts) => [payload.new, ...prevAlerts]);
            })
            .subscribe();

        return () => {
            supabase.removeSubscription(alertSubscription);
        };
    }, []);

    return { alerts, loading, error };
};

export default useAlerts;