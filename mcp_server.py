#!/usr/bin/env python3
"""
SmartTrip Planner - MCP (Model Context Protocol) Server

This module implements an MCP server that exposes SmartTrip Planner capabilities
as standardized tools accessible to AI models and other applications.

MCP Tools Available:
- generate_travel_plan: Generate complete travel itineraries
- search_locations: Find hotels, restaurants, attractions by proximity
- search_travel_info: Web search for travel information
"""

import asyncio
import json
from typing import Any
from app import TravelPlanningSystem

# Try to import mcp - if not available, provide graceful fallback
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Resource, Tool, TextContent
    MCP_AVAILABLE = True
except ImportError as e:
    MCP_AVAILABLE = False
    print(f"⚠️  MCP import error: {e}")


class SmartTripMCPServer:
    """MCP Server for SmartTrip Planner"""
    
    def __init__(self):
        self.travel_system = TravelPlanningSystem()
        if MCP_AVAILABLE:
            self.server = Server("SmartTrip-Planner", "1.0.0")
            self._setup_tools()
    
    def _setup_tools(self):
        """Register MCP tools"""
        if not MCP_AVAILABLE:
            return
        
        # Tool 1: Generate Travel Plan
        @self.server.list_tools()
        async def list_tools():
            return [
                {
                    "name": "generate_travel_plan",
                    "description": "Generate a complete personalized travel plan with itinerary, "
                                  "nearby places, and budget breakdown",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "destination": {
                                "type": "string",
                                "description": "Destination city (e.g., 'Mumbai', 'Delhi')"
                            },
                            "origin": {
                                "type": "string",
                                "description": "Origin city (e.g., 'Delhi')"
                            },
                            "departure_date": {
                                "type": "string",
                                "description": "Departure date (YYYY-MM-DD format)"
                            },
                            "return_date": {
                                "type": "string",
                                "description": "Return date (YYYY-MM-DD format)"
                            },
                            "budget": {
                                "type": "string",
                                "enum": ["budget", "mid", "premium", "luxury"],
                                "description": "Budget range"
                            },
                            "passengers": {
                                "type": "integer",
                                "description": "Number of travelers"
                            }
                        },
                        "required": ["destination", "departure_date", "return_date"]
                    }
                },
                {
                    "name": "search_locations",
                    "description": "Search for nearby locations (hotels, restaurants, attractions) "
                                  "sorted by proximity",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "City or location to search"
                            }
                        },
                        "required": ["location"]
                    }
                },
                {
                    "name": "search_travel_info",
                    "description": "Search web for travel information about a destination",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Travel information query (e.g., 'best time to visit Mumbai')"
                            }
                        },
                        "required": ["query"]
                    }
                }
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict):
            """Execute MCP tool"""
            try:
                if name == "generate_travel_plan":
                    return await self._handle_generate_plan(arguments)
                
                elif name == "search_locations":
                    return await self._handle_search_locations(arguments)
                
                elif name == "search_travel_info":
                    return await self._handle_search_info(arguments)
                
                else:
                    return {"error": f"Unknown tool: {name}"}
            
            except Exception as e:
                return {"error": str(e)}
    
    async def _handle_generate_plan(self, args: dict) -> dict:
        """Handle generate_travel_plan tool"""
        try:
            trip_data = {
                "to": args.get("destination", "").upper(),
                "from": args.get("origin", "Delhi").upper(),
                "departureDate": args.get("departure_date", ""),
                "returnDate": args.get("return_date", ""),
                "budget": args.get("budget", "mid"),
                "passengers": args.get("passengers", 1)
            }
            
            result = await self.travel_system.process_travel_request(trip_data)
            
            # Return comprehensive plan
            return {
                "success": result.get("success"),
                "destination": result.get("destination"),
                "duration": result.get("duration"),
                "budget": f"₹{result.get('budget'):,}",
                "travelers": result.get("travelers"),
                "comprehensive_plan": result.get("comprehensive_plan"),
                "maps_results": result.get("maps_results"),
                "search_results": result.get("search_results")
            }
        
        except Exception as e:
            return {"error": f"Failed to generate plan: {str(e)}"}
    
    async def _handle_search_locations(self, args: dict) -> dict:
        """Handle search_locations tool"""
        try:
            location = args.get("location", "")
            if not location:
                return {"error": "Location parameter required"}
            
            # Use maps search
            results = await self.travel_system.search_with_maps(
                f"hotels restaurants attractions in {location}"
            )
            
            return {
                "location": location,
                "results": results,
                "status": "success"
            }
        
        except Exception as e:
            return {"error": f"Location search failed: {str(e)}"}
    
    async def _handle_search_info(self, args: dict) -> dict:
        """Handle search_travel_info tool"""
        try:
            query = args.get("query", "")
            if not query:
                return {"error": "Query parameter required"}
            
            # Use web search
            results = await self.travel_system.search_with_tavily(query)
            
            return {
                "query": query,
                "results": results,
                "status": "success"
            }
        
        except Exception as e:
            return {"error": f"Travel info search failed: {str(e)}"}
    
    async def run(self):
        """Start the MCP server using stdio transport"""
        if not MCP_AVAILABLE:
            print("❌ MCP not available. Install with: pip install mcp")
            return
        
        print("🚀 SmartTrip Planner MCP Server initialized")
        print("📍 Available tools:")
        print("  - generate_travel_plan")
        print("  - search_locations")
        print("  - search_travel_info")
        print("\nStarting stdio transport...")
        
        # Use stdio transport for MCP communication
        async with stdio_server() as (read_stream, write_stream):
            print("✅ Server connected via stdio")
            try:
                await self.server.run(read_stream, write_stream, None)
            except Exception as e:
                print(f"Server error: {e}")


def start_mcp_server():
    """Start the MCP server"""
    server = SmartTripMCPServer()
    
    if MCP_AVAILABLE:
        asyncio.run(server.run())
    else:
        print("""
❌ MCP Server requires 'mcp' package.

To enable MCP support:
1. Install the MCP package:
   pip install mcp

2. Run the MCP server:
   python mcp_server.py

3. Configure your AI model to use SmartTrip Planner MCP:
   - Claude Desktop: Add to claude_desktop_config.json
   - Other LLMs: Configure MCP server endpoint

For more info: https://modelcontextprotocol.io
        """)


if __name__ == "__main__":
    start_mcp_server()
