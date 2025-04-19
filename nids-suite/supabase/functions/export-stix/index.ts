// File: /nids-suite/nids-suite/supabase/functions/export-stix/index.ts

import { createClient } from '@supabase/supabase-js';
import { Response } from 'express';

const supabaseUrl = process.env.SUPABASE_URL;
const supabaseKey = process.env.SUPABASE_KEY;
const supabase = createClient(supabaseUrl, supabaseKey);

export const exportStix = async (req: any, res: Response) => {
    try {
        const { data, error } = await supabase
            .from('alerts')
            .select('*');

        if (error) {
            return res.status(500).json({ error: error.message });
        }

        const stixData = data.map(alert => ({
            type: 'alert',
            id: alert.id,
            attributes: {
                created: alert.created_at,
                modified: alert.updated_at,
                name: alert.name,
                description: alert.description,
                severity: alert.severity,
                // Add other relevant fields here
            }
        }));

        res.setHeader('Content-Type', 'application/json');
        res.status(200).json(stixData);
    } catch (err) {
        res.status(500).json({ error: 'Internal Server Error' });
    }
};