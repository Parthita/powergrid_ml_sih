# PowerGrid ML: Predict Cost and Timeline Overruns

End-to-end workflow to forecast cost and timeline overruns for power infrastructure projects and visualize risks in a React dashboard. Includes a FastAPI backend, synthetic training pipeline, feature engineering, and a dashboard that accepts raw CSVs.

## Features

- **AI Predictions**: Advanced ML models for cost and timeline predictions
- **Risk Assessment**: Automatic risk level calculation based on predictions
- **Interactive Analytics**: Beautiful charts and visualizations with Plotly
- **Data Filtering**: Filter by project type and risk level
- **CSV Export**: Download results for further analysis
- **Responsive Design**: Modern UI that works on all devices

## Quick Start

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Train Overrun Models** (synthetic generator inside):
   ```bash
   python train_overrun.py
   ```

3. **(Optional) Generate Dummy CSVs**:
   ```bash
   python generate_test_csvs.py
   ```

4. **Start API**:
   ```bash
   uvicorn api:app --host 0.0.0.0 --port 8000
   ```

5. **Start React Dashboard**:
   ```bash
   cd dashboard
   npm install
   npm run dev
   ```

## Required CSV Format

Your CSV file must contain these columns:

### Required Columns:
- `ProjectID`: Unique project identifier
- `ProjectType`: Substation, Overhead Line, or Underground Cable
- `Terrain`: Plains, Hills, Forest, Urban, or Coastal
- `WeatherImpact`: Low, Medium, or High
- `DemandSupply`: Stable, Fluctuating, or High Demand
- `EstimatedCost` (recommended): Planned/estimated cost in ₹ lakhs
- `EstimatedTimeline` (recommended): Planned/estimated timeline in months
- If estimates are missing, the CLI will fallback to `TotalCost`/`Timeline` when present for overrun percentages.

### Optional Columns (handled automatically):
- `State`, `Vendor`
- `MaterialCost`, `LabourCost`, `CostEscalation`
- `Resources`, `ProjectLength`
- `RegulatoryTime`, `RegulatoryPermitDays`, `PermitVariance`
- `HistoricalDelay`, `HindranceCounts`, `HindranceRecentDays`
- `WeatherSeverityIndex`, `MaterialAvailabilityIndex`, `ResourceUtilization`, `StartMonth`, `VendorOnTimeRate`, `VendorAvgDelay`

## How to Use

1. **Upload Data**: Use the sidebar to upload your project data CSV
2. **Apply Filters**: Filter by project type and risk level
3. **View Results**: Explore predictions, charts, and detailed project data
4. **Download**: Export results as CSV for further analysis

## Dashboard Sections

### Summary Insights
- Total projects count
- Average predicted cost
- Average predicted timeline
- High-risk projects count

### Analytics Charts
- **Cost Distribution**: Histogram showing cost predictions by risk level
- **Timeline Distribution**: Histogram showing timeline predictions by risk level
- **Risk Analysis**: Pie chart showing risk level distribution
- **Cost vs Timeline**: Scatter plot with risk-based coloring

### Project Details Table
- Complete project information
- Predicted costs and timelines
- Risk assessments
- Overrun percentages

## Technical Details

### ML Models
- **Cost Prediction**: XGBoost model with feature engineering
- **Timeline Prediction**: XGBoost model with feature engineering
- **Risk Assessment**: Calculated based on cost and timeline overruns

### Features
- **Feature Engineering**: Automatic feature creation and transformation
- **Data Validation**: Comprehensive input validation
- **Error Handling**: Robust error handling and user feedback
- **Caching**: Efficient model loading and caching

## File Structure

```
ml_powergrid/
├── streamlit_app.py          # Main Streamlit application
├── feature_engineering.py    # Feature engineering functions
├── train_models.py           # Model training script
├── best_models.pkl           # Trained ML models
├── requirements.txt          # Python dependencies
├── test_csvs/                # Sample CSV files
│   ├── dummy_data_1_fixed.csv
│   ├── dummy_data_2_fixed.csv
│   └── dummy_data_3_fixed.csv
└── README.md                 # This file
```

## Using with React Dashboard

1. Start the API (`uvicorn api:app --port 8000`).
2. In the dashboard, upload a raw feature CSV (no Predicted_*). The app will call the API and render predictions.

## Deployment

### Deploy API
Containerize `api.py` with Uvicorn/Gunicorn and expose `/predict` to the dashboard origin.

### Docker
Create a Dockerfile for `api.py` and serve React separately or via a reverse proxy.

## Troubleshooting

### Models Not Loading
- Ensure `best_models.pkl` exists
- Run `python train_models.py` to create models
- Check file permissions

### Import Errors
- Install all dependencies: `pip install -r requirements.txt`
- Check Python version (3.8+ required)

### Prediction Errors
- Verify CSV format matches requirements
- Check for missing required columns
- Ensure data types are correct

## Sample Data

The `test_csvs/` directory contains sample CSV files that demonstrate the required format:
- `dummy_data_1_fixed.csv`: Sample substation projects
- `dummy_data_2_fixed.csv`: Sample overhead line projects  
- `dummy_data_3_fixed.csv`: Sample underground cable projects

## Model Performance

The trained models achieve high accuracy:
- **Cost Prediction**: R² > 0.99
- **Timeline Prediction**: R² > 0.80
- **Risk Assessment**: Based on prediction variance

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Verify your CSV file format
3. Ensure all dependencies are installed
4. Create an issue on GitHub

---

Ready to predict power grid project costs and timelines with AI!