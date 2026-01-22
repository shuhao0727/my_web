"""
教师分发表美化模块 - 基于xbk高一export_functions.py中的export_teacher_distribution函数
职责：对已导出的教师分发表Excel文件进行美化处理，包括标题、样式、列宽行高等
"""
import openpyxl
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from openpyxl.utils import get_column_letter
import logging
import sqlite3
import os
import sys

# 导入数据库连接函数 - 尝试相对导入，如果失败则尝试绝对导入
try:
    from ..database import get_db
except ImportError:
    # 如果相对导入失败，可能是直接运行此脚本，将父目录添加到sys.path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    grandparent_dir = os.path.dirname(parent_dir)
    sys.path.insert(0, grandparent_dir)
    from routers.xbk.database import get_db

logger = logging.getLogger(__name__)

def get_course_details(course_code: str, year: int, grade: str):
    """从数据库获取课程详细信息"""
    conn = None
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT 课程名称, 课程负责人, 上课地点 FROM course_catalog WHERE 课程代码 = ? AND 年份 = ? AND 年级 = ?",
            (course_code, year, grade)
        )
        result = cursor.fetchone()
        if result:
            return {
                '课程名称': result[0],
                '课程负责人': result[1],
                '上课地点': result[2]
            }
        else:
            return None
    except Exception as e:
        logger.error(f"获取课程详情失败: {str(e)}")
        return None
    finally:
        if conn:
            conn.close()

def apply_excel_style(ws, header_fill_color="CCE5FF"):
    """应用Excel样式 - 优化边框设定，确保所有单元格都有完整边框"""
    # 设置表头样式（第1行）
    header_fill = PatternFill(start_color=header_fill_color, end_color=header_fill_color, fill_type="solid")
    header_font = Font(bold=True, size=11)
    thin_border = Border(left=Side(style='thin'), right=Side(style='thin'),
                        top=Side(style='thin'), bottom=Side(style='thin'))
    
    # 获取所有合并区域
    merged_ranges = list(ws.merged_cells.ranges) if ws.merged_cells else []
    
    # 辅助函数：检查单元格是否为合并区域的左上角
    def is_top_left_of_merged(cell):
        cell_row, cell_col = cell.row, cell.column
        for merged_range in merged_ranges:
            # 合并区域左上角的最小行和列
            if cell_row == merged_range.min_row and cell_col == merged_range.min_col:
                return True
        return False
    
    # 辅助函数：检查单元格是否在合并区域内
    def is_in_merged(cell):
        cell_row, cell_col = cell.row, cell.column
        for merged_range in merged_ranges:
            if (merged_range.min_row <= cell_row <= merged_range.max_row and
                merged_range.min_col <= cell_col <= merged_range.max_col):
                return True
        return False
    
    # 只对第一行的非合并单元格或合并区域的左上角应用样式
    for col in range(1, ws.max_column + 1):
        cell = ws.cell(row=1, column=col)
        if not is_in_merged(cell) or is_top_left_of_merged(cell):
            cell.fill = header_fill
            cell.font = header_font
            cell.border = thin_border
            cell.alignment = Alignment(horizontal='center', vertical='center')
    
    # 设置数据单元格样式（从第2行开始）
    for row in range(2, ws.max_row + 1):
        for col in range(1, ws.max_column + 1):
            cell = ws.cell(row=row, column=col)
            if not is_in_merged(cell) or is_top_left_of_merged(cell):
                cell.border = thin_border
                cell.alignment = Alignment(horizontal='center', vertical='center')

def apply_merged_cell_borders(worksheet):
    """
    专门为合并单元格应用边框，确保合并区域的边框完整
    
    参数：
        worksheet: openpyxl Worksheet对象
    """
    thin_border = Border(left=Side(style='thin'), right=Side(style='thin'),
                        top=Side(style='thin'), bottom=Side(style='thin'))
    
    # 获取所有合并区域
    if worksheet.merged_cells:
        merged_ranges = list(worksheet.merged_cells.ranges)
        
        for merged_range in merged_ranges:
            # 获取合并区域的边界
            min_row = merged_range.min_row
            max_row = merged_range.max_row
            min_col = merged_range.min_col
            max_col = merged_range.max_col
            
            # 为合并区域的边界单元格设置边框
            # 上边界
            for col in range(min_col, max_col + 1):
                cell = worksheet.cell(row=min_row, column=col)
                # 只设置上边框，保持其他边框不变
                new_border = Border(
                    left=cell.border.left if cell.border else Side(style='thin'),
                    right=cell.border.right if cell.border else Side(style='thin'),
                    top=Side(style='thin'),  # 确保上边框为细线
                    bottom=cell.border.bottom if cell.border else Side(style='thin')
                )
                cell.border = new_border
            
            # 下边界
            for col in range(min_col, max_col + 1):
                cell = worksheet.cell(row=max_row, column=col)
                new_border = Border(
                    left=cell.border.left if cell.border else Side(style='thin'),
                    right=cell.border.right if cell.border else Side(style='thin'),
                    top=cell.border.top if cell.border else Side(style='thin'),
                    bottom=Side(style='thin')  # 确保下边框为细线
                )
                cell.border = new_border
            
            # 左边界
            for row in range(min_row, max_row + 1):
                cell = worksheet.cell(row=row, column=min_col)
                new_border = Border(
                    left=Side(style='thin'),  # 确保左边框为细线
                    right=cell.border.right if cell.border else Side(style='thin'),
                    top=cell.border.top if cell.border else Side(style='thin'),
                    bottom=cell.border.bottom if cell.border else Side(style='thin')
                )
                cell.border = new_border
            
            # 右边界
            for row in range(min_row, max_row + 1):
                cell = worksheet.cell(row=row, column=max_col)
                new_border = Border(
                    left=cell.border.left if cell.border else Side(style='thin'),
                    right=Side(style='thin'),  # 确保右边框为细线
                    top=cell.border.top if cell.border else Side(style='thin'),
                    bottom=cell.border.bottom if cell.border else Side(style='thin')
                )
                cell.border = new_border
            
            # 左上角单元格（确保所有边框都设置）
            top_left_cell = worksheet.cell(row=min_row, column=min_col)
            top_left_cell.border = thin_border
            
            # 右上角单元格
            top_right_cell = worksheet.cell(row=min_row, column=max_col)
            top_right_cell.border = thin_border
            
            # 左下角单元格
            bottom_left_cell = worksheet.cell(row=max_row, column=min_col)
            bottom_left_cell.border = thin_border
            
            # 右下角单元格
            bottom_right_cell = worksheet.cell(row=max_row, column=max_col)
            bottom_right_cell.border = thin_border

def adjust_column_widths(worksheet):
    """
    调整列宽，优化打印友好性，考虑中文字符宽度
    
    参数：
        worksheet: openpyxl Worksheet对象
    """
    # 定义各列推荐宽度（针对A4纸打印优化）
    # 教师分发表结构：A:班级, B:姓名, C-I:第1-7次签到
    recommended_widths = {
        'A': 12,   # 班级 - 适当宽度
        'B': 12,   # 姓名 - 适当宽度
        'C': 10,   # 第1次签到
        'D': 10,   # 第2次签到
        'E': 10,   # 第3次签到
        'F': 10,   # 第4次签到
        'G': 10,   # 第5次签到
        'H': 10,   # 第6次签到
        'I': 10    # 第7次签到
    }
    
    # 定义各列最大宽度限制，避免过宽
    max_widths = {
        'A': 15,   # 班级最大15字符
        'B': 15,   # 姓名最大15字符
        'C': 12,   # 签到列最大12字符
        'D': 12,
        'E': 12,
        'F': 12,
        'G': 12,
        'H': 12,
        'I': 12
    }
    
    # 计算总列宽，确保适合A4纸
    total_width = 0
    for col in worksheet.columns:
        col_letter = get_column_letter(col[0].column)
        recommended_width = recommended_widths.get(col_letter, 10)
        max_width = max_widths.get(col_letter, 15)
        
        # 检查内容长度
        max_content_length = 0
        for cell in col:
            # 跳过合并单元格（非左上角）
            if cell.value:
                # 计算字符串长度（中文字符算2个宽度）
                cell_length = 0
                for char in str(cell.value):
                    if '\u4e00' <= char <= '\u9fff':  # 中文字符
                        cell_length += 2
                    else:
                        cell_length += 1
                max_content_length = max(max_content_length, cell_length)
        
        # 设置列宽：取推荐宽度和内容所需宽度的较大值，但不超过最大限制
        # 加上2个字符的边距
        content_based_width = max_content_length + 2
        final_width = max(recommended_width, min(content_based_width, max_width))
        worksheet.column_dimensions[col_letter].width = final_width
        total_width += final_width
    
    # 记录总列宽（调试用）
    logger.debug(f"总列宽: {total_width:.1f} 字符")
    
    # 如果总宽度过大，建议横向打印（在页面设置中处理）
    if total_width > 50:  # 大约7英寸，A4纸可用宽度
        logger.debug(f"列宽较大({total_width:.1f})，建议横向打印")

def adjust_row_heights(worksheet):
    """
    调整行高，优化打印友好性
    
    参数：
        worksheet: openpyxl Worksheet对象
    """
    # 标题行高度 - 增加高度以突出标题
    if worksheet.max_row >= 1:
        worksheet.row_dimensions[1].height = 35
    
    # 课程信息行高度 - 增加高度以增强可读性
    if worksheet.max_row >= 2:
        worksheet.row_dimensions[2].height = 25
    
    # 任课教师签名行高度（第3-4行）
    if worksheet.max_row >= 3:
        worksheet.row_dimensions[3].height = 20
    if worksheet.max_row >= 4:
        worksheet.row_dimensions[4].height = 20
    
    # 数据行高度 - 根据内容调整（从第5行开始）
    for row in range(5, worksheet.max_row + 1):
        max_lines = 1
        # 检查该行所有单元格的内容
        for col in range(1, worksheet.max_column + 1):
            cell = worksheet.cell(row=row, column=col)
            if cell.value:
                # 计算文本行数（每30个字符或换行符算一行）
                text = str(cell.value)
                lines = text.count('\n') + 1
                # 长文本自动换行估算
                if len(text) > 30:
                    lines += len(text) // 30
                max_lines = max(max_lines, lines)
        
        # 设置行高：基础高度 + 额外行高度
        base_height = 18
        extra_height = (max_lines - 1) * 5
        worksheet.row_dimensions[row].height = min(base_height + extra_height, 40)

def set_page_settings(worksheet):
    """
    设置页面设置，优化打印效果
    
    参数：
        worksheet: openpyxl Worksheet对象
    """
    # 设置为横向打印，以适应较宽的表格
    worksheet.page_setup.orientation = 'landscape'  # 使用字符串 'landscape'
    
    # 设置纸张大小为A4（9代表A4）
    worksheet.page_setup.paperSize = 9  # 9 = A4
    
    # 设置缩放比例，确保表格适合页面宽度
    worksheet.page_setup.fitToWidth = 1
    worksheet.page_setup.fitToHeight = 0  # 不限制高度
    
    # 设置页边距（英寸）
    worksheet.page_margins.left = 0.3
    worksheet.page_margins.right = 0.3
    worksheet.page_margins.top = 0.5
    worksheet.page_margins.bottom = 0.5
    worksheet.page_margins.header = 0.2
    worksheet.page_margins.footer = 0.2
    
    # 设置打印选项
    worksheet.print_options.gridLines = True  # 打印网格线
    worksheet.print_options.horizontalCentered = True  # 水平居中
    
    # 设置标题行重复（第1-5行作为标题）
    worksheet.print_title_rows = '1:5'
    
    # 设置打印质量
    worksheet.sheet_properties.pageSetUpPr.fitToPage = True

def beautify_teacher_distribution_file(file_path: str, year_start: int, year_end: int, grade: str):
    """
    对教师分发表Excel文件进行美化处理
    
    参数：
        file_path: Excel文件路径
        year_start: 标题起始年份（也是数据年份）
        year_end: 标题结束年份
        grade: 年级
    
    美化逻辑基于xbk高一export_functions.py中的export_teacher_distribution函数
    """
    try:
        # 加载工作簿
        workbook = openpyxl.load_workbook(file_path)
        
        # 获取课程数据（从数据库中获取课程信息，但这里我们只能从现有工作表中提取）
        # 由于数据导出模块已经导出了数据，我们假设每个工作表都是一个课程，工作表名称是课程代码
        for sheet_name in workbook.sheetnames:
            ws = workbook[sheet_name]
            if ws is None:
                logger.warning(f"工作表 {sheet_name} 不存在，跳过")
                continue
            
            # 从工作表标题提取课程代码
            course_code = sheet_name
            
            # 从数据库获取课程详细信息
            course_details = get_course_details(course_code, year_start, grade)
            
            # 统计学生人数（从第5行开始的数据行数，排除空行）
            student_count = 0
            for row in range(5, ws.max_row + 1):
                class_cell = ws.cell(row=row, column=1).value  # A列：班级
                name_cell = ws.cell(row=row, column=2).value   # B列：姓名
                if class_cell and name_cell and str(class_cell).strip() != "暂无学生选课":
                    student_count += 1
            
            # 先设置值，再合并单元格
            # 标题行（A1）
            title_cell = ws.cell(row=1, column=1)  # A1
            title_cell.value = f"{year_start}-{year_end} 学年江苏省昆山中学 {grade} 校本课程学生签到表"  # type: ignore
            title_cell.font = Font(size=14, bold=True)
            title_cell.alignment = Alignment(horizontal='center', vertical='center')
            ws.merge_cells('A1:I1')
            
            # 课程信息行（A2）- 包含完整信息
            if course_details:
                course_name = course_details.get('课程名称', '')
                teacher = course_details.get('课程负责人', '')
                location = course_details.get('上课地点', '')
                info_text = (f"课程代码: {course_code}  课程名称: {course_name}  "
                           f"课程负责人: {teacher}  上课地点: {location}  人数: {student_count}")
            else:
                info_text = f"课程代码: {course_code}   人数: {student_count}"
            
            info_cell = ws.cell(row=2, column=1)  # A2
            info_cell.value = info_text  # type: ignore
            info_cell.alignment = Alignment(horizontal='center', vertical='center')
            ws.merge_cells('A2:I2')
            
            # 任课教师签名（A3）- 合并A3:B4
            teacher_sign_cell = ws.cell(row=3, column=1)  # A3
            teacher_sign_cell.value = "任课教师签名"  # type: ignore
            teacher_sign_cell.alignment = Alignment(horizontal='center', vertical='center')
            teacher_sign_cell.font = Font(bold=True)
            ws.merge_cells('A3:B4')
            
            # 第1-7次签到表头（第3行）- 不合并第4行，只设置第3行的值
            for idx, text in enumerate(["一", "二", "三", "四", "五", "六", "七"], start=3):
                col_idx = idx
                cell = ws.cell(row=3, column=col_idx)
                cell.value = f"第{text}次"  # type: ignore
                cell.alignment = Alignment(horizontal='center', vertical='center')
                cell.font = Font(bold=True)
                # 注意：不合并第4行，所以第4行保持为空
            
            # 数据列标题（第5行）- 只设置班级和姓名，签到列标题已在第3行设置
            headers = ['班级', '姓名']
            for col_idx, header in enumerate(headers, start=1):
                cell = ws.cell(row=5, column=col_idx)
                cell.value = header  # type: ignore
                cell.font = Font(bold=True)
                cell.alignment = Alignment(horizontal='center', vertical='center')
            
            # 清除C5到I5的值（签到列标题不应该在第5行显示）
            for col_idx in range(3, 10):
                cell = ws.cell(row=5, column=col_idx)
                cell.value = None
            
            # 手动设置合并单元格的样式（因为apply_excel_style会跳过合并单元格）
            # 设置A1:I1合并区域的样式（只有A1可访问）
            title_cell = ws.cell(row=1, column=1)
            title_cell.fill = PatternFill(start_color="E6F3FF", end_color="E6F3FF", fill_type="solid")
            
            # 设置A2:I2合并区域的样式（只有A2可访问）
            info_cell = ws.cell(row=2, column=1)
            info_cell.fill = PatternFill(start_color="F0F8FF", end_color="F0F8FF", fill_type="solid")
            
            # 设置A3:B4合并区域的样式（只有A3可访问）
            teacher_sign_cell = ws.cell(row=3, column=1)
            teacher_sign_cell.fill = PatternFill(start_color="CCE5FF", end_color="CCE5FF", fill_type="solid")
            
            # 设置第3行签到表头的样式（只有第3行的C3、D3等可访问）
            for col_idx in range(3, 10):
                cell = ws.cell(row=3, column=col_idx)
                cell.fill = PatternFill(start_color="CCE5FF", end_color="CCE5FF", fill_type="solid")
            
            # 应用样式到其他非合并单元格（包括第5行及以下的数据行）
            apply_excel_style(ws)
            
            # 专门为合并单元格应用边框，确保边框完整
            apply_merged_cell_borders(ws)
            
            # 应用优化列宽（替代硬编码的列宽设置）
            adjust_column_widths(ws)
            
            # 优化行高设置
            adjust_row_heights(ws)
            
            # 设置页面设置，优化打印效果
            set_page_settings(ws)
        
        # 保存文件
        workbook.save(file_path)
        logger.info(f"教师分发表美化成功: {file_path}")
        
    except Exception as e:
        logger.error(f"教师分发表美化失败: {str(e)}")
        raise

if __name__ == "__main__":
    # 测试代码
    import tempfile
    import pandas as pd
    
    # 创建测试数据 - 模拟数据导出模块的输出
    test_data = pd.DataFrame({
        '班级': ['1', '2', '3'],
        '姓名': ['张三', '李四', '王五'],
        '第1次': ['', '', ''],
        '第2次': ['', '', ''],
        '第3次': ['', '', ''],
        '第4次': ['', '', ''],
        '第5次': ['', '', ''],
        '第6次': ['', '', ''],
        '第7次': ['', '', '']
    })
    
    # 保存测试文件
    with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
        file_path = tmp.name
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            test_data.to_excel(writer, sheet_name='1', index=False, startrow=4)  # 从第5行开始
    
    # 测试美化功能
    try:
        beautify_teacher_distribution_file(file_path, 2024, 2025, '高一')
        print(f"测试成功，文件保存在: {file_path}")
        
        # 验证文件内容
        workbook = openpyxl.load_workbook(file_path)
        if workbook:
            ws = workbook.active
            if ws:
                print(f"工作表名称: {ws.title}")
                print(f"标题: {ws.cell(row=1, column=1).value}")
                print(f"课程信息: {ws.cell(row=2, column=1).value}")
                print(f"表头行数: {ws.max_row}")
            workbook.close()
        
    except Exception as e:
        print(f"测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
