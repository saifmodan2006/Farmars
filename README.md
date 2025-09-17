# Farmars
# Farmer Deaths Dashboard

This project contains a Streamlit dashboard that visualizes synthetic data about farmer deaths (2000-2025) by causes such as suicide, malnutrition, poor crop growth, pesticide exposure, and others.

Files:
- `data/generate_data.py` - script to generate the synthetic dataset (`data/farmer_deaths.csv`).
- `app.py` - Streamlit app with interactive filters and multiple visualizations (year/month, cause breakdown, heatmap, map placeholder).
- `requirements.txt` - Python dependencies.

How to run (Windows PowerShell):

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -r requirements.txt
python data/generate_data.py
streamlit run app.py
```

Notes:
- The dataset is synthetic and created for demonstration. Replace with real data if available.
- For deployment, consider Streamlit Cloud, Heroku (with proper buildpack) or Docker.

## License

This project is licensed under the MIT License — see the `LICENSE` file in the project root for details.
