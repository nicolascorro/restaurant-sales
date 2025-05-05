# Restaurant Sales Prediction Frontend

This is the frontend application for the Restaurant Sales Prediction system. It's built with React, TypeScript, and Material UI.

## Features

- CSV file upload and processing
- Sales forecast visualization
- Best-selling products analysis
- AI-generated business reports
- Responsive design for all devices

## Setup Instructions

### Prerequisites

- Node.js (v16 or later)
- npm or yarn
- Backend API running (FastAPI)

### Installation

1. Clone the repository
2. Navigate to the frontend directory:
   ```
   cd frontend
   ```
3. Install dependencies:
   ```
   npm install
   ```
   or if you use yarn:
   ```
   yarn install
   ```

### Development

To start the development server:

```
npm run dev
```

or with yarn:

```
yarn dev
```

This will start the development server at [http://localhost:3000](http://localhost:3000).

### Building for Production

To create a production build:

```
npm run build
```

or with yarn:

```
yarn build
```

The build artifacts will be stored in the `dist/` directory.

### Project Structure

```
frontend/
├── public/                 # Static assets
├── src/
│   ├── api/                # API integration
│   ├── components/         # Reusable components
│   │   ├── common/         # Shared UI components
│   │   └── ...
│   ├── context/            # Context API for state management
│   ├── pages/              # Application pages
│   ├── types/              # TypeScript type definitions
│   ├── utils/              # Utility functions
│   ├── App.tsx             # Main App component with routing
│   ├── main.tsx            # Entry point
│   └── index.css           # Global styles
├── package.json
└── tsconfig.json
```

## Connecting to the Backend

The frontend is configured to connect to the backend API running at `http://localhost:8000`. If your backend is running on a different URL, update the API base URL in `src/api/index.ts`.

## Workflow

1. Upload a CSV file containing restaurant sales data
2. The system processes the data and applies machine learning models
3. View sales forecasts, top-selling products, and business insights
4. Download charts and reports for offline use

## Additional Notes

- Make sure the backend API is running before using the frontend
- The application is designed to work with specific CSV format (see documentation)