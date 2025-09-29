# ⚡ PowerGrid Analytics Dashboard ⚡

An end-to-end application to forecast cost and timeline overruns for power infrastructure projects and visualize risks in a modern, interactive dashboard.

---

## ✨ Features

-   **AI-Powered Predictions**: Utilizes XGBoost models to predict project cost and timeline overruns with high accuracy.
-   **Interactive Dashboard**: A sleek and responsive user interface built with React for a seamless user experience.
-   **Dynamic Visualizations**: Leverages Recharts to provide a rich set of charts and graphs for in-depth analysis.
-   **Simple Data Input**: Users can upload their own project data in CSV format to get instant predictions and insights.

## 🛠️ Technology Stack

-   **Frontend**: React, Vite, Recharts
-   **Backend**: Python, FastAPI, Pandas, Scikit-learn, XGBoost
-   **Deployment**: Vercel (Frontend), Railway (Backend)

## 🚀 Getting Started

Follow these instructions to get a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

-   Git
-   Node.js and npm
-   Python 3.8+ and pip

### Local Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd ml_powergrid
    ```

2.  **Backend Setup:**
    ```bash
    cd backend
    pip install -r requirements.txt
    # The models are pre-trained, but you can retrain them by running:
    # python train_overrun.py
    uvicorn api:app --host 0.0.0.0 --port 8000
    ```

3.  **Frontend Setup:**
    ```bash
    cd frontend
    npm install
    npm run dev
    ```

    The frontend will be available at `http://localhost:5173` and will connect to the local backend server running on port 8000.

## ☁️ Deployment

The application is designed for a decoupled deployment on modern cloud platforms.

### Backend (Railway)

1.  Push your code to a GitHub repository.
2.  Create a new project on Railway and connect it to your repository.
3.  If prompted, set the service's root directory to `/backend`.
4.  Railway will use the `Procfile` to deploy the API and provide a public URL.

### Frontend (Vercel)

1.  In `frontend/src/App.jsx`, update the `fetch` URL to point to your deployed Railway backend URL.
2.  Push the changes to your GitHub repository.
3.  Create a new project on Vercel and connect it to the same repository.
4.  Set the project's root directory to `/frontend` in the Vercel settings.
5.  Vercel will build and deploy your frontend application.