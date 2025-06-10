# Daily Average Traffic Calculator

This application processes traffic data from CSV files to calculate monthly daily average midweek traffic. It allows users to either upload a CSV file or paste the data directly.

## Features

- Upload CSV files or paste data directly
- Calculate monthly daily average midweek traffic
- Process data for each hour of the day
- Clean and modern user interface

## Setup

1. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python app.py
```

4. Open your browser and navigate to `http://localhost:5000`

## CSV Format Requirements

The CSV file should contain the following columns:
- Date/Time (in a format that can be parsed as datetime)
- Traffic count

Example format:
```
datetime,traffic_count
2024-01-01 00:00:00,100
2024-01-01 01:00:00,150
...
```

## How It Works

The application:
1. Accepts traffic data through file upload or direct paste
2. Processes the data to identify midweek days (Monday-Friday)
3. Calculates hourly averages for each day
4. Sums up the hourly averages to get the daily average
5. Presents the results in a clear, readable format 