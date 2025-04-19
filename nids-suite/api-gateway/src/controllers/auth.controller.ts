// File: /nids-suite/nids-suite/api-gateway/src/controllers/auth.controller.ts

import { Request, Response } from 'express';
import { createClient } from '@supabase/supabase-js';
import jwt from 'jsonwebtoken';
import bcrypt from 'bcrypt';
import logger from '../utils/logger';

const SUPABASE_URL = process.env.SUPABASE_URL || '';
const SUPABASE_KEY = process.env.SUPABASE_KEY || '';
const JWT_SECRET = process.env.JWT_SECRET || 'your_jwt_secret'; // Use environment variable in production
const JWT_EXPIRY = '24h';

const supabase = createClient(SUPABASE_URL, SUPABASE_KEY);

export const register = async (req: Request, res: Response) => {
    const { email, password, name } = req.body;

    try {
        // Register with Supabase Auth
        const { data, error } = await supabase.auth.signUp({
            email,
            password,
            options: {
                data: {
                    name,
                    role: 'Viewer' // Default role for new users
                }
            }
        });

        if (error) {
            logger.error(`Registration error: ${error.message}`);
            return res.status(400).json({ message: error.message });
        }

        // Return user data (excluding sensitive information)
        return res.status(201).json({
            message: 'Registration successful. Please check your email to confirm your account.',
            user: {
                id: data.user?.id,
                email: data.user?.email,
                role: 'Viewer'
            }
        });
    } catch (error) {
        logger.error(`Server error during registration: ${error}`);
        return res.status(500).json({ message: 'Server error during registration' });
    }
};

export const login = async (req: Request, res: Response) => {
    const { email, password } = req.body;

    try {
        // Sign in with Supabase Auth
        const { data, error } = await supabase.auth.signInWithPassword({
            email,
            password
        });

        if (error) {
            logger.error(`Login error: ${error.message}`);
            return res.status(401).json({ message: 'Invalid credentials' });
        }

        // Generate a JWT token
        const token = jwt.sign(
            { 
                id: data.user.id,
                email: data.user.email,
                role: data.user.user_metadata.role || 'Viewer'
            },
            JWT_SECRET,
            { expiresIn: JWT_EXPIRY }
        );

        // Return the token and user data
        return res.status(200).json({
            message: 'Login successful',
            token,
            user: {
                id: data.user.id,
                email: data.user.email,
                role: data.user.user_metadata.role || 'Viewer'
            }
        });
    } catch (error) {
        logger.error(`Server error during login: ${error}`);
        return res.status(500).json({ message: 'Server error during login' });
    }
};

export const logout = async (req: Request, res: Response) => {
    try {
        // Sign out from Supabase Auth
        const { error } = await supabase.auth.signOut();

        if (error) {
            logger.error(`Logout error: ${error.message}`);
            return res.status(500).json({ message: error.message });
        }

        return res.status(200).json({ message: 'Logout successful' });
    } catch (error) {
        logger.error(`Server error during logout: ${error}`);
        return res.status(500).json({ message: 'Server error during logout' });
    }
};

export const getCurrentUser = async (req: Request, res: Response) => {
    try {
        if (!req.user) {
            return res.status(401).json({ message: 'Not authenticated' });
        }

        return res.status(200).json({ user: req.user });
    } catch (error) {
        logger.error(`Server error retrieving current user: ${error}`);
        return res.status(500).json({ message: 'Server error retrieving current user' });
    }
};

export const updateRole = async (req: Request, res: Response) => {
    const { userId, newRole } = req.body;
    const validRoles = ['Viewer', 'Analyst', 'Admin'];

    // Check if user is admin
    if (req.user?.role !== 'Admin') {
        return res.status(403).json({ message: 'Only admins can update user roles' });
    }

    // Validate role
    if (!validRoles.includes(newRole)) {
        return res.status(400).json({ message: 'Invalid role. Must be one of: Viewer, Analyst, Admin' });
    }

    try {
        // Update user metadata in Supabase
        const { data, error } = await supabase.auth.admin.updateUserById(userId, {
            user_metadata: { role: newRole }
        });

        if (error) {
            logger.error(`Role update error: ${error.message}`);
            return res.status(400).json({ message: error.message });
        }

        return res.status(200).json({
            message: 'User role updated successfully',
            user: {
                id: data.user.id,
                email: data.user.email,
                role: newRole
            }
        });
    } catch (error) {
        logger.error(`Server error updating role: ${error}`);
        return res.status(500).json({ message: 'Server error updating user role' });
    }
};