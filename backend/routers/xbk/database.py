"""
XBK数据库连接和工具函数
"""
import sqlite3
import os
from typing import Dict, Any, Tuple


def get_db():
    """获取XBK数据库连接"""
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "xbk.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # 返回字典格式的结果
    return conn


def build_where_clause(params: Dict[str, Any]) -> tuple:
    """构建SQL WHERE子句"""
    conditions = []
    values = []
    
    if params.get('year'):
        conditions.append("年份 = ?")
        values.append(params['year'])
    
    if params.get('grade'):
        conditions.append("年级 = ?")
        values.append(params['grade'])
    
    if params.get('class_name'):
        conditions.append("班级 = ?")
        values.append(params['class_name'])
    
    where_clause = " AND ".join(conditions) if conditions else "1=1"
    return where_clause, values


def build_search_where_clause(params: Dict[str, Any], data_type: str) -> tuple:
    """构建支持搜索的SQL WHERE子句"""
    conditions = []
    values = []
    
    if params.get('year'):
        conditions.append("年份 = ?")
        values.append(params['year'])
    
    if params.get('grade'):
        conditions.append("年级 = ?")
        values.append(params['grade'])
    
    if params.get('class_name'):
        conditions.append("班级 = ?")
        values.append(params['class_name'])
    
    # 搜索文本处理
    if params.get('search_text'):
        search_text = f"%{params['search_text']}%"
        # 根据数据类型确定搜索字段
        if data_type == 'catalog':
            search_conditions = [
                "课程代码 LIKE ?",
                "课程名称 LIKE ?",
                "课程负责人 LIKE ?",
                "上课地点 LIKE ?"
            ]
        elif data_type == 'student-info':
            search_conditions = [
                "学号 LIKE ?",
                "姓名 LIKE ?",
                "班级 LIKE ?"
            ]
        elif data_type == 'course-selection':
            search_conditions = [
                "学号 LIKE ?",
                "姓名 LIKE ?",
                "班级 LIKE ?",
                "课程代码 LIKE ?",
                "课程名称 LIKE ?"
            ]
        elif data_type == 'merged-data':
            search_conditions = [
                "学号 LIKE ?",
                "姓名 LIKE ?",
                "班级 LIKE ?",
                "课程代码 LIKE ?",
                "课程名称 LIKE ?",
                "课程负责人 LIKE ?",
                "上课地点 LIKE ?"
            ]
        else:
            search_conditions = []
        
        if search_conditions:
            # 为每个搜索条件添加相同的搜索文本值
            values.extend([search_text] * len(search_conditions))
            conditions.append(f"({' OR '.join(search_conditions)})")
    
    where_clause = " AND ".join(conditions) if conditions else "1=1"
    return where_clause, values


def get_table_name(data_type: str) -> str:
    """获取数据库表名"""
    table_map = {
        'catalog': 'course_catalog',
        'student-info': 'student_info',
        'course-selection': 'course_selection',
        'merged-data': 'merged_data',
    }
    return table_map.get(data_type, data_type)


def update_merged_data(year: int, grade: str, conn=None):
    """更新合并数据表
    Args:
        year: 年份
        grade: 年级
        conn: 可选的数据库连接，如果提供则使用该连接，否则创建新连接
    """
    close_conn = False
    if conn is None:
        conn = get_db()
        close_conn = True
    
    cursor = conn.cursor()
    
    try:
        # 删除旧的合并数据
        cursor.execute("DELETE FROM merged_data WHERE 年份 = ? AND 年级 = ?", (year, grade))
        
        # 插入新的合并数据（连接course_selection、student_info和course_catalog）
        cursor.execute("""
            INSERT INTO merged_data 
            (年份, 年级, 班级, 学号, 姓名, 课程代码, 课程名称, 课程负责人, 各班限报人数, 上课地点)
            SELECT 
                cs.年份,
                cs.年级,
                COALESCE(NULLIF(TRIM(cs.班级), ''), si.班级) as 班级,
                cs.学号,
                COALESCE(NULLIF(TRIM(cs.姓名), ''), si.姓名) as 姓名,
                cs.课程代码,
                COALESCE(NULLIF(TRIM(cs.课程名称), ''), cc.课程名称) as 课程名称,
                cc.课程负责人,
                cc.各班限报人数,
                cc.上课地点
            FROM course_selection cs
            LEFT JOIN student_info si ON 
                cs.年份 = si.年份 AND 
                cs.年级 = si.年级 AND 
                cs.学号 = si.学号
            LEFT JOIN course_catalog cc ON 
                cs.年份 = cc.年份 AND 
                cs.年级 = cc.年级 AND 
                cs.课程代码 = cc.课程代码
            WHERE cs.年份 = ? AND cs.年级 = ?
        """, (year, grade))
        
        if close_conn:
            conn.commit()
        
    except Exception as e:
        if close_conn:
            conn.rollback()
        raise e
    finally:
        if close_conn:
            conn.close()
