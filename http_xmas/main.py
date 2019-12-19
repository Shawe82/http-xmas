from typing import Dict, Optional

import httpx
import asyncio
import aiofiles

import os


async def get_all_comments() -> Dict:
    resp = await httpx.get("https://jsonplaceholder.typicode.com/comments")
    if resp.status_code == httpx.codes.OK:
        return resp.json()


async def get_post_from_comment(comment_id: int):
    async with httpx.Client(base_url="https://jsonplaceholder.typicode.com/") as api:
        resp = await api.get(f"comments/{comment_id}")
        resp.raise_for_status()
        comment = resp.json()
        resp = await api.get(f"posts/{comment['postId']}")
        resp.raise_for_status()
        return resp.json()


async def download(url:str, folder:str):
    filename = url.split("/")[-1]
    resp = await httpx.get(url)
    resp.raise_for_status()
    async with aiofiles.open(os.path.join(folder, filename), "wb") as f:
        await f.write(resp.content)


async def download_all_photos(out_dir: str):
    resp = await httpx.get("https://jsonplaceholder.typicode.com/photos")
    resp.raise_for_status()
    urls = list(set(d["url"] for d in resp.json()))
    os.makedirs(out_dir, exist_ok=True)
    await asyncio.gather(*[download(url, out_dir) for url in urls[:100]])


async def download_file(url: str, filename: Optional[str] = None) -> str:
    filename = filename or url.split("/")[-1]
    async with httpx.stream("GET", url) as resp:
        resp.raise_for_status()
        async with aiofiles.open(filename, "wb") as f:
            async for data in resp.aiter_bytes():
                if data:
                    await f.write(data)
    return filename


if __name__ == "__main__":
    asyncio.run(download_all_photos('din'))
    comments = asyncio.run(get_all_comments())
    post = asyncio.run(get_post_from_comment(1))
    filename = asyncio.run(
        download_file(
            "http://eforexcel.com/wp/wp-content/uploads/2017/07/1500000%20Sales%20Records.7z"
        )
    )
