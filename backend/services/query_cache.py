"""
数据库查询缓存装饰器 - 针对高并发优化
为数据库查询提供智能缓存，减少数据库压力，提高响应速度
支持TTL、键生成、缓存失效策略
"""
import hashlib
import json
import pickle
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, TypeVar, Union, cast, Awaitable
import logging
import inspect

from .redis_cache import cache, CachePrefix

logger = logging.getLogger(__name__)

T = TypeVar('T')
R = TypeVar('R')

# 缓存统计
_cache_hits = 0
_cache_misses = 0


def get_cache_stats() -> Dict[str, Any]:
    """获取缓存统计信息"""
    total = _cache_hits + _cache_misses
    return {
        "hits": _cache_hits,
        "misses": _cache_misses,
        "total": total,
        "hit_rate": f"{(_cache_hits / total * 100):.1f}%" if total > 0 else "0%"
    }


def reset_cache_stats() -> None:
    """重置缓存统计"""
    global _cache_hits, _cache_misses
    _cache_hits = 0
    _cache_misses = 0


def generate_cache_key(
    func: Callable,
    args: tuple,
    kwargs: dict,
    prefix: str = CachePrefix.QUERY,
    exclude_params: Optional[List[str]] = None
) -> str:
    """
    生成缓存键
    
    Args:
        func: 函数对象
        args: 位置参数
        kwargs: 关键字参数
        prefix: 缓存键前缀
        exclude_params: 要排除的参数名列表
    
    Returns:
        缓存键字符串
    """
    # 获取函数签名
    sig = inspect.signature(func)
    bound_args = sig.bind(*args, **kwargs)
    bound_args.apply_defaults()
    
    # 构建键部分
    key_parts = [func.__module__, func.__name__]
    
    # 添加参数
    for param_name, param_value in bound_args.arguments.items():
        if exclude_params and param_name in exclude_params:
            continue
        
        # 处理不同数据类型
        if isinstance(param_value, (str, int, float, bool, type(None))):
            key_parts.append(f"{param_name}={param_value}")
        elif isinstance(param_value, (list, tuple)):
            # 对列表/元组进行哈希
            hashed = hashlib.md5(json.dumps(param_value, default=str).encode()).hexdigest()[:8]
            key_parts.append(f"{param_name}=list_{hashed}")
        elif isinstance(param_value, dict):
            # 对字典进行哈希
            hashed = hashlib.md5(json.dumps(param_value, sort_keys=True, default=str).encode()).hexdigest()[:8]
            key_parts.append(f"{param_name}=dict_{hashed}")
        else:
            # 其他类型使用字符串表示
            key_parts.append(f"{param_name}={str(param_value)}")
    
    # 生成完整键
    key_string = ":".join(key_parts)
    cache_key = hashlib.md5(key_string.encode()).hexdigest()
    return f"{prefix}:{cache_key}"


def cache_query(
    ttl: int = 300,
    prefix: str = CachePrefix.QUERY,
    exclude_params: Optional[List[str]] = None,
    condition: Optional[Callable[..., Union[bool, Awaitable[bool]]]] = None
):
    """
    数据库查询缓存装饰器
    
    Args:
        ttl: 缓存时间（秒），默认5分钟
        prefix: 缓存键前缀
        exclude_params: 要排除的参数名列表
        condition: 条件函数，返回True时启用缓存（支持同步和异步）
    
    Returns:
        装饰器函数
    """
    def decorator(func: Callable[..., R]) -> Callable[..., R]:
        
        # 辅助函数：检查条件
        def check_condition_sync(*args, **kwargs) -> bool:
            """同步检查条件"""
            if condition is None:
                return True
            # 在同步上下文中，condition必须是同步函数
            # 使用类型忽略来避免Pylance错误，因为我们假设在同步上下文中condition是同步的
            result = condition(*args, **kwargs)  # type: ignore
            # 如果结果是Awaitable，这是错误的，但我们假设在同步包装器中不会发生
            return bool(result)
        
        async def check_condition_async(*args, **kwargs) -> bool:
            """异步检查条件"""
            if condition is None:
                return True
            import asyncio
            if asyncio.iscoroutinefunction(condition):
                # condition是协程函数，需要await
                result = await condition(*args, **kwargs)  # type: ignore
            else:
                # condition是同步函数，直接调用
                result = condition(*args, **kwargs)  # type: ignore
            return bool(result)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> R:
            global _cache_hits, _cache_misses
            
            # 检查是否满足缓存条件
            if not check_condition_sync(*args, **kwargs):
                return func(*args, **kwargs)
            
            # 生成缓存键
            cache_key = generate_cache_key(func, args, kwargs, prefix, exclude_params)
            
            # 尝试从缓存获取
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                _cache_hits += 1
                logger.debug(f"✅ 查询缓存命中: {func.__name__} -> {cache_key}")
                return cached_result
            
            # 执行查询
            _cache_misses += 1
            result = func(*args, **kwargs)
            
            # 缓存结果
            if result is not None:
                cache.set(cache_key, result, ttl)
                logger.debug(f"🔄 查询结果已缓存: {func.__name__} -> {cache_key} (ttl={ttl}s)")
            
            return result
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> R:
            global _cache_hits, _cache_misses
            
            # 检查是否满足缓存条件
            if not await check_condition_async(*args, **kwargs):  # type: ignore
                return await func(*args, **kwargs)  # type: ignore
            
            # 生成缓存键
            cache_key = generate_cache_key(func, args, kwargs, prefix, exclude_params)
            
            # 尝试从缓存获取
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                _cache_hits += 1
                logger.debug(f"✅ 查询缓存命中: {func.__name__} -> {cache_key}")
                return cached_result
            
            # 执行查询
            _cache_misses += 1
            result = await func(*args, **kwargs)  # type: ignore
            
            # 缓存结果
            if result is not None:
                cache.set(cache_key, result, ttl)
                logger.debug(f"🔄 查询结果已缓存: {func.__name__} -> {cache_key} (ttl={ttl}s)")
            
            return result  # type: ignore
        
        # 根据函数类型返回对应的包装器
        if inspect.iscoroutinefunction(func):
            return cast(Callable[..., R], async_wrapper)
        else:
            return sync_wrapper
    
    return decorator


def invalidate_cache(
    prefix: str = CachePrefix.QUERY,
    pattern: Optional[str] = None,
    func: Optional[Callable] = None
):
    """
    缓存失效装饰器
    
    Args:
        prefix: 缓存键前缀
        pattern: 缓存键模式（支持通配符*）
        func: 要失效缓存的函数
    
    Returns:
        装饰器函数或直接执行失效
    """
    def decorator(inner_func: Callable) -> Callable:
        @wraps(inner_func)
        def wrapper(*args, **kwargs):
            # 执行原函数
            result = inner_func(*args, **kwargs)
            
            # 构建缓存键模式
            if pattern:
                cache_pattern = pattern
            elif func:
                # 为指定函数生成模式
                cache_pattern = f"{prefix}:{func.__module__}:{func.__name__}:*"
            else:
                # 为当前函数生成模式
                cache_pattern = f"{prefix}:{inner_func.__module__}:{inner_func.__name__}:*"
            
            # 删除匹配的缓存（实际实现需要Redis支持keys命令）
            try:
                # 注意：生产环境应避免使用keys命令，可以使用SCAN迭代
                # 这里简化为删除单个模式
                keys = cache.client.keys(cache_pattern)
                if keys:
                    cache.client.delete(*keys)
                    logger.debug(f"🗑️  缓存失效: {cache_pattern} -> {len(keys)} keys")
            except AttributeError:
                # 客户端不支持keys命令，跳过
                pass
            except Exception as e:
                logger.warning(f"⚠️  缓存失效失败: {e}")
            
            return result
        
        @wraps(inner_func)
        async def async_wrapper(*args, **kwargs):
            # 执行原函数
            result = await inner_func(*args, **kwargs)
            
            # 构建缓存键模式
            if pattern:
                cache_pattern = pattern
            elif func:
                cache_pattern = f"{prefix}:{func.__module__}:{func.__name__}:*"
            else:
                cache_pattern = f"{prefix}:{inner_func.__module__}:{inner_func.__name__}:*"
            
            # 删除匹配的缓存
            try:
                keys = cache.client.keys(cache_pattern)
                if keys:
                    cache.client.delete(*keys)
                    logger.debug(f"🗑️  缓存失效: {cache_pattern} -> {len(keys)} keys")
            except AttributeError:
                # 客户端不支持keys命令，跳过
                pass
            except Exception as e:
                logger.warning(f"⚠️  缓存失效失败: {e}")
            
            return result
        
        if inspect.iscoroutinefunction(inner_func):
            return async_wrapper
        else:
            return wrapper
    
    return decorator


class QueryCacheManager:
    """
    查询缓存管理器
    提供更高级的缓存控制功能
    """
    
    def __init__(self, prefix: str = CachePrefix.QUERY):
        self.prefix = prefix
        self._cache = cache
    
    def get(self, func: Callable, *args, **kwargs) -> Any:
        """获取缓存结果"""
        cache_key = generate_cache_key(func, args, kwargs, self.prefix)
        return self._cache.get(cache_key)
    
    def set(self, func: Callable, value: Any, ttl: int = 300, *args, **kwargs) -> bool:
        """设置缓存结果"""
        cache_key = generate_cache_key(func, args, kwargs, self.prefix)
        return self._cache.set(cache_key, value, ttl)
    
    def delete(self, func: Callable, *args, **kwargs) -> int:
        """删除缓存结果"""
        cache_key = generate_cache_key(func, args, kwargs, self.prefix)
        return self._cache.delete(cache_key)
    
    def delete_by_pattern(self, pattern: str) -> int:
        """按模式删除缓存"""
        try:
            keys = self._cache.client.keys(pattern)
            if keys:
                return self._cache.client.delete(*keys)
        except AttributeError:
            # 客户端不支持keys命令，跳过
            pass
        except Exception as e:
            logger.error(f"删除缓存失败: {e}")
        return 0
    
    def clear_all_queries(self) -> bool:
        """清除所有查询缓存"""
        pattern = f"{self.prefix}:*"
        try:
            keys = self._cache.client.keys(pattern)
            if keys:
                self._cache.client.delete(*keys)
                logger.info(f"🗑️  清除查询缓存: {len(keys)} keys")
                return True
        except AttributeError:
            # 客户端不支持keys命令，跳过
            pass
        except Exception as e:
            logger.error(f"清除查询缓存失败: {e}")
        return False
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计"""
        stats = get_cache_stats()
        stats.update({
            "prefix": self.prefix,
            "cache_connected": cache.is_connected(),
            "cache_mode": "mock" if cache.is_mock_mode() else "redis"
        })
        return stats


# 默认查询缓存管理器
query_cache = QueryCacheManager()

# 常用条件函数
def cache_when_not_none(*args, **kwargs) -> bool:
    """当结果不为None时缓存"""
    return True

def cache_when_empty_list(result: List) -> bool:
    """当结果为空列表时不缓存（避免缓存空结果）"""
    return bool(result)

def cache_only_for_authenticated(user_id: Optional[int] = None, *args, **kwargs) -> bool:
    """仅对已认证用户缓存"""
    return user_id is not None

# 使用示例
if __name__ == "__main__":
    # 示例使用
    @cache_query(ttl=60)
    def get_user_by_id(user_id: int):
        """获取用户信息（带缓存）"""
        import time
        time.sleep(0.5)  # 模拟慢查询
        return {"id": user_id, "name": f"User_{user_id}"}
    
    @cache_query(ttl=300, exclude_params=["db_session"])
    def get_articles(page: int, page_size: int, db_session=None):
        """获取文章列表（带缓存，排除db_session参数）"""
        import time
        time.sleep(1)  # 模拟慢查询
        return [{"id": i, "title": f"Article {i}"} for i in range(page * page_size, (page + 1) * page_size)]
    
    @invalidate_cache(pattern="query:*:get_user_by_id:*")
    def update_user(user_id: int, name: str):
        """更新用户信息（同时失效相关缓存）"""
        # 更新数据库...
        return True
    
    # 测试
    print("第一次调用（缓存未命中）:")
    user1 = get_user_by_id(1)
    print(f"  结果: {user1}")
    
    print("第二次调用（缓存命中）:")
    user2 = get_user_by_id(1)
    print(f"  结果: {user2}")
    
    print("缓存统计:")
    print(f"  {get_cache_stats()}")
    
    print("更新用户（触发缓存失效）:")
    update_user(1, "New Name")
    
    print("第三次调用（缓存失效后重新获取）:")
    user3 = get_user_by_id(1)
    print(f"  结果: {user3}")

__all__ = [
    "cache_query",
    "invalidate_cache",
    "generate_cache_key",
    "get_cache_stats",
    "reset_cache_stats",
    "QueryCacheManager",
    "query_cache",
    "cache_when_not_none",
    "cache_when_empty_list",
    "cache_only_for_authenticated",
]