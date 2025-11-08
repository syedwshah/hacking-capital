#!/usr/bin/env python3

import os
import sys
sys.path.append('.')

from app.services.summary_service import SummaryService
from app.db.base import get_session

def run_batch_summaries():
    """Run batch AI-powered summaries for key symbols"""
    symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA"]
    period_days = 30

    print("🚀 Running batch AI-powered summarization for key symbols...")

    with get_session() as session:
        for symbol in symbols:
            print(f"📊 Generating AI summaries for {symbol}...")

            try:
                summaries = SummaryService().generate(symbol, "daily", period_days)

                if summaries:
                    print(f"✅ Generated {len(summaries)} summaries for {symbol}")
                    for summary in summaries:
                        print(f"   - Period: {summary['period']}, AI Summary: {summary.get('ai_summary', 'N/A')[:100]}...")
                else:
                    print(f"❌ No summaries generated for {symbol}")

            except Exception as e:
                print(f"❌ Error generating summaries for {symbol}: {e}")

    print("🎉 Batch summarization complete!")

if __name__ == "__main__":
    run_batch_summaries()
