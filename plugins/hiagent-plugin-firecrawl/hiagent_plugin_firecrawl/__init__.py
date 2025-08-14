import asyncio
import logging
import time
from collections.abc import Mapping
from typing import Annotated, Any, Optional
import os
from pathlib import Path

from pydantic import Field
from requests.exceptions import HTTPError

from hiagent_plugin_sdk import BasePlugin, set_meta, SecretField, ConfigValidateMixin, BuiltinCategory, assrf_request
from hiagent_plugin_firecrawl.crawl import CrawlResult
from hiagent_plugin_firecrawl.scrape import ScrapeResult
from hiagent_plugin_firecrawl.map import MapResult

logger = logging.getLogger(__name__)

current_dir = Path(os.path.dirname(os.path.abspath(__file__)))

@set_meta(cn_name="Firecrawl")
class FirecrawlPlugin(BasePlugin, ConfigValidateMixin):
    """Firecrawl API 集成，用于网页爬取和数据抓取。"""
    hiagent_tools = ["crawl", "crawl_job", "map", "scrape"]
    hiagent_category = BuiltinCategory.WebSearch

    def __init__(
        self,
        api_key: Annotated[str, SecretField(title="Firecrawl API 密钥", description="如何获取: https://www.firecrawl.dev/account")],
        base_url: Annotated[str, Field(description="Firecrawl服务器的API URL")] = "https://api.firecrawl.dev"
    ):
        self.api_key = api_key
        self.base_url = base_url or "https://api.firecrawl.dev"

    async def _validate(self):
        if not self.api_key:
            raise ValueError("api_key is empty")
        if not self.base_url:
            raise ValueError("base_url is empty")

    @classmethod
    def _icon_uri(cls) -> str:
        return f"file://{current_dir}/icon.png"

    async def crawl(
        self,
        url: Annotated[str, Field(description="要抓取并提取数据的网站URL。")]
    ) -> CrawlResult:
        """深度爬取。递归爬取一个网址的子域名，并收集内容。"""
        result = await self._crawl_url(url)
        return CrawlResult(**result)

    async def crawl_job(
        self,
        job_id: Annotated[str, Field(description="在深度爬取工具中将等待爬取结果设置为否可以获取Job ID。")],
        operation: Annotated[str, Field(description="操作。get：查询，cancel：取消。")]
    ) -> CrawlResult:
        """爬取任务处理。根据爬取任务ID获取爬取结果，或者取消爬取任务"""
        if operation == 'get':
            result = await self._check_crawl_status(job_id=job_id)
        elif operation == 'cancel':
            result = await self._cancel_crawl_job(job_id=job_id)
        else:
            raise ValueError(f'Invalid operation: {operation}')

        return CrawlResult(**result)

    async def map(
        self,
        url: Annotated[str, Field(description="要抓取并提取数据的网站URL。")],
        search: Annotated[str, Field(description="用于映射的搜索查询。在Alpha阶段，搜索功能的“智能”部分限制为最多100个搜索结果。然而，如果地图找到了更多结果，则不施加任何限制。")] = ""
    ) -> MapResult:
        """地图式爬取。输入一个网站，快速获取网站上的所有网址。"""
        result = await self._map_url(url, search)
        return MapResult(**result)

    async def scrape(
        self,
        url: Annotated[str, Field(description="要抓取并提取数据的网站URL。")]
    ) -> ScrapeResult:
        """单页面抓取。将任何网址转换为干净的数据。"""
        result = await self._scrape_url(url)
        return ScrapeResult(**result)

    async def _crawl_url(
        self, url: str,
        wait: bool = True,
        poll_interval: int = 2,
        idempotency_key: Optional[str] = None,
        timeout: float = 60,
        **kwargs
    ) -> Mapping[str, Any]:
        start_time = time.time()
        endpoint = f'{self.base_url}/v0/crawl'
        headers = self._prepare_headers(idempotency_key)
        data = {'url': url, **kwargs}
        logger.debug(f"Sent request to {endpoint=} body={data}")
        response = await self._request('POST', endpoint, data, headers, timeout=timeout)
        if response is None:
            raise HTTPError("Failed to initiate crawl after multiple retries")
        job_id: str = response['jobId']
        if wait:
            timeout = timeout - (time.time() - start_time)
            return await self._monitor_job_status(job_id=job_id, poll_interval=poll_interval, timeout=timeout)
        return response

    async def _scrape_url(
        self,
        url: str,
        **kwargs
    ):
        endpoint = f'{self.base_url}/v0/scrape'
        data = {'url': url, **kwargs}
        logger.debug(f"Sent request to {endpoint=} body={data}")
        response = await self._request('POST', endpoint, data)
        if response is None:
            raise HTTPError("Failed to scrape URL after multiple retries")
        return response

    async def _map_url(
        self,
        url: str,
        search: str = "",
        **kwargs
    ) -> Mapping[str, Any]:
        endpoint = f"{self.base_url}/v1/map"
        data = {"url": url}
        if search:
            data['search'] = search
        logger.debug(f"Sent request to {endpoint=} body={data}")
        response = await self._request("POST", endpoint, data)
        if response is None:
            raise HTTPError("Failed to perform map after multiple retries")
        return response

    async def _check_crawl_status(
        self,
        job_id: str
    ) -> Mapping[str, Any]:
        endpoint = f'{self.base_url}/v0/crawl/status/{job_id}'
        response = await self._request('GET', endpoint)
        if response is None:
            raise HTTPError(f"Failed to check status for job {job_id} after multiple retries")
        return response

    async def _cancel_crawl_job(
        self,
        job_id: str
    ) -> Mapping[str, Any]:
        endpoint = f'{self.base_url}/v0/crawl/cancel/{job_id}'
        response = await self._request('DELETE', endpoint)
        if response is None:
            raise HTTPError(f"Failed to cancel job {job_id} after multiple retries")
        return response

    async def _monitor_job_status(
        self,
        job_id: str,
        poll_interval: int,
        timeout: float
    ) -> Mapping[str, Any]:
        while True:
            status = await self._check_crawl_status(job_id)
            if status['status'] == 'completed':
                return status
            elif status['status'] == 'failed':
                raise HTTPError(f'Job {job_id} failed: {status["error"]}')
            timeout -= poll_interval
            if timeout <= 0:
                raise TimeoutError(f"Timeout while waiting for job {job_id} to complete.")
            await asyncio.sleep(poll_interval)

    def _prepare_headers(
        self,
        idempotency_key: Optional[str] = None,
    ) -> Mapping[str, str]:
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }
        if idempotency_key:
            headers['Idempotency-Key'] = idempotency_key
        return headers

    async def _request(
        self,
        method: str,
        url: str,
        data: Mapping[str, Any] | None = None,
        headers: Mapping[str, str] | None = None,
        timeout: float = 60,
    ) -> Mapping[str, Any]:
        if not headers:
            headers = self._prepare_headers()
        async with assrf_request(method, url, headers=headers, json=data, timeout_sec=timeout) as resp:
            resp.raise_for_status()
            return await resp.json()
