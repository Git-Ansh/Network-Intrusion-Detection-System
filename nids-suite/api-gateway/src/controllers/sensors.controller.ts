// File: /nids-suite/nids-suite/api-gateway/src/controllers/sensors.controller.ts

import { Request, Response } from 'express';
import { SensorService } from '../services/sensor.service';

class SensorsController {
    private sensorService: SensorService;

    constructor() {
        this.sensorService = new SensorService();
    }

    public async registerSensor(req: Request, res: Response): Promise<void> {
        try {
            const sensorData = req.body;
            const newSensor = await this.sensorService.registerSensor(sensorData);
            res.status(201).json(newSensor);
        } catch (error) {
            res.status(500).json({ message: 'Error registering sensor', error });
        }
    }

    public async getSensors(req: Request, res: Response): Promise<void> {
        try {
            const sensors = await this.sensorService.getSensors();
            res.status(200).json(sensors);
        } catch (error) {
            res.status(500).json({ message: 'Error retrieving sensors', error });
        }
    }

    public async updateSensor(req: Request, res: Response): Promise<void> {
        try {
            const sensorId = req.params.id;
            const sensorData = req.body;
            const updatedSensor = await this.sensorService.updateSensor(sensorId, sensorData);
            res.status(200).json(updatedSensor);
        } catch (error) {
            res.status(500).json({ message: 'Error updating sensor', error });
        }
    }

    public async deleteSensor(req: Request, res: Response): Promise<void> {
        try {
            const sensorId = req.params.id;
            await this.sensorService.deleteSensor(sensorId);
            res.status(204).send();
        } catch (error) {
            res.status(500).json({ message: 'Error deleting sensor', error });
        }
    }
}

export const sensorsController = new SensorsController();