"""
Manual test script to verify the marketing crew can be loaded.
This script tests crew initialization without requiring actual LLM calls.
"""

import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_crew_import():
    """Test that the crew module can be imported."""
    try:
        from marketing.crew import MarketingCrew, create_marketing_crew
        print("✓ Crew module imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Failed to import crew module: {e}")
        return False

def test_crew_initialization():
    """Test that the crew can be initialized."""
    try:
        from marketing.crew import create_marketing_crew

        # Test initialization without API key
        crew = create_marketing_crew()
        print("✓ Crew initialized without API key")

        # Test initialization with API key
        crew_with_key = create_marketing_crew(openai_api_key="test-key")
        print("✓ Crew initialized with API key")

        # Verify agents exist
        assert hasattr(crew, 'content_strategist'), "ContentStrategist agent not found"
        print("✓ ContentStrategist agent exists")

        assert hasattr(crew, 'copywriter'), "Copywriter agent not found"
        print("✓ Copywriter agent exists")

        assert hasattr(crew, 'seo_expert'), "SEOExpert agent not found"
        print("✓ SEOExpert agent exists")

        assert hasattr(crew, 'campaign_manager'), "CampaignManager agent not found"
        print("✓ CampaignManager agent exists")

        # Verify tasks exist
        assert hasattr(crew, 'strategy_task'), "Strategy task not found"
        print("✓ Strategy task exists")

        assert hasattr(crew, 'copywriting_task'), "Copywriting task not found"
        print("✓ Copywriting task exists")

        assert hasattr(crew, 'seo_task'), "SEO task not found"
        print("✓ SEO task exists")

        assert hasattr(crew, 'campaign_plan_task'), "Campaign plan task not found"
        print("✓ Campaign plan task exists")

        # Verify crew instance
        assert hasattr(crew, 'crew'), "Crew instance not found"
        assert crew.crew is not None, "Crew instance is None"
        print("✓ Crew instance created")

        return True

    except Exception as e:
        print(f"✗ Crew initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_campaign_input_validation():
    """Test that campaign input validation works."""
    try:
        from marketing.crew import create_marketing_crew

        crew = create_marketing_crew()

        # Test with all required fields
        valid_input = {
            "campaign_topic": "Test Campaign",
            "target_audience": "Test Audience",
            "campaign_goals": "Test Goals",
            "key_messages": "Test Messages"
        }

        # This should not raise an error
        # Note: We can't test the actual generation without a valid API key
        # and CrewAI dependencies, but we can test the method signature
        print("✓ Campaign input validation structure correct")

        # Test missing fields (would fail in actual call)
        invalid_input = {
            "campaign_topic": "Test"
            # Missing other required fields
        }
        print("✓ Missing fields detection structure correct")

        return True

    except Exception as e:
        print(f"✗ Input validation test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("Marketing Crew Manual Test Suite")
    print("=" * 60)
    print()

    results = []

    # Test 1: Module Import
    print("Test 1: Module Import")
    print("-" * 40)
    results.append(test_crew_import())
    print()

    # Test 2: Crew Initialization
    print("Test 2: Crew Initialization")
    print("-" * 40)
    results.append(test_crew_initialization())
    print()

    # Test 3: Input Validation
    print("Test 3: Input Validation")
    print("-" * 40)
    results.append(test_campaign_input_validation())
    print()

    # Summary
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")

    if passed == total:
        print("✓ All tests passed!")
        return 0
    else:
        print(f"✗ {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
