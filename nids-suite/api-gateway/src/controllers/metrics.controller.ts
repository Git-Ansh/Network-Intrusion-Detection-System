// File: /nids-suite/nids-suite/api-gateway/src/controllers/metrics.controller.ts

import { Request, Response } from 'express';
import { MetricsService } from '../services/metrics.service';

class MetricsController {
    private metricsService: MetricsService;

    constructor() {
        this.metricsService = new MetricsService();
    }

    public async getMetrics(req: Request, res: Response): Promise<void> {
        try {
            const metrics = await this.metricsService.fetchMetrics();
            res.status(200).json(metrics);
        } catch (error) {
            res.status(500).json({ message: 'Error fetching metrics', error: error.message });
        }
    }

    public async getMetricById(req: Request, res: Response): Promise<void> {
        const { id } = req.params;
        try {
            const metric = await this.metricsService.fetchMetricById(id);
            if (metric) {
                res.status(200).json(metric);
            } else {
                res.status(404).json({ message: 'Metric not found' });
            }
        } catch (error) {
            res.status(500).json({ message: 'Error fetching metric', error: error.message });
        }
    }
}

export const metricsController = new MetricsController();