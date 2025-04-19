// File: /nids-suite/nids-suite/api-gateway/src/routes/index.ts

import { Router } from 'express';
import alertsRoutes from './alerts.routes';
import authRoutes from './auth.routes';
import metricsRoutes from './metrics.routes';
import sensorsRoutes from './sensors.routes';

const router = Router();

// Mount routes
router.use('/alerts', alertsRoutes);
router.use('/auth', authRoutes);
router.use('/metrics', metricsRoutes);
router.use('/sensors', sensorsRoutes);

export default router;