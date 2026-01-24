"""
XBK数据处理路由 - API端点定义
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from fastapi.responses import FileResponse
from typing import List, Optional, Dict, Any
import pandas as pd
from datetime import datetime
import tempfile
import os

from .schemas import (
    ImportRequest,
    QueryRequest,
    DeleteRequest,
    ExportRequest,
    AnalysisRequest,
    SystemConfigResponse
)
from .database import (
    get_db,
    build_where_clause,
    build_search_where_clause,
    get_table_name,
    update_merged_data
)

data_router = APIRouter(tags=["xbk-data"])


@data_router.get("/config/system")
async def get_system_config():
    """获取系统配置"""
    conn = None
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # 获取所有可选的年份
        cursor.execute("SELECT DISTINCT 年份 FROM course_catalog ORDER BY 年份 DESC")
        available_years = [row[0] for row in cursor.fetchall()]
        
        # 获取所有可选的年级
        cursor.execute("SELECT DISTINCT 年级 FROM course_catalog ORDER BY 年级")
        available_grades = [row[0] for row in cursor.fetchall()]
        
        # 获取所有可选的班级
        cursor.execute("SELECT DISTINCT 班级 FROM student_info ORDER BY 班级")
        available_classes = [row[0] for row in cursor.fetchall()]
        
        # 获取当前配置（从system_config表）
        cursor.execute("SELECT config_key, config_value FROM system_config WHERE config_key IN ('current_year', 'current_grade')")
        config_rows = cursor.fetchall()
        config = {row[0]: row[1] for row in config_rows}
        
        current_year_str = config.get('current_year')
        current_year = int(current_year_str) if current_year_str and current_year_str.strip() else None
        current_grade = config.get('current_grade')
        
        return SystemConfigResponse(
            current_year=current_year,
            current_grade=current_grade,
            available_years=available_years,
            available_grades=available_grades,
            available_classes=available_classes
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取系统配置失败: {str(e)}")
    finally:
        if conn:
            conn.close()


@data_router.post("/config/system")
async def update_system_config(config: Dict[str, Any]):
    """更新系统配置"""
    conn = None
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        for key, value in config.items():
            cursor.execute(
                "INSERT OR REPLACE INTO system_config (config_key, config_value, updated_at) VALUES (?, ?, datetime('now'))",
                (key, str(value))
            )
        
        conn.commit()
        return {"success": True, "message": "系统配置更新成功"}
        
    except Exception as e:
        if conn:
            conn.rollback()
        raise HTTPException(status_code=500, detail=f"更新系统配置失败: {str(e)}")
    finally:
        if conn:
            conn.close()


@data_router.post("/import/{data_type}")
async def import_data(
    data_type: str,
    year: int = Query(...),
    grade: str = Query(...),
    file: UploadFile = File(...)
):
    """导入数据（课程目录、学生信息、选课结果）"""
    if data_type not in ['catalog', 'student-info', 'course-selection']:
        raise HTTPException(status_code=400, detail="不支持的数据类型")
    
    conn = None
    try:
        # 读取Excel文件
        content = await file.read()
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
            tmp.write(content)
            tmp_path = tmp.name
        
        try:
            # 使用pandas读取Excel
            df = pd.read_excel(tmp_path)
            
            # 这里应该根据原项目的逻辑进行数据处理
            # 目前先简单地将数据插入数据库
            
            conn = get_db()
            cursor = conn.cursor()
            
            # 获取表名
            table_name = get_table_name(data_type)
            
            # 插入数据
            for _, row in df.iterrows():
                # 这里需要根据不同的数据类型构建不同的插入语句
                # 目前先简单处理
                if data_type == 'catalog':
                    # 处理各班限报人数，处理NaN值
                    limit_num = row.get('各班限报人数', 3)
                    if pd.isna(limit_num):
                        limit_num = 3
                    else:
                        try:
                            limit_num = int(limit_num)
                        except (ValueError, TypeError):
                            limit_num = 3
                    
                    cursor.execute(f"""
                        INSERT OR REPLACE INTO {table_name} 
                        (年份, 年级, 课程代码, 课程名称, 课程负责人, 各班限报人数, 上课地点)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        year, grade,
                        str(row.get('课程代码', '')),
                        str(row.get('课程名称', '')),
                        str(row.get('课程负责人', '')),
                        limit_num,
                        str(row.get('上课地点', ''))
                    ))
                elif data_type == 'student-info':
                    # 处理不同的列名映射：'xm' -> '姓名'
                    name_field = row.get('姓名', '') or row.get('xm', '')
                    cursor.execute(f"""
                        INSERT OR REPLACE INTO {table_name} 
                        (年份, 年级, 班级, 学号, 姓名)
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        year, grade,
                        str(row.get('班级', '')),
                        str(row.get('学号', '')),
                        str(name_field)
                    ))
                elif data_type == 'course-selection':
                    # 从学生信息表获取班级和姓名
                    student_class = ''
                    student_name = ''
                    
                    # 尝试从Excel行获取班级和姓名
                    excel_class = str(row.get('班级', ''))
                    excel_name = str(row.get('姓名', ''))
                    
                    # 如果Excel中没有班级信息，尝试从学生信息表中查询
                    if not excel_class or excel_class == 'nan':
                        cursor.execute("SELECT 班级 FROM student_info WHERE 年份=? AND 年级=? AND 学号=?", 
                                      (year, grade, str(row.get('学号', ''))))
                        student_info = cursor.fetchone()
                        if student_info:
                            student_class = student_info[0]
                        else:
                            student_class = ''
                    else:
                        student_class = excel_class
                    
                    # 如果Excel中没有姓名信息，尝试从学生信息表中查询
                    if not excel_name or excel_name == 'nan':
                        cursor.execute("SELECT 姓名 FROM student_info WHERE 年份=? AND 年级=? AND 学号=?", 
                                      (year, grade, str(row.get('学号', ''))))
                        student_info = cursor.fetchone()
                        if student_info:
                            student_name = student_info[0]
                        else:
                            student_name = ''
                    else:
                        student_name = excel_name
                    
                    cursor.execute(f"""
                        INSERT OR REPLACE INTO {table_name} 
                        (年份, 年级, 班级, 学号, 姓名, 课程代码, 课程名称)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        year, grade,
                        student_class,
                        str(row.get('学号', '')),
                        student_name,
                        str(row.get('课程代码', '')),
                        str(row.get('课程名称', ''))
                    ))
            
            conn.commit()
            
            # 导入成功后，更新合并数据表
            update_merged_data(year, grade)
            
            return {
                "success": True,
                "message": f"数据导入成功，共导入 {len(df)} 条记录",
                "count": len(df)
            }
            
        finally:
            # 清理临时文件
            os.unlink(tmp_path)
            if conn:
                conn.close()
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"数据导入失败: {str(e)}")


@data_router.get("/data/{data_type}")
async def query_data(
    data_type: str,
    year: Optional[int] = None,
    grade: Optional[str] = None,
    class_name: Optional[str] = None,
    search_text: Optional[str] = None,
    page: int = 1,
    page_size: int = 20
):
    """查询数据"""
    if data_type not in ['catalog', 'student-info', 'course-selection', 'merged-data']:
        raise HTTPException(status_code=400, detail="不支持的数据类型")
    
    conn = None
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        table_name = get_table_name(data_type)
        where_clause, values = build_search_where_clause({
            'year': year,
            'grade': grade,
            'class_name': class_name,
            'search_text': search_text
        }, data_type)
        
        # 获取总记录数
        count_sql = f"SELECT COUNT(*) as total FROM {table_name} WHERE {where_clause}"
        cursor.execute(count_sql, values)
        total = cursor.fetchone()[0]
        
        # 获取分页数据
        offset = (page - 1) * page_size
        # 根据数据类型确定排序
        if data_type == 'catalog':
            # 使用CAST将课程代码转换为数字进行排序，确保1、2、3...10、11的顺序
            # 首先按数字转换后的课程代码升序，然后按课程代码原始值升序作为备用排序
            order_by = "CAST(课程代码 AS INTEGER) ASC, 课程代码 ASC"
            # 显式指定列名，避免sqlite3.Row可能的中文字段名问题
            columns = "id, 年份, 年级, 课程代码, 课程名称, 课程负责人, 各班限报人数, 上课地点, 创建时间"
        elif data_type == 'student-info':
            order_by = "班级 ASC, CAST(学号 AS INTEGER) ASC, 学号 ASC"
            columns = "id, 年份, 年级, 班级, 学号, 姓名"
        elif data_type == 'course-selection':
            order_by = "班级 ASC, CAST(学号 AS INTEGER) ASC, 学号 ASC, CAST(课程代码 AS INTEGER) ASC, 课程代码 ASC"
            columns = "id, 年份, 年级, 班级, 学号, 姓名, 课程代码, 课程名称"
        elif data_type == 'merged-data':
            order_by = "班级 ASC, CAST(学号 AS INTEGER) ASC, 学号 ASC, CAST(课程代码 AS INTEGER) ASC, 课程代码 ASC"
            columns = "id, 年份, 年级, 班级, 学号, 姓名, 课程代码, 课程名称, 课程负责人, 各班限报人数, 上课地点"
        else:
            order_by = "id DESC"
            columns = "*"
        query_sql = f"""
            SELECT {columns} FROM {table_name} 
            WHERE {where_clause}
            ORDER BY {order_by}
            LIMIT ? OFFSET ?
        """
        cursor.execute(query_sql, values + [page_size, offset])
        rows = cursor.fetchall()
        
        # 确保字典键名正确
        data = []
        for row in rows:
            row_dict = dict(row)
            # 如果字典键为空，尝试使用列名重新映射（备选方案）
            if not any(row_dict.keys()):
                # 这种情况一般不会发生，但以防万一
                pass
            data.append(row_dict)
        
        return {
            "success": True,
            "data": data,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total,
                "total_pages": (total + page_size - 1) // page_size
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询数据失败: {str(e)}")
    finally:
        if conn:
            conn.close()


@data_router.delete("/data/{data_type}")
async def delete_data(
    data_type: str,
    year: Optional[int] = None,
    grade: Optional[str] = None,
    class_name: Optional[str] = None
):
    """删除数据"""
    if data_type not in ['catalog', 'student-info', 'course-selection', 'merged-data', 'all']:
        raise HTTPException(status_code=400, detail="不支持的数据类型")
    
    conn = None
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        where_clause, values = build_where_clause({
            'year': year,
            'grade': grade,
            'class_name': class_name
        })
        
        deleted_counts = {}
        
        if data_type == 'all' or data_type == 'catalog':
            cursor.execute(f"DELETE FROM course_catalog WHERE {where_clause}", values)
            deleted_counts['course_catalog'] = cursor.rowcount
        
        if data_type == 'all' or data_type == 'student-info':
            cursor.execute(f"DELETE FROM student_info WHERE {where_clause}", values)
            deleted_counts['student_info'] = cursor.rowcount
        
        if data_type == 'all' or data_type == 'course-selection':
            cursor.execute(f"DELETE FROM course_selection WHERE {where_clause}", values)
            deleted_counts['course_selection'] = cursor.rowcount
        
        if data_type == 'all' or data_type == 'merged-data':
            cursor.execute(f"DELETE FROM merged_data WHERE {where_clause}", values)
            deleted_counts['merged_data'] = cursor.rowcount
        
        conn.commit()
        
        return {
            "success": True,
            "message": "数据删除成功",
            "deleted_counts": deleted_counts
        }
        
    except Exception as e:
        if conn:
            conn.rollback()
        raise HTTPException(status_code=500, detail=f"删除数据失败: {str(e)}")
    finally:
        if conn:
            conn.close()


@data_router.put("/data/{data_type}/{record_id}")
async def update_data(
    data_type: str,
    record_id: int,
    update_data: Dict[str, Any]
):
    """更新单条数据记录"""
    if data_type not in ['catalog', 'student-info', 'course-selection']:
        raise HTTPException(status_code=400, detail="不支持的数据类型")
    
    # 验证更新数据是否包含有效字段
    if not update_data:
        raise HTTPException(status_code=400, detail="更新数据不能为空")
    
    conn = None
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # 获取表名
        table_name = get_table_name(data_type)
        
        # 构建SET子句
        set_clause = ", ".join([f"{key} = ?" for key in update_data.keys()])
        values = list(update_data.values())
        values.append(record_id)  # WHERE条件中的id
        
        # 执行更新
        sql = f"UPDATE {table_name} SET {set_clause} WHERE id = ?"
        cursor.execute(sql, values)
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="记录不存在或未更新")
        
        # 获取年份和年级，用于更新合并数据
        cursor.execute(f"SELECT 年份, 年级 FROM {table_name} WHERE id = ?", (record_id,))
        record = cursor.fetchone()
        if record:
            year = record['年份']
            grade = record['年级']
            # 更新合并数据表，使用同一个连接
            update_merged_data(year, grade, conn)
        
        conn.commit()
        
        # 返回更新后的记录
        cursor.execute(f"SELECT * FROM {table_name} WHERE id = ?", (record_id,))
        updated_record = dict(cursor.fetchone())
        
        return {
            "success": True,
            "message": "数据更新成功",
            "data": updated_record
        }
        
    except HTTPException:
        raise
    except Exception as e:
        if conn:
            conn.rollback()
        raise HTTPException(status_code=500, detail=f"更新数据失败: {str(e)}")
    finally:
        if conn:
            conn.close()


@data_router.get("/analysis/course-stats")
async def analyze_course_stats(
    year: Optional[int] = None,
    grade: Optional[str] = None,
    class_name: Optional[str] = None
):
    """分析课程统计数据"""
    conn = None
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        where_clause, values = build_where_clause({
            'year': year,
            'grade': grade,
            'class_name': class_name
        })
        
        # 获取课程统计
        cursor.execute(f"""
            SELECT 
                课程代码,
                课程名称,
                COUNT(*) as 选课人数,
                AVG(各班限报人数) as 平均限报人数,
                MAX(各班限报人数) as 最大限报人数,
                MIN(各班限报人数) as 最小限报人数
            FROM merged_data
            WHERE {where_clause}
            GROUP BY 课程代码, 课程名称
            ORDER BY 选课人数 DESC
        """, values)
        
        rows = cursor.fetchall()
        course_stats = [dict(row) for row in rows]
        
        # 计算总体统计
        total_courses = len(course_stats)
        total_selected = sum([row['选课人数'] for row in course_stats])
        average_capacity = sum([row['平均限报人数'] for row in course_stats]) / total_courses if total_courses > 0 else 0
        fully_booked = sum([1 for row in course_stats if row['选课人数'] >= row['平均限报人数']])
        
        return {
            "success": True,
            "course_stats": course_stats,
            "summary": {
                "total_courses": total_courses,
                "total_selected": total_selected,
                "average_capacity": round(average_capacity, 1),
                "fully_booked": fully_booked,
                "available_courses": total_courses - fully_booked
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分析课程统计数据失败: {str(e)}")
    finally:
        if conn:
            conn.close()


@data_router.get("/analysis/class-stats")
async def analyze_class_stats(
    year: Optional[int] = None,
    grade: Optional[str] = None
):
    """分析班级统计数据"""
    conn = None
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        where_clause, values = build_where_clause({
            'year': year,
            'grade': grade
        })
        
        # 获取班级统计
        cursor.execute(f"""
            SELECT 
                班级,
                COUNT(DISTINCT 学号) as 总人数,
                COUNT(*) as 总选课数,
                COUNT(DISTINCT 课程代码) as 选课种类数
            FROM merged_data
            WHERE {where_clause}
            GROUP BY 班级
            ORDER BY 班级
        """, values)
        
        rows = cursor.fetchall()
        class_stats = [dict(row) for row in rows]
        
        return {
            "success": True,
            "class_stats": class_stats
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分析班级统计数据失败: {str(e)}")
    finally:
        if conn:
            conn.close()


@data_router.get("/analysis/students-without-courses")
async def analyze_students_without_courses(
    year: Optional[int] = None,
    grade: Optional[str] = None
):
    """分析未选课学生"""
    conn = None
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        where_clause, values = build_where_clause({
            'year': year,
            'grade': grade
        })
        
        # 查找未选课的学生
        cursor.execute(f"""
            SELECT 
                si.班级,
                si.学号,
                si.姓名
            FROM student_info si
            LEFT JOIN course_selection cs ON 
                si.年份 = cs.年份 AND 
                si.年级 = cs.年级 AND 
                si.学号 = cs.学号
            WHERE cs.id IS NULL AND {where_clause.replace('class_name', 'si.班级')}
            ORDER BY si.班级, si.学号
        """, values)
        
        rows = cursor.fetchall()
        students = [dict(row) for row in rows]
        
        return {
            "success": True,
            "students": students,
            "count": len(students)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分析未选课学生失败: {str(e)}")
    finally:
        if conn:
            conn.close()


from fastapi.responses import FileResponse
from fastapi import Query
import os
from .export_service import export_data as export_service_export_data


@data_router.get("/export/{export_type}")
async def export_data(
    export_type: str,
    year: Optional[int] = Query(None, description="用于数据库筛选的年份"),
    year_start: Optional[int] = Query(None, alias='yearStart', description="用于标题的起始年份"),
    year_end: Optional[int] = Query(None, alias='yearEnd', description="用于标题的结束年份"),
    grade: Optional[str] = None,
    class_name: Optional[str] = Query(None, alias='className'),
    format: str = 'xlsx'
):
    """导出数据"""
    if export_type not in ['course-selection', 'distribution', 'teacher-distribution']:
        raise HTTPException(status_code=400, detail="不支持的导出类型")
    
    # 必须提供用于数据库筛选的年份和年级
    if not year or not grade:
        raise HTTPException(status_code=400, detail="年份和年级为必填参数")
    
    try:
        # 调用导出服务生成Excel文件，传递year（数据库筛选年份）和可选的起始年、结束年用于标题
        file_path = export_service_export_data(export_type, year, grade, class_name, year_start, year_end)
        
        # 确定文件名：使用year_start和year_end作为标题年份，如果未提供则使用year
        title_year_start = year_start if year_start is not None else year
        title_year_end = year_end if year_end is not None else year
        
        # 生成文件名
        filename = None
        if export_type == 'course-selection':
            filename = f"选课表_{title_year_start}-{title_year_end}_{grade}"
        elif export_type == 'distribution':
            filename = f"选课分发表_{title_year_start}-{title_year_end}_{grade}"
        elif export_type == 'teacher-distribution':
            filename = f"教师分发表_{title_year_start}-{title_year_end}_{grade}"
        
        # 确保filename被定义
        if filename is None:
            raise HTTPException(status_code=400, detail="导出类型错误")
        
        if class_name:
            filename += f"_{class_name}"
        filename += f".{format}"
        
        # 返回文件响应
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导出数据失败: {str(e)}")
    finally:
        # 注意：FileResponse会在发送后自动清理临时文件，但我们这里需要确保文件存在
        # 实际上，由于我们使用的是临时文件，系统会自动清理，但我们可以在这里进行额外处理
        pass
