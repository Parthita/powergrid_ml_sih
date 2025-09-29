# PowerGrid Analytics Dashboard

## Overview

PowerGrid Analytics is a full-stack web application designed to provide predictive insights into infrastructure project management. It leverages a machine learning model to forecast cost and timeline overruns for power grid construction projects, presenting the results in an interactive and analytical dashboard. The platform is intended to assist project managers in identifying high-risk projects, understanding potential deviations from budget and schedule, and making data-driven decisions to mitigate risks.

## Table of Contents

- [Problem Domain](#problem-domain)
- [Solution Architecture](#solution-architecture)
- [The Machine Learning Model](#the-machine-learning-model)
- [Technology Stack](#technology-stack)
- [Local Development Setup](#local-development-setup)
- [Deployment](#deployment)
- [License](#license)

## Problem Domain

Large-scale infrastructure projects, particularly in the energy sector, are susceptible to significant cost and timeline overruns. These deviations are caused by a complex interplay of factors including terrain, weather, regulatory delays, and supply chain issues. The inability to accurately forecast these risks during the planning phase often leads to financial losses and delays in critical infrastructure delivery. This project aims to address this challenge by providing a tool for predictive risk assessment.

## Solution Architecture

The application is built on a decoupled, two-tier architecture:

-   **Frontend**: A client-side single-page application (SPA) built with React. It is responsible for all user interface elements, data visualization, and communication with the backend API. It is designed to be deployed as a static site on a platform like Vercel.

-   **Backend**: A Python-based API developed with the FastAPI framework. It exposes a secure endpoint that receives project data, performs feature engineering, executes the machine learning model, and returns predictions. The trained models are stored and loaded using `joblib`. The backend is designed for deployment on a platform like Railway.

## The Machine Learning Model

The core of the platform is a set of supervised learning models trained to predict project overruns.

-   **Model Objective**: The system uses two distinct models to predict the `CostOverrunPct` and `TimelineOverrunPct` as continuous percentage values.

-   **Model Type**: We utilize XGBoost (Extreme Gradient Boosting), a gradient boosting framework, for both regression tasks. This model was chosen for its high performance on structured, tabular data and its ability to capture complex, non-linear relationships between features.

-   **Feature Engineering**: The model's performance is enhanced by a feature engineering pipeline that transforms raw project data into a more informative feature set. This includes:
    -   **Interaction Features**: Combinations of categorical variables (e.g., `ProjectType` and `Terrain`) are created to model synergistic effects.
    -   **Ratio Features**: Ratios between estimated and actual baseline data are calculated to normalize differences.
    -   **Derived Risk Indicators**: New features are created to explicitly represent risk, such as `VendorDelayRisk` (derived from `VendorOnTimeRate`).
    -   **Encoding**: Categorical variables are one-hot encoded to be compatible with the model.

-   **Model Performance**: The models were validated on a test set, achieving high performance metrics that indicate a strong predictive capability:
    -   **Cost Overrun Prediction R²**: > 0.99
    -   **Timeline Overrun Prediction R²**: > 0.80

## Technology Stack

-   **Frontend**: React, Vite, Recharts
-   **Backend**: Python, FastAPI, Pandas, Scikit-learn, XGBoost
-   **Deployment**: Vercel (Frontend), Railway (Backend)

## Local Development Setup

To set up the project on a local machine, follow these steps.

### Prerequisites

-   Git
-   Node.js and npm
-   Python 3.8+ and pip

### Installation and Execution

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd ml_powergrid
    ```

2.  **Configure and run the backend:**
    ```bash
    cd backend
    pip install -r requirements.txt
    uvicorn api:app --host 0.0.0.0 --port 8000
    ```

3.  **Configure and run the frontend:**
    ```bash
    cd frontend
    npm install
    npm run dev
    ```
    The frontend will be available at `http://localhost:5173`.

## Deployment

The application is configured for deployment to separate hosting providers for the frontend and backend.

### Backend Deployment (Railway)

1.  Ensure the project is pushed to a GitHub repository.
2.  Create a new project on Railway and connect it to your repository.
3.  Set the service's root directory to `/backend` during setup.
4.  Railway will automatically use the `Procfile` to build and deploy the API.

### Frontend Deployment (Vercel)

1.  In `frontend/src/App.jsx`, modify the `fetch` request URL to point to the public URL of your deployed Railway backend.
2.  Push this change to your GitHub repository.
3.  Create a new project on Vercel and connect it to the same repository.
4.  Configure the project's root directory to `/frontend` in the Vercel settings.
5.  Vercel will then build and deploy the frontend application.

## License

This project is licensed under the MIT License.
