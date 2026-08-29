# CrowdCast: Event Demand & Overcrowding-Risk Prediction

CrowdCast is an event demand and overcrowding-risk prediction platform. It leverages machine learning models trained on marketplace ticket listing snapshots to predict significant ticket-listing depletion—a proxy for high demand and crowd pressure.

---

## 🏗️ Architecture Overview

The system is split into three main layers:

```
                  ┌──────────────────────┐
                  │    React Frontend    │  (Port 5173 - Vite)
                  └──────────┬───────────┘
                             │
                             │ HTTP POST /predict
                             ▼
                  ┌──────────────────────┐
                  │   FastAPI Backend    │  (Port 8000 - Uvicorn)
                  └──────────┬───────────┘
                             │
                             │ joblib.load()
                             ▼
                  ┌──────────────────────┐
                  │ crowdcast_model_v3   │  (Random Forest Pipeline)
                  └──────────────────────┘
```

1. **React Frontend**: A premium dark-themed dashboard presenting sliders and input controls for event context and market conditions. It sends raw snapshot parameters to the backend.
2. **FastAPI Backend**: Validates incoming requests, engineers the 9 derived features used during training, and performs fast inference using the loaded model.
3. **ML Model**: A pre-trained binary `RandomForestClassifier` pipeline serialized in a `.pkl` file.

---

## 🧠 Machine Learning Details

### ML Approach
The model uses marketplace snapshot attributes to predict whether ticket inventory will deplete rapidly. The target variable is derived by comparing consecutive snapshot intervals of events.

### Target Definition
- **Column**: `high_demand_next_snapshot`
- **Definition**:
  - `1` = High Demand (Next snapshot listing count decreased by **&ge; 25%**)
  - `0` = Normal Demand (Next snapshot listing count did not decrease by &ge; 25%)

### Dataset Description
- **Training Data**: `data/CrowdCast_ML_Dataset_V2.csv` (603 observations, cleaned of snapshot anomalies and sequences without a real subsequent snapshot).
- **Target Distribution**: ~62.5% Normal Demand vs. ~37.5% High Demand.

### Feature Engineering
Before predictions are run, the backend dynamically calculates the following 9 derived features from raw parameters:
- `listing_change_rate`
- `listing_ratio`
- `listing_pressure`
- `listings_per_section`
- `available_per_section`
- `listing_section_ratio`
- `deal_pressure`
- `event_urgency` (binned days: `Very_Immediate`, `Immediate`, `Near`, `Medium`, `Far`)
- `event_time_period` (binned event hour: `Night`, `Morning`, `Afternoon`, `Evening`, `Unknown`)

### Selected Model & Performance
The final model is a **Random Forest Classifier** selected for its strong F1 score and high recall for the high-demand class.

- **Accuracy**: 73.5%
- **Precision**: 57.1%
- **Recall**: 81.8%
- **F1 Score**: 67.3%
- **ROC-AUC**: 80.4%

---

## 🚀 Setup & Execution Instructions

### Prerequisites
- Python 3.10+
- Node.js 18+ (tested with v26)

---

### 1. Backend Setup & Run

Go to the backend folder or run from the root directory:

```bash
# Install python dependencies
pip install -r requirements.txt

# Start the FastAPI server on port 8000
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

The API docs will be available at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

---

### 2. Frontend Setup & Run

Go to the frontend folder:

```bash
cd frontend

# Install package dependencies
npm install

# Start the Vite React development server on port 5173
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) in your browser.

---

## 📡 API Reference

### Health Check
- **Endpoint**: `GET /health`
- **Response**:
  ```json
  {
    "status": "healthy",
    "model_loaded": true
  }
  ```

### Prediction
- **Endpoint**: `POST /predict`
- **Example Payload**:
  ```json
  {
    "days_until_event": 10.5,
    "event_hour": 19,
    "is_weekend": 1,
    "day_of_week": "Saturday",
    "city": "Dallas",
    "state": "TX",
    "metro": "dallas",
    "timezone": "America/Chicago",
    "addressCountryCode": "US",
    "listing_count": 120.0,
    "section_count": 8.0,
    "section_group_count": 4.0,
    "max_available_lot": 15.0,
    "avg_max_available_lot": 4.5,
    "deal_rate": 0.35,
    "ga_listing_rate": 0.85,
    "listing_count_prev": 150.0,
    "listing_change": -30.0,
    "latitude": 32.7767,
    "longitude": -96.7970
  }
  ```
- **Example Response**:
  ```json
  {
    "demand_probability": 0.6974198508600903,
    "prediction": 1,
    "risk_level": "HIGH"
  }
  ```

---

## 📊 Risk Level Definition
The `demand_probability` output from the Random Forest model is mapped into four user-friendly risk levels:
- **LOW**: Probability $< 30\%$
- **MODERATE**: $30\% \le \text{Probability} < 60\%$
- **HIGH**: $60\% \le \text{Probability} < 80\%$
- **CRITICAL**: $\text{Probability} \ge 80\%$
