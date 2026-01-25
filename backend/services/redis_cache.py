"""
Redis缓存服务
提供统一的缓存接口，支持多种数据类型和过期时间
如果Redis不可用，则自动降级到内存缓存（仅用于开发环境）
"""
import json
import pickle
import asyncio
from typing import Any, Optional, Union, List, Dict, Callable, TypeVar, cast
from datetime import timedelta, datetime
import logging
import os
import time

logger = logging.getLogger(__name__)

T = TypeVar('T')

# 检查Redis模块是否可用
REDIS_AVAILABLE = False
try:
    import redis  # type: ignore
    REDIS_AVAILABLE = True
except ImportError:
    logger.warning("Redis模块未安装，将使用内存缓存（仅用于开发）")

class MockRedis:
    """模拟Redis客户端，用于开发环境或Redis不可用时"""
    
    def __init__(self, *args, **kwargs):
        self._store: Dict[str, bytes] = {}
        self._expire_times: Dict[str, float] = {}
        self._start_time = time.time()
        logger.info("使用内存模拟Redis缓存")
    
    def ping(self) -> bool:
        return True
    
    def set(self, key: str, value: bytes, ex: Optional[int] = None, px: Optional[int] = None, 
            nx: bool = False, xx: bool = False) -> bool:
        self._store[key] = value
        if ex is not None:
            self._expire_times[key] = time.time() + ex
        elif px is not None:
            self._expire_times[key] = time.time() + (px / 1000.0)
        return True
    
    def setex(self, key: str, ttl: int, value: bytes) -> bool:
        return self.set(key, value, ex=ttl)
    
    def get(self, key: str) -> Optional[bytes]:
        # 检查过期时间
        if key in self._expire_times and time.time() > self._expire_times[key]:
            del self._store[key]
            del self._expire_times[key]
            return None
        return self._store.get(key)
    
    def delete(self, *keys: str) -> int:
        count = 0
        for key in keys:
            if key in self._store:
                del self._store[key]
                if key in self._expire_times:
                    del self._expire_times[key]
                count += 1
        return count
    
    def exists(self, key: str) -> bool:
        if key in self._expire_times and time.time() > self._expire_times[key]:
            del self._store[key]
            del self._expire_times[key]
            return False
        return key in self._store
    
    def expire(self, key: str, ttl: int) -> bool:
        if key in self._store:
            self._expire_times[key] = time.time() + ttl
            return True
        return False
    
    def mset(self, mapping: Dict[str, bytes]) -> bool:
        for key, value in mapping.items():
            self._store[key] = value
        return True
    
    def mget(self, keys: List[str]) -> List[Optional[bytes]]:
        return [self.get(key) for key in keys]
    
    def flushdb(self) -> bool:
        self._store.clear()
        self._expire_times.clear()
        return True
    
    def info(self, section: Optional[str] = None) -> Dict[str, Any]:
        # 返回模拟的info数据
        return {
            'used_memory': 0,
            'used_memory_human': '0B',
            'connected_clients': 1,
            'total_commands_processed': 0,
            'keyspace_hits': 0,
            'keyspace_misses': 0,
            'uptime_in_seconds': int(time.time() - self._start_time),
        }
    
    def pipeline(self) -> 'MockPipeline':
        return MockPipeline(self)
    
    def keys(self, pattern: str = "*") -> List[str]:
        """模拟Redis keys命令，支持简单通配符"""
        import fnmatch
        keys = list(self._store.keys())
        # 过滤过期键
        valid_keys = []
        for key in keys:
            if key in self._expire_times and time.time() > self._expire_times[key]:
                del self._store[key]
                del self._expire_times[key]
            else:
                valid_keys.append(key)
        # 使用fnmatch进行模式匹配
        return fnmatch.filter(valid_keys, pattern)


class MockPipeline:
    """模拟Redis管道"""
    
    def __init__(self, mock_redis: MockRedis):
        self.mock_redis = mock_redis
        self.commands: List[tuple] = []
    
    def setex(self, key: str, ttl: int, value: bytes) -> 'MockPipeline':
        self.commands.append(('setex', key, ttl, value))
        return self
    
    def set(self, key: str, value: bytes) -> 'MockPipeline':
        self.commands.append(('set', key, value))
        return self
    
    def execute(self) -> List[bool]:
        results = []
        for cmd in self.commands:
            if cmd[0] == 'setex':
                results.append(self.mock_redis.setex(cmd[1], cmd[2], cmd[3]))
            elif cmd[0] == 'set':
                results.append(self.mock_redis.set(cmd[1], cmd[2]))
        return results


class RedisCache:
    """Redis缓存客户端封装"""
    
    def __init__(self):
        self._client: Optional[Union['redis.Redis', MockRedis]] = None
        self._connected = False
        self._use_mock = not REDIS_AVAILABLE
        
    def _get_client(self) -> Union['redis.Redis', MockRedis]:
        """获取Redis客户端（真实或模拟）"""
        if self._client is None:
            self._connect()
        return self._client  # type: ignore
    
    @property
    def client(self) -> Union['redis.Redis', MockRedis]:
        """获取Redis客户端连接"""
        return self._get_client()
    
    def _connect(self) -> None:
        """连接到Redis服务器或创建模拟客户端"""
        if self._use_mock:
            # 使用模拟Redis
            self._client = MockRedis()
            self._connected = True
            logger.info("✅ 使用内存模拟Redis缓存")
            return
            
        try:
            # 使用真实Redis
            host = os.getenv("REDIS_HOST", "localhost")
            port = int(os.getenv("REDIS_PORT", "6379"))
            db = int(os.getenv("REDIS_DB", "0"))
            password = os.getenv("REDIS_PASSWORD")
            
            # 动态导入真实的redis模块，避免静态分析错误
            import redis as redis_module  # type: ignore
            self._client = redis_module.Redis(
                host=host,
                port=port,
                db=db,
                password=password,
                decode_responses=False,  # 返回bytes，便于处理多种数据类型
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30,
            )
            
            # 测试连接
            if self._client is not None:
                self._client.ping()
            self._connected = True
            logger.info(f"✅ Redis缓存服务已连接: {host}:{port}/{db}")
            
        except Exception as e:
            logger.error(f"❌ Redis连接失败: {e}")
            self._connected = False
            # 回退到模拟客户端
            self._client = MockRedis()
            self._use_mock = True
    
    def is_connected(self) -> bool:
        """检查Redis是否连接成功"""
        if not self._connected or self._client is None:
            return False
        try:
            # 此时client肯定不是None
            client = self._client
            client.ping()
            return True
        except:
            self._connected = False
            return False
    
    # ========== 基本缓存操作 ==========
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        设置缓存值
        
        Args:
            key: 缓存键
            value: 缓存值（支持Python对象）
            ttl: 过期时间（秒），None表示永不过期
        
        Returns:
            bool: 是否设置成功
        """
        if not self.is_connected():
            return False
            
        try:
            # 序列化值
            if isinstance(value, (str, int, float, bool, bytes)):
                serialized = value if isinstance(value, bytes) else str(value).encode('utf-8')
            else:
                serialized = pickle.dumps(value)
            
            if ttl is not None:
                result = self.client.setex(key, ttl, serialized)
            else:
                result = self.client.set(key, serialized)
            
            return bool(result)
        except Exception as e:
            logger.error(f"设置缓存失败 {key}: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取缓存值
        
        Args:
            key: 缓存键
            default: 默认值
        
        Returns:
            缓存值或默认值
        """
        if not self.is_connected():
            return default
            
        try:
            value = self.client.get(key)
            if value is None:
                return default
            
            # 尝试反序列化
            try:
                # 先尝试pickle
                return pickle.loads(value)
            except:
                # 再尝试JSON
                try:
                    return json.loads(value.decode('utf-8'))
                except:
                    # 最后返回原始字节或字符串
                    try:
                        return value.decode('utf-8')
                    except:
                        return value
        except Exception as e:
            logger.error(f"获取缓存失败 {key}: {e}")
            return default
    
    def delete(self, *keys: str) -> int:
        """删除一个或多个缓存键"""
        if not self.is_connected():
            return 0
            
        try:
            return self.client.delete(*keys)
        except Exception as e:
            logger.error(f"删除缓存失败 {keys}: {e}")
            return 0
    
    def exists(self, key: str) -> bool:
        """检查键是否存在"""
        if not self.is_connected():
            return False
            
        try:
            return bool(self.client.exists(key))
        except Exception as e:
            logger.error(f"检查缓存存在失败 {key}: {e}")
            return False
    
    def expire(self, key: str, ttl: int) -> bool:
        """设置过期时间"""
        if not self.is_connected():
            return False
            
        try:
            return bool(self.client.expire(key, ttl))
        except Exception as e:
            logger.error(f"设置缓存过期失败 {key}: {e}")
            return False
    
    # ========== 高级缓存操作 ==========
    
    def get_or_set(self, key: str, factory: Any, ttl: Optional[int] = None) -> Any:
        """
        获取缓存值，如果不存在则调用factory函数生成并缓存
        
        Args:
            key: 缓存键
            factory: 生成值的函数或值
            ttl: 过期时间
        
        Returns:
            缓存值或新生成的值
        """
        value = self.get(key)
        if value is not None:
            return value
        
        # 生成新值
        new_value = factory() if callable(factory) else factory
        if new_value is not None:
            self.set(key, new_value, ttl)
        return new_value
    
    async def get_or_set_async(self, key: str, factory: Any, ttl: Optional[int] = None) -> Any:
        """
        异步版本的get_or_set
        
        Args:
            key: 缓存键
            factory: 生成值的异步函数或值
            ttl: 过期时间
        
        Returns:
            缓存值或新生成的值
        """
        value = self.get(key)
        if value is not None:
            return value
        
        # 生成新值
        if asyncio.iscoroutinefunction(factory):
            new_value = await factory()
        elif callable(factory):
            new_value = factory()
        else:
            new_value = factory
            
        if new_value is not None:
            self.set(key, new_value, ttl)
        return new_value
    
    # ========== 批量操作 ==========
    
    def mset(self, mapping: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """批量设置缓存"""
        if not self.is_connected():
            return False
            
        try:
            pipe = self.client.pipeline()
            for key, value in mapping.items():
                if isinstance(value, (str, int, float, bool, bytes)):
                    serialized = value if isinstance(value, bytes) else str(value).encode('utf-8')
                else:
                    serialized = pickle.dumps(value)
                
                if ttl is not None:
                    pipe.setex(key, ttl, serialized)
                else:
                    pipe.set(key, serialized)
            
            pipe.execute()
            return True
        except Exception as e:
            logger.error(f"批量设置缓存失败: {e}")
            return False
    
    def mget(self, keys: List[str]) -> List[Any]:
        """批量获取缓存"""
        if not self.is_connected():
            return [None] * len(keys)
            
        try:
            values = self.client.mget(keys)
            result = []
            for value in values:
                if value is None:
                    result.append(None)
                else:
                    try:
                        result.append(pickle.loads(value))
                    except:
                        try:
                            result.append(json.loads(value.decode('utf-8')))
                        except:
                            try:
                                result.append(value.decode('utf-8'))
                            except:
                                result.append(value)
            return result
        except Exception as e:
            logger.error(f"批量获取缓存失败: {e}")
            return [None] * len(keys)
    
    # ========== 缓存模式 ==========
    
    def cache_result(self, ttl: int = 300):
        """
        函数结果缓存装饰器
        
        Args:
            ttl: 缓存时间（秒）
        
        Returns:
            装饰器函数
        """
        from functools import wraps
        
        def decorator(func: Callable[..., T]) -> Callable[..., T]:
            if asyncio.iscoroutinefunction(func):
                @wraps(func)
                async def async_wrapper(*args, **kwargs) -> T:
                    # 生成缓存键
                    key_parts = [func.__module__, func.__name__]
                    key_parts.extend(str(arg) for arg in args)
                    key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
                    cache_key = f"cache:{':'.join(key_parts)}"
                    
                    # 尝试获取缓存
                    cached = self.get(cache_key)
                    if cached is not None:
                        logger.debug(f"缓存命中: {cache_key}")
                        return cached
                    
                    # 执行函数并缓存结果
                    result = await func(*args, **kwargs)
                    if result is not None:
                        self.set(cache_key, result, ttl)
                    
                    return result
                
                return cast(Callable[..., T], async_wrapper)
            else:
                @wraps(func)
                def wrapper(*args, **kwargs) -> T:
                    # 生成缓存键
                    key_parts = [func.__module__, func.__name__]
                    key_parts.extend(str(arg) for arg in args)
                    key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
                    cache_key = f"cache:{':'.join(key_parts)}"
                    
                    # 尝试获取缓存
                    cached = self.get(cache_key)
                    if cached is not None:
                        logger.debug(f"缓存命中: {cache_key}")
                        return cached
                    
                    # 执行函数并缓存结果
                    result = func(*args, **kwargs)
                    if result is not None:
                        self.set(cache_key, result, ttl)
                    
                    return result
                
                return wrapper
        
        return decorator
    
    # ========== 统计信息 ==========
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        if not self.is_connected():
            return {"connected": False}
        
        try:
            info = self.client.info()
            stats = {
                "connected": True,
                "used_memory": info.get('used_memory_human', '0'),
                "connected_clients": info.get('connected_clients', 0),
                "total_commands_processed": info.get('total_commands_processed', 0),
                "keyspace_hits": info.get('keyspace_hits', 0),
                "keyspace_misses": info.get('keyspace_misses', 0),
                "uptime_in_seconds": info.get('uptime_in_seconds', 0),
            }
            
            # 计算命中率
            hits = stats["keyspace_hits"]
            misses = stats["keyspace_misses"]
            total = hits + misses
            stats["hit_rate"] = f"{(hits / total * 100):.1f}%" if total > 0 else "0%"
            
            return stats
        except Exception as e:
            logger.error(f"获取缓存统计失败: {e}")
            return {"connected": False, "error": str(e)}
    
    def clear_all(self) -> bool:
        """清空所有缓存（慎用！）"""
        if not self.is_connected():
            return False
            
        try:
            self.client.flushdb()
            logger.warning("Redis缓存已清空")
            return True
        except Exception as e:
            logger.error(f"清空缓存失败: {e}")
            return False
    
    def is_mock_mode(self) -> bool:
        """是否在使用模拟模式"""
        return self._use_mock


# 全局缓存实例
cache = RedisCache()

# 快捷函数
def get_cache() -> RedisCache:
    """获取缓存实例"""
    return cache

def cache_key(prefix: str, *args: Any) -> str:
    """生成缓存键"""
    parts = [prefix]
    parts.extend(str(arg) for arg in args)
    return ":".join(parts)

# 常用缓存键前缀
class CachePrefix:
    USER = "user"
    SESSION = "session"
    API = "api"
    CONFIG = "config"
    CONTENT = "content"
    STATS = "stats"
    TEMP = "temp"
    QUERY = "query"
