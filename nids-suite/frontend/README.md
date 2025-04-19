# NIDS Suite Frontend README

# NIDS Suite Frontend

Welcome to the NIDS Suite Frontend! This project is part of a comprehensive Real-Time Network Intrusion Detection System (NIDS) designed to monitor network traffic, detect threats, and provide actionable insights through an intuitive user interface.

## Table of Contents

1. [Project Overview](#project-overview)
2. [Getting Started](#getting-started)
3. [Project Structure](#project-structure)
4. [Dependencies](#dependencies)
5. [Development](#development)
6. [Testing](#testing)
7. [Deployment](#deployment)
8. [Contributing](#contributing)
9. [License](#license)

## Project Overview

The NIDS Suite Frontend is built using React and Vite, providing a responsive and interactive user experience. It communicates with the API Gateway to fetch and display real-time data regarding network traffic and alerts.

## Getting Started

To get started with the NIDS Suite Frontend, follow these steps:

1. Clone the repository:
   ```bash
   git clone https://github.com/acme/nids-suite.git
   cd nids-suite/frontend
   ```

2. Install the dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

4. Open your browser and navigate to `http://localhost:3001` to view the application.

## Project Structure

The project structure is organized as follows:

```
frontend
├── public
│   └── favicon.svg
├── src
│   ├── components
│   │   ├── alerts
│   │   ├── dashboard
│   │   ├── network
│   │   ├── packets
│   │   └── layout
│   ├── contexts
│   ├── hooks
│   ├── lib
│   ├── pages
│   ├── types
│   ├── utils
│   ├── App.tsx
│   └── main.tsx
├── index.html
├── package.json
├── tailwind.config.js
├── tsconfig.json
└── vite.config.ts
```

## Dependencies

The following dependencies are used in this project:

- React
- Vite
- Tailwind CSS
- Supabase

## Development

During development, you can utilize the following commands:

- `npm run dev`: Start the development server.
- `npm run build`: Build the application for production.
- `npm run preview`: Preview the production build.

## Testing

To run tests, use the following command:

```bash
npm test
```

Make sure to write unit tests for components and hooks to ensure code quality.

## Deployment

For deployment, build the application and serve the static files using a web server or deploy to a CDN.

1. Build the application:
   ```bash
   npm run build
   ```

2. Deploy the contents of the `dist` folder to your preferred hosting service.

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/YourFeature`).
3. Make your changes and commit them (`git commit -m 'Add some feature'`).
4. Push to the branch (`git push origin feature/YourFeature`).
5. Open a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](../LICENSE) file for details.