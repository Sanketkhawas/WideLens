Write-Host "Creating AI Business Expansion Advisor Project Structure..."

# Root Folder
$root = "WideLens"

# Create Root
New-Item -ItemType Directory -Force -Path $root | Out-Null

# ==========================
# Root Files
# ==========================
New-Item "$root/app.py" -ItemType File
New-Item "$root/config.py" -ItemType File
New-Item "$root/requirements.txt" -ItemType File
New-Item "$root/README.md" -ItemType File
New-Item "$root/.env" -ItemType File

# ==========================
# Static
# ==========================
mkdir "$root/static/css" -Force | Out-Null
mkdir "$root/static/js" -Force | Out-Null
mkdir "$root/static/images" -Force | Out-Null
mkdir "$root/static/icons" -Force | Out-Null

New-Item "$root/static/css/style.css" -ItemType File
New-Item "$root/static/css/dashboard.css" -ItemType File

New-Item "$root/static/js/dashboard.js" -ItemType File
New-Item "$root/static/js/analytics.js" -ItemType File
New-Item "$root/static/js/maps.js" -ItemType File

# ==========================
# Templates
# ==========================
mkdir "$root/templates" -Force | Out-Null

@(
"index.html",
"login.html",
"register.html",
"dashboard.html",
"upload.html",
"customer_analytics.html",
"sales_analytics.html",
"recommendation.html",
"map.html",
"report.html",
"profile.html",
"admin.html"
) | ForEach-Object {
    New-Item "$root/templates/$_" -ItemType File
}

# ==========================
# Uploads
# ==========================
@(
"customers",
"sales",
"competitors",
"demographics",
"temp"
) | ForEach-Object {
    mkdir "$root/uploads/$_" -Force | Out-Null
}

# ==========================
# Processed Data
# ==========================
@(
"cleaned",
"engineered",
"geo",
"json"
) | ForEach-Object {
    mkdir "$root/processed_data/$_" -Force | Out-Null
}

# ==========================
# Database
# ==========================
mkdir "$root/database" -Force | Out-Null

@(
"database.py",
"models.py",
"schema.sql",
"business.db",
"seed.py"
) | ForEach-Object {
    New-Item "$root/database/$_" -ItemType File
}

# ==========================
# Routes
# ==========================
mkdir "$root/routes" -Force | Out-Null

@(
"auth_routes.py",
"dashboard_routes.py",
"upload_routes.py",
"customer_routes.py",
"sales_routes.py",
"recommendation_routes.py",
"map_routes.py",
"report_routes.py",
"admin_routes.py",
"api_routes.py"
) | ForEach-Object {
    New-Item "$root/routes/$_" -ItemType File
}

# ==========================
# Services
# ==========================
$services = @(
"preprocessing",
"analytics",
"prediction",
"recommendation",
"visualization",
"reports"
)

foreach ($folder in $services){
    mkdir "$root/services/$folder" -Force | Out-Null
}

# Preprocessing
@(
"data_cleaner.py",
"feature_engineering.py",
"geo_processing.py"
) | % {New-Item "$root/services/preprocessing/$_" -ItemType File}

# Analytics
@(
"customer_segmentation.py",
"sales_analysis.py",
"customer_statistics.py"
) | % {New-Item "$root/services/analytics/$_" -ItemType File}

# Prediction
@(
"revenue_prediction.py",
"sales_prediction.py"
) | % {New-Item "$root/services/prediction/$_" -ItemType File}

# Recommendation
@(
"location_ranker.py",
"recommendation_engine.py",
"business_insights.py"
) | % {New-Item "$root/services/recommendation/$_" -ItemType File}

# Visualization
@(
"heatmap.py",
"charts.py",
"map_generator.py"
) | % {New-Item "$root/services/visualization/$_" -ItemType File}

# Reports
@(
"pdf_generator.py",
"report_builder.py"
) | % {New-Item "$root/services/reports/$_" -ItemType File}

# ==========================
# Models
# ==========================
mkdir "$root/models" -Force | Out-Null

@(
"customer_segmentation.pkl",
"revenue_prediction.pkl",
"sales_prediction.pkl",
"scaler.pkl",
"encoder.pkl"
) | % {New-Item "$root/models/$_" -ItemType File}

# ==========================
# Training
# ==========================
mkdir "$root/training/datasets" -Force | Out-Null

@(
"customers.csv",
"sales.csv",
"competitors.csv",
"demographics.csv",
"locations.csv"
) | % {New-Item "$root/training/datasets/$_" -ItemType File}

@(
"train_segmentation.py",
"train_sales_prediction.py",
"train_revenue_prediction.py"
) | % {New-Item "$root/training/$_" -ItemType File}

# ==========================
# Utils
# ==========================
mkdir "$root/utils" -Force | Out-Null

@(
"helpers.py",
"validators.py",
"geo_utils.py",
"logger.py",
"charts.py",
"constants.py"
) | % {New-Item "$root/utils/$_" -ItemType File}

# ==========================
# Reports
# ==========================
mkdir "$root/reports/templates" -Force | Out-Null
mkdir "$root/reports/exported_reports" -Force | Out-Null

New-Item "$root/reports/report_generator.py" -ItemType File

# ==========================
# Sample Data
# ==========================
mkdir "$root/sample_data" -Force | Out-Null

@(
"sample_customers.csv",
"sample_sales.csv",
"sample_competitors.csv",
"sample_locations.csv",
"sample_demographics.csv"
) | % {New-Item "$root/sample_data/$_" -ItemType File}

# ==========================
# Tests
# ==========================
mkdir "$root/tests" -Force | Out-Null

@(
"test_auth.py",
"test_customer.py",
"test_sales.py",
"test_prediction.py",
"test_recommendation.py",
"test_api.py"
) | % {New-Item "$root/tests/$_" -ItemType File}

Write-Host ""
Write-Host "Project Structure Created Successfully!"
Write-Host "Location: $root"