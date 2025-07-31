"""
MCP Server Startup Script

Launch the Vehicle Price Prediction MCP Server
"""

import os
import sys
import logging
from pathlib import Path

# Add src directory to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from src.mcp_server import VehiclePriceMCPServer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('mcp_server.log')
    ]
)

logger = logging.getLogger(__name__)


def main():
    """Main function to start MCP server."""
    try:
        print("🚗 Vehicle Price Prediction MCP Server")
        print("=" * 50)
        print("🔧 Initializing MCP server...")
        
        # Create and run MCP server
        server = VehiclePriceMCPServer()
        server.run(host="localhost", port=3000)
        
    except KeyboardInterrupt:
        print("\\n⏹️  Server stopped by user")
        logger.info("MCP server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {str(e)}")
        logger.error(f"MCP server error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
