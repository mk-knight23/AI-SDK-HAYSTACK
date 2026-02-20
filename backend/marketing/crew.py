"""
CrewAI Marketing Crew for TrendFactory.

This module defines a crew of AI agents that collaborate to create
comprehensive marketing campaigns for trend analysis products.
"""

from crewai import Agent, Crew, Process, Task
from crewai.tools import tool
from typing import Dict, List, Any
import json


class MarketingCrew:
    """
    Marketing crew that orchestrates AI agents for campaign generation.

    The crew consists of:
    - ContentStrategist: Develops content strategy and messaging
    - Copywriter: Creates compelling copy for all channels
    - SEOExpert: Optimizes content for search engines
    - CampaignManager: Coordinates and manages the campaign
    """

    def __init__(self, openai_api_key: str = None):
        """Initialize the marketing crew with optional API key."""
        self.openai_api_key = openai_api_key
        self.crew = None
        self._create_agents()
        self._create_tasks()
        self._create_crew()

    def _create_agents(self) -> None:
        """Create all marketing agents with their specific roles."""

        self.content_strategist = Agent(
            role="Content Strategist",
            goal="Develop compelling content strategies that resonate with target audiences "
                 "and align with brand voice for trend analysis products",
            backstory="You are a seasoned content strategist with 10+ years of experience "
                      "in B2B SaaS marketing. You excel at understanding audience pain points "
                      "and crafting messaging that converts. You have deep expertise in "
                      "data analytics and trend analysis markets.",
            verbose=True,
            allow_delegation=True,
            llm_config={
                "model": "gpt-4",
                "temperature": 0.7,
            } if self.openai_api_key else None
        )

        self.copywriter = Agent(
            role="Copywriter",
            goal="Create engaging, persuasive copy for marketing campaigns that drives "
                 "conversions across all channels (email, social, web, ads)",
            backstory="You are an award-winning copywriter who has worked with Fortune 500 "
                      "companies. Your copy has generated millions in revenue. You specialize "
                      "in writing for data-driven products and making complex concepts accessible "
                      "and appealing to business audiences.",
            verbose=True,
            allow_delegation=False,
            llm_config={
                "model": "gpt-4",
                "temperature": 0.8,
            } if self.openai_api_key else None
        )

        self.seo_expert = Agent(
            role="SEO Expert",
            goal="Optimize all content for maximum search visibility and organic traffic "
                 "while maintaining readability and conversion potential",
            backstory="You are an SEO specialist with deep expertise in technical SEO, "
                      "content optimization, and keyword research. You have helped numerous "
                      "SaaS companies achieve first-page rankings for competitive keywords. "
                      "You stay current with all Google algorithm updates.",
            verbose=True,
            allow_delegation=False,
            llm_config={
                "model": "gpt-4",
                "temperature": 0.6,
            } if self.openai_api_key else None
        )

        self.campaign_manager = Agent(
            role="Campaign Manager",
            goal="Orchestrate all marketing activities into a cohesive campaign with "
                 "clear timelines, deliverables, and success metrics",
            backstory="You are a senior marketing campaign manager who has led go-to-market "
                      "strategies for multiple successful product launches. You excel at "
                      "project management, cross-functional coordination, and ensuring "
                      "all campaign elements work together seamlessly.",
            verbose=True,
            allow_delegation=True,
            llm_config={
                "model": "gpt-4",
                "temperature": 0.7,
            } if self.openai_api_key else None
        )

    def _create_tasks(self) -> None:
        """Create tasks for the marketing crew."""

        self.strategy_task = Task(
            description="""
            Develop a comprehensive content strategy for a marketing campaign about:
            {campaign_topic}

            Target Audience: {target_audience}
            Campaign Goals: {campaign_goals}
            Key Messages: {key_messages}

            Your output should include:
            1. Audience persona analysis
            2. Key messaging framework
            3. Content pillars and themes
            4. Channel strategy recommendations
            5. Content calendar outline

            Format your response as a structured strategy document.
            """,
            expected_output="A comprehensive content strategy document with all sections completed",
            agent=self.content_strategist
        )

        self.copywriting_task = Task(
            description="""
            Based on the content strategy provided, create compelling copy for:
            {campaign_topic}

            Create the following deliverables:
            1. Email sequence (3 emails: welcome, value proposition, CTA)
            2. Social media posts (2 for LinkedIn, 2 for Twitter/X)
            3. Landing page hero section copy
            4. Ad copy (Google Ads headline + description, 2 variations)
            5. Call-to-action variations (3 options)

            Ensure all copy:
            - Follows the messaging framework
            - Has a consistent brand voice
            - Includes compelling hooks
            - Drives toward the campaign goals

            Format as a copy deck with clear section headers.
            """,
            expected_output="A complete copy deck with all requested deliverables",
            agent=self.copywriter,
            context=[self.strategy_task]
        )

        self.seo_task = Task(
            description="""
            Optimize the campaign content for SEO:
            {campaign_topic}

            Provide the following:
            1. Primary keyword target with search volume estimate
            2. Secondary keywords (5-7 long-tail keywords)
            3. Title tag optimization (under 60 characters)
            4. Meta description (under 160 characters)
            5. Header structure recommendations (H1, H2, H3)
            6. Content optimization suggestions for landing page
            7. Internal linking strategy
            8. Schema markup recommendations

            Ensure all recommendations are actionable and specific to this campaign.
            """,
            expected_output="Complete SEO optimization guide with specific recommendations",
            agent=self.seo_expert,
            context=[self.strategy_task, self.copywriting_task]
        )

        self.campaign_plan_task = Task(
            description="""
            Create a comprehensive campaign execution plan for:
            {campaign_topic}

            Synthesize inputs from the strategy, copywriting, and SEO tasks to create:
            1. Campaign timeline with milestones
            2. Deliverables checklist
            3. Channel deployment schedule
            4. Success metrics and KPIs
            5. Budget allocation recommendations
            6. Risk mitigation strategies
            7. A/B testing plan
            8. Post-campaign analysis framework

            Format as a professional campaign plan document.
            """,
            expected_output="Complete campaign execution plan ready for implementation",
            agent=self.campaign_manager,
            context=[self.strategy_task, self.copywriting_task, self.seo_task]
        )

    def _create_crew(self) -> None:
        """Create the crew with all agents and tasks."""

        self.crew = Crew(
            agents=[
                self.content_strategist,
                self.copywriter,
                self.seo_expert,
                self.campaign_manager
            ],
            tasks=[
                self.strategy_task,
                self.copywriting_task,
                self.seo_task,
                self.campaign_plan_task
            ],
            process=Process.sequential,
            verbose=True
        )

    def generate_campaign(self, campaign_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a complete marketing campaign.

        Args:
            campaign_input: Dictionary containing:
                - campaign_topic: Main topic of the campaign
                - target_audience: Description of target audience
                - campaign_goals: What the campaign aims to achieve
                - key_messages: Core messages to communicate

        Returns:
            Dictionary with campaign results from all agents
        """
        result = self.crew.kickoff(inputs=campaign_input)

        return {
            "success": True,
            "campaign_topic": campaign_input.get("campaign_topic"),
            "results": result,
            "agents_used": [
                "ContentStrategist",
                "Copywriter",
                "SEOExpert",
                "CampaignManager"
            ]
        }


def create_marketing_crew(openai_api_key: str = None) -> MarketingCrew:
    """
    Factory function to create a marketing crew instance.

    Args:
        openai_api_key: Optional OpenAI API key for LLM access

    Returns:
        Configured MarketingCrew instance
    """
    return MarketingCrew(openai_api_key=openai_api_key)
