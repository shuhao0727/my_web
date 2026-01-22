"""
学生选课表数据导出器

功能：只负责从数据库导出学生选课表数据到Excel，不包含任何美化逻辑。
设计原则：
1. 单一职责：仅负责数据读取和写入
2. 无状态：不修改文件样式、验证、保护等
3. 可组合：输出可以被其他美化工具处理
"""
import pandas as pd
import sqlite3
import tempfile
import os
import logging
import shutil
from pathlib import Path

# 设置日志记录
logger = logging.getLogger(__name__)

# ==================== 纯数据导出函数 ====================

def export_course_selection(year: int, grade: str, year_start: int, year_end: int) -> str:
    """
    导出学生选课表数据（纯数据，无样式）
    
    参数:
        year: 用于数据库筛选的年份
        grade: 用于数据库筛选的年级
        year_start: 用于文件命名的起始年份
        year_end: 用于文件命名的结束年份
        
    返回:
        导出的Excel文件路径（已重命名包含年份和年级信息）
    """
    conn = None
    temp_file = None
    save_path = None
    try:
        # 创建临时文件
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
        temp_file.close()
        save_path = temp_file.name
        
        # 连接到数据库
        from ..database import get_db
        conn = get_db()
        
        # 构建查询条件
        where_conditions = ["年份 = ?", "年级 = ?"]
        params = [year, grade]
        where_clause = " AND ".join(where_conditions)
        
        # 获取课程目录 - 只选择需要的字段，不包含id、年份、创建时间等
        course_catalog = pd.read_sql_query(
            f'SELECT 课程代码, 课程名称, 课程负责人, 各班限报人数, 上课地点 FROM course_catalog WHERE {where_clause}',
            conn, params=params
        )
        
        # 确保所有列都没有None值
        course_catalog = course_catalog.fillna('')
        
        # 重新排列列顺序以匹配样例文件格式（删除"对选课学生的要求"列）
        course_catalog = course_catalog[['课程代码', '课程名称', '课程负责人', '各班限报人数', '上课地点']]
        
        # 获取学生信息 - 选择需要的字段
        student_info = pd.read_sql_query(
            f'SELECT 班级, 学号, 姓名 FROM student_info WHERE {where_clause}',
            conn, params=params
        )
        
        if student_info.empty:
            raise ValueError("没有找到学生信息数据")
        
        # 确保学生信息也没有None值
        student_info = student_info.fillna('')
        
        # 创建Excel写入器
        with pd.ExcelWriter(save_path, engine='openpyxl') as writer:
            # 写入课程目录（第一个工作表）- 不添加标题，保持纯数据
            if not course_catalog.empty:
                # 保存原始数据，不添加标题（标题会在美化时添加）
                # 使用keep_default_na=False确保空值不被转换为NaN
                course_catalog.to_excel(writer, sheet_name='校本课程目录', index=False, na_rep='')
            else:
                # 创建空的工作表
                pd.DataFrame({'提示': ['暂无课程目录数据']}).to_excel(
                    writer, sheet_name='校本课程目录', index=False
                )
            
            # 按班级分组写入学生信息
            classes = sorted(student_info['班级'].unique(), key=lambda x: int(str(x)))
            
            for cls in classes:
                class_df = student_info[student_info['班级'] == cls].copy()
                # 重命名列名以匹配样例文件格式
                class_df = class_df.rename(columns={'姓名': 'xm'})
                # 确保xm列没有None值
                class_df['xm'] = class_df['xm'].fillna('')
                
                # 添加课程代码列（空列），删除xb列
                class_df['课程代码'] = ''  # 空列，用于学生填写
                
                # 确保空值为空字符串而不是None
                class_df['课程代码'] = class_df['课程代码'].fillna('')
                
                # 重新排列列顺序以匹配样例文件格式（删除xb列）
                columns = ['班级', '学号', 'xm', '课程代码']
                class_df = class_df[columns]
                
                # 写入数据
                sheet_name = f"{cls}"
                class_df.to_excel(writer, sheet_name=sheet_name, index=False, na_rep='')
        
        # 重命名文件，包含年份和年级信息
        final_path = rename_export_file(save_path, year_start, year_end, grade)
        
        logger.info(f"学生选课表数据导出成功: {final_path}")
        return final_path
        
    except Exception as e:
        logger.error(f"导出学生选课表数据失败: {str(e)}")
        # 清理临时文件
        if save_path and os.path.exists(save_path):
            os.unlink(save_path)
        raise
    finally:
        if conn:
            conn.close()


def rename_export_file(file_path: str, year_start: int, year_end: int, grade: str) -> str:
    """
    重命名导出文件，包含年份和年级信息
    """
    # 构建新文件名
    dir_name = os.path.dirname(file_path)
    new_filename = f"学生选课表_{year_start}-{year_end}_{grade}.xlsx"
    new_path = os.path.join(dir_name, new_filename)
    
    # 如果目标文件已存在，先删除
    if os.path.exists(new_path):
        os.unlink(new_path)
    
    # 移动文件
    shutil.move(file_path, new_path)
    
    return new_path


# ==================== 测试函数 ====================

def test_export():
    """测试纯数据导出功能"""
    try:
        # 测试导出
        result = export_course_selection(
            year=2025,
            grade="高一",
            year_start=2024,
            year_end=2025
        )
        print(f"数据导出成功: {result}")
        
        # 验证文件存在
        if os.path.exists(result):
            print(f"文件大小: {os.path.getsize(result)} 字节")
            
            # 尝试读取文件，验证基本结构
            try:
                import openpyxl
                wb = openpyxl.load_workbook(result)
                print(f"工作表数量: {len(wb.sheetnames)}")
                print(f"工作表名称: {wb.sheetnames}")
                
                # 检查校本课程目录
                if "校本课程目录" in wb.sheetnames:
                    ws = wb["校本课程目录"]
                    print(f"\n=== 校本课程目录 ===")
                    print(f"行数: {ws.max_row}")
                    print(f"列数: {ws.max_column}")
                    
                    # 读取表头
                    headers = [ws.cell(row=1, column=col).value for col in range(1, ws.max_column + 1)]
                    print(f"表头: {headers}")
                    
                    # 读取前3行数据
                    print("前3行数据:")
                    for row in range(1, min(4, ws.max_row + 1)):
                        row_data = [ws.cell(row=row, column=col).value for col in range(1, ws.max_column + 1)]
                        print(f"行{row}: {row_data}")
                
                # 检查班级工作表
                for sheet_name in wb.sheetnames:
                    if sheet_name != "校本课程目录":
                        ws = wb[sheet_name]
                        print(f"\n=== {sheet_name}班 ===")
                        print(f"行数: {ws.max_row}")
                        print(f"列数: {ws.max_column}")
                        
                        # 读取表头
                        headers = [ws.cell(row=1, column=col).value for col in range(1, ws.max_column + 1)]
                        print(f"表头: {headers}")
                        
                        # 读取前3行数据
                        print("前3行数据:")
                        for row in range(1, min(4, ws.max_row + 1)):
                            row_data = [ws.cell(row=row, column=col).value for col in range(1, ws.max_column + 1)]
                            print(f"行{row}: {row_data}")
                        
                wb.close()
            except Exception as e:
                print(f"读取Excel文件时出错: {e}")
                import traceback
                traceback.print_exc()
                
        return True
    except Exception as e:
        print(f"数据导出失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # 运行测试
    print("=== 测试学生选课表数据导出 ===")
    print("注意：此测试仅验证数据导出功能，不包含美化")
    print()
    test_export()
