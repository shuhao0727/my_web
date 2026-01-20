#!/usr/bin/env python3
"""
AI智能体对话增强监测系统
专门用于实时监控对话数据和时间戳，验证时间转换准确性

使用方法：
1. 启动监控：python3 conversation_monitor_enhanced.py
2. 监控会显示实时对话记录和时间戳验证
3. 按Ctrl+C停止监控
"""
import sqlite3
import time
from datetime import datetime, timedelta
import sys
import os
import json

def get_db_path():
    """获取数据库路径"""
    # 尝试多个可能的路径
    possible_paths = [
        'znt.db',
        os.path.join(os.path.dirname(__file__), 'znt.db'),
        os.path.join(os.path.dirname(__file__), '..', 'znt.db')
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return os.path.abspath(path)
    
    # 如果都找不到，询问用户
    print("错误: 找不到数据库文件 znt.db")
    print("请提供数据库文件路径:")
    custom_path = input("路径: ").strip()
    if os.path.exists(custom_path):
        return os.path.abspath(custom_path)
    else:
        print(f"错误: 文件不存在: {custom_path}")
        sys.exit(1)

def parse_db_time_to_local(db_time_string):
    """模拟前端的时间解析函数，用于验证时间戳转换"""
    # 数据库时间格式可能是 '2026-01-20 06:29:07' (UTC时间)
    # 也可能是ISO格式 '2026-01-20T06:29:07'
    
    # 首先，如果字符串已经是ISO格式（包含T），直接解析
    if 'T' in db_time_string:
        return datetime.fromisoformat(db_time_string.replace('Z', '+00:00'))
    
    # 否则，假设是'YYYY-MM-DD HH:MM:SS'格式，并且是UTC时间
    # 使用正则表达式提取日期时间组件
    import re
    match = re.match(r'^(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2})$', db_time_string)
    if match:
        year, month, day, hour, minute, second = match.groups()
        # 构造UTC时间
        utc_time = datetime(
            int(year), int(month), int(day),
            int(hour), int(minute), int(second)
        )
        # 假设数据库存储的是UTC时间
        return utc_time
    
    # 如果解析失败，尝试其他格式
    try:
        return datetime.fromisoformat(db_time_string)
    except ValueError:
        print(f"警告: 时间解析失败: {db_time_string}")
        return datetime.now()

def format_time_for_display(date_input):
    """模拟前端的时间格式化函数"""
    if isinstance(date_input, str):
        # 从数据库字符串解析
        date = parse_db_time_to_local(date_input)
    else:
        date = date_input
    
    # 使用本地时区显示
    return date.strftime('%H:%M')

def setup_enhanced_monitoring(db_path):
    """设置增强监控"""
    print("=" * 100)
    print("AI智能体对话增强监测系统 - 时间戳验证版")
    print("=" * 100)
    print(f"数据库: {db_path}")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"本地时区: {time.tzname[0] if time.tzname else '未知'}")
    print(f"UTC偏移: {time.timezone // -3600}小时")
    print("-" * 100)
    
    # 检查数据库连接
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ai_messages'")
        if not cursor.fetchone():
            print("错误: 数据库中没有 ai_messages 表")
            conn.close()
            return None
        
        # 获取当前最新的消息ID作为基准
        cursor.execute("SELECT MAX(id) FROM ai_messages")
        result = cursor.fetchone()
        last_message_id = result[0] if result[0] else 0
        
        print(f"当前最新消息ID: {last_message_id}")
        print("监控已启动，等待新消息...")
        print("说明: UTC时间 -> 本地时间 (UTC+8)")
        print("-" * 100)
        
        conn.close()
        return last_message_id
        
    except sqlite3.Error as e:
        print(f"数据库连接错误: {e}")
        return None

def monitor_enhanced_conversations(db_path, start_message_id):
    """增强监控对话"""
    conn = None
    last_id = start_message_id
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        
        print("正在监控对话... (按Ctrl+C停止)")
        print()
        
        # 初始显示最近5条消息作为参考
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, conversation_id, role, content, created_at, tokens
            FROM ai_messages 
            WHERE id <= ? 
            ORDER BY id DESC 
            LIMIT 5
        """, (last_id,))
        
        recent_messages = cursor.fetchall()
        if recent_messages:
            print("[初始参考] 最近5条消息的时间戳验证:")
            print("-" * 80)
            for msg in recent_messages:
                display_enhanced_message(msg, is_reference=True)
            print("-" * 80)
            print()
        
        while True:
            cursor = conn.cursor()
            
            # 查询新消息
            query = """
                SELECT 
                    m.id, m.conversation_id, m.role, m.content, 
                    m.tokens, m.created_at,
                    c.user_id, c.agent_id, c.session_id,
                    a.name as agent_name,
                    u.username as user_name
                FROM ai_messages m
                JOIN ai_conversations c ON m.conversation_id = c.id
                JOIN ai_agents a ON c.agent_id = a.id
                JOIN ai_users u ON c.user_id = u.id
                WHERE m.id > ?
                ORDER BY m.id ASC
            """
            
            cursor.execute(query, (last_id,))
            new_messages = cursor.fetchall()
            
            if new_messages:
                current_time = datetime.now().strftime('%H:%M:%S')
                print(f"[{current_time}] 发现 {len(new_messages)} 条新消息")
                print("=" * 100)
                
                for msg in new_messages:
                    display_enhanced_message(msg)
                    last_id = msg['id']
                
                print("=" * 100)
                print()
            
            # 检查对话状态更新
            check_enhanced_conversation_updates(conn)
            
            conn.commit()
            time.sleep(1)  # 1秒检查一次
            
    except KeyboardInterrupt:
        print()
        print("监控已停止")
        print(f"最后处理的消息ID: {last_id}")
    except Exception as e:
        print(f"监控错误: {e}")
    finally:
        if conn:
            conn.close()

def display_enhanced_message(msg, is_reference=False):
    """显示增强消息详情，包含时间戳验证"""
    role_symbol = "👤" if msg['role'] == 'user' else "🤖"
    role_name = "用户" if msg['role'] == 'user' else "AI助手"
    
    # 时间戳分析
    db_time_str = msg['created_at']
    db_time = parse_db_time_to_local(db_time_str)
    local_display = format_time_for_display(db_time_str)
    
    # 计算时间差（用于验证）
    current_utc = datetime.utcnow()
    time_diff = current_utc - db_time
    
    # 显示消息头
    prefix = "[参考]" if is_reference else "[实时]"
    print(f"{prefix} {role_symbol} {role_name} | 消息ID: {msg['id']} | 对话ID: {msg['conversation_id']}")
    
    # 显示用户和智能体信息（如果不是参考消息）
    if not is_reference and 'user_name' in msg.keys():
        print(f"  用户: {msg['user_name']} (ID: {msg['user_id']}) | 智能体: {msg['agent_name']} (ID: {msg['agent_id']})")
    
    # 显示时间戳详细信息
    print(f"  ⏰ 时间戳分析:")
    print(f"    数据库原始时间: {db_time_str}")
    print(f"    解析为UTC时间: {db_time.strftime('%Y-%m-%d %H:%M:%S')} UTC")
    print(f"    转换为本地时间: {db_time.strftime('%Y-%m-%d %H:%M:%S')} (显示: {local_display})")
    
    # 验证时间转换
    utc_hour = db_time.hour
    expected_local_hour = (utc_hour + 8) % 24  # UTC+8
    actual_local_hour = db_time.hour  # 注意：parse_db_time_to_local返回的是本地时间对象
    
    print(f"    验证: UTC {utc_hour:02d}:00 -> 应显示本地 {expected_local_hour:02d}:00")
    
    # 显示内容
    content = msg['content']
    if len(content) > 120:
        preview = content[:120] + "..."
    else:
        preview = content
    
    print(f"  💬 内容: {preview}")
    print(f"  📊 Token数: {msg['tokens'] or '未知'}")
    
    if not is_reference:
        print(f"  ⏱️  距现在: {format_timedelta(time_diff)}")
    
    print()

def format_timedelta(td):
    """格式化时间差"""
    if td.days > 0:
        return f"{td.days}天{td.seconds//3600}小时前"
    elif td.seconds > 3600:
        return f"{td.seconds//3600}小时{(td.seconds%3600)//60}分钟前"
    elif td.seconds > 60:
        return f"{td.seconds//60}分钟前"
    else:
        return f"{td.seconds}秒前"

def check_enhanced_conversation_updates(conn):
    """检查增强对话状态更新"""
    cursor = conn.cursor()
    
    # 获取最近更新的对话
    query = """
        SELECT 
            c.id, c.session_id, c.title, c.total_messages, 
            c.total_tokens, c.start_time, c.end_time, c.updated_at,
            u.username as user_name,
            a.name as agent_name
        FROM ai_conversations c
        JOIN ai_users u ON c.user_id = u.id
        JOIN ai_agents a ON c.agent_id = a.id
        WHERE c.updated_at >= datetime('now', '-10 seconds')
        ORDER BY c.updated_at DESC
        LIMIT 3
    """
    
    cursor.execute(query)
    updated_conversations = cursor.fetchall()
    
    if updated_conversations:
        current_time = datetime.now().strftime('%H:%M:%S')
        print(f"[{current_time}] 对话状态更新:")
        for conv in updated_conversations:
            start_time = parse_db_time_to_local(conv['start_time'])
            end_time = parse_db_time_to_local(conv['end_time']) if conv['end_time'] else None
            
            print(f"  📝 对话: {conv['title']} (ID: {conv['id']})")
            print(f"    会话ID: {conv['session_id']}")
            print(f"    用户: {conv['user_name']} | 智能体: {conv['agent_name']}")
            print(f"    消息数: {conv['total_messages']} | Token总数: {conv['total_tokens']}")
            print(f"    开始时间: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
            if end_time:
                duration = end_time - start_time
                print(f"    结束时间: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"    持续时间: {duration}")
            print(f"    最后更新: {conv['updated_at']}")
        print()

def show_enhanced_summary(db_path):
    """显示增强状态摘要"""
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        print("\n" + "=" * 80)
        print("增强状态摘要")
        print("=" * 80)
        
        # 总体统计
        cursor.execute("SELECT COUNT(*) as total FROM ai_conversations")
        total_conversations = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as total FROM ai_messages")
        total_messages = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as total FROM ai_users")
        total_users = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as total FROM ai_agents")
        total_agents = cursor.fetchone()['total']
        
        print(f"📊 总体统计:")
        print(f"  用户数: {total_users}")
        print(f"  智能体数: {total_agents}")
        print(f"  总对话数: {total_conversations}")
        print(f"  总消息数: {total_messages}")
        
        # 最近1小时活动
        cursor.execute("""
            SELECT COUNT(DISTINCT user_id) as active_users,
                   COUNT(DISTINCT conversation_id) as active_conversations,
                   COUNT(*) as message_count,
                   SUM(tokens) as token_count
            FROM ai_messages 
            WHERE created_at >= datetime('now', '-1 hour')
        """)
        hour_stats = cursor.fetchone()
        
        print(f"\n⏰ 最近1小时活动:")
        print(f"  活跃用户: {hour_stats['active_users'] or 0}")
        print(f"  活跃对话: {hour_stats['active_conversations'] or 0}")
        print(f"  消息数: {hour_stats['message_count'] or 0}")
        print(f"  Token消耗: {hour_stats['token_count'] or 0}")
        
        # 时间戳分析
        cursor.execute("""
            SELECT 
                MIN(created_at) as earliest,
                MAX(created_at) as latest,
                COUNT(*) as total
            FROM ai_messages
        """)
        time_stats = cursor.fetchone()
        
        if time_stats['earliest'] and time_stats['latest']:
            earliest = parse_db_time_to_local(time_stats['earliest'])
            latest = parse_db_time_to_local(time_stats['latest'])
            
            print(f"\n🕐 时间戳范围:")
            print(f"  最早消息: {earliest.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"  最新消息: {latest.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"  时间跨度: {latest - earliest}")
        
        # 智能体使用排名
        cursor.execute("""
            SELECT a.name, COUNT(m.id) as message_count,
                   SUM(m.tokens) as total_tokens
            FROM ai_messages m
            JOIN ai_conversations c ON m.conversation_id = c.id
            JOIN ai_agents a ON c.agent_id = a.id
            GROUP BY a.id, a.name
            ORDER BY message_count DESC
            LIMIT 5
        """)
        agent_stats = cursor.fetchall()
        
        if agent_stats:
            print(f"\n🏆 智能体使用排名:")
            for i, agent in enumerate(agent_stats, 1):
                print(f"  {i}. {agent['name']}: {agent['message_count']}条消息, {agent['total_tokens'] or 0} tokens")
        
        # 最近对话
        cursor.execute("""
            SELECT c.id, c.title, u.username, a.name as agent_name,
                   c.start_time, c.total_messages, c.total_tokens
            FROM ai_conversations c
            JOIN ai_users u ON c.user_id = u.id
            JOIN ai_agents a ON c.agent_id = a.id
            ORDER BY c.id DESC
            LIMIT 3
        """)
        recent_convs = cursor.fetchall()
        
        if recent_convs:
            print(f"\n📅 最近对话:")
            for conv in recent_convs:
                start_time = parse_db_time_to_local(conv['start_time'])
                print(f"  {conv['title']} (ID: {conv['id']})")
                print(f"    用户: {conv['username']} | 智能体: {conv['agent_name']}")
                print(f"    开始时间: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"    消息数: {conv['total_messages']} | Token数: {conv['total_tokens']}")
        
        print("=" * 80)
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"获取摘要时出错: {e}")

def main():
    """主函数"""
    # 获取数据库路径
    db_path = get_db_path()
    
    # 设置监控
    start_message_id = setup_enhanced_monitoring(db_path)
    if start_message_id is None:
        return
    
    # 显示初始摘要
    show_enhanced_summary(db_path)
    
    # 开始监控
    try:
        monitor_enhanced_conversations(db_path, start_message_id)
    except Exception as e:
        print(f"监控过程中出现错误: {e}")
    
    # 显示最终摘要
    show_enhanced_summary(db_path)
    print(f"\n监控结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
