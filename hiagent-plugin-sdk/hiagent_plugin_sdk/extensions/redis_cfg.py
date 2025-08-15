from typing import Literal, List, Tuple
import logging
from redis.connection import Connection, ConnectionPool, SSLConnection

from functools import cache
from pydantic import BaseModel, ConfigDict


class RedisConfig(BaseModel):
    """Redis配置"""
    model_config = ConfigDict(frozen=True)

    cluster_type: Literal["single", "cluster", "sentinel"] = "single"
    host: str = "127.0.0.1:6379"
    # port: int = 6379
    master_name: str = ""
    password: str = ""
    db: int = 0
    ssl: bool = False

    @cache
    def get_redis_client(self):
        if self.cluster_type == "single":
            return init_generic_redis_client(self)
        if self.cluster_type == "cluster":
            return init_cluster_redis_client(self)
        if self.cluster_type == "sentinel":
            return init_sentinel_redis_client(self)
        raise ValueError(f"unsupported redis type: {self.cluster_type}")

def get_host_and_port(cfg: RedisConfig) -> List[Tuple[str, int]]:
    endpoints = cfg.host.split(",")

    host_and_ports = []
    for endpoint in endpoints:
        host_and_port = endpoint.strip().split(":")
        host = host_and_port[0]
        port = int(host_and_port[1])
        host_and_ports.append((host, port))

    return host_and_ports


def init_sentinel_redis_client(cfg: RedisConfig):
    from redis.sentinel import Sentinel
    host_and_ports = get_host_and_port(cfg)

    sentinel = Sentinel(
        host_and_ports,
        socket_timeout=3.0,
        password=cfg.password,
        db=cfg.db,
        encoding="utf-8",
        encoding_errors="strict",
        # decode_responses=True, # https://github.com/rq/rq/pull/1833/files
    )
    redis_client = sentinel.master_for(cfg.master_name, socket_timeout=3.0)

    return redis_client


def init_cluster_redis_client(cfg: RedisConfig):
    from redis.cluster import ClusterNode, RedisCluster

    # cluster 模式下，host 值为 host[:port],host[:port],host[:port]
    host_and_ports = get_host_and_port(cfg)
    cluster_nodes = []

    for endpoint in host_and_ports:
        node = ClusterNode(
            host=endpoint[0],
            port=endpoint[1],
        )
        cluster_nodes.append(node)

    return RedisCluster( # type: ignore
        startup_nodes=cluster_nodes,
        password=cfg.password,
        encoding="utf-8",
        encoding_errors="strict",
        # decode_responses=True, # https://github.com/rq/rq/pull/1833/files
        ssl=cfg.ssl,
        socket_timeout=5.0,
    )


def init_generic_redis_client(cfg: RedisConfig):
    from redis import Redis

    connection_class: type[Connection] = Connection
    if cfg.ssl:
        connection_class = SSLConnection
    host, port = cfg.host.split(":")

    connection_pool = ConnectionPool(
        connection_class=connection_class,
        host=host,
        port=port,
        password=cfg.password,
        db=cfg.db,
        encoding="utf-8",
        encoding_errors="strict",
        # decode_responses=True, # https://github.com/rq/rq/pull/1833/files
    )

    redis_client = Redis(connection_pool=connection_pool)

    return redis_client

