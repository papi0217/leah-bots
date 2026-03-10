#!/usr/bin/env python3
"""
LEAH Bots Platform — Unified Launcher
Runs both Demo Bot and Onboarding Bot simultaneously
"""

import os
import sys
import asyncio
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(name)s: %(message)s',
    handlers=[
        logging.FileHandler('leah_bots.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Import bot modules
try:
    from demo_bot import main_demo_bot
    from onboarding_bot import main_onboarding_bot
except ImportError as e:
    logger.error(f"❌ Failed to import bot modules: {str(e)}")
    sys.exit(1)

# ============================================================================
# UNIFIED LAUNCHER
# ============================================================================

async def run_both_bots():
    """Run both bots simultaneously"""
    
    logger.info("=" * 70)
    logger.info("🚀 LEAH BOTS PLATFORM — STARTING BOTH BOTS")
    logger.info("=" * 70)
    
    # Create tasks for both bots
    demo_task = asyncio.create_task(main_demo_bot())
    onboarding_task = asyncio.create_task(main_onboarding_bot())
    
    logger.info("")
    logger.info("✅ Both bots are now running!")
    logger.info("")
    logger.info("📱 Demo Bot: @leah_luxury_host_demo_bot")
    logger.info("   Purpose: Guest-facing luxury concierge")
    logger.info("")
    logger.info("📱 Onboarding Bot: @Leah_onboarding_bot")
    logger.info("   Purpose: Host-facing property management")
    logger.info("")
    logger.info("=" * 70)
    
    try:
        # Wait for both tasks
        await asyncio.gather(demo_task, onboarding_task)
    except KeyboardInterrupt:
        logger.info("")
        logger.info("🛑 Shutting down both bots...")
        demo_task.cancel()
        onboarding_task.cancel()
        logger.info("✅ Both bots stopped")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Fatal error: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    try:
        asyncio.run(run_both_bots())
    except KeyboardInterrupt:
        logger.info("🛑 Platform shutting down...")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Fatal error: {str(e)}")
        sys.exit(1)
