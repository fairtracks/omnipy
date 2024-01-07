import asyncio
from multiprocessing.pool import ThreadPool

import httpx


async def download_file_to_memory_async(url: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code == 200:
            return response.content
        else:
            return None


def run_in_thread(url):
    return asyncio.run(download_file_to_memory_async(url))


def download_file_to_memory(url: str) -> bytes | None:
    with ThreadPool(processes=1) as pool:
        async_result = pool.apply_async(run_in_thread, (url,))
        return async_result.get()
