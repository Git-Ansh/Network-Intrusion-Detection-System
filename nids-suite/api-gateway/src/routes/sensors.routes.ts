// File: /nids-suite/nids-suite/api-gateway/src/routes/sensors.routes.ts

import { Router } from 'express';
import { getAllSensors, getSensorById, createSensor, updateSensor, deleteSensor } from '../controllers/sensors.controller';

const router = Router();

// Route to get all sensors
router.get('/', getAllSensors);

// Route to get a specific sensor by ID
router.get('/:id', getSensorById);

// Route to create a new sensor
router.post('/', createSensor);

// Route to update an existing sensor
router.put('/:id', updateSensor);

// Route to delete a sensor
router.delete('/:id', deleteSensor);

export default router;