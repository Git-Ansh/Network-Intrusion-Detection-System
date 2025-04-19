// File: /nids-suite/nids-suite/scripts/install-sensor.js

const { exec } = require('child_process');
const fs = require('fs');
const path = require('path');

// Check if the Supabase service key is provided
const SUPABASE_SERVICE_KEY = process.argv[2];
if (!SUPABASE_SERVICE_KEY) {
    console.error('Error: Supabase service key is required as an argument.');
    process.exit(1);
}

// Define the sensor installation command
const installCommand = `npx nids-sensor install --token ${SUPABASE_SERVICE_KEY}`;

// Execute the installation command
exec(installCommand, (error, stdout, stderr) => {
    if (error) {
        console.error(`Installation failed: ${error.message}`);
        return;
    }
    if (stderr) {
        console.error(`Error: ${stderr}`);
        return;
    }
    console.log(`Sensor installed successfully:\n${stdout}`);
});

// Optional: Create a log file for installation
const logFilePath = path.join(__dirname, 'install-sensor.log');
const logMessage = `Sensor installation executed at ${new Date().toISOString()}\nCommand: ${installCommand}\n\n`;
fs.appendFile(logFilePath, logMessage, (err) => {
    if (err) {
        console.error(`Failed to write to log file: ${err.message}`);
    }
});