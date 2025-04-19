// File: /nids-suite/nids-suite/api-gateway/src/middleware/rate-limiter.middleware.ts

import { Request, Response, NextFunction } from 'express';
import rateLimit from 'express-rate-limit';

// Configure rate limiter
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // limit each IP to 100 requests per windowMs
  message: {
    status: 429,
    error: 'Too many requests, please try again later.',
  },
});

// Apply the rate limiter to all requests
export const rateLimiter = (req: Request, res: Response, next: NextFunction) => {
  limiter(req, res, next);
};