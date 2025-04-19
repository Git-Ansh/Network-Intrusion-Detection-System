import express from 'express';
import helmet from 'helmet';
import rateLimit from 'express-rate-limit';
import { json } from 'body-parser';
import { authMiddleware } from './middleware/auth.middleware';
import { errorHandler } from './middleware/error-handler.middleware';
import { alertsRoutes } from './routes/alerts.routes';
import { authRoutes } from './routes/auth.routes';
import { metricsRoutes } from './routes/metrics.routes';
import { sensorsRoutes } from './routes/sensors.routes';

const app = express();

// Middleware
app.use(helmet());
app.use(json());
app.use(rateLimit({
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 100 // limit each IP to 100 requests per windowMs
}));
app.use(authMiddleware);

// Routes
app.use('/api/alerts', alertsRoutes);
app.use('/api/auth', authRoutes);
app.use('/api/metrics', metricsRoutes);
app.use('/api/sensors', sensorsRoutes);

// Error handling middleware
app.use(errorHandler);

export default app;