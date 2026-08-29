from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from backend.schemas import PredictionRequest, PredictionResponse
from backend.model_service import model_service

app = FastAPI(
    title="CrowdCast API",
    description="FastAPI Backend for CrowdCast Event Demand / Overcrowding-Risk Predictions",
    version="1.0.0"
)

# Enable CORS for the local React development server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify local react ports or domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", status_code=status.HTTP_200_OK)
def health_check():
    """
    Readiness and health check endpoint.
    Verifies that the model is loaded and backend is healthy.
    """
    if model_service.model is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="ML Model is not loaded"
        )
    return {"status": "healthy", "model_loaded": True}

@app.post(
    "/predict",
    response_model=PredictionResponse,
    status_code=status.HTTP_200_OK
)
def predict_demand(request: PredictionRequest):
    """
    Prediction endpoint.
    Accepts raw event and market parameters, engineers features,
    runs the inference pipeline, and returns the demand risk.
    """
    try:
        prob, pred, risk = model_service.predict_risk(request)
        return PredictionResponse(
            demand_probability=prob,
            prediction=pred,
            risk_level=risk
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Inference error: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
