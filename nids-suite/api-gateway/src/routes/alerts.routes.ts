import { Router } from 'express';
import { getAlerts, getAlertById, createAlert, updateAlert, deleteAlert, getAlertStats } from '../controllers/alerts.controller';
import { authMiddleware, roleCheck } from '../middleware/auth.middleware';

const router = Router();

// Apply authentication middleware to all alert routes
router.use(authMiddleware);

// Routes accessible by all authenticated users (Viewer, Analyst, Admin)
router.get('/', getAlerts);
router.get('/stats', getAlertStats);
router.get('/:id', getAlertById);

// Routes restricted to Analyst and Admin roles
router.post('/', roleCheck(['Analyst', 'Admin']), createAlert);
router.put('/:id', roleCheck(['Analyst', 'Admin']), updateAlert);

// Routes restricted to Admin role
router.delete('/:id', roleCheck(['Admin']), deleteAlert);

export default router;