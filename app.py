"""
app.py — SolutionA4U Leah AI Concierge Platform
Runs both bots concurrently using asyncio.
"""

import asyncio
import logging
import os
import sys

# Create logs directory if it doesn't exist
logs_dir = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(logs_dir, exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(os.path.join(logs_dir, "leah_platform.log")),
    ],
)
log = logging.getLogger(__name__)

from storage import init_db
from demo_bot import build_demo_app
from onboarding_bot import build_onboarding_app


async def run_both_bots():
    """Run both bots concurrently using asyncio."""
    init_db()
    log.info("=" * 60)
    log.info("  SolutionA4U Leah AI Concierge Platform")
    log.info("  Starting both bots...")
    log.info("=" * 60)

    demo_app = build_demo_app()
    onboarding_app = build_onboarding_app()

    # Initialize both applications
    async with demo_app, onboarding_app:
        await demo_app.start()
        await onboarding_app.start()

        log.info("✅ Demo bot started — @naples_luxury_guest_bot")
        log.info("✅ Onboarding bot started — @property_onboarding_bot")
        log.info("🚀 Both bots are live and polling for messages...")

        # Start polling for both bots
        await demo_app.updater.start_polling(drop_pending_updates=True)
        await onboarding_app.updater.start_polling(drop_pending_updates=True)

        # Keep running until interrupted
        try:
            await asyncio.Event().wait()
        except (KeyboardInterrupt, SystemExit):
            log.info("Shutdown signal received...")
        finally:
            await demo_app.updater.stop()
            await onboarding_app.updater.stop()
            await demo_app.stop()
            await onboarding_app.stop()
            log.info("Both bots stopped gracefully.")


if __name__ == "__main__":
    try:
        asyncio.run(run_both_bots())
    except KeyboardInterrupt:
        log.info("Platform stopped by user.")
