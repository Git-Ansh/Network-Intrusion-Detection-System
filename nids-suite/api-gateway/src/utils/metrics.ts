// File: /nids-suite/nids-suite/api-gateway/src/utils/metrics.ts

import { Histogram, Counter, Registry } from 'prom-client';

// Create a registry for metrics
const registry = new Registry();

// Define a histogram for request duration
const requestDurationHistogram = new Histogram({
  name: 'http_request_duration_seconds',
  help: 'Duration of HTTP requests in seconds',
  labelNames: ['method', 'route', 'status'],
  buckets: [0.1, 0.5, 1, 2, 5, 10], // Define buckets for latency
});

// Define a counter for total requests
const totalRequestsCounter = new Counter({
  name: 'http_requests_total',
  help: 'Total number of HTTP requests',
  labelNames: ['method', 'route', 'status'],
});

// Function to record request duration
export const recordRequestDuration = (method: string, route: string, status: string, duration: number) => {
  requestDurationHistogram.observe({ method, route, status }, duration);
};

// Function to increment total requests
export const incrementTotalRequests = (method: string, route: string, status: string) => {
  totalRequestsCounter.inc({ method, route, status });
};

// Function to get the metrics registry
export const getMetricsRegistry = () => {
  return registry;
};

// Register metrics with the registry
registry.registerMetric(requestDurationHistogram);
registry.registerMetric(totalRequestsCounter);