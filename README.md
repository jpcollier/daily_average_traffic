# Daily Average Traffic Analysis

A Flask web application for analyzing and calculating daily average traffic data, with support for holiday exclusions and directional analysis.

## Features

- Upload or paste traffic count data in CSV format
- Calculate monthly daily average midweek traffic
- Option to exclude holiday/restriction periods
- Support for directional traffic analysis
- Handles data with or without direction information
- Validates data coverage and formats
- Interactive web interface for data input and results display

## Prerequisites

- Python 3.9 or higher
- pip (Python package installer)
- Virtual environment (recommended)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/jpcollier/daily_average_traffic.git
cd daily_average_traffic
```

2. Create and activate a virtual environment:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the Flask application:
```bash
python -m flask run
```

2. Open your web browser and navigate to `http://localhost:5000`

3. Input your traffic data either by:
   - Uploading a CSV file
   - Pasting CSV data directly into the text area

4. Configure your analysis:
   - Choose whether to aggregate directions
   - Select whether to exclude holiday periods
   - Map your CSV columns to the required fields

5. View the results:
   - Monthly daily averages
   - Standard errors
   - Excluded dates (if holiday exclusion is enabled)

## Data Format

The application expects CSV data with the following columns:
- `datetime`: Date and time of traffic count (format: YYYY-MM-DD HH:MM:SS)
- `traffic_count`: Number of vehicles counted
- `direction` (optional): Direction of traffic flow
- `Coverage %` (optional): Data coverage percentage

Example CSV format:
```csv
datetime,traffic_count,direction,Coverage %
2023-01-01 00:00:00,100,Northbound,100
2023-01-01 00:15:00,150,Southbound,100
```

## Holiday/Restriction Periods

The application includes a predefined list of holiday and restriction periods from 2023-2025. These dates are automatically excluded from calculations when the "Exclude Holidays" option is enabled.

## Development

The application is built using:
- Flask 2.3.3
- pandas 2.0.3
- numpy 1.24.3
- Other dependencies listed in `requirements.txt`

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Contact

For questions or support, please open an issue in the GitHub repository. 