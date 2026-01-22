"""
各班分发表美化模块

职责：专注于对已导出的各班分发表Excel文件进行美化处理
包括：添加标题、设置样式、调整列宽行高、应用边框等
设计原则：单一职责，只负责样式美化，不涉及数据导出
"""
import openpyxl
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from openpyxl.utils import get_column_letter
from openpyxl.cell.cell import MergedCell
import logging

logger = logging.getLogger(__name__)

def beautify_distribution_file(file_path: str, year_start: int, year_end: int, grade: str):
    """
    对各班分发表Excel文件进行美化处理
    
    参数：
        file_path: Excel文件路径
        year_start: 标题起始年份
        year_end: 标题结束年份
        grade: 年级
    """
    try:
        # 加载工作簿
        workbook = openpyxl.load_workbook(file_path)
        
        # 为每个工作表应用美化
        for sheet_name in workbook.sheetnames:
            ws = workbook[sheet_name]
            
            # 添加标题行（合并A1:E1）
            ws.merge_cells('A1:E1')
            title_cell = ws['A1']
            title_cell.value = f"{year_start}-{year_end} 学年江苏省昆山中学 {grade} {sheet_name}班选课分发表"
            title_cell.font = Font(size=14, bold=True)
            title_cell.alignment = Alignment(horizontal='center', vertical='center')
            
            # 设置列标题（第2行）
            headers = ['课程代码', '课程名称', '课程负责人', '上课地点', '姓名']
            for col_idx, header in enumerate(headers, start=1):
                cell = ws.cell(row=2, column=col_idx)
                # 跳过合并单元格（理论上第2行不应该有合并单元格，但安全起见）
                if isinstance(cell, MergedCell):
                    continue
                cell.value = header
                cell.font = Font(bold=True)
                cell.alignment = Alignment(horizontal='center', vertical='center')
            
            # 应用样式到所有单元格
            apply_distribution_style(ws)
            
            # 调整列宽（考虑中文字符宽度）
            adjust_column_widths(ws)
            
            # 调整行高
            adjust_row_heights(ws)
            
            # 设置页面设置，优化打印效果
            set_page_settings(ws)
        
        # 保存文件
        workbook.save(file_path)
        logger.info(f"各班分发表美化成功: {file_path}")
        
    except Exception as e:
        logger.error(f"各班分发表美化失败: {str(e)}")
        raise

def apply_distribution_style(worksheet):
    """
    应用样式到工作表
    
    参数：
        worksheet: openpyxl Worksheet对象
    """
    # 定义边框样式
    thin_border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )
    
    # 定义表头填充样式（蓝色背景）
    header_fill = PatternFill(start_color="CCE5FF", end_color="CCE5FF", fill_type="solid")
    
    # 定义交替行填充样式（浅灰色）
    alternate_fill = PatternFill(start_color="F5F5F5", end_color="F5F5F5", fill_type="solid")
    
    # 应用样式到所有单元格
    for row in worksheet.iter_rows():
        for cell in row:
            # 跳过合并单元格（非左上角）
            if isinstance(cell, MergedCell):
                continue
                
            # 应用边框
            cell.border = thin_border
            
            # 设置对齐方式
            cell.alignment = Alignment(horizontal='center', vertical='center')
            
            # 表头样式（第2行）
            if cell.row == 2:
                cell.fill = header_fill
                cell.font = Font(bold=True, size=11)
            
            # 数据行样式（从第3行开始）
            elif cell.row >= 3:
                # 交替行颜色
                if cell.row % 2 == 0:
                    cell.fill = alternate_fill

def adjust_column_widths(worksheet):
    """
    调整列宽，优化打印友好性
    
    参数：
        worksheet: openpyxl Worksheet对象
    """
    # 定义各列推荐宽度（针对A4纸打印优化）
    recommended_widths = {
        'A': 8,    # 课程代码 - 进一步缩小宽度（之前10仍然偏宽）
        'B': 25,   # 课程名称 - 增加宽度以显示完整课程名
        'C': 15,   # 课程负责人 - 适当增加
        'D': 18,   # 上课地点 - 适当增加
        'E': 10    # 姓名 - 适当增加
    }
    
    # 定义各列最大宽度限制，避免过宽
    max_widths = {
        'A': 12,   # 课程代码最大12字符（进一步限制）
        'B': 30,   # 课程名称最大30字符
        'C': 20,   # 课程负责人最大20字符
        'D': 25,   # 上课地点最大25字符
        'E': 15    # 姓名最大15字符
    }
    
    # 计算总列宽，确保适合A4纸
    total_width = 0
    for col in worksheet.columns:
        col_letter = get_column_letter(col[0].column)
        recommended_width = recommended_widths.get(col_letter, 12)
        max_width = max_widths.get(col_letter, 20)
        
        # 检查内容长度
        max_content_length = 0
        for cell in col:
            # 跳过合并单元格（非左上角）
            if isinstance(cell, MergedCell):
                continue
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
    
    # 列标题行高度 - 增加高度以增强可读性
    if worksheet.max_row >= 2:
        worksheet.row_dimensions[2].height = 25
    
    # 数据行高度 - 根据内容调整
    for row in range(3, worksheet.max_row + 1):
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
    
    # 设置标题行重复（第1-2行作为标题）
    # 注意：print_title_rows 应该通过 worksheet.print_title_rows 设置，但 openpyxl 中正确的属性是 worksheet.print_title_rows
    # 实际上，openpyxl 中设置打印标题行的方法是通过 worksheet.print_options 或直接赋值 print_title_rows
    # 我们使用 worksheet.print_title_rows 属性
    worksheet.print_title_rows = '1:2'
    
    # 设置打印质量
    worksheet.sheet_properties.pageSetUpPr.fitToPage = True

if __name__ == "__main__":
    # 测试代码
    import tempfile
    import pandas as pd
    
    # 创建测试数据
    test_data = pd.DataFrame({
        '课程代码': [1, 2, 3],
        '课程名称': ['史记选读', '唐诗宋词选读', '数学与生活'],
        '课程负责人': ['潘佳颖', '潘佳颖', '戚涵彬'],
        '上课地点': ['高一1班', '高一2班', '高一3班'],
        '姓名': ['瞿梓萱', '张涵柯', '姚泽轩']
    })
    
    # 保存测试文件
    with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
        file_path = tmp.name
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            test_data.to_excel(writer, sheet_name='1', index=False)
    
    # 测试美化功能
    try:
        beautify_distribution_file(file_path, 2024, 2025, '高一')
        print(f"测试成功，文件保存在: {file_path}")
    except Exception as e:
        print(f"测试失败: {str(e)}")
