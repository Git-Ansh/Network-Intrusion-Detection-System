// File: /nids-suite/nids-suite/api-gateway/src/routes/auth.routes.ts

import { Router } from 'express';
import { login, register, logout, getCurrentUser, updateRole } from '../controllers/auth.controller';
import { validateLogin, validateRegister, authMiddleware, roleCheck } from '../middleware/auth.middleware';

const router = Router();

// Public routes
router.post('/register', validateRegister, register);
router.post('/login', validateLogin, login);

// Protected routes
router.post('/logout', authMiddleware, logout);
router.get('/me', authMiddleware, getCurrentUser);
router.put('/role', authMiddleware, roleCheck(['Admin']), updateRole);

export default router;