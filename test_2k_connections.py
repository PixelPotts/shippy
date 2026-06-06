#!/usr/bin/env python3
"""
Test 2000 connections using the fixed batch processing approach
"""

import asyncio
import aiohttp
import time
from dataclasses import dataclass

@dataclass
class TestResult:
    session_id: int
    status_code: int
    duration: float
    data_received: int
    error: str = None

async def test_2k_connections():
    """Test with 2000 connections using batch processing"""
    api_url = "https://api.tryshippy.com/chat"
    jwt_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJlYWYzOGIzMC0zZTNiLTQ0YTAtYmE1Mi1lNjFkOWVlMzU3MTgiLCJpYXQiOjE3MzM1MDUzODAsImV4cCI6MTczNjA5NzM4MH0.9YBB2nWPADcKfpgQs6u9V-6Ey67kGYhNDi8p_xTFKqc"
    
    connections = 2000
    max_concurrent = 500  # Cap concurrent connections
    batch_size = 250
    
    print(f"Testing {connections} connections in batches of {batch_size}...")
    print(f"Max concurrent per batch: {max_concurrent}")
    
    connector = aiohttp.TCPConnector(
        limit=max_concurrent * 2,
        limit_per_host=max_concurrent,
        keepalive_timeout=30,
        enable_cleanup_closed=True,
        ttl_dns_cache=300,
        use_dns_cache=True,
        force_close=False
    )
    
    timeout = aiohttp.ClientTimeout(total=300, connect=60, sock_read=60)
    
    async def make_request(session, session_id):
        headers = {
            "Authorization": f"Bearer {jwt_token}",
            "Content-Type": "application/json",
            "Accept": "text/event-stream",
            "User-Agent": f"Test2K-{session_id}",
            "Connection": "keep-alive"
        }
        
        payload = {
            "messages": [{"role": "user", "content": f"Test request #{session_id}"}],
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 50,
            "stream": True
        }
        
        start_time = time.time()
        
        try:
            # Progressive delay for high session IDs
            if session_id > 500:
                await asyncio.sleep(0.001 * (session_id - 500))
            
            async with session.post(api_url, json=payload, headers=headers) as response:
                status_code = response.status
                total_data = 0
                
                if response.status == 200:
                    async for chunk in response.content.iter_chunked(8192):
                        total_data += len(chunk)
                    error = None
                else:
                    try:
                        error_text = await response.text()
                        error = f"HTTP {response.status}: {error_text[:100]}"
                    except:
                        error = f"HTTP {response.status}: Unable to read response"
                    
        except aiohttp.ClientConnectorError as e:
            error = f"Connection failed: {str(e)[:100]}"
            status_code = 0
            total_data = 0
        except Exception as e:
            error = f"Error: {str(e)[:100]}"
            status_code = 0
            total_data = 0
        
        duration = time.time() - start_time
        
        return TestResult(
            session_id=session_id,
            status_code=status_code,
            duration=duration,
            data_received=total_data,
            error=error
        )
    
    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        start_time = time.time()
        all_results = []
        
        # Process in batches
        for batch_num, batch_start in enumerate(range(0, connections, batch_size), 1):
            batch_end = min(batch_start + batch_size, connections)
            batch_ids = list(range(batch_start, batch_end))
            
            print(f"Processing batch {batch_num}: sessions {batch_start}-{batch_end-1}")
            
            # Create semaphore for this batch
            batch_semaphore = asyncio.Semaphore(max_concurrent)
            
            async def limited_request(session_id):
                async with batch_semaphore:
                    return await make_request(session, session_id)
            
            # Create and execute batch tasks
            batch_tasks = [limited_request(i) for i in batch_ids]
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            
            all_results.extend(batch_results)
            
            # Quick batch analysis
            batch_successful = sum(1 for r in batch_results if not isinstance(r, Exception) and not r.error)
            batch_failed = len(batch_results) - batch_successful
            
            print(f"  Batch {batch_num} complete: {batch_successful} successful, {batch_failed} failed")
            
            # Small delay between batches
            await asyncio.sleep(0.5)
        
        total_duration = time.time() - start_time
        
        # Final analysis
        successful = 0
        failed = 0
        exceptions = 0
        
        for result in all_results:
            if isinstance(result, Exception):
                exceptions += 1
            elif result.error:
                failed += 1
            else:
                successful += 1
        
        print(f"\n{'='*60}")
        print(f"FINAL RESULTS for {connections} connections:")
        print(f"{'='*60}")
        print(f"Total time: {total_duration:.2f}s")
        print(f"Successful: {successful}")
        print(f"Failed: {failed}")
        print(f"Exceptions: {exceptions}")
        print(f"Success rate: {successful/connections*100:.1f}%")
        print(f"Throughput: {successful/total_duration:.2f} req/sec")
        
        if failed > 0 or exceptions > 0:
            print(f"\nSample errors:")
            error_count = 0
            for result in all_results[:20]:  # Check first 20 results
                if isinstance(result, Exception):
                    print(f"  Exception: {str(result)[:100]}")
                    error_count += 1
                elif result.error:
                    print(f"  Error: {result.error}")
                    error_count += 1
                if error_count >= 5:
                    break

if __name__ == "__main__":
    asyncio.run(test_2k_connections())