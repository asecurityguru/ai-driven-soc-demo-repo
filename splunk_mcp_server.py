#!/usr/bin/env python3
"""
Splunk MCP Server for AI-Powered SOC Operations
Provides tools for Claude to interact with Splunk for security analysis
"""

import asyncio
import json
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import splunklib.client as client
import splunklib.results as results
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent


class SplunkMCPServer:
    def __init__(self):
        self.server = Server("splunk-soc-server")
        self.splunk_service = None
        self.setup_handlers()
        
    def connect_to_splunk(self):
        """Connect to Splunk instance"""
        try:
            self.splunk_service = client.connect(
                host=os.getenv('SPLUNK_HOST', 'localhost'),
                port=int(os.getenv('SPLUNK_PORT', '8089')),
                username=os.getenv('SPLUNK_USERNAME', 'admin'),
                password=os.getenv('SPLUNK_PASSWORD', 'Admin123!'),
                autologin=True
            )
            return True
        except Exception as e:
            print(f"Failed to connect to Splunk: {e}")
            return False

    def setup_handlers(self):
        """Register MCP tool handlers"""
        
        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List available Splunk tools"""
            return [
                Tool(
                    name="search_splunk",
                    description="Execute SPL search query in Splunk. Use for investigating security events, threats, and anomalies.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "SPL (Search Processing Language) query to execute"
                            },
                            "earliest_time": {
                                "type": "string",
                                "description": "Start time for search (e.g., '-24h', '-7d', '2024-02-01T00:00:00')",
                                "default": "-1h"
                            },
                            "latest_time": {
                                "type": "string",
                                "description": "End time for search (default: now)",
                                "default": "now"
                            }
                        },
                        "required": ["query"]
                    }
                ),
                Tool(
                    name="get_security_alerts",
                    description="Retrieve recent security alerts and notables from Splunk. Perfect for alert triage and prioritization.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "severity": {
                                "type": "string",
                                "description": "Filter by severity: critical, high, medium, low",
                                "enum": ["critical", "high", "medium", "low", "all"]
                            },
                            "time_range": {
                                "type": "string",
                                "description": "Time range to search (e.g., '-1h', '-24h', '-7d')",
                                "default": "-24h"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of alerts to return",
                                "default": 50
                            }
                        }
                    }
                ),
                Tool(
                    name="investigate_ip",
                    description="Investigate an IP address across all Splunk data sources. Shows all activity, connections, and threats.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "ip_address": {
                                "type": "string",
                                "description": "IP address to investigate"
                            },
                            "time_range": {
                                "type": "string",
                                "description": "Time range to search",
                                "default": "-24h"
                            }
                        },
                        "required": ["ip_address"]
                    }
                ),
                Tool(
                    name="investigate_user",
                    description="Investigate a user account across authentication, access, and activity logs.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "username": {
                                "type": "string",
                                "description": "Username to investigate"
                            },
                            "time_range": {
                                "type": "string",
                                "description": "Time range to search",
                                "default": "-24h"
                            }
                        },
                        "required": ["username"]
                    }
                ),
                Tool(
                    name="get_threat_intel",
                    description="Query threat intelligence data and IOCs (Indicators of Compromise) in Splunk.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "ioc_type": {
                                "type": "string",
                                "description": "Type of IOC: ip, domain, hash, url",
                                "enum": ["ip", "domain", "hash", "url", "all"]
                            },
                            "time_range": {
                                "type": "string",
                                "description": "Time range to search",
                                "default": "-7d"
                            }
                        }
                    }
                ),
                Tool(
                    name="get_security_metrics",
                    description="Get security operations metrics and KPIs for reporting and dashboards.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "metric_type": {
                                "type": "string",
                                "description": "Type of metrics: alerts, incidents, response_time, threat_trends",
                                "enum": ["alerts", "incidents", "response_time", "threat_trends", "all"]
                            },
                            "time_range": {
                                "type": "string",
                                "description": "Time range for metrics",
                                "default": "-24h"
                            }
                        }
                    }
                ),
                Tool(
                    name="analyze_failed_logins",
                    description="Analyze failed login attempts to detect brute force attacks or credential stuffing.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "threshold": {
                                "type": "integer",
                                "description": "Minimum number of failed attempts to flag",
                                "default": 5
                            },
                            "time_range": {
                                "type": "string",
                                "description": "Time range to analyze",
                                "default": "-1h"
                            }
                        }
                    }
                ),
                Tool(
                    name="detect_data_exfiltration",
                    description="Detect potential data exfiltration by analyzing unusual data transfer volumes.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "threshold_mb": {
                                "type": "integer",
                                "description": "Data transfer threshold in MB to flag",
                                "default": 100
                            },
                            "time_range": {
                                "type": "string",
                                "description": "Time range to analyze",
                                "default": "-1h"
                            }
                        }
                    }
                )
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Any) -> list[TextContent]:
            """Handle tool calls"""
            
            # Ensure connection
            if not self.splunk_service:
                if not self.connect_to_splunk():
                    return [TextContent(
                        type="text",
                        text="Error: Failed to connect to Splunk. Check connection settings."
                    )]
            
            try:
                if name == "search_splunk":
                    result = await self.search_splunk(
                        arguments.get("query"),
                        arguments.get("earliest_time", "-1h"),
                        arguments.get("latest_time", "now")
                    )
                elif name == "get_security_alerts":
                    result = await self.get_security_alerts(
                        arguments.get("severity", "all"),
                        arguments.get("time_range", "-24h"),
                        arguments.get("limit", 50)
                    )
                elif name == "investigate_ip":
                    result = await self.investigate_ip(
                        arguments.get("ip_address"),
                        arguments.get("time_range", "-24h")
                    )
                elif name == "investigate_user":
                    result = await self.investigate_user(
                        arguments.get("username"),
                        arguments.get("time_range", "-24h")
                    )
                elif name == "get_threat_intel":
                    result = await self.get_threat_intel(
                        arguments.get("ioc_type", "all"),
                        arguments.get("time_range", "-7d")
                    )
                elif name == "get_security_metrics":
                    result = await self.get_security_metrics(
                        arguments.get("metric_type", "all"),
                        arguments.get("time_range", "-24h")
                    )
                elif name == "analyze_failed_logins":
                    result = await self.analyze_failed_logins(
                        arguments.get("threshold", 5),
                        arguments.get("time_range", "-1h")
                    )
                elif name == "detect_data_exfiltration":
                    result = await self.detect_data_exfiltration(
                        arguments.get("threshold_mb", 100),
                        arguments.get("time_range", "-1h")
                    )
                else:
                    result = f"Unknown tool: {name}"
                
                return [TextContent(type="text", text=str(result))]
                
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"Error executing {name}: {str(e)}"
                )]

    async def search_splunk(self, query: str, earliest_time: str, latest_time: str) -> str:
        """Execute SPL search query"""
        try:
            kwargs = {
                "earliest_time": earliest_time,
                "latest_time": latest_time,
                "output_mode": "json"
            }
            
            job = self.splunk_service.jobs.create(query, **kwargs)
            
            # Wait for job to complete
            while not job.is_done():
                await asyncio.sleep(0.5)
            
            # Get results
            result_stream = job.results(output_mode='json')
            results_data = json.loads(result_stream.read())
            
            # Format results
            if 'results' in results_data and results_data['results']:
                formatted_results = {
                    "query": query,
                    "event_count": len(results_data['results']),
                    "time_range": f"{earliest_time} to {latest_time}",
                    "results": results_data['results'][:20]  # Limit to first 20
                }
                return json.dumps(formatted_results, indent=2)
            else:
                return json.dumps({
                    "query": query,
                    "event_count": 0,
                    "message": "No results found"
                })
                
        except Exception as e:
            return json.dumps({"error": str(e)})

    async def get_security_alerts(self, severity: str, time_range: str, limit: int) -> str:
        """Get security alerts"""
        severity_filter = "" if severity == "all" else f'severity="{severity}"'
        
        query = f'''
        search index=* sourcetype=* {severity_filter}
        | where isnotnull(severity) OR isnotnull(signature) OR isnotnull(alert_type)
        | head {limit}
        | table _time, src_ip, dest_ip, user, severity, signature, category, action, message
        | sort - _time
        '''
        
        return await self.search_splunk(query, time_range, "now")

    async def investigate_ip(self, ip_address: str, time_range: str) -> str:
        """Investigate IP address"""
        query = f'''
        search index=* ({ip_address})
        | stats count by sourcetype, action, dest_ip, dest_port, signature
        | sort - count
        '''
        
        return await self.search_splunk(query, time_range, "now")

    async def investigate_user(self, username: str, time_range: str) -> str:
        """Investigate user account"""
        query = f'''
        search index=* user="{username}" OR src_user="{username}"
        | stats count by action, src_ip, dest, sourcetype, status
        | sort - count
        '''
        
        return await self.search_splunk(query, time_range, "now")

    async def get_threat_intel(self, ioc_type: str, time_range: str) -> str:
        """Get threat intelligence data"""
        query = '''
        search index=* (threat OR malware OR suspicious OR ioc)
        | stats count by src_ip, dest_ip, signature, category, severity
        | where count > 1
        | sort - count
        '''
        
        return await self.search_splunk(query, time_range, "now")

    async def get_security_metrics(self, metric_type: str, time_range: str) -> str:
        """Get security metrics"""
        if metric_type == "alerts" or metric_type == "all":
            query = '''
            search index=* severity=*
            | stats count by severity
            | eval total=sum(count)
            '''
        elif metric_type == "threat_trends":
            query = '''
            search index=* (threat OR attack OR malware)
            | timechart span=1h count by category
            '''
        else:
            query = '''
            search index=*
            | stats count by sourcetype
            | sort - count
            '''
        
        return await self.search_splunk(query, time_range, "now")

    async def analyze_failed_logins(self, threshold: int, time_range: str) -> str:
        """Analyze failed login attempts"""
        query = f'''
        search index=* (failed OR failure OR invalid) (login OR authentication OR logon)
        | stats count by user, src_ip
        | where count >= {threshold}
        | sort - count
        '''
        
        return await self.search_splunk(query, time_range, "now")

    async def detect_data_exfiltration(self, threshold_mb: int, time_range: str) -> str:
        """Detect data exfiltration attempts"""
        query = f'''
        search index=* bytes > 0
        | eval mb = bytes/1024/1024
        | stats sum(mb) as total_mb by src_ip, dest_ip, user
        | where total_mb > {threshold_mb}
        | sort - total_mb
        '''
        
        return await self.search_splunk(query, time_range, "now")


async def main():
    """Run the MCP server"""
    server_instance = SplunkMCPServer()
    
    # Connect to Splunk on startup
    server_instance.connect_to_splunk()
    
    async with stdio_server() as (read_stream, write_stream):
        await server_instance.server.run(
            read_stream,
            write_stream,
            server_instance.server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
