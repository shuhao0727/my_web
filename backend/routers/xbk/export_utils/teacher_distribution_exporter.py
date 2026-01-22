"""
教师分发表数据导出模块

职责：专注于从数据库导出教师分发表原始数据到Excel文件，不包含任何样式美化
设计原则：单一职责，只负责数据查询和导出，不涉及样式设置
"""
import pandas as pd
import sqlite3
import tempfile
import os
from datetime import datetime
import logging

# 导入数据库连接函数
from ..database import get_db

logger = logging.getLogger(__name__)

def export_teacher_distribution_data(year: int, grade: str, year_start: int, year_end: int) -> str:
    """
    导出教师分发表原始数据到Excel文件
    
    参数：
        year: 数据年份（如2025）
        grade: 年级（如'高一'）
        year_start: 标题起始年份（如2025）
        year_end: 标题结束年份（如2026）
    
    返回：
        导出的Excel文件路径
    """
    conn = None
    try:
        # 创建临时文件
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
            save_path = tmp.name
        
        logger.info(f"开始导出教师分发表数据: 年份={year}, 年级={grade}, 学年={year_start}-{year_end}")
        
        conn = get_db()
        
        # 获取课程目录数据（按课程代码排序）
        where_clause = "年份 = ? AND 年级 = ?"
        params = [year, grade]
        
        course_catalog = pd.read_sql_query(
            f'SELECT * FROM course_catalog WHERE {where_clause}',
            conn, params=params
        )
        
        if course_catalog.empty:
            logger.warning(f"没有找到课程目录数据: 年份={year}, 年级={grade}")
            # 返回空文件路径，由上层处理
            return save_path
        
        # 获取合并数据（用于获取每个课程的学生列表）
        merged_data = pd.read_sql_query(
            f'SELECT * FROM merged_data WHERE {where_clause}',
            conn, params=params
        )
        
        # 创建Excel写入器
        with pd.ExcelWriter(save_path, engine='openpyxl') as writer:
            # 按课程代码排序
            course_catalog = course_catalog.sort_values(by='课程代码', key=lambda x: x.astype(int))
            
            total_courses = len(course_catalog)
            logger.info(f"共发现 {total_courses} 门课程")
            
            for idx, course in course_catalog.iterrows():
                course_code = course['课程代码']
                course_name = course['课程名称']
                teacher = course['课程负责人']
                location = course['上课地点']
                
                # 获取该课程的学生列表
                course_students = merged_data[merged_data['课程代码'] == course_code].copy()
                student_count = len(course_students)
                
                # 创建数据框
                if not course_students.empty:
                    # 选择需要的列：班级、姓名
                    student_df = course_students[['班级', '姓名']].copy()
                    # 按班级和姓名排序
                    student_df = student_df.sort_values(by=['班级', '姓名'], 
                                                       key=lambda x: x.astype(int) if x.name == '班级' else x)
                    
                    # 添加7个签到列（空列）- 使用空字符串作为列名，但需要确保列名不重复
                    for i in range(1, 8):
                        # 使用唯一的列名，但实际值是空字符串
                        col_name = f'签到{i}'
                        student_df[col_name] = ''
                else:
                    # 没有学生选课的情况
                    student_df = pd.DataFrame({
                        '班级': ['暂无学生选课'],
                        '姓名': [''],
                    })
                    # 添加7个空列
                    for i in range(1, 8):
                        col_name = f'签到{i}'
                        student_df[col_name] = ''
                
                # 写入工作表（从第5行开始，为标题留出空间）
                sheet_name = f"{course_code}"
                student_df.to_excel(writer, sheet_name=sheet_name, index=False, startrow=4)
                
                logger.debug(f"写入课程 {course_code}: {student_count} 名学生")
        
        logger.info(f"教师分发表数据导出成功: {save_path}")
        return save_path
        
    except Exception as e:
        logger.error(f"导出教师分发表数据失败: {str(e)}")
        raise
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    # 测试代码
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # 设置日志
    logging.basicConfig(level=logging.INFO,
                       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    try:
        # 测试导出功能
        save_path = export_teacher_distribution_data(
            year=2025,
            grade='高一',
            year_start=2025,
            year_end=2026
        )
        
        print(f"测试成功，文件保存在: {save_path}")
        
        # 验证文件内容
        import openpyxl
        wb = openpyxl.load_workbook(save_path)
        print(f"工作簿包含 {len(wb.sheetnames)} 个工作表")
        for sheet_name in wb.sheetnames[:3]:  # 只查看前3个
            ws = wb[sheet_name]
            print(f"  工作表 '{sheet_name}': 行数={ws.max_row}, 列数={ws.max_column}")
        wb.close()
        
        # 清理临时文件
        os.unlink(save_path)
        print(f"清理临时文件: {save_path}")
        
    except Exception as e:
        print(f"测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
