# PowerGrid Analytics Dashboard

An end-to-end application to forecast cost and timeline overruns for power infrastructure projects and visualize risks in a modern, interactive dashboard.

## Architecture

The project is divided into a frontend and a backend:

- **Frontend**: A React application built with Vite, responsible for the user interface and data visualization. It is deployed on Vercel.
- **Backend**: A Python FastAPI application that serves the machine learning models for prediction. It is deployed on Railway.

Here is a diagram of the architecture:

```mermaid
graph TD
    A[User] --> B{Frontend (Vercel)};
    B --> C{Backend (Railway)};
    C --> D[ML Models];
    C --> B;
```

## Features

- **AI-Powered Predictions**: Utilizes XGBoost models to predict project cost and timeline overruns.
- **Interactive Dashboard**: A sleek and responsive user interface built with React and Recharts for data visualization.
- **CSV Upload**: Users can upload their own project data in CSV format to get instant predictions and insights.
- **Rich Visualizations**: The dashboard includes a variety of charts to analyze the results from different perspectives.

## Dashboard Visualizations

The dashboard provides the following visualizations:

- **Key Metrics**: A summary of key statistics like total projects, average cost, average timeline, and the number of high-risk projects.
- **Cost and Timeline Trends**: Line charts showing the predicted cost and timeline for each project.
- **Risk Distribution**: A pie chart showing the distribution of projects by risk level (Low, Medium, High).
- **Cost vs. Timeline**: A scatter plot to visualize the relationship between predicted cost and timeline.
- **Overrun Series**: Line charts showing the cost and timeline overrun percentages for each project.
- **Breakdowns by Project Type and Terrain**: Charts showing average cost, timeline, and overruns grouped by project type and terrain.
- **Project Details**: A detailed table view of all projects with their predictions and risk assessments.

## Technology Stack

- **Frontend**: React, Vite, Recharts, PapaParse
- **Backend**: FastAPI, Python, Pandas, Scikit-learn, XGBoost
- **Deployment**: Vercel (Frontend), Railway (Backend)

## Getting Started

### Prerequisites

- Git
- Node.js and npm
- Python 3.8+ and pip

### Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd ml_powergrid
    ```

2.  **Backend Setup:**
    ```bash
    cd backend
    pip install -r requirements.txt
    # To train the models (optional, pre-trained models are included)
    # python train_overrun.py
    # To start the backend server
    uvicorn api:app --host 0.0.0.0 --port 8000
    ```

3.  **Frontend Setup:**
    ```bash
    cd frontend
    npm install
    npm run dev
    ```
    The frontend will be available at `http://localhost:5173`.

## Deployment

### Backend (Railway)

1.  Push the code to a GitHub repository.
2.  Create a new project on Railway and connect it to your GitHub repository.
3.  When adding a service, specify `backend` as the root directory if prompted.
4.  Railway will use the `Procfile` to start the application and provide a public URL.

### Frontend (Vercel)

1.  Update the backend URL in `frontend/src/App.jsx` to the URL provided by Railway.
2.  Push the code to your GitHub repository.
3.  Create a new project on Vercel and connect it to your GitHub repository.
4.  Set the root directory to `frontend` in the Vercel project settings.
5.  Vercel will build and deploy your frontend.
