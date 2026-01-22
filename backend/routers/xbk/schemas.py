"""
XBK数据处理的Pydantic模型定义
"""
from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class ImportRequest(BaseModel):
    year: int
    grade: str
    type: str  # 'catalog', 'student-info', 'course-selection'


class QueryRequest(BaseModel):
    year: Optional[int] = None
    grade: Optional[str] = None
    class_name: Optional[str] = None
    page: int = 1
    page_size: int = 20


class DeleteRequest(BaseModel):
    year: Optional[int] = None
    grade: Optional[str] = None
    class_name: Optional[str] = None
    type: str  # 'course-catalog', 'student-info', 'course-selection', 'merged-data', 'all'


class ExportRequest(BaseModel):
    year: Optional[int] = None
    grade: Optional[str] = None
    class_name: Optional[str] = None
    type: str  # 'course-selection', 'distribution', 'teacher-distribution'
    format: str = 'xlsx'  # 'xlsx' or 'xls'


class AnalysisRequest(BaseModel):
    year: Optional[int] = None
    grade: Optional[str] = None
    class_name: Optional[str] = None


class SystemConfigResponse(BaseModel):
    current_year: Optional[int] = None
    current_grade: Optional[str] = None
    available_years: List[int] = []
    available_grades: List[str] = []
    available_classes: List[str] = []
