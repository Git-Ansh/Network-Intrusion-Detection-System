#!/usr/bin/env python3
"""
Development script to run all microservices locally
"""

import os
import sys
import time
import signal
import argparse
import subprocess
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any

# Define microservices
MICROSERVICES = {
    'packet_capture': {
        'command': ['python', '-m', 'packet_capture.src.capture'],
        'env': {
            'INTERFACE': 'any',  # Use 'any' for development, specify actual interface in production
            'API_GATEWAY_URL': 'http://localhost:5001',
            'LOG_LEVEL': 'DEBUG'
        }
    },
    'ml_engine_inference': {
        'command': ['python', '-m', 'ml_engine.src.app', '--mode', 'inference'],
        'env': {
            'API_GATEWAY_URL': 'http://localhost:5001',
            'LOG_LEVEL': 'DEBUG'
        }
    },
    'ml_engine_training': {
        'command': ['python', '-m', 'ml_engine.src.app', '--mode', 'training'],
        'env': {
            'API_GATEWAY_URL': 'http://localhost:5001',
            'LOG_LEVEL': 'DEBUG',
            'TRAINING_INTERVAL_HOURS': '1'  # More frequent training in development
        }
    }
}

# Global flag for graceful shutdown
running = True
processes: Dict[str, subprocess.Popen] = {}

def load_env():
    """Load environment variables from .env file"""
    env_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
    if os.path.exists(env_file):
        print(f"Loading environment from {env_file}")
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    os.environ[key] = value
    else:
        print("No .env file found, using existing environment variables")

def run_service(name: str, config: Dict[str, Any]):
    """Run a microservice in a subprocess"""
    print(f"Starting {name}...")
    
    # Set environment variables
    env = os.environ.copy()
    if 'env' in config:
        env.update(config['env'])
    
    # Start process
    process = subprocess.Popen(
        config['command'],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1  # Line buffered
    )
    
    processes[name] = process
    print(f"{name} started with PID {process.pid}")
    
    # Monitor output
    while running and process.poll() is None:
        output = process.stdout.readline()
        if output:
            print(f"[{name}] {output.strip()}")
    
    # Process ended
    if process.poll() is not None:
        print(f"{name} exited with code {process.returncode}")
    
    # Cleanup
    try:
        process.terminate()
        process.wait(timeout=5)
    except:
        process.kill()
        print(f"Killed {name}")

def signal_handler(sig, frame):
    """Handle interrupt signals"""
    global running
    print("Shutdown signal received, stopping all services...")
    running = False
    
    for name, process in processes.items():
        print(f"Stopping {name}...")
        try:
            process.terminate()
            process.wait(timeout=5)
        except:
            process.kill()
            print(f"Killed {name}")
    
    print("All services stopped")
    sys.exit(0)

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Run NIDS microservices locally')
    parser.add_argument('--services', type=str, default='all',
                        help='Comma-separated list of services to run, or "all"')
    args = parser.parse_args()
    
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Load environment variables
    load_env()
    
    # Determine which services to run
    services_to_run = {}
    if args.services.lower() == 'all':
        services_to_run = MICROSERVICES
    else:
        service_names = [s.strip() for s in args.services.split(',')]
        for name in service_names:
            if name in MICROSERVICES:
                services_to_run[name] = MICROSERVICES[name]
            else:
                print(f"Warning: Unknown service '{name}'")
    
    print(f"Starting {len(services_to_run)} microservices...")
    
    # Run each service in a separate thread
    with ThreadPoolExecutor(max_workers=len(services_to_run)) as executor:
        futures = {}
        for name, config in services_to_run.items():
            futures[executor.submit(run_service, name, config)] = name
    
    # Wait for all services to complete
    print("All services started. Press Ctrl+C to stop.")
    
    # Keep the main thread alive
    while running:
        time.sleep(1)

if __name__ == '__main__':
    main()