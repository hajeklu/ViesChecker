#!/usr/bin/env python3
"""
VIES API Checker - Advanced monitoring for EU VIES API
Measures availability, response time and VAT number validation
"""

import json
import time
import requests
from datetime import datetime
import os
import subprocess
import sys
from typing import Dict, List, Any

class VIESChecker:
    def __init__(self, config_file: str = "config.json"):
        """Initialize VIES checker"""
        self.config = self.load_config(config_file)
        self.results_file = "results.json"
        self.measurements = self.load_measurements()  # All measurements
        self.results = []  # Will be populated with current measurements
        
        # Load existing results to continue from where we left off
        self.load_existing_results()
        
        # Session with optimized settings for API
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'VIES-Checker/1.0',
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip, deflate'
        })
    
    def load_config(self, config_file: str) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Error: Configuration file {config_file} not found!")
            sys.exit(1)
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in {config_file}")
            sys.exit(1)
    
    def load_measurements(self) -> List[Dict[str, Any]]:
        """Load existing measurements from measurements.json"""
        measurements_file = "measurements.json"
        if os.path.exists(measurements_file):
            try:
                with open(measurements_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return []
        return []
    
    def load_existing_results(self) -> None:
        """Load existing results from results.json to continue from where we left off"""
        if os.path.exists(self.results_file):
            try:
                with open(self.results_file, 'r', encoding='utf-8') as f:
                    existing_results = json.load(f)
                
                # If we have existing results, we need to reconstruct measurements
                # from the last_10_values to continue the sequence
                if existing_results.get('last_10_values'):
                    # Clear current measurements and load from results
                    self.measurements = []
                    
                    # Reconstruct measurements from last_10_values
                    for value in existing_results['last_10_values']:
                        measurement = {
                            "timestamp": value['timestamp'] + ".000000",  # Add microseconds back
                            "name": "VIES API",
                            "url": "https://ec.europa.eu/taxation_customs/vies/rest-api/ms/CZ/vat/CZ26185610",
                            "status_code": 200 if value['success'] else None,
                            "response_time_ms": value['response_time_ms'],
                            "success": value['success'],
                            "error": None if value['success'] else "Previous error"
                        }
                        self.measurements.append(measurement)
                    
                    print(f"📊 Loaded {len(self.measurements)} measurements from existing results")
                    
            except (json.JSONDecodeError, FileNotFoundError, KeyError) as e:
                print(f"⚠️  Could not load existing results: {e}")
                # Continue with empty measurements
    
    def check_vies_api(self, url_config: Dict[str, Any]) -> Dict[str, Any]:
        """Check VIES API focusing on response time and success/fail"""
        name = url_config['name']
        url = url_config['url']
        timeout = url_config.get('timeout', 15)
        expected_status = url_config.get('expected_status', 200)
        expected_content = url_config.get('expected_content', 'isValid')
        description = url_config.get('description', '')
        
        start_time = time.time()
        timestamp = datetime.now().isoformat()
        
        try:
            # Simple measurement focused on response time
            response = self.session.get(url, timeout=timeout)
            response_time = round((time.time() - start_time) * 1000, 2)
            
            # Basic success check
            status_check = response.status_code == expected_status
            content_check = expected_content in response.text if expected_content else True
            success = status_check and content_check
            
            # Simple result structure
            result = {
                "timestamp": timestamp,
                "name": name,
                "url": url,
                "status_code": response.status_code,
                "response_time_ms": response_time,
                "success": success,
                "error": None
            }
            
            # Simple output focused on time and success
            status_icon = "✅" if success else "❌"
            print(f"{status_icon} {name}: {response.status_code} ({response_time}ms)")
            
        except requests.exceptions.Timeout:
            timeout_time = round((time.time() - start_time) * 1000, 2)
            result = {
                "timestamp": timestamp,
                "name": name,
                "url": url,
                "status_code": None,
                "response_time_ms": timeout_time,
                "success": False,
                "error": "Timeout"
            }
            print(f"⏰ {name}: Timeout after {timeout_time}ms")
            
        except requests.exceptions.ConnectionError:
            connection_time = round((time.time() - start_time) * 1000, 2)
            result = {
                "timestamp": timestamp,
                "name": name,
                "url": url,
                "status_code": None,
                "response_time_ms": connection_time,
                "success": False,
                "error": "Connection Error"
            }
            print(f"🔌 {name}: Connection Error after {connection_time}ms")
            
        except Exception as e:
            error_time = round((time.time() - start_time) * 1000, 2)
            result = {
                "timestamp": timestamp,
                "name": name,
                "url": url,
                "status_code": None,
                "response_time_ms": error_time,
                "success": False,
                "error": str(e)
            }
            print(f"❌ {name}: {str(e)} after {error_time}ms")
        
        return result
    
    
    def check_vies_api_endpoint(self) -> None:
        """Check VIES API endpoint"""
        print(f"\n🔍 VIES API Monitoring - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        new_results = []
        for url_config in self.config['urls']:
            result = self.check_vies_api(url_config)
            new_results.append(result)
        
        # Add new results to existing measurements
        self.measurements.extend(new_results)
        
        # Save measurements and generate statistics
        self.save_measurements()
        self.save_results()
        
        # Publish to GitHub (if enabled)
        if self.config.get('auto_publish', False):
            self.publish_to_github()
    
    def save_measurements(self) -> None:
        """Save individual measurements to measurements.json"""
        try:
            with open("measurements.json", 'w', encoding='utf-8') as f:
                json.dump(self.measurements, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ Error saving measurements: {e}")
    
    
    def save_results(self) -> None:
        """Save statistics to results.json"""
        try:
            # Get current statistics
            stats = self.get_vies_stats()
            
            # Add timestamp to stats
            stats["last_updated"] = datetime.now().isoformat()
            stats["checker_version"] = "1.0"
            
            with open(self.results_file, 'w', encoding='utf-8') as f:
                json.dump(stats, f, indent=2, ensure_ascii=False)
            print(f"\n💾 VIES statistics saved to {self.results_file}")
        except Exception as e:
            print(f"❌ Error saving results: {e}")
    
    def publish_to_github(self) -> None:
        """Publish results to GitHub"""
        try:
            print("\n🚀 Publishing VIES results to GitHub...")
            
            if not os.path.exists('.git'):
                print("⚠️  Not a git repository, skipping publication")
                return
            
            subprocess.run(['git', 'add', self.results_file], check=True)
            commit_message = f"VIES API results update - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            subprocess.run(['git', 'commit', '-m', commit_message], check=True)
            subprocess.run(['git', 'push'], check=True)
            
            print("✅ VIES results successfully uploaded to GitHub!")
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Error publishing to GitHub: {e}")
        except Exception as e:
            print(f"❌ Unexpected error during publication: {e}")
    
    def get_vies_stats(self) -> Dict[str, Any]:
        """Return VIES API statistics focused on response time and success/fail"""
        if not self.measurements:
            return {"total_checks": 0}
        
        # Calculate statistics from all measurements
        total_checks = len(self.measurements)
        successful_checks = sum(1 for r in self.measurements if r['success'])
        failed_checks = total_checks - successful_checks
        
        # Calculate success rate from all measurements
        success_rate = round((successful_checks / total_checks) * 100, 1) if total_checks > 0 else 0
        
        # Calculate response time statistics from all measurements
        response_times = [r['response_time_ms'] for r in self.measurements if r['response_time_ms']]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        min_response_time = min(response_times) if response_times else 0
        max_response_time = max(response_times) if response_times else 0
        
        # Calculate median from all measurements
        median_response_time = 0
        if response_times:
            sorted_times = sorted(response_times)
            n = len(sorted_times)
            if n % 2 == 0:
                median_response_time = (sorted_times[n//2 - 1] + sorted_times[n//2]) / 2
            else:
                median_response_time = sorted_times[n//2]
        
        # Last 10 measurements statistics (for recent trends)
        last_10_results = self.measurements[-10:] if len(self.measurements) >= 10 else self.measurements
        last_10_response_times = [r['response_time_ms'] for r in last_10_results if r['response_time_ms']]
        last_10_avg = sum(last_10_response_times) / len(last_10_response_times) if last_10_response_times else 0
        last_10_successful = sum(1 for r in last_10_results if r['success'])
        last_10_failed = len(last_10_results) - last_10_successful
        
        # Individual response times for graphing
        last_10_values = []
        for i, result in enumerate(last_10_results):
            timestamp = result['timestamp'][:19]  # Remove microseconds
            response_time = result['response_time_ms']
            success = result['success']
            last_10_values.append({
                "measurement": i + 1,
                "timestamp": timestamp,
                "response_time_ms": response_time,
                "success": success
            })
        
        return {
            "total_checks": total_checks,
            "successful_checks": successful_checks,
            "failed_checks": failed_checks,
            "success_rate": success_rate,
            "avg_response_time_ms": round(avg_response_time, 2),
            "median_response_time_ms": round(median_response_time, 2),
            "min_response_time_ms": round(min_response_time, 2),
            "max_response_time_ms": round(max_response_time, 2),
            "last_10_avg_response_time_ms": round(last_10_avg, 2),
            "last_10_successful": last_10_successful,
            "last_10_failed": last_10_failed,
            "last_10_success_rate": round((last_10_successful / len(last_10_results)) * 100, 1) if last_10_results else 0,
            "last_10_values": last_10_values
        }
    
    def run_once(self) -> None:
        """Run single VIES API check"""
        self.check_vies_api_endpoint()
        stats = self.get_vies_stats()
        print(f"\n📊 VIES API Statistics:")
        print(f"   Total checks: {stats['total_checks']}")
        print(f"   ✅ Success: {stats['successful_checks']}")
        print(f"   ❌ Failed: {stats['failed_checks']}")
        print(f"   Success rate: {stats['success_rate']}%")
        print(f"   ⏱️  Average response time: {stats['avg_response_time_ms']}ms")
        print(f"   📊 Median response time: {stats['median_response_time_ms']}ms")
        print(f"   ⚡ Fastest: {stats['min_response_time_ms']}ms")
        print(f"   🐌 Slowest: {stats['max_response_time_ms']}ms")
        print(f"\n📈 Last 10 measurements (for graphing):")
        print(f"   ✅ Success: {stats['last_10_successful']}")
        print(f"   ❌ Failed: {stats['last_10_failed']}")
        print(f"   Success rate: {stats['last_10_success_rate']}%")
        print(f"   ⏱️  Average response time: {stats['last_10_avg_response_time_ms']}ms")
        print(f"\n📊 Individual values:")
        for value in stats['last_10_values']:
            status_icon = "✅" if value['success'] else "❌"
            print(f"   {status_icon} #{value['measurement']}: {value['response_time_ms']}ms ({value['timestamp']})")
    
    def run_continuous(self) -> None:
        """Run continuous VIES API monitoring"""
        interval = self.config.get('check_interval_minutes', 1)
        print(f"🔄 Starting VIES API monitoring (interval: {interval} minutes)")
        print("Press Ctrl+C to stop")
        
        try:
            while True:
                self.run_once()
                print(f"\n⏳ Waiting {interval} minutes...")
                time.sleep(interval * 60)
        except KeyboardInterrupt:
            print("\n\n👋 VIES API monitoring stopped by user")

def main():
    """Main function for VIES checker"""
    import argparse
    
    parser = argparse.ArgumentParser(description='VIES API Checker - monitoring EU VIES API')
    parser.add_argument('--once', action='store_true', help='Run single check only')
    parser.add_argument('--config', default='config.json', help='Path to configuration file')
    
    args = parser.parse_args()
    
    checker = VIESChecker(args.config)
    
    if args.once:
        checker.run_once()
    else:
        checker.run_continuous()

if __name__ == "__main__":
    main()
