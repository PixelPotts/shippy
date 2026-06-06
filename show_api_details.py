#!/usr/bin/env python3
"""
Show exactly what the load testing tool sends and receives
"""

import json
import asyncio
import aiohttp

def show_request_details():
    """Display the exact API request details"""
    
    print("🌐 ENDPOINT BEING TESTED")
    print("=" * 50)
    print(f"URL: https://api.tryshippy.com/chat")
    print(f"Method: POST")
    print(f"Content-Type: application/json")
    print(f"Accept: text/event-stream")
    print()
    
    print("🔑 AUTHENTICATION")
    print("=" * 50)
    print("Uses JWT Bearer token in Authorization header")
    print("Token format: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
    print()
    
    print("📤 REQUEST PAYLOAD (JSON)")
    print("=" * 50)
    
    # Show example payloads for each size
    payloads = {
        "Small": {
            "messages": [{"role": "user", "content": "Hello, provide a brief response."}],
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 4096,
            "temperature": 0.7,
            "stream": True
        },
        "Medium": {
            "messages": [{"role": "user", "content": "Write a detailed explanation of API load testing including best practices, common metrics, and how to interpret results."}],
            "model": "claude-3-5-sonnet-20241022", 
            "max_tokens": 4096,
            "temperature": 0.7,
            "stream": True
        },
        "Large": {
            "messages": [{"role": "user", "content": "Generate a comprehensive guide to building scalable web applications including architecture patterns, database design, caching strategies, load balancing, monitoring, and deployment best practices with detailed examples."}],
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 4096,
            "temperature": 0.7,
            "stream": True
        }
    }
    
    for size, payload in payloads.items():
        print(f"\n{size} Request:")
        print(json.dumps(payload, indent=2))
    
    print("\n📥 RESPONSE FORMAT")
    print("=" * 50)
    print("Content-Type: text/event-stream")
    print("Response is Server-Sent Events (SSE) stream format:")
    print()
    print("Example response chunks:")
    print('event: delta')
    print('data: {"type":"delta","text":"Hi"}')
    print('')
    print('event: delta') 
    print('data: {"type":"delta","text":" there! How can I help you today?"}')
    print('')
    print('event: done')
    print('data: {"type":"done","reply":"Hi there! How can I help you today?"}')
    print()
    
    print("🧪 WHAT THE LOAD TEST MEASURES")
    print("=" * 50)
    print("✅ HTTP Status Code (200 = success, 5xx = server error)")
    print("✅ Response Time (from request start to stream completion)")
    print("✅ Data Transferred (total bytes received in SSE stream)")
    print("✅ Connection Failures (timeouts, connection refused, etc.)")
    print("✅ Concurrent Request Handling (multiple users at once)")
    print()
    
    print("🎯 BUSINESS IMPACT")
    print("=" * 50)
    print("This tests your core chat functionality under load:")
    print("• Can handle multiple users chatting simultaneously?")
    print("• Response times stay acceptable during traffic spikes?")
    print("• Server remains stable under heavy usage?")
    print("• Ready for advertising campaign traffic?")

async def show_live_example():
    """Show a real API call example (optional - requires valid token)"""
    print("\n🔴 LIVE API EXAMPLE")
    print("=" * 50)
    
    # This would show a real example but requires authentication
    print("To see a live example, the tool sends this curl equivalent:")
    print()
    print("curl -X POST https://api.tryshippy.com/chat \\")
    print('  -H "Authorization: Bearer YOUR_JWT_TOKEN" \\')
    print('  -H "Content-Type: application/json" \\')
    print('  -H "Accept: text/event-stream" \\')
    print('  -d \'{"messages":[{"role":"user","content":"Hello"}],"model":"claude-3-5-sonnet-20241022","max_tokens":4096,"temperature":0.7,"stream":true}\'')

if __name__ == "__main__":
    show_request_details()
    asyncio.run(show_live_example())