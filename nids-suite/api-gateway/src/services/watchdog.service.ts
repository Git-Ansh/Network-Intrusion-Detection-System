// File: /nids-suite/nids-suite/api-gateway/src/services/watchdog.service.ts

import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

class WatchdogService {
    private readonly serviceName: string;

    constructor(serviceName: string) {
        this.serviceName = serviceName;
    }

    public async restartService(): Promise<void> {
        try {
            await execAsync(`systemctl restart ${this.serviceName}`);
            console.log(`Service ${this.serviceName} restarted successfully.`);
        } catch (error) {
            console.error(`Failed to restart service ${this.serviceName}:`, error);
        }
    }

    public async checkServiceStatus(): Promise<string> {
        try {
            const { stdout } = await execAsync(`systemctl is-active ${this.serviceName}`);
            return stdout.trim();
        } catch (error) {
            console.error(`Failed to check status of service ${this.serviceName}:`, error);
            return 'unknown';
        }
    }

    public async monitorService(): Promise<void> {
        const status = await this.checkServiceStatus();
        if (status !== 'active') {
            console.warn(`Service ${this.serviceName} is not active. Attempting to restart...`);
            await this.restartService();
        } else {
            console.log(`Service ${this.serviceName} is running smoothly.`);
        }
    }
}

export default WatchdogService;