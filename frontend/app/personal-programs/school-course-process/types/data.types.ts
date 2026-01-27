export interface CourseCatalog {
  id: number;
  年份: number;
  年级: string;
  学年?: string;
  课程代码: string;
  课程名称: string;
  课程负责人?: string;
  各班限报人数?: number;
  上课地点?: string;
  创建时间?: string;
}

export interface StudentInfo {
  id: number;
  年份: number;
  年级: string;
  学年?: string;
  班级: string;
  学号: string;
  姓名: string;
  创建时间?: string;
}

export interface CourseSelection {
  id: number;
  年份: number;
  年级: string;
  学年?: string;
  班级: string;
  学号: string;
  姓名: string;
  课程代码: string;
  课程名称?: string;
  创建时间?: string;
}

export interface MergedData {
  id: number;
  年份: number;
  年级: string;
  学年?: string;
  班级: string;
  学号: string;
  姓名: string;
  课程代码: string;
  课程名称: string;
  课程负责人?: string;
  各班限报人数?: number;
  上课地点?: string;
  创建时间?: string;
}

export interface Filters {
  year?: number;
  grade?: string;
  semester?: string;
  class?: string;
  searchText?: string;
}

export interface DataSet {
  courseCatalog: CourseCatalog[];
  studentInfo: StudentInfo[];
  courseSelection: CourseSelection[];
  mergedData: MergedData[];
}

export interface ImportSettings {
  year: number;
  grade: string;
  semester?: string;
  type: 'catalog' | 'student-info' | 'course-selection';
}

export interface ExportSettings {
  year: number;                     // 用于数据库筛选的年份
  yearStart: number;                // 用于标题的起始年份
  yearEnd: number;                  // 用于标题的结束年份
  grade: string;                    // 用于数据库筛选的年级
  semester?: string;                // 学年
  type: 'course-selection' | 'distribution' | 'teacher-distribution';
  format: 'xlsx' | 'xls';
}

export interface AnalysisResult {
  courseStats: any;
  classStats: any;
  studentsWithoutCourses: any;
}

export interface SystemConfig {
  currentYear?: number;
  currentGrade?: string;
  currentSemester?: string;
  availableYears: number[];
  availableGrades: string[];
  availableSemesters: string[];
  availableClasses: string[];
}
