// File: /nids-suite/nids-suite/api-gateway/src/controllers/alerts.controller.ts

import { Request, Response } from 'express';
import { AlertService } from '../services/alert.service';
import logger from '../utils/logger';

const alertService = new AlertService();

export const getAlerts = async (req: Request, res: Response): Promise<void> => {
    try {
        // Parse query parameters for filtering and pagination
        const {
            limit,
            offset,
            severity,
            startDate,
            endDate
        } = req.query;

        const options: any = {};

        // Parse and apply optional filters
        if (limit) options.limit = parseInt(limit as string, 10);
        if (offset) options.offset = parseInt(offset as string, 10);
        if (severity) options.severity = severity as string;
        if (startDate) options.startDate = new Date(startDate as string);
        if (endDate) options.endDate = new Date(endDate as string);

        const alerts = await alertService.getAllAlerts(options);
        res.status(200).json({ alerts });
    } catch (error) {
        logger.error(`Error retrieving alerts: ${error}`);
        res.status(500).json({ message: 'Error retrieving alerts', error: error.message });
    }
};

export const getAlertById = async (req: Request, res: Response): Promise<void> => {
    try {
        const alertId = req.params.id;
        const alert = await alertService.getAlertById(alertId);

        if (!alert) {
            res.status(404).json({ message: 'Alert not found' });
            return;
        }

        res.status(200).json({ alert });
    } catch (error) {
        logger.error(`Error retrieving alert ${req.params.id}: ${error}`);
        res.status(500).json({ message: 'Error retrieving alert', error: error.message });
    }
};

export const createAlert = async (req: Request, res: Response): Promise<void> => {
    try {
        const alertData = req.body;

        // Validate required fields
        if (!alertData.severity || !alertData.message) {
            res.status(400).json({ message: 'Severity and message are required fields' });
            return;
        }

        // Validate severity level
        if (!['low', 'medium', 'high'].includes(alertData.severity)) {
            res.status(400).json({ message: 'Severity must be one of: low, medium, high' });
            return;
        }

        // Add timestamp if not provided
        if (!alertData.timestamp) {
            alertData.timestamp = new Date();
        }

        const newAlert = await alertService.createAlert(alertData);
        res.status(201).json({ message: 'Alert created successfully', alert: newAlert });
    } catch (error) {
        logger.error(`Error creating alert: ${error}`);
        res.status(500).json({ message: 'Error creating alert', error: error.message });
    }
};

export const updateAlert = async (req: Request, res: Response): Promise<void> => {
    try {
        const alertId = req.params.id;
        const alertData = req.body;

        // Validate severity if provided
        if (alertData.severity && !['low', 'medium', 'high'].includes(alertData.severity)) {
            res.status(400).json({ message: 'Severity must be one of: low, medium, high' });
            return;
        }

        const updatedAlert = await alertService.updateAlert(alertId, alertData);

        if (!updatedAlert) {
            res.status(404).json({ message: 'Alert not found' });
            return;
        }

        res.status(200).json({ message: 'Alert updated successfully', alert: updatedAlert });
    } catch (error) {
        logger.error(`Error updating alert ${req.params.id}: ${error}`);
        res.status(500).json({ message: 'Error updating alert', error: error.message });
    }
};

export const deleteAlert = async (req: Request, res: Response): Promise<void> => {
    try {
        const alertId = req.params.id;
        const deleted = await alertService.deleteAlert(alertId);

        if (!deleted) {
            res.status(404).json({ message: 'Alert not found' });
            return;
        }

        res.status(204).send();
    } catch (error) {
        logger.error(`Error deleting alert ${req.params.id}: ${error}`);
        res.status(500).json({ message: 'Error deleting alert', error: error.message });
    }
};

export const getAlertStats = async (req: Request, res: Response): Promise<void> => {
    try {
        const stats = await alertService.getAlertStats();
        res.status(200).json({ stats });
    } catch (error) {
        logger.error(`Error retrieving alert statistics: ${error}`);
        res.status(500).json({ message: 'Error retrieving alert statistics', error: error.message });
    }
};