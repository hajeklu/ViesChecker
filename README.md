# VIES API Checker

Advanced monitoring system for EU VIES API with automatic GitHub publishing.

## Architecture

1. **Raspberry Pi** - Data collection
   - Python script measures VIES API availability
   - Stores results in `results.json`
   - Automatically publishes to GitHub

2. **GitHub** - Results publishing
   - Publicly available `results.json` file
   - Automatic updates on each measurement
   - Simple data download

## Project Structure

```
urlChecker/
├── README.md
├── requirements.txt
├── checker.py              # Main VIES API checker
├── results.json           # Measurement results
├── config.json           # URL configuration
├── setup.sh              # Initialization script
└── deploy.sh             # GitHub publishing script
```

## Installation and Setup

1. **Initialize project:**
```bash
chmod +x setup.sh
./setup.sh
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure URL in `config.json`**
   - Edit list of URLs to monitor
   - Set check interval

4. **Setup GitHub repository:**
```bash
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPO.git
git push -u origin main
```

5. **Run monitoring:**
```bash
# Single check
python checker.py --once

# Continuous monitoring
python checker.py
```

## Automation

For automatic execution on Raspberry Pi use cron:
```bash
# VIES API monitoring every 1 minute
*/1 * * * * cd /path/to/urlChecker && python checker.py
```

## VIES API Monitoring

Specialized checker for [EU VIES API](https://ec.europa.eu/taxation_customs/vies/rest-api/ms/CZ/vat/CZ26185610) focused on response time and success/fail tracking:

### What it measures:
- **Response time** - how long the API takes to respond (milliseconds)
- **Success/Fail rate** - tracking successful vs failed requests
- **API availability** - monitoring EU system uptime
- **Performance statistics** - fastest, slowest, average response times

### Example results:
```json
{
  "timestamp": "2024-01-15T10:00:00.123456",
  "name": "VIES API - AGROFERT",
  "status_code": 200,
  "response_time_ms": 1247.83,
  "success": true,
  "error": null
}
```

## Results

Results are automatically published to `results.json` in GitHub repository. Data includes:

### Key metrics:
- **Timestamp** - when the check was performed
- **Response time** - how long the API took to respond (ms)
- **Success/Fail** - whether the request was successful
- **Status code** - HTTP response code
- **Error details** - if the request failed

### Statistics tracked:
- **Total checks** - number of measurements
- **Success count** - successful requests
- **Fail count** - failed requests  
- **Success rate** - percentage of successful requests
- **Average response time** - mean response time
- **Median response time** - middle value (50th percentile)
- **Fastest response** - minimum response time
- **Slowest response** - maximum response time
- **Last 10 measurements** - recent performance trends

## Example output

```
📊 VIES API Statistics:
   Total checks: 10
   ✅ Success: 9
   ❌ Failed: 1
   Success rate: 90.0%
   ⏱️  Average response time: 1456.2ms
   📊 Median response time: 1472.2ms
   ⚡ Fastest: 331.82ms
   🐌 Slowest: 2309.95ms

📈 Last 10 measurements (for graphing):
   ✅ Success: 9
   ❌ Failed: 1
   Success rate: 90.0%
   ⏱️  Average response time: 1456.2ms

📊 Individual values:
   ✅ #1: 1247.83ms (2024-01-15T10:00:00)
   ✅ #2: 892.45ms (2024-01-15T10:01:00)
   ✅ #3: 2159.9ms (2024-01-15T10:02:00)
   ❌ #4: 15000.0ms (2024-01-15T10:03:00)
   ✅ #5: 331.82ms (2024-01-15T10:04:00)
   ✅ #6: 1927.18ms (2024-01-15T10:05:00)
   ✅ #7: 1503.94ms (2024-01-15T10:06:00)
   ✅ #8: 1472.17ms (2024-01-15T10:07:00)
   ✅ #9: 1787.64ms (2024-01-15T10:08:00)
   ✅ #10: 2309.95ms (2024-01-15T10:09:00)
```