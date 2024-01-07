import asyncio

import httpx


async def download_file_to_memory_async(url: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code == 200:
            return response.content
        else:
            print(f'Failed to download file from {url}')
            return None


def download_file_to_memory(url: str) -> bytes | None:
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(download_file_to_memory_async(url))
    except RuntimeError:
        loop = asyncio.new_event_loop()
        return loop.run_until_complete(download_file_to_memory_async(url))
