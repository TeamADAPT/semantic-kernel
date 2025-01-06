import pytest
import logging
from src.skills.summarization_skill import SummarizationSkill

# Configure logging for tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@pytest.fixture
def summarization_skill():
    """Fixture to create a SummarizationSkill instance"""
    return SummarizationSkill()

@pytest.fixture
def sample_text():
    """Fixture providing sample text for testing"""
    return """
    Artificial Intelligence (AI) has transformed various industries in recent years.
    Machine learning algorithms can now process vast amounts of data to identify patterns
    and make predictions. Deep learning, a subset of machine learning, has particularly
    excelled in areas like image recognition and natural language processing. The impact
    of AI continues to grow as new applications are discovered and implemented across
    different sectors.
    """

@pytest.mark.asyncio
async def test_summarize_text(summarization_skill, sample_text):
    """Test the summarize_text function"""
    try:
        result = await summarization_skill.summarize_text(sample_text)
        
        assert result is not None
        assert isinstance(result, str)
        assert len(result) > 0
        
        # Check if the prompt contains key requirements
        assert "concise summary" in result.lower()
        assert "core message" in result.lower()
        assert sample_text in result
        
        logger.info("summarize_text test passed successfully")
    except Exception as e:
        logger.error(f"summarize_text test failed: {str(e)}")
        raise

@pytest.mark.asyncio
async def test_summarize_text_with_length_constraint(summarization_skill, sample_text):
    """Test summarize_text with max_length parameter"""
    max_length = 100
    try:
        result = await summarization_skill.summarize_text(sample_text, max_length)
        
        assert result is not None
        assert isinstance(result, str)
        assert f"under {max_length} words" in result.lower()
        
        logger.info("summarize_text with length constraint test passed successfully")
    except Exception as e:
        logger.error(f"summarize_text with length constraint test failed: {str(e)}")
        raise

@pytest.mark.asyncio
async def test_extract_key_points(summarization_skill, sample_text):
    """Test the extract_key_points function"""
    try:
        result = await summarization_skill.extract_key_points(sample_text)
        
        assert result is not None
        assert isinstance(result, str)
        assert "bullet points" in result.lower()
        assert sample_text in result
        
        logger.info("extract_key_points test passed successfully")
    except Exception as e:
        logger.error(f"extract_key_points test failed: {str(e)}")
        raise

@pytest.mark.asyncio
async def test_extract_key_points_with_custom_number(summarization_skill, sample_text):
    """Test extract_key_points with custom number of points"""
    num_points = 3
    try:
        result = await summarization_skill.extract_key_points(sample_text, num_points)
        
        assert result is not None
        assert isinstance(result, str)
        assert str(num_points) in result
        
        logger.info("extract_key_points with custom number test passed successfully")
    except Exception as e:
        logger.error(f"extract_key_points with custom number test failed: {str(e)}")
        raise

@pytest.mark.asyncio
async def test_generate_title(summarization_skill, sample_text):
    """Test the generate_title function"""
    try:
        result = await summarization_skill.generate_title(sample_text)
        
        assert result is not None
        assert isinstance(result, str)
        assert "generate" in result.lower()
        assert "title" in result.lower()
        assert sample_text in result
        
        logger.info("generate_title test passed successfully")
    except Exception as e:
        logger.error(f"generate_title test failed: {str(e)}")
        raise

@pytest.mark.asyncio
async def test_generate_title_with_style(summarization_skill, sample_text):
    """Test generate_title with different styles"""
    styles = ["professional", "creative", "academic"]
    
    for style in styles:
        try:
            result = await summarization_skill.generate_title(sample_text, style)
            
            assert result is not None
            assert isinstance(result, str)
            assert style in result.lower()
            
            logger.info(f"generate_title with {style} style test passed successfully")
        except Exception as e:
            logger.error(f"generate_title with {style} style test failed: {str(e)}")
            raise

@pytest.mark.asyncio
async def test_analyze_sentiment(summarization_skill, sample_text):
    """Test the analyze_sentiment function"""
    try:
        result = await summarization_skill.analyze_sentiment(sample_text)
        
        assert result is not None
        assert isinstance(result, dict)
        assert "prompt" in result
        assert "sentiment" in result["prompt"].lower()
        assert "emotional tone" in result["prompt"].lower()
        
        logger.info("analyze_sentiment test passed successfully")
    except Exception as e:
        logger.error(f"analyze_sentiment test failed: {str(e)}")
        raise

@pytest.mark.asyncio
async def test_create_abstract(summarization_skill, sample_text):
    """Test the create_abstract function"""
    try:
        result = await summarization_skill.create_abstract(sample_text)
        
        assert result is not None
        assert isinstance(result, str)
        assert "abstract" in result.lower()
        assert "academic" in result.lower()
        assert sample_text in result
        
        logger.info("create_abstract test passed successfully")
    except Exception as e:
        logger.error(f"create_abstract test failed: {str(e)}")
        raise

@pytest.mark.asyncio
async def test_create_abstract_with_target_audience(summarization_skill, sample_text):
    """Test create_abstract with different target audiences"""
    audiences = ["general", "academic", "technical"]
    
    for audience in audiences:
        try:
            result = await summarization_skill.create_abstract(sample_text, audience)
            
            assert result is not None
            assert isinstance(result, str)
            assert audience in result.lower()
            
            logger.info(f"create_abstract with {audience} audience test passed successfully")
        except Exception as e:
            logger.error(f"create_abstract with {audience} audience test failed: {str(e)}")
            raise

@pytest.mark.asyncio
async def test_error_handling(summarization_skill):
    """Test error handling with invalid inputs"""
    with pytest.raises(Exception):
        await summarization_skill.summarize_text(None)
    
    with pytest.raises(Exception):
        await summarization_skill.extract_key_points("")
    
    with pytest.raises(Exception):
        await summarization_skill.generate_title(None)
    
    logger.info("Error handling tests passed successfully")
