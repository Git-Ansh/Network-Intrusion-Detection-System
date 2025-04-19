// File: /nids-suite/nids-suite/api-gateway/src/services/alert.service.ts

import { createClient } from '@supabase/supabase-js';
import { Alert } from '../types/index';
import logger from '../utils/logger';

const SUPABASE_URL = process.env.SUPABASE_URL || '';
const SUPABASE_KEY = process.env.SUPABASE_KEY || '';

const supabase = createClient(SUPABASE_URL, SUPABASE_KEY);

export class AlertService {
    /**
     * Create a new alert
     */
    async createAlert(alertData: Omit<Alert, 'id'>): Promise<Alert> {
        try {
            const { data, error } = await supabase
                .from('alerts')
                .insert([alertData])
                .select()
                .single();

            if (error) {
                logger.error(`Error creating alert: ${error.message}`);
                throw new Error(`Error creating alert: ${error.message}`);
            }

            return data as Alert;
        } catch (error) {
            logger.error(`Unexpected error creating alert: ${error}`);
            throw error;
        }
    }

    /**
     * Get all alerts with optional filtering and pagination
     */
    async getAllAlerts(options: { 
        limit?: number;
        offset?: number;
        severity?: string;
        startDate?: Date;
        endDate?: Date;
    } = {}): Promise<Alert[]> {
        try {
            let query = supabase
                .from('alerts')
                .select('*');
            
            // Apply filters if provided
            if (options.severity) {
                query = query.eq('severity', options.severity);
            }
            
            if (options.startDate) {
                query = query.gte('timestamp', options.startDate.toISOString());
            }
            
            if (options.endDate) {
                query = query.lte('timestamp', options.endDate.toISOString());
            }
            
            // Apply pagination if provided
            if (options.limit) {
                query = query.limit(options.limit);
            }
            
            if (options.offset) {
                query = query.range(options.offset, options.offset + (options.limit || 10) - 1);
            }
            
            // Order by timestamp descending
            query = query.order('timestamp', { ascending: false });
            
            const { data, error } = await query;

            if (error) {
                logger.error(`Error fetching alerts: ${error.message}`);
                throw new Error(`Error fetching alerts: ${error.message}`);
            }

            return data as Alert[];
        } catch (error) {
            logger.error(`Unexpected error fetching alerts: ${error}`);
            throw error;
        }
    }

    /**
     * Get a single alert by ID
     */
    async getAlertById(alertId: string): Promise<Alert | null> {
        try {
            const { data, error } = await supabase
                .from('alerts')
                .select('*')
                .eq('id', alertId)
                .single();

            if (error) {
                if (error.code === 'PGRST116') { // Record not found error code
                    return null;
                }
                logger.error(`Error fetching alert: ${error.message}`);
                throw new Error(`Error fetching alert: ${error.message}`);
            }

            return data as Alert;
        } catch (error) {
            logger.error(`Unexpected error fetching alert: ${error}`);
            throw error;
        }
    }

    /**
     * Update an existing alert
     */
    async updateAlert(alertId: string, alertData: Partial<Alert>): Promise<Alert | null> {
        try {
            const { data, error } = await supabase
                .from('alerts')
                .update(alertData)
                .eq('id', alertId)
                .select()
                .single();

            if (error) {
                logger.error(`Error updating alert: ${error.message}`);
                throw new Error(`Error updating alert: ${error.message}`);
            }

            if (!data) {
                return null;
            }

            return data as Alert;
        } catch (error) {
            logger.error(`Unexpected error updating alert: ${error}`);
            throw error;
        }
    }

    /**
     * Delete an alert by ID
     */
    async deleteAlert(alertId: string): Promise<boolean> {
        try {
            const { error } = await supabase
                .from('alerts')
                .delete()
                .eq('id', alertId);

            if (error) {
                logger.error(`Error deleting alert: ${error.message}`);
                throw new Error(`Error deleting alert: ${error.message}`);
            }

            return true;
        } catch (error) {
            logger.error(`Unexpected error deleting alert: ${error}`);
            throw error;
        }
    }

    /**
     * Get alert statistics
     */
    async getAlertStats(): Promise<{
        total: number;
        bySeverity: Record<string, number>;
        last24Hours: number;
    }> {
        try {
            // Get total count
            const { count: total, error: totalError } = await supabase
                .from('alerts')
                .select('*', { count: 'exact', head: true });

            if (totalError) {
                throw new Error(`Error getting alert count: ${totalError.message}`);
            }

            // Get count by severity
            const { data: severityData, error: severityError } = await supabase
                .from('alerts')
                .select('severity, count')
                .group('severity');

            if (severityError) {
                throw new Error(`Error getting alert severity stats: ${severityError.message}`);
            }

            const bySeverity = severityData.reduce((acc, curr) => {
                acc[curr.severity] = curr.count;
                return acc;
            }, {} as Record<string, number>);

            // Get count for last 24 hours
            const yesterday = new Date();
            yesterday.setDate(yesterday.getDate() - 1);
            
            const { count: last24Hours, error: recentError } = await supabase
                .from('alerts')
                .select('*', { count: 'exact', head: true })
                .gte('timestamp', yesterday.toISOString());

            if (recentError) {
                throw new Error(`Error getting recent alert count: ${recentError.message}`);
            }

            return {
                total: total || 0,
                bySeverity,
                last24Hours: last24Hours || 0
            };
        } catch (error) {
            logger.error(`Error calculating alert statistics: ${error}`);
            throw error;
        }
    }
}