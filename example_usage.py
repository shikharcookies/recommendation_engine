"""Example usage of the Counterparty Recommendation Engine."""
import asyncio
from app.services.analysis_service import AnalysisService


async def main():
    """Run example analysis."""
    
    # Sample counterparty data
    counterparty_data = {
        "name": "Example Bank",
        "country": "USA",
        "sector": "Banking",
        "intrinsic_hrc": 3.5,
        "intrinsic_pd": 0.02,
        "counterparty_hrc": 3.2,
        "counterparty_pd": 0.015
    }
    
    # Sample analysis text
    analysis_text = """
    Company Profile:
    Example Bank is a leading financial institution with strong market presence.
    
    Assets:
    The bank maintains a diversified asset portfolio with NPL ratio of 2.3%.
    
    Liquidity:
    Strong liquidity position with LCR of 145%.
    
    Strategy:
    Focus on digital transformation and customer experience.
    
    Means:
    Well-capitalized with CET1 ratio of 13.5%.
    
    Performance:
    ROAE of 11.2% and cost-to-income ratio of 55%.
    """
    
    analysis_input = {
        "analysis_text": analysis_text
    }
    
    # Create analysis service
    service = AnalysisService()
    
    print("Running analysis...")
    try:
        result = await service.create_analysis(
            counterparty_data=counterparty_data,
            analysis_input=analysis_input
        )
        
        print(f"\n✓ Analysis completed successfully!")
        print(f"Analysis ID: {result['analysis_id']}")
        print(f"\nScores:")
        print(f"  Asset Quality: {result['scores']['asset_quality']}/5")
        print(f"  Liquidity: {result['scores']['liquidity']}/5")
        print(f"  Capitalisation: {result['scores']['capitalisation']}/5")
        print(f"  Profitability: {result['scores']['profitability']}/5")
        print(f"\nMemo:\n{result['memo']}")
        
    except Exception as e:
        print(f"✗ Error: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main())
