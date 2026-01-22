"""
各班分发表数据导出模块

职责：专注于从数据库导出各班分发表原始数据，不包含任何样式逻辑
设计原则：单一职责，只负责数据查询、排序和写入Excel原始文件
"""
import pandas as pd
import sqlite3
import tempfile
import os
import logging
from typing import Optional, List, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

def export_distribution(year: int, grade: str, class_name: Optional[str] = None, 
                       year_start: Optional[int] = None, year_end: Optional[int] = None) -> str:
    """
    导出各班分发表原始数据
    
    参数：
        year: 数据库筛选年份
        grade: 数据库筛选年级
        class_name: 可选，指定班级（如'1'），如果为None则导出所有班级
        year_start: 可选，标题起始年份
        year_end: 可选，标题结束年份
        
    返回：
        导出的Excel文件路径
    """
    conn = None
    try:
        # 创建临时文件
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
            save_path = tmp.name
        
        # 如果未提供标题年份，使用默认值
        if year_start is None:
            year_start = year
        if year_end is None:
            year_end = year + 1
            
        year_str = f"{year_start}-{year_end}"
        
        # 连接数据库 - 使用绝对导入，如果失败则尝试相对导入
        try:
            from backend.routers.xbk.database import get_db
        except ImportError:
            from ..database import get_db
        conn = get_db()
        
        # 构建查询条件
        where_conditions = ["m.年份 = ?", "m.年级 = ?"]
        params = [year, grade]
        
        if class_name:
            where_conditions.append("m.班级 = ?")
            params.append(class_name)
        
        where_clause = " AND ".join(where_conditions)
        
        # 获取合并数据（包含学生信息和课程信息）
        query = f"""
            SELECT 
                m.班级, m.学号, m.姓名, m.课程代码, m.课程名称,
                m.课程负责人, m.上课地点
            FROM merged_data m
            WHERE {where_clause}
            ORDER BY m.班级, CAST(m.学号 AS INTEGER), CAST(m.课程代码 AS INTEGER)
        """
        
        merged_data = pd.read_sql_query(query, conn, params=params)
        
        if merged_data.empty:
            raise ValueError(f"没有找到选课数据: year={year}, grade={grade}")
        
        # 创建Excel写入器
        with pd.ExcelWriter(save_path, engine='openpyxl') as writer:
            # 按班级分组写入数据
            classes = sorted(merged_data['班级'].unique(), key=lambda x: int(str(x)))
            
            for cls in classes:
                class_df = merged_data[merged_data['班级'] == cls].copy()
                
                # 重新排列列顺序（按照样例文件格式）
                # 样例文件列顺序：课程代码、课程名称、课程负责人、上课地点、姓名
                columns = ['课程代码', '课程名称', '课程负责人', '上课地点', '姓名']
                class_df = class_df[columns]
                
                # 按课程代码升序排序（样例文件中是按课程代码排序的）
                class_df = class_df.sort_values(by='课程代码', key=lambda x: x.astype(int))
                
                # 写入数据，从第3行开始（第1行是标题，第2行是表头，由美化模块添加）
                # 不添加标题行（header=False），因为美化模块会添加表头
                sheet_name = str(cls)  # 工作表名为班级数字，如"1"
                class_df.to_excel(writer, sheet_name=sheet_name, index=False, header=False, startrow=2)
                
                # 注意：不需要插入空行了，因为startrow=2已经预留了标题和表头行
        
        logger.info(f"各班分发表原始数据导出成功: {save_path}")
        return save_path
        
    except Exception as e:
        logger.error(f"导出各班分发表数据失败: {str(e)}")
        raise
    finally:
        if conn:
            conn.close()
