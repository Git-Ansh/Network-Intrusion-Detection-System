# README.md for API Gateway

# NIDS Suite - API Gateway

## Overview

The API Gateway serves as the central point for managing requests and responses between the frontend and the backend services of the NIDS Suite. It is built using Express and TypeScript, providing a robust and scalable solution for handling authentication, authorization, and routing of API calls.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Directory Structure](#directory-structure)
- [API Endpoints](#api-endpoints)
- [Middleware](#middleware)
- [Controllers](#controllers)
- [Services](#services)
- [Testing](#testing)
- [Contributing](#contributing)
- [License](#license)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/acme/nids-suite.git
   cd nids-suite/api-gateway
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Set up environment variables:
   - Create a `.env` file based on the `.env.example` provided and fill in the required values.

## Usage

To start the API Gateway, run the following command:

```bash
npm run dev
```

This will start the server on the default port (5001). You can access the API documentation at `http://localhost:5001/docs`.

## Directory Structure

```
api-gateway
├── src
│   ├── controllers          # Contains the logic for handling requests
│   ├── middleware           # Custom middleware for authentication and error handling
│   ├── routes               # API route definitions
│   ├── services             # Business logic and service layer
│   ├── types                # Type definitions
│   ├── utils                # Utility functions
│   ├── app.ts               # Main application setup
│   └── server.ts            # Server initialization
├── package.json             # Project metadata and dependencies
└── tsconfig.json            # TypeScript configuration
```

## API Endpoints

- **Authentication**
  - `POST /auth/login` - User login
  - `POST /auth/register` - User registration

- **Alerts**
  - `GET /alerts` - Retrieve all alerts
  - `POST /alerts` - Create a new alert

- **Metrics**
  - `GET /metrics` - Retrieve system metrics

- **Sensors**
  - `GET /sensors` - List all sensors
  - `POST /sensors` - Register a new sensor

## Middleware

- **Auth Middleware**: Validates JWT tokens for protected routes.
- **Error Handler Middleware**: Centralized error handling for the API.
- **Rate Limiter Middleware**: Limits the number of requests from a single IP.

## Controllers

- **Alerts Controller**: Manages alert-related requests.
- **Auth Controller**: Handles authentication and user management.
- **Metrics Controller**: Provides system metrics.
- **Sensors Controller**: Manages sensor-related requests.

## Services

- **Alert Service**: Business logic for alerts.
- **Circuit Breaker Service**: Implements circuit breaker pattern for resilience.
- **Watchdog Service**: Monitors the health of services.

## Testing

To run tests, use the following command:

```bash
npm test
```

Ensure that you have set up the testing environment as specified in the documentation.

## Contributing

Contributions are welcome! Please read the [CONTRIBUTING.md](../CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.