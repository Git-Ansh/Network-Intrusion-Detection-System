// File: /nids-suite/nids-suite/api-gateway/src/routes/metrics.routes.ts

import { Router } from 'express';
import { getMetrics } from '../controllers/metrics.controller';

const router = Router();

// Route to get metrics
router.get('/metrics', getMetrics);

export default router;