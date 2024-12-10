import logging
from typing import Optional, Dict, Any
from semantic_kernel.functions.kernel_function_decorator import kernel_function

logger = logging.getLogger(__name__)

class SummarizationSkill:
    """
    A skill for text summarization and analysis tasks.
    Provides capabilities for summarizing text, extracting key points,
    and generating titles.
    """

    def __init__(self):
        self.name = "SummarizationSkill"

    @kernel_function(
        description="Summarize the provided text content while maintaining key information",
        name="summarize_text"
    )
    async def summarize_text(self, context: str, max_length: Optional[int] = None) -> str:
        """
        Summarize the provided text content
        
        Args:
            context: The text content to summarize
            max_length: Optional maximum length for the summary
            
        Returns:
            str: A concise summary of the input text
        """
        try:
            if context is None:
                raise ValueError("Input text cannot be None")
                
            length_constraint = f"Keep the summary under {max_length} words." if max_length else ""
            
            prompt = f"""
            Please provide a concise summary of the following text:
            
            {context}
            
            Requirements:
            - Maintain the core message and key points
            - Use clear and professional language
            - Ensure accuracy and factual correctness
            {length_constraint}
            """
            
            logger.info(f"Executing text summarization for text of length {len(context)}")
            return prompt
        except Exception as e:
            logger.error(f"Summarization failed: {str(e)}")
            raise

    @kernel_function(
        description="Extract key points from the provided text",
        name="extract_key_points"
    )
    async def extract_key_points(self, context: str, num_points: Optional[int] = 5) -> str:
        """
        Extract key points from the provided text
        
        Args:
            context: The text content to analyze
            num_points: Optional number of key points to extract (default: 5)
            
        Returns:
            str: A list of key points from the text
        """
        try:
            if not context:
                raise ValueError("Input text cannot be empty")
                
            prompt = f"""
            Please extract {num_points} main key points from the following text:
            
            {context}
            
            Requirements:
            - Present points in order of importance
            - Use bullet points for clear formatting
            - Keep each point concise but informative
            - Maintain factual accuracy
            """
            
            logger.info(f"Executing key points extraction targeting {num_points} points")
            return prompt
        except Exception as e:
            logger.error(f"Key points extraction failed: {str(e)}")
            raise

    @kernel_function(
        description="Generate a title for the provided text",
        name="generate_title"
    )
    async def generate_title(self, context: str, style: str = "professional") -> str:
        """
        Generate a title for the provided text
        
        Args:
            context: The text content to generate a title for
            style: The style of the title (professional, creative, academic)
            
        Returns:
            str: A relevant title for the text
        """
        try:
            if context is None:
                raise ValueError("Input text cannot be None")
                
            style_guidance = {
                "professional": "clear, straightforward, and business-appropriate",
                "creative": "engaging, catchy, and memorable",
                "academic": "formal, descriptive, and scholarly"
            }.get(style, "professional")

            prompt = f"""
            Please generate a {style_guidance} title for the following text:
            
            {context}
            
            Requirements:
            - Title should be concise and relevant
            - Reflect the main topic or theme
            - Be appropriate for the {style} context
            - Capture reader interest
            """
            
            logger.info(f"Executing title generation with {style} style")
            return prompt
        except Exception as e:
            logger.error(f"Title generation failed: {str(e)}")
            raise

    @kernel_function(
        description="Analyze the sentiment and emotional tone of the provided text",
        name="analyze_sentiment"
    )
    async def analyze_sentiment(self, context: str) -> Dict[str, Any]:
        """
        Analyze the sentiment and emotional tone of the provided text
        
        Args:
            context: The text content to analyze
            
        Returns:
            Dict containing sentiment analysis results
        """
        try:
            prompt = f"""
            Please analyze the sentiment and emotional tone of the following text:
            
            {context}
            
            Provide analysis of:
            - Overall sentiment (positive/negative/neutral)
            - Emotional tones present
            - Confidence level in analysis
            - Key emotional indicators
            
            Format the response as a structured analysis.
            """
            
            logger.info("Executing sentiment analysis")
            return {"prompt": prompt}
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {str(e)}")
            raise

    @kernel_function(
        description="Create an academic-style abstract of the provided text",
        name="create_abstract"
    )
    async def create_abstract(self, context: str, target_audience: str = "general") -> str:
        """
        Create an academic-style abstract of the provided text
        
        Args:
            context: The text content to create an abstract for
            target_audience: The intended audience (general, academic, technical)
            
        Returns:
            str: An academic abstract of the text
        """
        try:
            prompt = f"""
            Please create a comprehensive abstract for the following text,
            targeted at a {target_audience} audience:
            
            {context}
            
            Requirements:
            - Follow academic abstract structure
            - Include research context
            - Summarize methodology (if applicable)
            - State key findings or arguments
            - Indicate implications or conclusions
            - Keep within 250 words
            """
            
            logger.info(f"Creating abstract for {target_audience} audience")
            return prompt
        except Exception as e:
            logger.error(f"Abstract creation failed: {str(e)}")
            raise
