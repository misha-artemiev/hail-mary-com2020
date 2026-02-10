from internal.geolocation.location import get_location
import asyncio


async def some():
    print(await get_location("university of exeter, exeter"))


asyncio.run(some())
