"""Script to run content analyzer directly."""
import asyncio
import argparse
import logging
from pathlib import Path
import sys

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.append(str(project_root))

from think_mcp_server.tools.content_analyzer import analyze_content

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),  # 输出到标准输出
        logging.FileHandler('content_analyzer.log', encoding='utf-8')  # 输出到文件
    ]
)

# 确保所有相关模块的日志级别都是 DEBUG
logging.getLogger('think_mcp').setLevel(logging.DEBUG)
logging.getLogger('think_mcp.tools').setLevel(logging.DEBUG)
logging.getLogger('think_mcp.tools.content_analyzer').setLevel(logging.DEBUG)

async def main():
    parser = argparse.ArgumentParser(description='Run content analyzer on a file or directory')
    parser.add_argument('path', help='Path to file or directory to analyze')
    args = parser.parse_args()

    try:
        # Convert to absolute path
        abs_path = str(Path(args.path).resolve())
        print(f"\nAnalyzing: {abs_path}")
        
        # Call analyze_content
        result = await analyze_content({"file_path": abs_path})
        
        print("\nAnalysis Result:")
        for content in result:
            print(content.text)
            
    except Exception as e:
        print(f"\nError: {str(e)}")
        logging.error("Error running content analyzer", exc_info=True)

if __name__ == '__main__':
    asyncio.run(main())
