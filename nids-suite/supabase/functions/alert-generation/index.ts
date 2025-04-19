// File: /nids-suite/nids-suite/supabase/functions/alert-generation/index.ts

import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.SUPABASE_URL;
const supabaseKey = process.env.SUPABASE_KEY;
const supabase = createClient(supabaseUrl, supabaseKey);

export const handler = async (event) => {
    const { body } = event;
    const alertData = JSON.parse(body);

    // Validate alert data
    if (!alertData.type || !alertData.severity || !alertData.description) {
        return {
            statusCode: 400,
            body: JSON.stringify({ message: 'Invalid alert data' }),
        };
    }

    // Insert alert into the database
    const { data, error } = await supabase
        .from('alerts')
        .insert([
            {
                type: alertData.type,
                severity: alertData.severity,
                description: alertData.description,
                created_at: new Date().toISOString(),
            },
        ]);

    if (error) {
        return {
            statusCode: 500,
            body: JSON.stringify({ message: 'Error inserting alert', error }),
        };
    }

    return {
        statusCode: 201,
        body: JSON.stringify({ message: 'Alert created successfully', data }),
    };
};