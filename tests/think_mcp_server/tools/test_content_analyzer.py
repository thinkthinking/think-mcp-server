"""Test content analyzer tool."""
import os
import pytest
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
from think_mcp_server.tools.content_analyzer import analyze_file_content, generate_front_matter, analyze_content

@pytest.fixture
def temp_test_file():
    """Create a temporary test file."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write("Test content for analysis")
        temp_path = f.name
    yield temp_path
    os.unlink(temp_path)

@pytest.fixture
def temp_test_dir():
    """Create a temporary test directory with some files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a few test files
        for i in range(2):
            with open(os.path.join(temp_dir, f'test_{i}.txt'), 'w') as f:
                f.write(f"Test content {i}")
        yield temp_dir

@pytest.mark.asyncio
async def test_analyze_file_content_single_file(temp_test_file):
    """Test analyzing a single file."""
    mock_response = {"type": "text", "text": "This is a test analysis"}
    
    with patch('think_mcp.tools.content_analyzer.LLMClient') as mock_client:
        # Setup mock client
        mock_instance = MagicMock()
        mock_instance.chat = AsyncMock(return_value=(None, "This is a test analysis"))
        mock_client.return_value = mock_instance

        result = await analyze_file_content(temp_test_file)
        
        assert isinstance(result, dict)
        assert result["type"] == "text"
        assert isinstance(result["text"], str)
        assert mock_instance.chat.called

@pytest.mark.asyncio
async def test_analyze_file_content_directory(temp_test_dir):
    """Test analyzing a directory."""
    with patch('think_mcp.tools.content_analyzer.LLMClient') as mock_client:
        # Setup mock client
        mock_instance = MagicMock()
        mock_instance.chat = AsyncMock(return_value=(None, "Test analysis"))
        mock_client.return_value = mock_instance

        result = await analyze_file_content(temp_test_dir)
        
        assert isinstance(result, dict)
        assert result["type"] == "text"
        assert isinstance(result["text"], str)
        assert "test_0.txt" in result["text"]
        assert "test_1.txt" in result["text"]
        assert mock_instance.chat.call_count == 2

@pytest.mark.asyncio
async def test_analyze_file_content_nonexistent_path():
    """Test analyzing a non-existent path."""
    result = await analyze_file_content("/nonexistent/path")
    assert isinstance(result, dict)
    assert result["type"] == "text"
    assert "Error" in result["text"]

def test_generate_front_matter():
    """Test front matter generation."""
    description = "Test description"
    file_path = "test.md"
    front_matter = generate_front_matter(file_path, description)
    
    assert "---" in front_matter
    assert "description: Test description" in front_matter
    assert "name: test" in front_matter

@pytest.mark.asyncio
async def test_analyze_content(temp_test_file):
    """Test the analyze_content function."""
    with patch('think_mcp.tools.content_analyzer.analyze_file_content') as mock_analyze:
        mock_analyze.return_value = {"type": "text", "text": "Test analysis"}
        
        arguments = {"file_path": temp_test_file}
        await analyze_content(arguments)
        
        assert mock_analyze.called
        mock_analyze.assert_called_once_with(temp_test_file)

@pytest.mark.asyncio
async def test_analyze_content_no_arguments():
    """Test analyze_content with no arguments."""
    with pytest.raises(ValueError, match="Missing file_path argument"):
        await analyze_content(None)
