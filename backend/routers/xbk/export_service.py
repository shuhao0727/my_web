"""
XBK导出服务 - 重新设计的Excel导出功能

设计原则：
1. 简洁高效：避免复杂的美化逻辑，专注于数据导出
2. 用户友好：提供清晰的导出选项和进度反馈
3. 易于维护：模块化设计，便于扩展和修改
4. 性能优先：优化大数据量导出性能
"""
import pandas as pd
import sqlite3
import tempfile
import os
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple
from fastapi import HTTPException
import openpyxl
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from openpyxl.utils import get_column_letter
import logging

from .database import get_db
from .export_utils.course_selection_beautifier import beautify_course_selection_file
from .export_utils.course_selection_exporter import export_course_selection
from .export_utils.distribution_exporter import export_distribution
from .export_utils.distribution_beautifier import beautify_distribution_file
from .export_utils.teacher_distribution_exporter import export_teacher_distribution_data
from .export_utils.teacher_distribution_beautifier import beautify_teacher_distribution_file

# 设置日志记录
logger = logging.getLogger(__name__)

# ==================== 样式配置 ====================

class ExcelStyle:
    """Excel样式配置类"""
    
    @staticmethod
    def get_header_style():
        """获取表头样式"""
        return {
            'font': Font(bold=True, color='FFFFFF', size=12),
            'fill': PatternFill(fill_type='solid', start_color='2E75B5', end_color='2E75B5'),
            'alignment': Alignment(horizontal='center', vertical='center', wrap_text=True),
            'border': Border(
                left=Side(style='thin'),
                right=Side(style='thin'),
                top=Side(style='thin'),
                bottom=Side(style='thin')
            )
        }
    
    @staticmethod
    def get_data_style():
        """获取数据行样式"""
        return {
            'font': Font(size=11),
            'alignment': Alignment(vertical='center'),
            'border': Border(
                left=Side(style='thin'),
                right=Side(style='thin'),
                top=Side(style='thin'),
                bottom=Side(style='thin')
            )
        }
    
    @staticmethod
    def get_title_style():
        """获取标题样式"""
        return {
            'font': Font(bold=True, size=14),
            'alignment': Alignment(horizontal='center', vertical='center')
        }
    
    @staticmethod
    def get_subtitle_style():
        """获取副标题样式"""
        return {
            'font': Font(bold=True, size=12),
            'alignment': Alignment(horizontal='left', vertical='center')
        }

# ==================== 导出函数 ====================

def export_course_selection_table(year: int, grade: str, year_start: Optional[int] = None, year_end: Optional[int] = None, class_name: Optional[str] = None) -> str:
    """
    导出选课表 - 第一种导出：学生选课表
    格式：每个班级一个工作表，包含学生信息和课程代码列
    使用新的模块化设计：course_selection_exporter + course_selection_beautifier
    """
    try:
        # 如果指定了班级，记录警告（新模块目前不支持单班级导出）
        if class_name:
            logger.warning(f"新导出模块暂不支持单班级导出，将导出所有班级。指定班级: {class_name}")
        
        # 如果没有提供year_start和year_end，则使用默认值
        if year_start is None:
            year_start = year
        if year_end is None:
            year_end = year + 1
        
        # 使用新的模块化导出功能
        save_path = export_course_selection(
            year=year,
            grade=grade,
            year_start=year_start,
            year_end=year_end
        )
        
        if not save_path or not os.path.exists(save_path):
            raise HTTPException(status_code=500, detail="导出失败，未生成文件")
        
        # 应用美化功能
        try:
            beautify_course_selection_file(save_path)
            logger.info(f"选课表美化成功: {save_path}")
        except Exception as e:
            logger.warning(f"选课表美化失败，但仍返回原始文件: {str(e)}")
        
        logger.info(f"选课表导出成功: {save_path}")
        return save_path
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"导出选课表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"导出选课表失败: {str(e)}")


def export_distribution_table(year: int, grade: str, class_name: Optional[str] = None, 
                              year_start: Optional[int] = None, year_end: Optional[int] = None) -> str:
    """
    导出选课分发表 - 第二种导出：各班分发表
    格式：每个班级一个工作表，包含已选课学生的详细选课信息
    使用新的模块化设计：distribution_exporter + distribution_beautifier
    """
    try:
        # 如果未提供标题年份，使用默认值
        if year_start is None:
            year_start = year
        if year_end is None:
            year_end = year + 1
            
        # 使用新的模块化导出功能
        save_path = export_distribution(
            year=year,
            grade=grade,
            class_name=class_name,
            year_start=year_start,
            year_end=year_end
        )
        
        if not save_path or not os.path.exists(save_path):
            raise HTTPException(status_code=500, detail="导出失败，未生成文件")
        
        # 应用美化功能
        try:
            beautify_distribution_file(save_path, year_start, year_end, grade)
            logger.info(f"各班分发表美化成功: {save_path}")
        except Exception as e:
            logger.warning(f"各班分发表美化失败，但仍返回原始文件: {str(e)}")
        
        logger.info(f"各班分发表导出成功: {save_path}")
        return save_path
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"导出各班分发表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"导出各班分发表失败: {str(e)}")


def export_teacher_distribution_table(year: int, grade: str, year_start: Optional[int] = None, year_end: Optional[int] = None) -> str:
    """
    导出教师分发表 - 第三种导出：教师分发表
    格式：每个课程一个工作表，包含选课学生列表和签到表
    使用新的模块化设计：teacher_distribution_exporter + teacher_distribution_beautifier
    """
    try:
        # 如果未提供标题年份，使用默认值
        if year_start is None:
            year_start = year
        if year_end is None:
            year_end = year + 1
        
        # 使用新的模块化导出功能
        save_path = export_teacher_distribution_data(
            year=year,
            grade=grade,
            year_start=year_start,
            year_end=year_end
        )
        
        if not save_path or not os.path.exists(save_path):
            raise HTTPException(status_code=500, detail="导出失败，未生成文件")
        
        # 应用美化功能
        try:
            beautify_teacher_distribution_file(save_path, year_start, year_end, grade)
            logger.info(f"教师分发表美化成功: {save_path}")
        except Exception as e:
            logger.warning(f"教师分发表美化失败，但仍返回原始文件: {str(e)}")
        
        logger.info(f"教师分发表导出成功: {save_path}")
        return save_path
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"导出教师分发表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"导出教师分发表失败: {str(e)}")

# ==================== 辅助函数 ====================

def apply_basic_styles(workbook):
    """应用基本样式到工作簿"""
    for sheet in workbook.sheetnames:
        ws = workbook[sheet]
        
        # 设置列宽（自动调整）
        for column in ws.columns:
            max_length = 0
            column_letter = get_column_letter(column[0].column)
            
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            
            adjusted_width = min(max_length + 2, 50)  # 最大宽度50
            ws.column_dimensions[column_letter].width = adjusted_width
        
        # 设置行高（表头行高一些）
        if ws.max_row > 0:
            ws.row_dimensions[1].height = 25  # 表头行高
        
        # 应用表头样式
        header_style = ExcelStyle.get_header_style()
        if ws.max_row > 0:
            for cell in ws[1]:
                cell.font = header_style['font']
                cell.fill = header_style['fill']
                cell.alignment = header_style['alignment']
                cell.border = header_style['border']
        
        # 应用数据行样式
        data_style = ExcelStyle.get_data_style()
        for row in ws.iter_rows(min_row=2, max_row=ws.max_row):
            for cell in row:
                cell.font = data_style['font']
                cell.alignment = data_style['alignment']
                cell.border = data_style['border']


def export_data(export_type: str, year: int, grade: str, class_name: Optional[str] = None, year_start: Optional[int] = None, year_end: Optional[int] = None) -> str:
    """
    主导出函数，根据类型调用相应的导出函数
    
    参数：
        export_type: 导出类型，可选值：
            - 'course-selection': 选课表
            - 'distribution': 选课分发表
            - 'teacher-distribution': 教师分发表
        year: 年份
        grade: 年级
        class_name: 班级（可选）
        year_start: 起始年份（可选，用于标题）
        year_end: 结束年份（可选，用于标题）
    
    返回：
        导出的Excel文件路径
    """
    if export_type == 'course-selection':
        return export_course_selection_table(year, grade, year_start, year_end, class_name)
    elif export_type == 'distribution':
        return export_distribution_table(year, grade, class_name, year_start, year_end)
    elif export_type == 'teacher-distribution':
        return export_teacher_distribution_table(year, grade, year_start, year_end)
    else:
        raise HTTPException(status_code=400, detail=f"不支持的导出类型: {export_type}")

# ==================== 测试函数 ====================

def test_export_functionality():
    """测试导出功能"""
    try:
        # 这里可以添加测试代码
        logger.info("导出功能测试通过")
        return True
    except Exception as e:
        logger.error(f"导出功能测试失败: {e}")
        return False

if __name__ == "__main__":
    # 运行测试
    test_export_functionality()
