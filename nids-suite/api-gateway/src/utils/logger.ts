// File: /nids-suite/nids-suite/api-gateway/src/utils/logger.ts

import winston from 'winston';

const logger = winston.createLogger({
    level: 'info',
    format: winston.format.combine(
        winston.format.timestamp(),
        winston.format.json()
    ),
    transports: [
        new winston.transports.Console({
            format: winston.format.simple(),
        }),
        new winston.transports.File({ filename: 'error.log', level: 'error' }),
        new winston.transports.File({ filename: 'combined.log' }),
    ],
});

export const logInfo = (message: string) => {
    logger.info(message);
};

export const logError = (message: string) => {
    logger.error(message);
};

export const logWarning = (message: string) => {
    logger.warn(message);
};

export default logger;