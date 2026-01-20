/**
 * 智能体连接测试服务
 * 提供测试AI智能体API连接的功能
 */

import { aiAgentApi } from './aiApi';
import { message } from 'antd';

// 测试连接参数类型
export interface TestConnectionParams {
  api_type: 'deepseek' | 'dify';
  api_key: string;
  base_url: string;
  model?: string;
  app_id?: string;
  agentId?: number; // 可选，如果已存在智能体ID
}

// 测试连接结果类型
export interface TestConnectionResult {
  success: boolean;
  message: string;
  test_result?: any;
  agent?: {
    id: number;
    name: string;
    api_type: string;
  };
}

/**
 * 测试智能体连接
 * @param params 连接参数
 * @returns 测试结果
 */
export const testAgentConnection = async (
  params: TestConnectionParams
): Promise<TestConnectionResult> => {
  // 验证必要字段
  if (!params.api_key || !params.base_url) {
    return {
      success: false,
      message: '请先填写API密钥和基础URL',
    };
  }

  if (params.api_type === 'deepseek' && !params.model) {
    return {
      success: false,
      message: 'DeepSeek类需要填写模型名称',
    };
  }

  // 注意：对于Dify类，app_id现在是可选的，系统会自动从API密钥中提取
  // 如果用户提供了app_id，则使用；如果未提供，系统会尝试从API密钥中提取（以'app-'开头）

  try {
    // 如果已有智能体ID，直接测试现有智能体
    if (params.agentId) {
      const result = await aiAgentApi.testAgentConnection(params.agentId);
      return result;
    } else {
      // 创建模式下，先创建临时智能体来测试
      const createResult = await aiAgentApi.createAgent({
        name: `测试连接_${Date.now()}`,
        api_type: params.api_type,
        api_key: params.api_key,
        base_url: params.base_url,
        model: params.model,
        app_id: params.app_id,
        is_active: false, // 设置为不活跃，避免影响真实环境
      });

      if (createResult.success) {
        const testResult = await aiAgentApi.testAgentConnection(createResult.agent.id);
        
        // 删除临时智能体
        await aiAgentApi.deleteAgent(createResult.agent.id);
        
        return testResult;
      } else {
        return {
          success: false,
          message: `创建测试智能体失败: ${createResult.message}`,
        };
      }
    }
  } catch (error: any) {
    console.error('测试连接出错:', error);
    return {
      success: false,
      message: `测试连接失败: ${error.message || '未知错误'}`,
    };
  }
};

/**
 * 验证表单数据（前端验证）
 * @param params 连接参数
 * @returns 验证结果，如果通过返回null，否则返回错误消息
 */
export const validateConnectionParams = (params: TestConnectionParams): string | null => {
  if (!params.api_key || !params.base_url) {
    return '请先填写API密钥和基础URL';
  }

  if (params.api_type === 'deepseek' && !params.model) {
    return 'DeepSeek类需要填写模型名称';
  }

  // 注意：对于Dify类，app_id现在是可选的，系统会自动从API密钥中提取
  // 不再要求app_id必填
  
  return null;
};

/**
 * 执行测试连接并显示用户反馈
 * @param params 连接参数
 * @param showMessage 是否显示消息提示（默认true）
 * @returns 测试结果
 */
export const testConnectionWithFeedback = async (
  params: TestConnectionParams,
  showMessage: boolean = true
): Promise<TestConnectionResult> => {
  const validationError = validateConnectionParams(params);
  if (validationError) {
    if (showMessage) {
      message.error(validationError);
    }
    return {
      success: false,
      message: validationError,
    };
  }

  if (showMessage) {
    message.info('正在测试连接...');
  }

  const result = await testAgentConnection(params);

  if (showMessage) {
    if (result.success) {
      message.success(`连接测试成功: ${result.message}`);
    } else {
      message.error(`连接测试失败: ${result.message}`);
    }
  }

  return result;
};
