"""
Database Log Viewer

This module provides functionality to view and analyze prediction logs
stored in the SQLite database. It displays recent predictions with
timestamps and relevant metadata.

Usage:
    python logs/view_logs.py
    
Features:
    - View recent predictions
    - Filter by date range
    - Export logs to CSV
    - Summary statistics
"""

import sqlite3
import pandas as pd
import argparse
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class PredictionLogViewer:
    """
    A utility class for viewing and analyzing prediction logs from the database.
    
    This class provides methods to query, filter, and display prediction logs
    with various formatting and export options.
    """
    
    def __init__(self, db_path: str = "predictions.db"):
        """
        Initialize the log viewer with database connection.
        
        Args:
            db_path: Path to the SQLite database file
            
        Raises:
            FileNotFoundError: If database file doesn't exist
        """
        self.db_path = db_path
        if not os.path.exists(db_path):
            raise FileNotFoundError(f"Database file not found: {db_path}")
        
        self.conn = None
    
    def connect(self) -> None:
        """Establish database connection."""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row  # Enable column access by name
            print(f"Connected to database: {self.db_path}")
        except sqlite3.Error as e:
            print(f"Error connecting to database: {e}")
            raise
    
    def disconnect(self) -> None:
        """Close database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None
            print("Database connection closed")
    
    def view_recent_predictions(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        View the most recent predictions from the database.
        
        Args:
            limit: Maximum number of predictions to retrieve
            
        Returns:
            List of prediction records as dictionaries
        """
        try:
            cursor = self.conn.cursor()
            
            query = """
            SELECT * FROM predictions 
            ORDER BY timestamp DESC 
            LIMIT ?
            """
            
            cursor.execute(query, (limit,))
            rows = cursor.fetchall()
            
            # Convert rows to list of dictionaries
            predictions = []
            for row in rows:
                prediction = {
                    'id': row['id'],
                    'timestamp': row['timestamp'],
                    'vehicle_age': row.get('vehicle_age', 'N/A'),
                    'mileage': row.get('mileage', 'N/A'),
                    'predicted_price': row.get('predicted_price', 'N/A'),
                    'confidence_score': row.get('confidence_score', 'N/A')
                }
                predictions.append(prediction)
            
            return predictions
            
        except sqlite3.Error as e:
            print(f"Error querying database: {e}")
            return []
    
    def view_predictions_by_date(
        self, 
        start_date: Optional[str] = None, 
        end_date: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        View predictions filtered by date range.
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            
        Returns:
            List of filtered prediction records
        """
        try:
            cursor = self.conn.cursor()
            
            # Build query with date filters
            query = "SELECT * FROM predictions WHERE 1=1"
            params = []
            
            if start_date:
                query += " AND date(timestamp) >= ?"
                params.append(start_date)
            
            if end_date:
                query += " AND date(timestamp) <= ?"
                params.append(end_date)
            
            query += " ORDER BY timestamp DESC"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            # Convert to list of dictionaries
            predictions = []
            for row in rows:
                prediction = dict(row)
                predictions.append(prediction)
            
            return predictions
            
        except sqlite3.Error as e:
            print(f"Error querying database: {e}")
            return []
    
    def get_summary_statistics(self) -> Dict[str, Any]:
        """
        Get summary statistics for all predictions.
        
        Returns:
            Dictionary containing summary statistics
        """
        try:
            cursor = self.conn.cursor()
            
            # Get basic counts and statistics
            stats_query = """
            SELECT 
                COUNT(*) as total_predictions,
                AVG(predicted_price) as avg_price,
                MIN(predicted_price) as min_price,
                MAX(predicted_price) as max_price,
                MIN(timestamp) as earliest_prediction,
                MAX(timestamp) as latest_prediction
            FROM predictions
            WHERE predicted_price IS NOT NULL
            """
            
            cursor.execute(stats_query)
            stats = cursor.fetchone()
            
            # Get predictions by date (last 7 days)
            daily_query = """
            SELECT 
                date(timestamp) as prediction_date,
                COUNT(*) as count
            FROM predictions
            WHERE timestamp >= datetime('now', '-7 days')
            GROUP BY date(timestamp)
            ORDER BY prediction_date DESC
            """
            
            cursor.execute(daily_query)
            daily_stats = cursor.fetchall()
            
            return {
                'total_predictions': stats['total_predictions'],
                'average_price': round(stats['avg_price'], 2) if stats['avg_price'] else 0,
                'min_price': stats['min_price'],
                'max_price': stats['max_price'],
                'earliest_prediction': stats['earliest_prediction'],
                'latest_prediction': stats['latest_prediction'],
                'daily_counts': [dict(row) for row in daily_stats]
            }
            
        except sqlite3.Error as e:
            print(f"Error getting statistics: {e}")
            return {}
    
    def export_to_csv(self, output_file: str, limit: Optional[int] = None) -> bool:
        """
        Export predictions to CSV file.
        
        Args:
            output_file: Path for the output CSV file
            limit: Maximum number of records to export
            
        Returns:
            True if export successful, False otherwise
        """
        try:
            # Get predictions
            if limit:
                predictions = self.view_recent_predictions(limit)
            else:
                predictions = self.view_predictions_by_date()
            
            if not predictions:
                print("No predictions to export")
                return False
            
            # Convert to DataFrame and export
            df = pd.DataFrame(predictions)
            df.to_csv(output_file, index=False)
            
            print(f"Exported {len(predictions)} predictions to {output_file}")
            return True
            
        except Exception as e:
            print(f"Error exporting to CSV: {e}")
            return False
    
    def display_predictions(self, predictions: List[Dict[str, Any]]) -> None:
        """
        Display predictions in a formatted table.
        
        Args:
            predictions: List of prediction dictionaries to display
        """
        if not predictions:
            print("No predictions found")
            return
        
        print(f"\n{'='*80}")
        print(f"{'PREDICTION LOGS':^80}")
        print(f"{'='*80}")
        
        # Table header
        header = f"{'ID':<6} {'Timestamp':<20} {'Age':<4} {'Mileage':<8} {'Price':<10} {'Confidence':<10}"
        print(header)
        print("-" * len(header))
        
        # Table rows
        for pred in predictions:
            timestamp = pred['timestamp'][:19] if pred['timestamp'] else 'N/A'
            age = str(pred['vehicle_age']) if pred['vehicle_age'] != 'N/A' else 'N/A'
            mileage = f"{pred['mileage']:,}" if pred['mileage'] != 'N/A' else 'N/A'
            price = f"${pred['predicted_price']:,.2f}" if pred['predicted_price'] != 'N/A' else 'N/A'
            confidence = f"{pred['confidence_score']:.3f}" if pred['confidence_score'] != 'N/A' else 'N/A'
            
            row = f"{pred['id']:<6} {timestamp:<20} {age:<4} {mileage:<8} {price:<10} {confidence:<10}"
            print(row)
        
        print(f"\nTotal records displayed: {len(predictions)}")
    
    def display_summary(self, stats: Dict[str, Any]) -> None:
        """
        Display summary statistics in a formatted way.
        
        Args:
            stats: Dictionary containing summary statistics
        """
        if not stats:
            print("No statistics available")
            return
        
        print(f"\n{'='*50}")
        print(f"{'PREDICTION SUMMARY':^50}")
        print(f"{'='*50}")
        
        print(f"Total Predictions: {stats['total_predictions']:,}")
        print(f"Average Price: ${stats['average_price']:,.2f}")
        print(f"Price Range: ${stats['min_price']:,.2f} - ${stats['max_price']:,.2f}")
        print(f"Date Range: {stats['earliest_prediction']} to {stats['latest_prediction']}")
        
        if stats['daily_counts']:
            print(f"\nDaily Activity (Last 7 Days):")
            for day in stats['daily_counts']:
                print(f"  {day['prediction_date']}: {day['count']} predictions")


def main():
    """
    Main function to handle command line interface for the log viewer.
    
    Supports various command line options for filtering and displaying logs.
    """
    parser = argparse.ArgumentParser(description="View vehicle price prediction logs")
    
    parser.add_argument(
        "--limit", 
        type=int, 
        default=20, 
        help="Maximum number of predictions to display (default: 20)"
    )
    
    parser.add_argument(
        "--start-date", 
        type=str, 
        help="Start date for filtering (YYYY-MM-DD format)"
    )
    
    parser.add_argument(
        "--end-date", 
        type=str, 
        help="End date for filtering (YYYY-MM-DD format)"
    )
    
    parser.add_argument(
        "--export", 
        type=str, 
        help="Export results to CSV file"
    )
    
    parser.add_argument(
        "--summary", 
        action="store_true", 
        help="Display summary statistics"
    )
    
    parser.add_argument(
        "--db-path", 
        type=str, 
        default="predictions.db", 
        help="Path to database file (default: predictions.db)"
    )
    
    args = parser.parse_args()
    
    # Initialize log viewer
    try:
        viewer = PredictionLogViewer(args.db_path)
        viewer.connect()
        
        # Display summary if requested
        if args.summary:
            stats = viewer.get_summary_statistics()
            viewer.display_summary(stats)
        
        # Get predictions based on filters
        if args.start_date or args.end_date:
            predictions = viewer.view_predictions_by_date(args.start_date, args.end_date)
        else:
            predictions = viewer.view_recent_predictions(args.limit)
        
        # Display predictions
        viewer.display_predictions(predictions)
        
        # Export if requested
        if args.export:
            viewer.export_to_csv(args.export, args.limit if not (args.start_date or args.end_date) else None)
        
    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        if 'viewer' in locals():
            viewer.disconnect()


if __name__ == "__main__":
    main()