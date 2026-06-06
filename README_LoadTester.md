# Shippy API Load Testing Tool

Professional GUI application for testing API endpoint performance under various load conditions.

## Quick Start for Management

### Option 1: Simple Launch
```bash
./launch_load_tester.sh
```

### Option 2: Direct Python Launch
```bash
source stress_test_env/bin/activate
python3 load_test_gui.py
```

## Features

### Test Configuration
- **Concurrent Connections**: 1-2000 simultaneous requests
- **Data Size Options**:
  - Small: Brief responses (~100 tokens)
  - Medium: Detailed responses (~1000 tokens) 
  - Large: Comprehensive responses (~2000 tokens)
  - Maximum: Extensive responses (~4000 tokens)
- **Test Duration**: 10-600 seconds

### Real-Time Monitoring
- Live progress tracking
- Success/error rate monitoring
- Average response time display
- Data transfer metrics

### Professional Reporting
- Executive summary with verdict
- Detailed per-request results
- JSON export capability
- Performance recommendations

## Understanding Results

### Success Rate Verdicts
- **99%+ Success**: ✅ EXCELLENT - Ready for high-volume production
- **95-98% Success**: ✅ GOOD - Handles load well with minimal issues  
- **90-94% Success**: ⚠️ ACCEPTABLE - Some performance degradation
- **<90% Success**: ❌ NEEDS ATTENTION - Significant failures detected

### Key Metrics
- **Success Rate**: Percentage of requests completed without errors
- **Average Response Time**: Mean time for successful requests
- **Throughput**: Requests processed per second
- **Data Transfer**: Total bandwidth utilization

## Recommended Test Scenarios

### Production Readiness Test
- Connections: 100-500
- Data Size: Medium
- Duration: 60s
- Target: >95% success rate

### Peak Load Simulation  
- Connections: 500-1000
- Data Size: Large
- Duration: 120s
- Target: >90% success rate

### Stress Test
- Connections: 1000+
- Data Size: Maximum  
- Duration: 300s
- Target: System remains responsive

## Files

- `load_test_gui.py` - Main GUI application
- `launch_load_tester.sh` - Launcher script
- `stress_test_concurrent.py` - Command-line stress tester
- `stress_test_env/` - Python virtual environment

## Technical Notes

- Uses async HTTP client for efficient concurrent connections
- Implements proper connection pooling and timeouts
- Real-time progress updates without blocking UI
- Professional results export in JSON format
- Designed for non-technical management use

## System Requirements

- Python 3.7+
- Graphical desktop environment
- Network access to API endpoint
- 2GB+ RAM for high connection counts