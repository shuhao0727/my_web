/**
 * 仓库同步API服务
 * 用于调用新的GitHub仓库同步接口
 */

const API_BASE = 'http://localhost:8000/api';

export interface RepoStatus {
  exists: boolean;
  status: 'not_cloned' | 'cloned' | 'not_git_repo' | 'error';
  last_updated: string | null;
  branch: string | null;
  commit: string | null;
  commit_message?: string;
  commit_date?: string;
  remote_accessible?: boolean;
  remote_error?: string;
  token_expired?: boolean;
  error?: string;
}

export interface RepoStructure {
  chapters: {
    exists: boolean;
    count: number;
  };
  style: {
    exists: boolean;
    files: string[];
  };
  image: {
    exists: boolean;
    count: number;
  };
  main_typ: {
    exists: boolean;
    size: number;
  };
}

export interface RepoFile {
  name: string;
  type: 'directory' | 'file';
  path: string;
  size: number;
  modified: string;
  extension: string;
}

export interface RepoFileList {
  success: boolean;
  path: string;
  files: RepoFile[];
  count: number;
  error?: string;
}

export interface RepoFileContent {
  success: boolean;
  path: string;
  content: string;
  size: number;
  modified: string;
  is_binary?: boolean;
  binary_size?: number;
  error?: string;
}

export interface SyncResult {
  success: boolean;
  message: string;
  path?: string;
  branch?: string;
  error?: string;
  details?: string;
  output?: string;
  before?: any;
  after?: any;
  updated?: boolean;
  pdf_cache_generated?: boolean;
  pdf_cache_message?: string;
  pdf_cache_results?: any;
}

export interface PdfCacheInfo {
  success: boolean;
  exists: boolean;
  count: number;
  total_size: number;
  files: Array<{
    name: string;
    size: number;
    modified: string;
  }>;
  error?: string;
}

export interface PdfUrlResult {
  success: boolean;
  file_path: string;
  pdf_url: string;
  pdf_filename: string | null;
}

export interface PdfCacheGenerateResult {
  success: boolean;
  message: string;
  results?: {
    total: number;
    success: number;
    failed: number;
    skipped: number;
    details: Array<{
      file: string;
      status: 'success' | 'failed' | 'skipped';
      reason?: string;
      error?: string;
      output_path?: string;
    }>;
  };
  error?: string;
}

export interface ChapterInfo {
  id: string; // 使用路径作为ID
  title: string;
  path: string;
  isDirectory: boolean;
  level: number;
  children?: ChapterInfo[];
}

/**
 * 获取仓库状态
 */
export async function getRepoStatus(): Promise<RepoStatus> {
  const response = await fetch(`${API_BASE}/repo/status`);
  if (!response.ok) {
    throw new Error(`获取仓库状态失败: ${response.status}`);
  }
  return response.json();
}

/**
 * 同步仓库（克隆或拉取）
 */
export async function syncRepository(forceCloned = false): Promise<SyncResult> {
  const response = await fetch(`${API_BASE}/repo/sync`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ force_clone: forceCloned }),
  });
  if (!response.ok) {
    throw new Error(`同步仓库失败: ${response.status}`);
  }
  return response.json();
}

/**
 * 获取仓库结构概览
 */
export async function getRepoStructure(): Promise<{
  success: boolean;
  structure: RepoStructure;
  repo_path: string;
  error?: string;
}> {
  const response = await fetch(`${API_BASE}/repo/structure`);
  if (!response.ok) {
    throw new Error(`获取仓库结构失败: ${response.status}`);
  }
  return response.json();
}

/**
 * 列出指定路径下的文件和目录
 */
export async function listFiles(path = ''): Promise<RepoFileList> {
  const encodedPath = encodeURIComponent(path);
  const response = await fetch(`${API_BASE}/repo/list?path=${encodedPath}`);
  if (!response.ok) {
    throw new Error(`列出文件失败: ${response.status}`);
  }
  return response.json();
}

/**
 * 获取文件内容
 */
export async function getFileContent(path: string): Promise<RepoFileContent> {
  const encodedPath = encodeURIComponent(path);
  const response = await fetch(`${API_BASE}/repo/file?path=${encodedPath}`);
  if (!response.ok) {
    throw new Error(`获取文件内容失败: ${response.status}`);
  }
  return response.json();
}

/**
 * 获取main.typ文件内容
 */
export async function getMainTyp(): Promise<RepoFileContent> {
  const response = await fetch(`${API_BASE}/repo/main-typ`);
  if (!response.ok) {
    throw new Error(`获取main.typ失败: ${response.status}`);
  }
  return response.json();
}

/**
 * 列出所有章节
 */
export async function listChapters(): Promise<RepoFileList> {
  const response = await fetch(`${API_BASE}/repo/chapters`);
  if (!response.ok) {
    throw new Error(`列出章节失败: ${response.status}`);
  }
  return response.json();
}

/**
 * 列出特定章节目录下的文件
 */
export async function listChapterFiles(chapterPath: string): Promise<RepoFileList> {
  const encodedPath = encodeURIComponent(chapterPath);
  const response = await fetch(`${API_BASE}/repo/chapters/${encodedPath}`);
  if (!response.ok) {
    throw new Error(`列出章节文件失败: ${response.status}`);
  }
  return response.json();
}

/**
 * 获取章节文件内容
 */
export async function getChapterFile(filePath: string): Promise<RepoFileContent> {
  const encodedPath = encodeURIComponent(filePath);
  const response = await fetch(`${API_BASE}/repo/chapter-file/${encodedPath}`);
  if (!response.ok) {
    throw new Error(`获取章节文件失败: ${response.status}`);
  }
  return response.json();
}

/**
 * 获取章节文件的PDF版本（编译或从缓存返回）
 */
export async function getChapterPdf(filePath: string): Promise<Blob> {
  const encodedPath = encodeURIComponent(filePath);
  const response = await fetch(`${API_BASE}/repo/chapter-pdf/${encodedPath}`);
  if (!response.ok) {
    const errorText = await response.text();
    try {
      const errorJson = JSON.parse(errorText);
      throw new Error(`获取PDF失败: ${errorJson.detail || errorJson.error || '未知错误'}`);
    } catch {
      throw new Error(`获取PDF失败: ${response.status} ${response.statusText}`);
    }
  }
  return response.blob();
}

/**
 * 获取章节文件的静态PDF URL（直接访问缓存的PDF文件）
 */
export async function getChapterPdfStaticUrl(filePath: string): Promise<PdfUrlResult> {
  const encodedPath = encodeURIComponent(filePath);
  const response = await fetch(`${API_BASE}/repo/chapter-pdf-url/${encodedPath}`);
  if (!response.ok) {
    const errorText = await response.text();
    try {
      const errorJson = JSON.parse(errorText);
      throw new Error(`获取PDF URL失败: ${errorJson.detail || errorJson.error || '未知错误'}`);
    } catch {
      throw new Error(`获取PDF URL失败: ${response.status} ${response.statusText}`);
    }
  }
  return response.json();
}

/**
 * 获取章节文件的静态PDF URL（直接访问缓存的PDF文件）
 */
export async function getChapterPdfUrl(filePath: string): Promise<string | null> {
  try {
    // 使用API路由获取PDF，确保正确编码和CORS头部
    const encodedPath = encodeURIComponent(filePath);
    return `http://localhost:8000/api/repo/chapter-pdf-static/${encodedPath}`;
  } catch {
    return null;
  }
}

/**
 * 获取章节文件的静态PDF文件（直接访问缓存的PDF文件）
 */
export async function getChapterPdfStatic(filePath: string): Promise<Blob> {
  const encodedPath = encodeURIComponent(filePath);
  const response = await fetch(`${API_BASE}/repo/chapter-pdf-static/${encodedPath}`);
  if (!response.ok) {
    const errorText = await response.text();
    try {
      const errorJson = JSON.parse(errorText);
      throw new Error(`获取静态PDF失败: ${errorJson.detail || errorJson.error || '未知错误'}`);
    } catch {
      throw new Error(`获取静态PDF失败: ${response.status} ${response.statusText}`);
    }
  }
  return response.blob();
}

/**
 * 获取PDF缓存信息
 */
export async function getPdfCacheInfo(): Promise<PdfCacheInfo> {
  const response = await fetch(`${API_BASE}/repo/pdf-cache/info`);
  if (!response.ok) {
    throw new Error(`获取PDF缓存信息失败: ${response.status}`);
  }
  return response.json();
}

/**
 * 手动触发生成所有PDF缓存
 */
export async function generatePdfCache(): Promise<PdfCacheGenerateResult> {
  const response = await fetch(`${API_BASE}/repo/pdf-cache/generate`, {
    method: 'POST',
  });
  if (!response.ok) {
    throw new Error(`生成PDF缓存失败: ${response.status}`);
  }
  return response.json();
}

/**
 * 列出style目录下的文件
 */
export async function listStyleFiles(): Promise<RepoFileList> {
  const response = await fetch(`${API_BASE}/repo/style`);
  if (!response.ok) {
    throw new Error(`列出样式文件失败: ${response.status}`);
  }
  return response.json();
}

/**
 * 列出image目录下的文件
 */
export async function listImageFiles(): Promise<RepoFileList> {
  const response = await fetch(`${API_BASE}/repo/image`);
  if (!response.ok) {
    throw new Error(`列出图片失败: ${response.status}`);
  }
  return response.json();
}

/**
 * 递归获取章节树结构
 */
export async function getChapterTree(): Promise<ChapterInfo[]> {
  const chapters = await listChapters();
  
  if (!chapters.success || chapters.files.length === 0) {
    return [];
  }

  const tree: ChapterInfo[] = [];
  
  // 遍历章节目录，递归获取子目录结构
  for (const file of chapters.files) {
    if (file.type === 'directory') {
      const chapterNode = await buildChapterTree(file.path, 0);
      if (chapterNode) {
        tree.push(chapterNode);
      }
    }
  }

  return tree;
}

/**
 * 构建章节树
 */
async function buildChapterTree(path: string, level: number): Promise<ChapterInfo | null> {
  try {
    const dirContents = await listFiles(path);
    
    if (!dirContents.success) {
      return null;
    }

    const nodeName = path.split('/').pop() || path;
    const node: ChapterInfo = {
      id: path,
      title: formatChapterTitle(nodeName),
      path,
      isDirectory: true,
      level,
      children: [],
    };

    // 对文件进行排序：目录在前，文件在后，按名称排序
    const sortedFiles = [...dirContents.files].sort((a, b) => {
      if (a.type !== b.type) {
        return a.type === 'directory' ? -1 : 1;
      }
      return a.name.localeCompare(b.name);
    });

    for (const file of sortedFiles) {
      if (file.name === '.git') continue;
      
      if (file.type === 'directory') {
        const childNode = await buildChapterTree(file.path, level + 1);
        if (childNode) {
          node.children!.push(childNode);
        }
      } else if (file.extension === '.typ') {
        // Typst文件
        node.children!.push({
          id: file.path,
          title: formatChapterTitle(file.name),
          path: file.path,
          isDirectory: false,
          level: level + 1,
        });
      }
    }

    return node;
  } catch (error) {
    console.error(`构建章节树失败: ${path}`, error);
    return null;
  }
}

/**
 * 格式化章节标题
 */
function formatChapterTitle(filename: string): string {
  // 移除扩展名
  const nameWithoutExt = filename.replace(/\.typ$/, '');
  
  // 尝试解析类似 "1.1-c++.typ" 的文件名
  const match = nameWithoutExt.match(/^(\d+(?:\.\d+)*)\s*[-_]\s*(.+)$/);
  if (match) {
    const [, number, title] = match;
    return `${number} ${title.charAt(0).toUpperCase() + title.slice(1)}`;
  }
  
  // 尝试解析纯数字
  if (/^\d+(\.\d+)*$/.test(nameWithoutExt)) {
    return `第 ${nameWithoutExt} 章`;
  }
  
  // 使用文件名作为标题，首字母大写
  return nameWithoutExt.charAt(0).toUpperCase() + nameWithoutExt.slice(1);
}
