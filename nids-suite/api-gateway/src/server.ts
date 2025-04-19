import express from 'express';
import helmet from 'helmet';
import rateLimit from 'express-rate-limit';
import { json } from 'body-parser';
import { authMiddleware } from './middleware/auth.middleware';
import { errorHandler } from './middleware/error-handler.middleware';
import { alertsRouter } from './routes/alerts.routes';
import { authRouter } from './routes/auth.routes';
import { metricsRouter } from './routes/metrics.routes';
import { sensorsRouter } from './routes/sensors.routes';

const app = express();
const PORT = process.env.PORT || 5001;

// Middleware
app.use(helmet());
app.use(json());
app.use(rateLimit({
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 100 // limit each IP to 100 requests per windowMs
}));
app.use(authMiddleware);

// Routes
app.use('/api/alerts', alertsRouter);
app.use('/api/auth', authRouter);
app.use('/api/metrics', metricsRouter);
app.use('/api/sensors', sensorsRouter);

// Error handling
app.use(errorHandler);

// Start server
app.listen(PORT, () => {
    console.log(`API Gateway is running on http://localhost:${PORT}`);
});