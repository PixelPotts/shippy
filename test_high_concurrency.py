#!/usr/bin/env python3
"""
Test high concurrency fixes with a manageable load
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

async def test_concurrency(connections=100):
    """Test with specified number of connections"""
    api_url = "https://api.tryshippy.com/chat"
    jwt_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJlYWYzOGIzMC0zZTNiLTQ0YTAtYmE1Mi1lNjFkOWVlMzU3MTgiLCJpYXQiOjE3MzM1MDUzODAsImV4cCI6MTczNjA5NzM4MH0.9YBB2nWPADcKfpgQs6u9V-6Ey67kGYhNDi8p_xTFKqc"
    
    print(f"Testing {connections} concurrent connections...")
    
    # Use improved settings
    max_concurrent = min(connections, 500)
    connector_limit = max_concurrent * 2
    
    connector = aiohttp.TCPConnector(
        limit=connector_limit,
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
            "User-Agent": f"TestSession-{session_id}",
            "Connection": "keep-alive"
        }
        
        payload = {
            "messages": [{"role": "user", "content": "Quick test response"}],
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 100,
            "stream": True
        }
        
        start_time = time.time()
        
        try:
            # Small delay for high session IDs
            if session_id > 50:
                await asyncio.sleep(0.001 * (session_id - 50))
            
            async with session.post(api_url, json=payload, headers=headers) as response:
                status_code = response.status
                total_data = 0
                
                if response.status == 200:
                    async for chunk in response.content.iter_chunked(8192):
                        total_data += len(chunk)
                    error = None
                else:
                    error_text = await response.text()
                    error = f"HTTP {response.status}: {error_text[:100]}"
                    
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
        
        # Use semaphore to control concurrency
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def limited_request(session_id):
            async with semaphore:
                return await make_request(session, session_id)
        
        # Create and run all tasks
        tasks = [limited_request(i) for i in range(connections)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        total_duration = time.time() - start_time
        
        # Analyze results
        successful = 0
        failed = 0
        exceptions = 0
        
        for result in results:
            if isinstance(result, Exception):
                exceptions += 1
            elif result.error:
                failed += 1
            else:
                successful += 1
        
        print(f"\nResults for {connections} connections:")
        print(f"Total time: {total_duration:.2f}s")
        print(f"Successful: {successful}")
        print(f"Failed: {failed}")
        print(f"Exceptions: {exceptions}")
        print(f"Success rate: {successful/connections*100:.1f}%")
        
        if failed > 0:
            print(f"\nFirst few errors:")
            error_count = 0
            for result in results:
                if not isinstance(result, Exception) and result.error:
                    print(f"  - {result.error}")
                    error_count += 1
                    if error_count >= 3:
                        break

async def main():
    """Test with increasing connection counts"""
    test_counts = [50, 100, 200, 500]
    
    for count in test_counts:
        await test_concurrency(count)
        print("\n" + "="*60 + "\n")
        await asyncio.sleep(2)  # Brief pause between tests

if __name__ == "__main__":
    asyncio.run(main())