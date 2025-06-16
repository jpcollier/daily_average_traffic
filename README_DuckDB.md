# Daily Average Traffic Calculator - DuckDB WebAssembly Edition

A modern, client-side web application for analyzing and calculating daily average traffic data using DuckDB WebAssembly. All processing happens in your browser - no server required!

## 🚀 Key Features

- **Powered by DuckDB WebAssembly** - Lightning-fast analytical database running in your browser
- **Client-side Processing** - No data leaves your computer, ensuring privacy and security
- **No Server Required** - Runs entirely in the browser as a static website
- **High Performance** - Can handle large CSV files efficiently
- **Offline Capable** - Works without internet connection after initial load

## 📊 Analysis Features

- Upload or paste traffic count data in CSV format
- **Flexible grouping options** - Analyze by month or collection period
- Calculate monthly daily average midweek traffic
- **Collection period analysis** - Group days within 6 days of each other
- **Multi-site support** - Analyze data from multiple count locations
- Option to exclude holiday/restriction periods
- Support for directional traffic analysis
- Handles data with or without direction information
- **Site selection** - Filter analysis to specific count locations
- Validates data coverage and formats
- Interactive web interface for data input and results display
- Real-time chart visualization with site-specific titles

## 🔧 Technical Advantages

### Compared to the Flask Version:
- **No Python dependencies** - Runs in any modern browser
- **No server costs** - Deploy to any static hosting service
- **Better performance** - DuckDB is optimized for analytical queries
- **Enhanced privacy** - All data processing happens locally
- **Improved scalability** - No server-side resource limitations

## 📁 Data Format

The application expects CSV data with the following columns:
- `datetime`: Date and time of traffic count (format: YYYY-MM-DD HH:MM:SS)
- `traffic_count`: Number of vehicles counted
- `direction` (optional): Direction of traffic flow
- `site` (optional): Site/location identifier for multi-site analysis
- `Coverage %` (optional): Data coverage percentage

Example CSV format:
```csv
datetime,traffic_count,direction,site,Coverage %
2023-01-01 00:00:00,100,Northbound,Site_A,100
2023-01-01 00:15:00,150,Southbound,Site_A,100
2023-01-01 00:00:00,75,Northbound,Site_B,100
2023-01-01 00:15:00,90,Southbound,Site_B,100
```

### Multi-Site Support

When your CSV contains data from multiple count locations:

1. **Map the Site Column**: Select the column that contains site/location identifiers
2. **Choose Analysis Scope**: 
   - Select "(All sites)" to analyze combined data from all locations
   - Select a specific site to analyze only that location's data
3. **Site Information**: The interface shows how many unique sites are detected
4. **Results Display**: Charts and tables will indicate which site was analyzed

## 🚀 Deployment

### Static Hosting (Recommended)
This application can be deployed to any static hosting service:

1. **Vercel** (recommended):
   ```bash
   # Use the provided vercel_duckdb.json configuration
   vercel --prod
   ```

2. **Netlify**:
   - Simply drag and drop the `index_duckdb.html` file to Netlify

3. **GitHub Pages**:
   - Rename `index_duckdb.html` to `index.html`
   - Push to a GitHub repository
   - Enable GitHub Pages

4. **AWS S3 + CloudFront**:
   - Upload the HTML file to an S3 bucket
   - Configure static website hosting

### Local Development
1. Open `index_duckdb.html` directly in a modern web browser
2. Or serve with any local web server:
   ```bash
   # Python
   python -m http.server 8000
   
   # Node.js
   npx serve .
   
   # PHP
   php -S localhost:8000
   ```

## 📖 Usage

### Basic Workflow

1. **Load Data**: Upload a CSV file or paste CSV data
2. **Map Columns**: Select which columns contain datetime, traffic count, direction, and site information
3. **Configure Analysis**: 
   - Choose whether to aggregate directions and exclude holidays
   - **Select grouping method**: Monthly or Collection Period analysis
4. **Select Site** (if applicable): Choose a specific site or analyze all sites combined
5. **Process**: Click "Process Data" to run the analysis
6. **View Results**: Review the calculated averages and visualizations

### Grouping Methods

#### Monthly Analysis
- Traditional approach grouping data by calendar month
- Useful for seasonal trends and year-over-year comparisons
- Results display as "Jan '24", "Feb '24", etc.

#### Collection Period Analysis  
- **Innovative approach** for traffic data collection campaigns
- Automatically detects collection periods where days are within 6 days of each other
- **Per-site calculation**: Each site's collection periods are calculated independently
- Ideal for discontinuous data collection scenarios
- Results display as "Site_A - Period 1 (Jan 2, 2024)", "Site_A - Period 2 (Jan 16, 2024)", etc.

**When to use Collection Period Analysis:**
- Data collected in separate campaigns/phases
- Irregular data collection schedules  
- Wanting to compare specific collection efforts within sites
- Data has natural gaps of more than 6 days
- Multi-site studies with different collection schedules per site

### Multi-Site Analysis

When working with data from multiple count locations:

#### Step 1: Upload Multi-Site Data
- Ensure your CSV includes a column identifying different sites/locations
- Common column names: `site`, `location`, `station`, `point`

#### Step 2: Map the Site Column
- The application will try to auto-detect site columns
- Manually select the appropriate column if needed
- The site selector will appear showing available sites

#### Step 3: Choose Analysis Scope
- **"(All sites)"**: Combines data from all locations for overall analysis
- **Specific Site**: Analyzes only the selected location's traffic data

#### Step 4: Review Results
- Table headers and chart titles will indicate which site was analyzed
- Results show daily averages specific to your selection

### Example Multi-Site Scenarios

1. **Regional Analysis**: Compare traffic between different highway segments
2. **Urban Planning**: Analyze traffic at multiple intersections
3. **Temporal Studies**: Track changes at various monitoring stations
4. **Network Assessment**: Evaluate traffic flow across multiple points

## 🌐 Browser Requirements

- Modern browsers with WebAssembly support (Chrome 57+, Firefox 52+, Safari 11+, Edge 16+)
- ES6 modules support
- File API support for drag & drop

## 🔄 Migration from Flask Version

The DuckDB version provides the same functionality as the original Flask application:

1. **Same calculation logic** - Identical results for traffic analysis
2. **Same UI/UX** - Familiar interface with DuckDB branding
3. **Same holiday exclusions** - Built-in restriction dates from 2023-2025
4. **Enhanced performance** - Faster processing with DuckDB
5. **Better reliability** - No server-side dependencies

## 🛠️ How It Works

1. **DuckDB Initialization**: Loads DuckDB WebAssembly engine in the browser
2. **Data Import**: Creates in-memory table from uploaded CSV data
3. **Data Processing**: Uses SQL queries to filter and aggregate data
4. **Analysis**: Calculates daily averages using the same logic as the Flask version
5. **Visualization**: Displays results in interactive charts and tables

## 📊 Calculation Method

The application follows these steps using DuckDB SQL:

1. Data is filtered to include only **Tuesday, Wednesday, and Thursday** (midweek days)
2. If the "Coverage %" column exists, only records with 100% coverage are included
3. If "Exclude holidays/restriction dates" is checked, dates within holiday/restriction periods are excluded
4. If direction data is present and "Aggregate all directions" is checked, traffic counts are summed across all directions
5. For each month (and direction, if not aggregating):
   - Data is grouped by hour (0-23)
   - For each hour, the mean traffic count is calculated
   - The daily average is the sum of these hourly means
   - The standard error (SE) is calculated as: √(sum of (variance/count) for each hour)

## 🔒 Privacy & Security

- **Complete Privacy**: All data processing happens in your browser
- **No Data Upload**: CSV files are processed locally, never sent to servers
- **No Dependencies**: No external data processing services
- **GDPR Compliant**: No data collection or storage

## 📈 Performance

DuckDB WebAssembly provides excellent performance for analytical workloads:
- **Fast CSV parsing** - Optimized CSV reader
- **Efficient aggregations** - Columnar processing
- **Memory efficient** - Minimal memory footprint
- **Scalable** - Can handle datasets with millions of rows

## 🆚 Comparison with Original Flask Version

| Feature | Flask Version | DuckDB Version |
|---------|---------------|----------------|
| **Deployment** | Requires Python server | Static hosting |
| **Dependencies** | pandas, numpy, Flask | None (browser only) |
| **Performance** | Limited by server resources | Client CPU/memory |
| **Privacy** | Data sent to server | Data stays local |
| **Offline** | No | Yes (after initial load) |
| **Scalability** | Server-dependent | Client-dependent |
| **Cost** | Server hosting costs | Free static hosting |

## 🤝 Contributing

1. Fork the repository
2. Make your changes to `index_duckdb.html`
3. Test locally in a browser
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **DuckDB** - For the excellent WebAssembly implementation
- **Chart.js** - For beautiful data visualization
- **Bootstrap** - For responsive UI components
