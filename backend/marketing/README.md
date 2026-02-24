# CrewAI Marketing Crew

The Marketing Crew uses CrewAI to orchestrate multiple AI agents for generating comprehensive marketing campaigns.

## Overview

This module implements a team of 4 specialized AI agents that collaborate to create end-to-end marketing campaigns:

1. **ContentStrategist** - Analyzes audience and develops messaging strategy
2. **Copywriter** - Creates compelling copy across all channels
3. **SEOExpert** - Optimizes content for search visibility
4. **CampaignManager** - Synthesizes outputs into actionable execution plan

## Architecture

### Agent Workflow

```
User Input
    ↓
ContentStrategist (strategy_task)
    ↓
Copywriter (copywriting_task) ← context from strategy
    ↓
SEOExpert (seo_task) ← context from strategy + copy
    ↓
CampaignManager (campaign_plan_task) ← context from all previous
    ↓
Comprehensive Campaign Output
```

### Agent Configuration

| Agent | Role | Allow Delegation | Temperature | Purpose |
|-------|------|------------------|-------------|---------|
| ContentStrategist | Strategy development | Yes | 0.7 | Analyze audience, create messaging framework |
| Copywriter | Content creation | No | 0.8 | Write emails, social posts, ads |
| SEOExpert | Search optimization | No | 0.6 | Keywords, meta tags, structure |
| CampaignManager | Campaign orchestration | Yes | 0.7 | Timeline, KPIs, execution plan |

## Usage

### Basic Usage

```python
from marketing.crew import MarketingCrew, create_marketing_crew

# Method 1: Direct instantiation
crew = MarketingCrew(openai_api_key="your-api-key")

# Method 2: Factory function
crew = create_marketing_crew(openai_api_key="your-api-key")

# Generate campaign
campaign_input = {
    "campaign_topic": "AI-Powered Trend Analysis Platform Launch",
    "target_audience": "Data analysts and marketing managers",
    "campaign_goals": "Generate 500 qualified leads",
    "key_messages": "Real-time insights, competitive advantage"
}

result = crew.generate_campaign(campaign_input)

if result["success"]:
    print(f"Campaign generated for: {result['campaign_topic']}")
    print(f"Agents used: {result['agents_used']}")
    print(f"Results: {result['results']}")
else:
    print(f"Error: {result['error']}")
```

### Environment Configuration

Set your OpenAI API key:

```bash
export OPENAI_API_KEY=your-api-key-here
```

The crew will automatically pick up the API key from the environment.

## API Integration

### Endpoint

**POST** `/api/v1/generate-campaign`

### Request Schema

```json
{
  "campaign_topic": "string (required, max 500 chars)",
  "target_audience": "string (required, max 1000 chars)",
  "campaign_goals": "string (required, max 500 chars)",
  "key_messages": "string (required, max 1000 chars)"
}
```

### Response Schema

```json
{
  "success": boolean,
  "error": string | null,
  "data": {
    "campaign_topic": string,
    "results": {
      "strategy": "Content strategy document",
      "copy": "Copy deck with all deliverables",
      "seo": "SEO optimization guide",
      "campaign_plan": "Execution plan document"
    },
    "agents_used": ["ContentStrategist", "Copywriter", "SEOExpert", "CampaignManager"]
  }
}
```

## Task Details

### 1. Strategy Task

**Agent:** ContentStrategist

**Output:** Comprehensive content strategy document including:
- Audience persona analysis
- Key messaging framework
- Content pillars and themes
- Channel strategy recommendations
- Content calendar outline

### 2. Copywriting Task

**Agent:** Copywriter

**Context:** Strategy document

**Output:** Complete copy deck including:
- Email sequence (3 emails)
- Social media posts (2 LinkedIn, 2 Twitter/X)
- Landing page hero section
- Ad copy (Google Ads, 2 variations)
- Call-to-action variations (3 options)

### 3. SEO Task

**Agent:** SEOExpert

**Context:** Strategy + Copy

**Output:** SEO optimization guide including:
- Primary keyword target with search volume
- Secondary keywords (5-7 long-tail)
- Title tag optimization (under 60 chars)
- Meta description (under 160 chars)
- Header structure recommendations
- Content optimization suggestions
- Internal linking strategy
- Schema markup recommendations

### 4. Campaign Plan Task

**Agent:** CampaignManager

**Context:** All previous tasks

**Output:** Campaign execution plan including:
- Campaign timeline with milestones
- Deliverables checklist
- Channel deployment schedule
- Success metrics and KPIs
- Budget allocation recommendations
- Risk mitigation strategies
- A/B testing plan
- Post-campaign analysis framework

## Error Handling

The `generate_campaign` method includes comprehensive error handling:

```python
result = crew.generate_campaign(campaign_input)

if result["success"]:
    # Handle success
    pass
else:
    # Handle error
    error_msg = result["error"]
    if "Missing required fields" in error_msg:
        # Validate input
    elif "CrewAI not installed" in error_msg:
        # Install CrewAI
    else:
        # Generic error
```

## Testing

### Run Tests

```bash
# All tests
pytest tests/test_crew.py -v

# Specific test class
pytest tests/test_crew.py::TestContentStrategistAgent -v

# With coverage
pytest tests/test_crew.py --cov=marketing --cov-report=html
```

### Test Coverage

The test suite includes:
- Initialization tests (with/without API key)
- Agent configuration tests
- Task creation tests
- Campaign generation workflow tests
- Factory function tests

## Dependencies

- **crewai>=0.80.0** - Multi-agent orchestration framework
- **openai>=1.50.0** - LLM API for agent operations

## Troubleshooting

### CrewAI Import Error

```
ModuleNotFoundError: No module named 'crewai'
```

**Solution:**
```bash
pip install crewai>=0.80.0
```

### API Key Not Working

**Solution:**
1. Verify API key is valid
2. Check environment variable: `echo $OPENAI_API_KEY`
3. Ensure sufficient credits in OpenAI account

### Timeout Errors

**Solution:**
1. Check network connectivity
2. Reduce campaign complexity
3. Increase timeout in CrewAI configuration

## Advanced Configuration

### Custom LLM Configuration

```python
crew = MarketingCrew(openai_api_key="your-key")

# Access individual agents for custom configuration
crew.content_strategist.llm_config = {
    "model": "gpt-4-turbo",
    "temperature": 0.8,
    "max_tokens": 2000
}
```

### Parallel Execution

To run agents in parallel (advanced):

```python
from crewai import Process

crew.crew = Crew(
    agents=crew.crew.agents,
    tasks=crew.crew.tasks,
    process=Process.hierarchical,  # Instead of sequential
    verbose=True
)
```

## Best Practices

1. **Specific Inputs**: Provide detailed, specific campaign topics for better results
2. **Clear Goals**: Define measurable campaign goals
3. **Audience Understanding**: Be specific about target audience characteristics
4. **Iterative Refinement**: Use initial outputs to refine subsequent requests
5. **Review and Edit**: Always review AI-generated content before publishing

## License

MIT License - see [LICENSE](../../LICENSE) for details.
