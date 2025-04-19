// File: /nids-suite/nids-suite/api-gateway/src/middleware/auth.middleware.ts

import { Request, Response, NextFunction } from 'express';
import jwt from 'jsonwebtoken';
import { createClient } from '@supabase/supabase-js';
import { User } from '../types'; 

const JWT_SECRET = process.env.JWT_SECRET || 'your_jwt_secret'; // Use environment variable in production
const SUPABASE_URL = process.env.SUPABASE_URL || '';
const SUPABASE_KEY = process.env.SUPABASE_KEY || '';

const supabase = createClient(SUPABASE_URL, SUPABASE_KEY);

export const authMiddleware = async (req: Request, res: Response, next: NextFunction) => {
    const token = req.headers['authorization']?.split(' ')[1];

    if (!token) {
        return res.status(401).json({ message: 'No token provided' });
    }

    try {
        // Verify the JWT token
        const decoded = jwt.verify(token, JWT_SECRET) as User;
        
        // Check if the token is valid in Supabase
        const { data, error } = await supabase.auth.getUser(token);
        
        if (error || !data.user) {
            return res.status(403).json({ message: 'Invalid or expired token' });
        }
        
        // Add user information to the request
        req.user = {
            id: data.user.id,
            email: data.user.email || '',
            role: data.user.user_metadata.role || 'Viewer' // Default to Viewer if role not specified
        };
        
        next();
    } catch (err) {
        return res.status(403).json({ message: 'Failed to authenticate token' });
    }
};

// Middleware to check if user has required role
export const roleCheck = (requiredRoles: string[]) => {
    return (req: Request, res: Response, next: NextFunction) => {
        if (!req.user) {
            return res.status(401).json({ message: 'Unauthorized' });
        }

        const userRole = req.user.role;
        
        if (!requiredRoles.includes(userRole)) {
            return res.status(403).json({ message: 'Insufficient permissions' });
        }
        
        next();
    };
};

// Middleware to validate login request
export const validateLogin = (req: Request, res: Response, next: NextFunction) => {
    const { email, password } = req.body;
    
    if (!email || !password) {
        return res.status(400).json({ message: 'Email and password are required' });
    }
    
    // Basic email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        return res.status(400).json({ message: 'Invalid email format' });
    }
    
    next();
};

// Middleware to validate registration request
export const validateRegister = (req: Request, res: Response, next: NextFunction) => {
    const { email, password, name } = req.body;
    
    if (!email || !password || !name) {
        return res.status(400).json({ message: 'Email, password, and name are required' });
    }
    
    // Basic email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        return res.status(400).json({ message: 'Invalid email format' });
    }
    
    // Password strength validation
    if (password.length < 8) {
        return res.status(400).json({ message: 'Password must be at least 8 characters long' });
    }
    
    next();
};