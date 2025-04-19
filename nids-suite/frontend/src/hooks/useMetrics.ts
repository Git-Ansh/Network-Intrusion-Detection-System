// File: /nids-suite/nids-suite/frontend/src/hooks/useMetrics.ts

import { useEffect, useState } from 'react';
import { supabase } from '../lib/supabase';

const useMetrics = () => {
    const [metrics, setMetrics] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchMetrics = async () => {
            try {
                setLoading(true);
                const { data, error } = await supabase
                    .from('metrics')
                    .select('*')
                    .order('timestamp', { ascending: false })
                    .limit(10);

                if (error) throw error;

                setMetrics(data);
            } catch (err) {
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };

        fetchMetrics();

        const subscription = supabase
            .from('metrics')
            .on('INSERT', payload => {
                setMetrics(prevMetrics => [payload.new, ...prevMetrics]);
            })
            .subscribe();

        return () => {
            supabase.removeSubscription(subscription);
        };
    }, []);

    return { metrics, loading, error };
};

export default useMetrics;