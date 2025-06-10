from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
from io import StringIO
from datetime import datetime, timedelta
import json
import traceback
import logging
import os
import sys

# Set up logging to stdout for serverless environment
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stdout  # Log to stdout instead of file
)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50 MB upload limit
app.config['JSON_SORT_KEYS'] = False  # Maintain JSON order

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NumpyEncoder, self).default(obj)

app.json_encoder = NumpyEncoder

def load_restriction_dates():
    try:
        # Load holiday restriction periods and build a set of restricted dates
        csv_path = os.path.join(os.path.dirname(__file__), 'Traffic_Data_Collection_Holidays_2023-2025.csv')
        logging.info(f"Loading restrictions from: {csv_path}")
        restriction_periods = []
        
        if os.path.exists(csv_path):
            holidays_df = pd.read_csv(csv_path)
            for _, row in holidays_df.iterrows():
                start = pd.to_datetime(row['Beginning of Restriction']).date()
                end = pd.to_datetime(row['End of Restriction']).date()
                restriction_periods.extend(pd.date_range(start, end).date)
        else:
            logging.warning(f"Restrictions file not found at {csv_path}, using hardcoded dates")
            # Hardcoded fallback (2023-2026, as provided)
            ranges = [
                (datetime(2022,12,30).date(), datetime(2023,1,1).date()),
                (datetime(2023,1,16).date(), datetime(2023,1,16).date()),
                (datetime(2023,2,20).date(), datetime(2023,2,20).date()),
                (datetime(2023,5,26).date(), datetime(2023,5,30).date()),
                (datetime(2023,6,19).date(), datetime(2023,6,19).date()),
                (datetime(2023,6,30).date(), datetime(2023,7,7).date()),
                (datetime(2023,9,1).date(), datetime(2023,9,8).date()),
                (datetime(2023,10,9).date(), datetime(2023,10,9).date()),
                (datetime(2023,11,20).date(), datetime(2023,11,27).date()),
                (datetime(2023,12,22).date(), datetime(2023,12,29).date()),
                (datetime(2023,12,29).date(), datetime(2024,1,1).date()),
                (datetime(2024,1,15).date(), datetime(2024,1,15).date()),
                (datetime(2024,2,19).date(), datetime(2024,2,19).date()),
                (datetime(2024,5,24).date(), datetime(2024,5,28).date()),
                (datetime(2024,6,19).date(), datetime(2024,6,19).date()),
                (datetime(2024,7,1).date(), datetime(2024,7,7).date()),
                (datetime(2024,8,30).date(), datetime(2024,9,6).date()),
                (datetime(2024,10,14).date(), datetime(2024,10,14).date()),
                (datetime(2024,11,11).date(), datetime(2024,11,11).date()),
                (datetime(2024,11,25).date(), datetime(2024,12,2).date()),
                (datetime(2024,12,20).date(), datetime(2024,12,27).date()),
                (datetime(2024,12,27).date(), datetime(2025,1,5).date()),
                (datetime(2025,1,20).date(), datetime(2025,1,20).date()),
                (datetime(2025,2,17).date(), datetime(2025,2,17).date()),
                (datetime(2025,5,23).date(), datetime(2025,5,27).date()),
                (datetime(2025,6,19).date(), datetime(2025,6,20).date()),
                (datetime(2025,7,3).date(), datetime(2025,7,6).date()),
                (datetime(2025,8,29).date(), datetime(2025,9,5).date()),
                (datetime(2025,10,13).date(), datetime(2025,10,13).date()),
                (datetime(2025,11,11).date(), datetime(2025,11,11).date()),
                (datetime(2025,11,24).date(), datetime(2025,12,1).date()),
                (datetime(2025,12,20).date(), datetime(2025,12,26).date()),
                (datetime(2025,12,26).date(), datetime(2026,1,4).date()),
            ]
            for start, end in ranges:
                restriction_periods.extend(pd.date_range(start, end).date)
        restriction_dates = set(restriction_periods)
        return restriction_dates
    except Exception as e:
        logging.error(f"Error loading restriction dates: {str(e)}")
        logging.error(traceback.format_exc())
        raise

def process_traffic_data(df, aggregate_directions=True, midweek_days=None, exclude_holidays=True):
    """Process traffic data to calculate monthly daily average midweek traffic.
    Matches external script logic with hardcoded Tuesday, Wednesday, Thursday (1,2,3).
    Optionally excludes holiday/restriction dates if exclude_holidays is True.
    Can process data with or without direction aggregation.
    """
    try:
        logging.info(f"Starting data processing (aggregate_directions={aggregate_directions}, exclude_holidays={exclude_holidays})")
        logging.debug(f"Input DataFrame shape: {df.shape}")
        
        # Convert datetime column to datetime type if it's not already
        df['datetime'] = pd.to_datetime(df['datetime'])
        logging.debug("Datetime conversion successful")
        
        # Filter to only rows with 100% coverage if column exists (matching external script)
        if 'Coverage %' in df.columns:
            df = df[df['Coverage %'] == 100]
            logging.debug(f"Filtered to 100% coverage, shape: {df.shape}")
        
        # Add date and day of week columns (0 = Monday, 6 = Sunday)
        df['date'] = df['datetime'].dt.date
        df['day_of_week'] = df['datetime'].dt.dayofweek
        
        # Handle holiday/restriction dates if requested
        excluded_dates = []
        if exclude_holidays:
            restriction_dates = load_restriction_dates()
            excluded_dates = sorted(list(restriction_dates))
            df = df[~df['date'].isin(restriction_dates)]
            logging.debug(f"Filtered out holiday dates, shape: {df.shape}")
        
        # Hardcode midweek days to Tuesday, Wednesday, Thursday (1,2,3) to match external script
        midweek_days = [1, 2, 3]  # Tuesday, Wednesday, Thursday
        midweek_data = df[df['day_of_week'].isin(midweek_days)].copy()
        logging.debug(f"Midweek data shape: {midweek_data.shape}")
        
        if len(midweek_data) == 0:
            raise ValueError("No midweek days found in the data.")
        
        # Add hour column
        midweek_data['hour'] = midweek_data['datetime'].dt.hour
        
        results = []
        
        # Handle direction aggregation based on user choice
        if 'direction' in midweek_data.columns:
            if aggregate_directions:
                # Sum across directions
                midweek_data = midweek_data.groupby(['datetime', 'hour', 'date'], as_index=False)['traffic_count'].sum()
                # Group by month and hour
                grouped = midweek_data.groupby([
                    midweek_data['datetime'].dt.to_period('M'),
                    'hour'
                ])['traffic_count']
                
                hourly_stats = grouped.agg(['mean', 'var', 'count']).reset_index()
                hourly_stats.rename(columns={'datetime': 'period'}, inplace=True)
                
                # Calculate daily averages for each month
                for period, group_stats in hourly_stats.groupby('period'):
                    daily_avg = float(group_stats['mean'].sum())
                    se = float(np.sqrt((group_stats['var'] / group_stats['count']).fillna(0).sum()))
                    # Format month as "Jan '24"
                    month_name = f"{period.strftime('%b')} '{period.strftime('%y')}"
                    
                    results.append({
                        'month': month_name,
                        'daily_average': round(daily_avg),
                        'se': round(se),
                        'period': str(period)
                    })
            else:
                # Process each direction separately
                grouped = midweek_data.groupby([
                    midweek_data['datetime'].dt.to_period('M'),
                    'direction',
                    'hour'
                ])['traffic_count']
                
                hourly_stats = grouped.agg(['mean', 'var', 'count']).reset_index()
                hourly_stats.rename(columns={'datetime': 'period'}, inplace=True)
                
                # Calculate daily averages for each month and direction
                for (period, direction), group_stats in hourly_stats.groupby(['period', 'direction']):
                    daily_avg = float(group_stats['mean'].sum())
                    se = float(np.sqrt((group_stats['var'] / group_stats['count']).fillna(0).sum()))
                    # Format month as "Jan '24"
                    month_name = f"{period.strftime('%b')} '{period.strftime('%y')}"
                    
                    results.append({
                        'month': month_name,
                        'direction': direction,
                        'daily_average': round(daily_avg),
                        'se': round(se),
                        'period': str(period)
                    })
        else:
            # No direction column, process as single stream
            grouped = midweek_data.groupby([
                midweek_data['datetime'].dt.to_period('M'),
                'hour'
            ])['traffic_count']
            
            hourly_stats = grouped.agg(['mean', 'var', 'count']).reset_index()
            hourly_stats.rename(columns={'datetime': 'period'}, inplace=True)
            
            # Calculate daily averages for each month
            for period, group_stats in hourly_stats.groupby('period'):
                daily_avg = float(group_stats['mean'].sum())
                se = float(np.sqrt((group_stats['var'] / group_stats['count']).fillna(0).sum()))
                # Format month as "Jan '24"
                month_name = f"{period.strftime('%b')} '{period.strftime('%y')}"
                
                results.append({
                    'month': month_name,
                    'daily_average': round(daily_avg),
                    'se': round(se),
                    'period': str(period)
                })
        
        logging.info("Data processing completed successfully")
        return results, [d.strftime('%Y-%m-%d') for d in excluded_dates]
        
    except Exception as e:
        logging.error(f"Error in process_traffic_data: {str(e)}")
        logging.error(traceback.format_exc())
        raise

@app.route('/')
def index():
    try:
        return render_template('index.html')
    except Exception as e:
        logging.error(f"Error rendering index: {str(e)}")
        logging.error(traceback.format_exc())
        return jsonify({'error': 'Error rendering template'}), 500

@app.route('/process-data', methods=['POST'])
def process_data():
    try:
        logging.info("Received data processing request")
        aggregate_directions = request.form.get('aggregate_directions', '1') == '1'
        exclude_holidays = request.form.get('exclude_holidays', '1') == '1'
        
        # Get column mapping from form
        datetime_col = request.form.get('datetime_col', 'datetime')
        count_col = request.form.get('count_col', 'traffic_count')
        direction_col = request.form.get('direction_col', '')
        # Hardcode midweek days to Tuesday, Wednesday, Thursday (1, 2, 3)
        midweek_days = [1, 2, 3]
        
        if 'file' in request.files:
            # Handle file upload
            file = request.files['file']
            if file.filename == '':
                logging.error("No file selected")
                return jsonify({'error': 'No file selected'}), 400
            # Read the file content
            content = file.read().decode('utf-8')
            logging.debug(f"File content preview: {content[:200]}")
            df = pd.read_csv(StringIO(content))
        else:
            # Handle pasted data
            data = request.form.get('data')
            if not data:
                logging.error("No data provided")
                return jsonify({'error': 'No data provided'}), 400
            logging.debug(f"Pasted data preview: {data[:200]}")
            df = pd.read_csv(StringIO(data))
        
        # Log DataFrame info
        logging.info("\nDataFrame Info:")
        buffer = StringIO()
        df.info(buf=buffer)
        logging.info(buffer.getvalue())
        logging.info(f"\nFirst few rows:\n{df.head()}")
        
        # Rename columns based on mapping
        rename_map = {datetime_col: 'datetime', count_col: 'traffic_count'}
        if direction_col:
            rename_map[direction_col] = 'direction'
        df = df.rename(columns=rename_map)
        
        # Validate required columns
        required_columns = ['datetime', 'traffic_count']
        if not all(col in df.columns for col in required_columns):
            missing_cols = [col for col in required_columns if col not in df.columns]
            logging.error(f"Missing required columns: {missing_cols}")
            return jsonify({'error': f'Missing required columns: {', '.join(missing_cols)}'}), 400
        
        # Validate data types
        try:
            pd.to_datetime(df['datetime'])
            logging.debug("Datetime validation successful")
        except Exception as e:
            logging.error(f"Invalid datetime format: {str(e)}")
            return jsonify({'error': f'Invalid datetime format: {str(e)}'}), 400
        
        try:
            df['traffic_count'] = pd.to_numeric(df['traffic_count'])
            logging.debug("Traffic count validation successful")
        except Exception as e:
            logging.error(f"Invalid traffic_count format: {str(e)}")
            return jsonify({'error': f'Invalid traffic_count format: {str(e)}'}), 400
        
        # Process the data
        results, excluded_dates = process_traffic_data(df, aggregate_directions, midweek_days, exclude_holidays)
        logging.info(f"Processing completed successfully. Results: {results}")
        return jsonify({'results': results, 'excluded_dates': excluded_dates})
        
    except Exception as e:
        error_msg = f"Error processing data: {str(e)}\n{traceback.format_exc()}"
        logging.error(error_msg)
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

# Error handlers
@app.errorhandler(500)
def internal_error(error):
    logging.error(f"500 error: {str(error)}")
    logging.error(traceback.format_exc())
    return jsonify({'error': 'Internal server error', 'details': str(error)}), 500

@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'error': 'Not found'}), 404

# Remove the if __name__ == '__main__' block since we're using serverless
# The app will be imported and used by the Vercel handler 