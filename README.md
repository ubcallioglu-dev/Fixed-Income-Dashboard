# Fixed Income Dashboard

A small Streamlit prototype for monitoring a USD investment-grade bond portfolio.

## Run locally

```bash
git clone https://github.com/ubcallioglu-dev/Fixed-Income-Dashboard.git
cd Fixed-Income-Dashboard
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Then open the local address Streamlit prints (normally http://localhost:8501).

## Try it

Use the **Parallel rate shock** slider in the sidebar. The dashboard immediately recalculates estimated rate-shock P&L and shifts the Treasury curve. The figures are illustrative sample data.
