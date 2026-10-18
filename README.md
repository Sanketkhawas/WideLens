# WideLens — Store expansion advisor for Nagpur, Maharashtra

Upload an Excel sheet of your customers → get a dashboard that says **which Nagpur locality should host your next store**,
with a customer heat-map, ranked sites, a robustness check, what-if sliders, a revenue forecast and a PDF report.

## Run it
```bash
python -m venv venv && venv\Scripts\activate        # Windows  (Linux/macOS: source venv/bin/activate)
pip install -r requirements.txt
python app.py                                       # http://127.0.0.1:5000
```
Register → **Upload data** → click *Use the Nagpur sample data* (or upload your own workbook).
Regenerate the sample workbook any time with `python training/generate_sample_data.py`.
Run the tests with `python -m pytest tests`.

## Excel format (`sample_data/WideLens_Nagpur_Sample.xlsx`)
| Sheet | Required | Columns |
|---|---|---|
| **Customers** | yes | `customer_id`, `total_spent` (+ `customer_name, age, gender, area, city, latitude, longitude, purchase_frequency`) |
| **Sales** | no | `customer_id`, `amount`, `sale_date` (+ `sale_id, product, quantity, payment_method`) → trend + forecast |
| **Stores** | no | `store_name`, `area` or `latitude`/`longitude` → your existing stores |
| **Areas** | no | `area`, `population`, `avg_rent` (₹/sq ft/month), `competitor_count` → override locality data |

Column names are matched flexibly (`lat`, `locality`, `spend`, …). Missing coordinates are filled from the locality; blank or
mis-typed localities are inferred from coordinates; duplicates and out-of-city rows are removed and reported in "Data quality notes".

## How the recommendation works
1. **Candidates** – 31 Nagpur localities (editable via the Areas sheet).
2. **Per candidate**, within the catchment radius (default 3 km): customers, spend, *unserved* spend (customers with no existing
   store within the radius), average spend, plus area competitors, rent and population.
3. **Score 0–100** = weighted sum of six min-max-normalised factors (demand 30 %, unserved demand 25 %, competition 15 %,
   spend 10 %, rent 10 %, population 10 %) × a cannibalisation factor for sites < 2.5 km from an existing store. All weights are sliders.
4. **Robustness** – 500 random re-weightings (Dirichlet around your weights); shows how often each site is #1 / top-3.
5. **Economics** – revenue = capture rate × catchment spend (unserved spend in full, already-served spend at 50 %), scaled by how much
   of real sales the file represents; profit = revenue × contribution margin − rent × size; payback = (fit-out + deposit) ÷ profit.
6. **Roadmap** – greedy: open the best viable site, count it as a store, repeat; stops when nothing pays back within 5 years.
7. **Forecast** – linear trend × month-of-year seasonality, with an 80 % band.
8. Customers are also segmented with k-means (Champions / Loyal / Occasional / At-risk).

## Honest limitations
* The sample file is **synthetic**; locality population, rent and competitor counts are **illustrative** — replace them via the Areas sheet
  with surveyed numbers (broker rent quotes, Google Maps competitor counts) before acting.
* Revenue / payback numbers are planning estimates driven by editable assumptions, not forecasts for a specific shop.
* Locality centroids are approximate; confirm real shop availability and footfall on the ground.
* Map tiles need internet access (OpenStreetMap); everything else is served locally.

## Layout
`app.py` · `routes/` (auth, upload, dashboard, api) · `services/` (preprocessing, analytics, prediction, recommendation, visualization, reports) ·
`templates/` · `static/` (css, js, vendored Leaflet + Chart.js) · `tests/` · `sample_data/`
