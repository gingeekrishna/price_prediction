"""
AWS Bedrock Agent for Foundation Model Integration

Provides natural language explanations and insights using AWS Bedrock foundation models.
Supports Claude via Bedrock, Amazon Titan, AI21 Jurassic, and other foundation models.
"""

import os
import json
import logging
from typing import Dict, Any, Optional

try:
    import boto3
    from botocore.exceptions import ClientError, NoCredentialsError
except ImportError:
    boto3 = None
    ClientError = Exception
    NoCredentialsError = Exception

logger = logging.getLogger(__name__)

class BedrockAgent:
    """
    Agent for interacting with AWS Bedrock foundation models.
    """
    
    def __init__(self, 
                 model_id: str = "anthropic.claude-3-sonnet-20240229-v1:0",
                 region_name: str = "us-east-1",
                 aws_access_key_id: str = None,
                 aws_secret_access_key: str = None,
                 timeout: int = 30):
        """
        Initialize Bedrock Agent.
        
        Args:
            model_id: Bedrock foundation model ID
            region_name: AWS region name
            aws_access_key_id: AWS access key (optional, can use IAM roles)
            aws_secret_access_key: AWS secret key (optional, can use IAM roles)
            timeout: Request timeout in seconds
        """
        self.model_id = model_id
        self.region_name = region_name
        self.timeout = timeout
        
        # Get AWS credentials from environment or parameters
        self.aws_access_key_id = aws_access_key_id or os.getenv("AWS_ACCESS_KEY_ID")
        self.aws_secret_access_key = aws_secret_access_key or os.getenv("AWS_SECRET_ACCESS_KEY")
        
        # Initialize availability check
        self.available = False
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the Bedrock client."""
        if boto3 is None:
            logger.warning("Bedrock agent not available: boto3 package not installed.")
            return
        
        # Check for local development mode
        use_mock = os.getenv("BEDROCK_USE_MOCK", "false").lower() == "true"
        if use_mock:
            logger.info("Using mock Bedrock agent for local development")
            self.available = True
            self.client = "mock"  # Mock client indicator
            return
        
        try:
            # Create Bedrock client
            if self.aws_access_key_id and self.aws_secret_access_key:
                self.client = boto3.client(
                    'bedrock-runtime',
                    region_name=self.region_name,
                    aws_access_key_id=self.aws_access_key_id,
                    aws_secret_access_key=self.aws_secret_access_key
                )
            else:
                # Use default credential chain (IAM roles, profiles, etc.)
                self.client = boto3.client(
                    'bedrock-runtime',
                    region_name=self.region_name
                )
            
            # Test connection
            self._test_connection()
            self.available = True
            logger.info(f"Bedrock agent initialized successfully with model: {self.model_id}")
            
        except NoCredentialsError:
            logger.warning("Bedrock agent not available: AWS credentials not found.")
        except Exception as e:
            logger.warning(f"Bedrock agent not available: {e}")
            
            # Fall back to mock mode for local development
            if os.getenv("BEDROCK_FALLBACK_TO_MOCK", "true").lower() == "true":
                logger.info("Falling back to mock Bedrock agent for local development")
                self.available = True
                self.client = "mock"
    
    def _test_connection(self):
        """Test the Bedrock connection."""
        try:
            # Make a simple call to verify connection
            test_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 10,
                "messages": [{"role": "user", "content": "Hello"}]
            }
            
            self.client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(test_body)
            )
        except Exception as e:
            raise Exception(f"Bedrock connection test failed: {e}")
    
    def generate_explanation(self, vehicle_data: Dict[str, Any], market_data: Dict[str, Any], predicted_price: float) -> str:
        """
        Generate vehicle price explanation using Bedrock foundation model.
        
        Args:
            vehicle_data: Dictionary containing vehicle information
            market_data: Dictionary containing market data
            predicted_price: Predicted price value
            
        Returns:
            Generated explanation string
        """
        if not self.available:
            return "AWS Bedrock not available. Please configure AWS credentials and install boto3."
        
        # Check if using mock mode
        if self.client == "mock":
            return self._generate_mock_explanation(vehicle_data, market_data, predicted_price)
        
        # Create prompt
        prompt = f"""
As an automotive expert, explain this vehicle price prediction concisely:

Vehicle: {vehicle_data.get('year', 'Unknown')} {vehicle_data.get('make', '')} {vehicle_data.get('model', '')}, {vehicle_data.get('mileage', 'Unknown')} miles
Market: {market_data.get('trend', 'N/A')}, Avg Price: ${market_data.get('avg_price', 'N/A')}
Predicted Price: ${predicted_price:,.2f}

Provide a brief explanation covering:
1. Why this price is reasonable based on market conditions
2. Key factors affecting the vehicle's value (age, mileage, brand reputation)
3. One actionable recommendation for the buyer/seller

Keep response under 150 words and professional. Focus on data-driven insights.
"""
        
        try:
            return self._invoke_model(prompt)
        except Exception as e:
            logger.error(f"Bedrock API error: {e}")
            return f"Bedrock LLM error: {str(e)}"
    
    def _generate_mock_explanation(self, vehicle_data: Dict[str, Any], market_data: Dict[str, Any], predicted_price: float) -> str:
        """Generate mock explanation for local development."""
        import time
        import random
        
        # Simulate API delay
        time.sleep(random.uniform(0.5, 1.0))
        
        make = vehicle_data.get('make', 'Unknown')
        model = vehicle_data.get('model', 'Unknown')
        year = vehicle_data.get('year', 'Unknown')
        mileage = vehicle_data.get('mileage', 'Unknown')
        age = vehicle_data.get('vehicle_age', 'Unknown')
        
        mock_explanation = f"""This {year} {make} {model} is priced at ${predicted_price:,.2f}, which aligns well with current market conditions.

Key Value Factors:
• Vehicle Age: {age} years - {'Excellent' if age < 3 else 'Good' if age < 7 else 'Fair'} depreciation position
• Mileage: {mileage:,} miles - {'Low' if mileage < 50000 else 'Average' if mileage < 100000 else 'High'} usage indicator  
• Brand Reputation: {make} maintains {'strong' if make in ['Toyota', 'Honda', 'Lexus'] else 'solid'} resale value

Market Analysis: Current trend shows {market_data.get('trend', 'stable')} conditions with average prices around ${market_data.get('avg_price', predicted_price):,.2f}.

Recommendation: {'Consider this a good value' if predicted_price < market_data.get('avg_price', predicted_price) else 'Price is competitive but verify maintenance records'} and compare with similar vehicles in your area.

🏗️ [LOCAL DEVELOPMENT MODE - Mock Bedrock Response]"""
        
        return mock_explanation
    
    def _invoke_model(self, prompt: str) -> str:
        """
        Invoke the Bedrock model with the given prompt.
        
        Args:
            prompt: Input prompt string
            
        Returns:
            Model response text
        """
        # Handle different model families
        if "anthropic.claude" in self.model_id:
            return self._invoke_claude_bedrock(prompt)
        elif "amazon.titan" in self.model_id:
            return self._invoke_titan(prompt)
        elif "ai21.j2" in self.model_id:
            return self._invoke_ai21(prompt)
        elif "cohere.command" in self.model_id:
            return self._invoke_cohere(prompt)
        else:
            # Default to Claude format
            return self._invoke_claude_bedrock(prompt)
    
    def _invoke_claude_bedrock(self, prompt: str) -> str:
        """Invoke Claude model via Bedrock."""
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 300,
            "temperature": 0.7,
            "messages": [{"role": "user", "content": prompt}]
        }
        
        response = self.client.invoke_model(
            modelId=self.model_id,
            body=json.dumps(body)
        )
        
        response_body = json.loads(response['body'].read())
        return response_body['content'][0]['text']
    
    def _invoke_titan(self, prompt: str) -> str:
        """Invoke Amazon Titan model."""
        body = {
            "inputText": prompt,
            "textGenerationConfig": {
                "maxTokenCount": 300,
                "temperature": 0.7,
                "stopSequences": []
            }
        }
        
        response = self.client.invoke_model(
            modelId=self.model_id,
            body=json.dumps(body)
        )
        
        response_body = json.loads(response['body'].read())
        return response_body['results'][0]['outputText']
    
    def _invoke_ai21(self, prompt: str) -> str:
        """Invoke AI21 Jurassic model."""
        body = {
            "prompt": prompt,
            "maxTokens": 300,
            "temperature": 0.7,
            "topP": 1,
            "stopSequences": [],
            "countPenalty": {"scale": 0},
            "presencePenalty": {"scale": 0},
            "frequencyPenalty": {"scale": 0}
        }
        
        response = self.client.invoke_model(
            modelId=self.model_id,
            body=json.dumps(body)
        )
        
        response_body = json.loads(response['body'].read())
        return response_body['completions'][0]['data']['text']
    
    def _invoke_cohere(self, prompt: str) -> str:
        """Invoke Cohere Command model."""
        body = {
            "prompt": prompt,
            "max_tokens": 300,
            "temperature": 0.7,
            "p": 0.75,
            "k": 0,
            "stop_sequences": [],
            "return_likelihoods": "NONE"
        }
        
        response = self.client.invoke_model(
            modelId=self.model_id,
            body=json.dumps(body)
        )
        
        response_body = json.loads(response['body'].read())
        return response_body['generations'][0]['text']
    
    def get_available_models(self) -> list:
        """
        Get list of available Bedrock foundation models.
        
        Returns:
            List of available model IDs
        """
        if not self.available:
            return []
        
        try:
            bedrock_client = boto3.client('bedrock', region_name=self.region_name)
            response = bedrock_client.list_foundation_models()
            return [model['modelId'] for model in response['modelSummaries']]
        except Exception as e:
            logger.error(f"Error listing Bedrock models: {e}")
            return []
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the current model.
        
        Returns:
            Dictionary with model information
        """
        return {
            "model_id": self.model_id,
            "region": self.region_name,
            "available": self.available,
            "provider": "AWS Bedrock",
            "model_family": self._get_model_family()
        }
    
    def _get_model_family(self) -> str:
        """Get the model family name."""
        if "anthropic.claude" in self.model_id:
            return "Anthropic Claude"
        elif "amazon.titan" in self.model_id:
            return "Amazon Titan"
        elif "ai21.j2" in self.model_id:
            return "AI21 Jurassic"
        elif "cohere.command" in self.model_id:
            return "Cohere Command"
        elif "meta.llama" in self.model_id:
            return "Meta Llama"
        else:
            return "Unknown"


class BedrockAgentManager:
    """
    Manager for multiple Bedrock agents with different models.
    """
    
    def __init__(self):
        self.agents = {}
        self.default_models = [
            "anthropic.claude-3-sonnet-20240229-v1:0",
            "anthropic.claude-3-haiku-20240307-v1:0", 
            "amazon.titan-text-express-v1",
            "ai21.j2-ultra-v1",
            "cohere.command-text-v14"
        ]
    
    def get_agent(self, model_id: str = None) -> BedrockAgent:
        """
        Get or create a Bedrock agent for the specified model.
        
        Args:
            model_id: Model ID to use (optional)
            
        Returns:
            BedrockAgent instance
        """
        if not model_id:
            model_id = self.default_models[0]
        
        if model_id not in self.agents:
            self.agents[model_id] = BedrockAgent(model_id=model_id)
        
        return self.agents[model_id]
    
    def get_best_available_agent(self) -> Optional[BedrockAgent]:
        """
        Get the best available Bedrock agent.
        
        Returns:
            BedrockAgent instance or None if none available
        """
        for model_id in self.default_models:
            agent = self.get_agent(model_id)
            if agent.available:
                return agent
        return None
    
    def list_available_models(self) -> Dict[str, bool]:
        """
        List all models and their availability status.
        
        Returns:
            Dictionary mapping model IDs to availability status
        """
        status = {}
        for model_id in self.default_models:
            agent = self.get_agent(model_id)
            status[model_id] = agent.available
        return status
