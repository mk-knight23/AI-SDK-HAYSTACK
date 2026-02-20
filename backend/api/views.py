from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import os


@api_view(['GET'])
def health_check(request):
    """Health check endpoint for monitoring and load balancers."""
    return Response({
        'status': 'healthy',
        'service': 'trendfactory-backend',
        'version': '1.0.0'
    })


@api_view(['POST'])
def generate_campaign(request):
    """
    Generate a marketing campaign using CrewAI.

    Request Body:
        - campaign_topic (str): Main topic of the campaign
        - target_audience (str): Description of target audience
        - campaign_goals (str): What the campaign aims to achieve
        - key_messages (str): Core messages to communicate

    Returns:
        - success (bool): Whether the campaign generation was successful
        - campaign_topic (str): The topic of the generated campaign
        - results (dict): Full campaign results from all agents
        - agents_used (list): List of agents that contributed

    Example:
        POST /api/v1/generate-campaign
        {
            "campaign_topic": "AI-Powered Trend Analysis Platform Launch",
            "target_audience": "Data analysts and marketing managers at mid-market companies",
            "campaign_goals": "Generate 500 qualified leads in Q1 2025",
            "key_messages": "Real-time insights, competitive advantage, easy integration"
        }
    """
    try:
        # Validate required fields
        required_fields = ['campaign_topic', 'target_audience', 'campaign_goals', 'key_messages']
        missing_fields = [field for field in required_fields if field not in request.data]

        if missing_fields:
            return Response({
                'success': False,
                'error': f"Missing required fields: {', '.join(missing_fields)}",
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)

        # Import marketing crew
        from marketing.crew import create_marketing_crew

        # Get API key from environment (optional - crew can work without it in demo mode)
        openai_api_key = os.environ.get('OPENAI_API_KEY')

        # Create marketing crew
        crew = create_marketing_crew(openai_api_key=openai_api_key)

        # Prepare campaign input
        campaign_input = {
            'campaign_topic': request.data.get('campaign_topic'),
            'target_audience': request.data.get('target_audience'),
            'campaign_goals': request.data.get('campaign_goals'),
            'key_messages': request.data.get('key_messages')
        }

        # Generate campaign
        result = crew.generate_campaign(campaign_input)

        return Response({
            'success': True,
            'data': result,
            'error': None
        }, status=status.HTTP_200_OK)

    except ImportError as e:
        return Response({
            'success': False,
            'error': f"CrewAI not installed or import error: {str(e)}",
            'data': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except Exception as e:
        return Response({
            'success': False,
            'error': f"Campaign generation failed: {str(e)}",
            'data': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
