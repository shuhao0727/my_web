#!/usr/bin/env python3
"""
简易AI聊天脚本 - 根据智能体配置直接调用API
用法：
  交互模式: python3 simple_ai_chat.py
  命令行模式: python3 simple_ai_chat.py --agent_id 6 --message "你好"
  指定用户: python3 simple_ai_chat.py --agent_id 6 --user_id 1 --message "你好"
  
  作为模块导入：
  from simple_ai_chat import chat_with_agent_id
  response = await chat_with_agent_id(db_path, agent_id, message, user_id)
"""
import sys
import os
import json
import sqlite3
import argparse
from typing import Dict, Any, Optional
import asyncio

# 添加当前目录到路径，以便导入现有模块
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

try:
    from services.deepseek_client import DeepSeekClient
    from services.dify_client import DifyClient
except ImportError as e:
    print(f"导入模块失败: {e}")
    print("请确保在backend目录下运行此脚本")
    sys.exit(1)

def check_network() -> bool:
    """检查网络连接"""
    import socket
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        return False

def load_agent_config(db_path: str, agent_id: int) -> Optional[Dict[str, Any]]:
    """
    从数据库加载智能体配置
    
    Args:
        db_path: 数据库文件路径
        agent_id: 智能体ID
        
    Returns:
        智能体配置字典，如果找不到则返回None
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT id, name, api_type, api_key, base_url, model, app_id, is_active FROM ai_agents WHERE id = ?",
            (agent_id,)
        )
        agent = cursor.fetchone()
        
        if not agent:
            print(f"错误: 找不到ID为{agent_id}的智能体")
            return None
        
        # 检查智能体是否激活
        if agent[7] != 1:
            print(f"警告: 智能体 '{agent[1]}' 未激活")
        
        config = {
            "id": agent[0],
            "name": agent[1],
            "api_type": agent[2],
            "api_key": agent[3],
            "base_url": agent[4],
            "model": agent[5],
            "app_id": agent[6],
            "is_active": agent[7]
        }
        
        conn.close()
        return config
        
    except sqlite3.Error as e:
        print(f"数据库错误: {e}")
        return None

def save_config_to_temp(config: Dict[str, Any]) -> str:
    """
    将配置保存到临时文件（可选）
    
    Args:
        config: 智能体配置
        
    Returns:
        临时文件路径
    """
    import tempfile
    import time
    
    # 创建临时文件名
    temp_dir = tempfile.gettempdir()
    filename = f"ai_agent_{config['id']}_{int(time.time())}.json"
    temp_path = os.path.join(temp_dir, filename)
    
    # 保存配置到JSON文件
    with open(temp_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    
    print(f"配置已保存到临时文件: {temp_path}")
    return temp_path

async def chat_with_agent(config: Dict[str, Any], message: str, user_id: Optional[int] = None) -> str:
    """
    使用智能体配置与AI聊天
    
    Args:
        config: 智能体配置
        message: 用户消息
        user_id: 用户ID（可选，用于Dify等需要用户标识的API）
        
    Returns:
        AI回复
    """
    api_type = config.get("api_type", "").lower()
    agent_name = config.get("name", "未知智能体")
    
    print(f"正在使用智能体: {agent_name} ({api_type})")
    
    try:
        if api_type == "deepseek":
            # DeepSeek API配置
            api_key = config.get("api_key", "")
            base_url = config.get("base_url", "https://api.deepseek.com")
            model = config.get("model", "deepseek-chat")
            
            if not api_key:
                return "错误: DeepSeek API密钥未配置"
            
            client = DeepSeekClient(
                api_key=api_key,
                base_url=base_url,
                model=model,
                temperature=0.7,
                max_tokens=2000,
                timeout=30
            )
            
            # 调用DeepSeek API
            response = await client.chat(
                user_message=message,
                system_prompt=f"你是{agent_name}，一个AI助手"
            )
            return response
            
        elif api_type == "dify":
            # Dify API配置
            api_key = config.get("api_key", "")
            base_url = config.get("base_url", "http://wangsh.cn:6606/v1")
            app_id = config.get("app_id", "")
            
            if not api_key:
                return "错误: Dify API密钥未配置"
            if not app_id:
                return "错误: Dify应用ID未配置"
            
            client = DifyClient(
                api_key=api_key,
                base_url=base_url,
                app_id=app_id,
                timeout=30
            )
            
            # Dify需要用户标识
            user_identifier = str(user_id) if user_id else "anonymous"
            response = await client.chat(
                user_message=message,
                user_id=user_identifier
            )
            return response
            
        elif api_type == "mock" or api_type == "echo":
            # 模拟回复，用于测试
            if api_type == "mock":
                return f"[模拟回复] 我是{agent_name}，我收到你的消息：'{message}'。我正在思考如何回答..."
            else:
                return f"[回声回复] 你说了：{message}"
                
        else:
            return f"错误: 不支持的API类型 '{api_type}'"
            
    except Exception as e:
        return f"调用API时出错: {str(e)}"

def list_agents(db_path: str):
    """列出所有智能体"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT id, name, api_type, is_active FROM ai_agents ORDER BY id"
        )
        agents = cursor.fetchall()
        
        if not agents:
            print("数据库中没有智能体")
            return
        
        print("=" * 60)
        print("智能体列表:")
        print("=" * 60)
        for agent in agents:
            status = "✓ 激活" if agent[3] == 1 else "✗ 禁用"
            print(f"ID: {agent[0]:2d} | 名称: {agent[1]:20s} | 类型: {agent[2]:10s} | 状态: {status}")
        print("=" * 60)
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"数据库错误: {e}")

async def interactive_chat(db_path: str):
    """交互式聊天模式"""
    print("=" * 60)
    print("简易AI聊天脚本 - 交互模式")
    print("=" * 60)
    
    # 检查网络
    if not check_network():
        print("警告: 网络连接不可用，部分API可能无法使用")
        response = input("是否继续? (y/n): ")
        if response.lower() != 'y':
            return
    else:
        print("网络连接正常")
    
    # 列出智能体
    list_agents(db_path)
    
    while True:
        try:
            # 选择智能体
            agent_input = input("\n请输入智能体ID (输入 'q' 退出，'l' 重新列表): ").strip()
            
            if agent_input.lower() == 'q':
                print("再见！")
                break
            elif agent_input.lower() == 'l':
                list_agents(db_path)
                continue
            
            try:
                agent_id = int(agent_input)
            except ValueError:
                print("错误: 请输入有效的数字ID")
                continue
            
            # 加载智能体配置
            config = load_agent_config(db_path, agent_id)
            if not config:
                print(f"智能体ID {agent_id} 不存在，请重试")
                continue
            
            # 保存配置到临时文件（可选）
            save_temp = input("是否保存配置到临时文件? (y/n): ").strip().lower()
            if save_temp == 'y':
                temp_file = save_config_to_temp(config)
                print(f"配置已保存到: {temp_file}")
            
            # 输入用户ID
            user_id = None
            user_id_input = input("请输入用户ID (可选，直接回车跳过): ").strip()
            if user_id_input:
                try:
                    user_id = int(user_id_input)
                except ValueError:
                    print("警告: 用户ID无效，将使用匿名用户")
            
            # 聊天循环
            print(f"\n开始与 '{config['name']}' 聊天 (输入 'quit' 退出聊天，'back' 返回智能体选择)")
            print("-" * 40)
            
            while True:
                # 输入消息
                message = input("你: ").strip()
                
                if message.lower() == 'quit':
                    print("退出程序")
                    return
                elif message.lower() == 'back':
                    print("返回智能体选择")
                    break
                elif not message:
                    print("消息不能为空")
                    continue
                
                # 调用AI
                print(f"{config['name']}: ", end="", flush=True)
                response = await chat_with_agent(config, message, user_id)
                print(response)
                print("-" * 40)
                
        except KeyboardInterrupt:
            print("\n\n检测到中断，退出程序")
            break
        except Exception as e:
            print(f"发生错误: {e}")

async def chat_with_agent_id(db_path: str, agent_id: int, message: str, user_id: Optional[int] = None) -> str:
    """
    通过智能体ID与AI聊天（供其他模块调用）
    
    Args:
        db_path: 数据库文件路径
        agent_id: 智能体ID
        message: 用户消息
        user_id: 用户ID（可选，用于Dify等需要用户标识的API）
        
    Returns:
        AI回复字符串
    """
    # 检查网络（可选，但为了稳定性保留）
    if not check_network():
        return "错误: 网络连接不可用"
    
    # 加载智能体配置
    config = load_agent_config(db_path, agent_id)
    if not config:
        return f"错误: 找不到ID为{agent_id}的智能体"
    
    # 检查智能体是否激活
    if config.get("is_active") != 1:
        return f"警告: 智能体 '{config['name']}' 未激活"
    
    # 调用AI
    response = await chat_with_agent(config, message, user_id)
    return response


async def main():
    parser = argparse.ArgumentParser(description="简易AI聊天脚本")
    parser.add_argument("--agent_id", type=int, help="智能体ID")
    parser.add_argument("--user_id", type=int, help="用户ID (可选)")
    parser.add_argument("--message", type=str, help="要发送的消息")
    parser.add_argument("--list", action="store_true", help="列出所有智能体")
    parser.add_argument("--db", type=str, default="znt.db", help="数据库文件路径 (默认: znt.db)")
    
    args = parser.parse_args()
    
    # 数据库路径
    db_path = args.db
    if not os.path.exists(db_path):
        print(f"错误: 数据库文件 '{db_path}' 不存在")
        print("请确保在backend目录下运行，或使用 --db 参数指定数据库路径")
        sys.exit(1)
    
    # 列出智能体模式
    if args.list:
        list_agents(db_path)
        return
    
    # 命令行模式
    if args.agent_id and args.message:
        # 检查网络
        if not check_network():
            print("错误: 网络连接不可用")
            sys.exit(1)
        
        # 加载智能体配置
        config = load_agent_config(db_path, args.agent_id)
        if not config:
            print(f"错误: 找不到ID为{args.agent_id}的智能体")
            sys.exit(1)
        
        # 调用AI
        response = await chat_with_agent(config, args.message, args.user_id)
        print(response)
        
    # 交互模式
    else:
        await interactive_chat(db_path)

if __name__ == "__main__":
    asyncio.run(main())
