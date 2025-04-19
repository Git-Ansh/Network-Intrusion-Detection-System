// File: /nids-suite/nids-suite/api-gateway/src/services/circuit-breaker.service.ts

import { ServiceUnavailableError } from 'http-errors';

interface CircuitBreakerOptions {
    failureThreshold: number;
    recoveryTime: number;
}

class CircuitBreaker {
    private failureCount: number = 0;
    private successCount: number = 0;
    private isOpen: boolean = false;
    private lastFailureTime: number = 0;
    private options: CircuitBreakerOptions;

    constructor(options: CircuitBreakerOptions) {
        this.options = options;
    }

    public async execute<T>(fn: () => Promise<T>): Promise<T> {
        if (this.isOpen) {
            throw new ServiceUnavailableError('Circuit breaker is open');
        }

        try {
            const result = await fn();
            this.recordSuccess();
            return result;
        } catch (error) {
            this.recordFailure();
            throw error;
        }
    }

    private recordSuccess() {
        this.successCount++;
        this.failureCount = 0;
        if (this.successCount >= this.options.failureThreshold) {
            this.isOpen = false;
            this.successCount = 0;
        }
    }

    private recordFailure() {
        this.failureCount++;
        this.lastFailureTime = Date.now();
        if (this.failureCount >= this.options.failureThreshold) {
            this.isOpen = true;
            setTimeout(() => {
                this.isOpen = false;
                this.failureCount = 0;
            }, this.options.recoveryTime);
        }
    }
}

export default CircuitBreaker;