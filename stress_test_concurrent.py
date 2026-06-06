#!/usr/bin/env python3
"""
Concurrent load testing script for API endpoint
Tests 1,000 concurrent sessions with prompts designed to return maximum data
"""

import asyncio
import aiohttp
import json
import time
import sys
from datetime import datetime

# Configuration
API_URL = "https://api.tryshippy.com/chat"
CONCURRENT_SESSIONS = 1000
JWT_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJlYWYzOGIzMC0zZTNiLTQ0YTAtYmE1Mi1lNjFkOWVlMzU3MTgiLCJpYXQiOjE3MzM1MDUzODAsImV4cCI6MTczNjA5NzM4MH0.9YBB2nWPADcKfpgQs6u9V-6Ey67kGYhNDi8p_xTFKqc"

# Prompts designed to generate maximum output
STRESS_PROMPTS = [
    "Write a comprehensive 10,000-word analysis of artificial intelligence covering history, current applications, technical details, ethical considerations, future predictions, and provide detailed examples for each section with extensive explanations.",
    "Generate a complete Python tutorial covering all language features, data structures, algorithms, web frameworks, machine learning libraries, with detailed code examples, explanations, and best practices for each topic.",
    "Create an extensive business plan for a technology startup including market analysis, financial projections, technical architecture, marketing strategy, competitive analysis, risk assessment, and implementation timeline with detailed explanations.",
    "Write a detailed technical documentation for building a distributed system including architecture diagrams, API specifications, database schemas, security protocols, scaling strategies, monitoring solutions, and deployment procedures.",
    "Generate a comprehensive guide to cybersecurity covering all attack vectors, defense strategies, compliance frameworks, incident response procedures, technical tools, and provide detailed examples and case studies.",
    "Create an exhaustive explanation of blockchain technology including consensus mechanisms, smart contracts, DeFi protocols, NFTs, scaling solutions, and provide detailed technical implementations and use cases.",
    "Write a complete guide to modern web development covering frontend frameworks, backend technologies, databases, DevOps practices, testing strategies, performance optimization, and provide extensive code examples.",
    "Generate a detailed analysis of global economic systems including monetary policy, international trade, cryptocurrency impact, emerging markets, and provide comprehensive data and projections.",
    "Create an extensive medical research paper on latest treatments, drug development processes, clinical trials, regulatory approval, and provide detailed scientific explanations and data analysis.",
    "Write a comprehensive guide to space exploration including rocket technology, mission planning, life support systems, planetary science, and provide detailed technical specifications and future missions."
]

async def make_request(session, prompt, session_id):
    """Make a single API request"""
    headers = {
        "Authorization": f"Bearer {JWT_TOKEN}",
        "Content-Type": "application/json",
        "Accept": "text/event-stream",
        "User-Agent": f"StressTest-Session-{session_id}"
    }
    
    payload = {
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "model": "claude-3-5-sonnet-20241022",
        "max_tokens": 8192,  # Maximum tokens to stress the system
        "temperature": 0.7,
        "stream": True
    }
    
    start_time = time.time()
    total_data = 0
    error = None
    status_code = None
    
    try:
        async with session.post(API_URL, json=payload, headers=headers, timeout=300) as response:
            status_code = response.status
            
            if response.status == 200:
                async for chunk in response.content.iter_chunked(1024):
                    total_data += len(chunk)
                    # Process SSE data
                    if chunk:
                        chunk_str = chunk.decode('utf-8', errors='ignore')
                        # Count actual data events
                        if 'data: ' in chunk_str:
                            continue
            else:
                error_text = await response.text()
                error = f"HTTP {response.status}: {error_text[:200]}"
                
    except asyncio.TimeoutError:
        error = "Request timeout"
    except Exception as e:
        error = f"Connection error: {str(e)[:200]}"
    
    duration = time.time() - start_time
    
    return {
        'session_id': session_id,
        'status_code': status_code,
        'duration': duration,
        'data_received': total_data,
        'error': error,
        'prompt_length': len(prompt)
    }

async def run_stress_test():
    """Run the stress test with concurrent sessions"""
    print(f"Starting stress test with {CONCURRENT_SESSIONS} concurrent sessions...")
    print(f"Target: {API_URL}")
    print(f"Timestamp: {datetime.now()}")
    print("-" * 60)
    
    # Create connector with custom settings for high concurrency
    connector = aiohttp.TCPConnector(
        limit=CONCURRENT_SESSIONS + 100,  # Total connection pool size
        limit_per_host=CONCURRENT_SESSIONS + 50,  # Per-host connection limit
        keepalive_timeout=300,
        enable_cleanup_closed=True
    )
    
    timeout = aiohttp.ClientTimeout(total=300, connect=30)
    
    async with aiohttp.ClientSession(
        connector=connector,
        timeout=timeout,
        read_bufsize=65536  # Larger buffer for streaming data
    ) as session:
        
        # Create tasks for all concurrent requests
        tasks = []
        for i in range(CONCURRENT_SESSIONS):
            prompt = STRESS_PROMPTS[i % len(STRESS_PROMPTS)]
            task = make_request(session, prompt, i + 1)
            tasks.append(task)
        
        # Execute all requests concurrently
        start_time = time.time()
        print(f"Launching {CONCURRENT_SESSIONS} concurrent requests...")
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        total_duration = time.time() - start_time
        
        # Analyze results
        successful = [r for r in results if not isinstance(r, Exception) and r['error'] is None]
        errors = [r for r in results if isinstance(r, Exception) or (hasattr(r, 'get') and r.get('error'))]
        
        print(f"\n{'='*60}")
        print("STRESS TEST RESULTS")
        print(f"{'='*60}")
        print(f"Total requests: {CONCURRENT_SESSIONS}")
        print(f"Successful: {len(successful)}")
        print(f"Errors: {len(errors)}")
        print(f"Success rate: {len(successful)/CONCURRENT_SESSIONS*100:.1f}%")
        print(f"Total test duration: {total_duration:.2f} seconds")
        
        if successful:
            avg_duration = sum(r['duration'] for r in successful) / len(successful)
            total_data = sum(r['data_received'] for r in successful)
            avg_data = total_data / len(successful) if successful else 0
            
            print(f"\nPerformance Metrics:")
            print(f"Average response time: {avg_duration:.2f} seconds")
            print(f"Total data received: {total_data / (1024*1024):.2f} MB")
            print(f"Average data per request: {avg_data / 1024:.2f} KB")
            print(f"Throughput: {len(successful) / total_duration:.2f} requests/second")
            
        if errors:
            print(f"\nError Analysis:")
            error_types = {}
            for result in results:
                if isinstance(result, Exception):
                    error_type = type(result).__name__
                elif hasattr(result, 'get') and result.get('error'):
                    error_type = result['error'].split(':')[0] if ':' in str(result['error']) else str(result['error'])[:50]
                else:
                    continue
                    
                error_types[error_type] = error_types.get(error_type, 0) + 1
            
            for error_type, count in sorted(error_types.items(), key=lambda x: x[1], reverse=True):
                print(f"  {error_type}: {count} occurrences")
        
        # Status code analysis
        status_codes = {}
        for result in results:
            if not isinstance(result, Exception) and result.get('status_code'):
                code = result['status_code']
                status_codes[code] = status_codes.get(code, 0) + 1
        
        if status_codes:
            print(f"\nStatus Code Distribution:")
            for code, count in sorted(status_codes.items()):
                print(f"  HTTP {code}: {count} responses")

if __name__ == "__main__":
    print("High-Concurrency API Stress Test")
    print("WARNING: This will create 1,000 concurrent connections!")
    
    # Skip interactive prompt for automated execution
    if len(sys.argv) > 1 and sys.argv[1] == "--auto":
        proceed = True
    else:
        try:
            response = input("Proceed with stress test? (yes/no): ")
            proceed = response.lower() in ['yes', 'y']
        except EOFError:
            # Non-interactive environment, proceed automatically
            proceed = True
            print("Running in non-interactive mode, proceeding automatically...")
    
    if not proceed:
        print("Test cancelled.")
        sys.exit(0)
    
    try:
        asyncio.run(run_stress_test())
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"Test failed: {e}")