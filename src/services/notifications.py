import aiohttp
from config import settings
import asyncio


async def send_price_alert(
    product_name: str, old_price: float, new_price: float, url: str
):
    drop_percentage = ((old_price - new_price) / old_price) * 100

    message = {
        "embeds": [
            {
                "title": "Price Drop Alert! 🎉",
                "description": f"**{product_name}**\nPrice dropped by {drop_percentage:.1f}%!\n"
                f"Old price: ${old_price:.2f}\n"
                f"New price: ${new_price:.2f}\n"
                f"[View Product]({url})",
            }
        ]
    }

    async with aiohttp.ClientSession() as session:
        await session.post(settings.DISCORD_WEBHOOK_URL, json=message)
