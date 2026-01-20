import React from 'react';
import { TeamOutlined, RobotOutlined, DatabaseOutlined } from '@ant-design/icons';
import { Layout, Menu } from 'antd';
import type { AdminLayoutProps } from './types';

const { Sider, Content } = Layout;

const AdminLayout: React.FC<AdminLayoutProps> = ({
  user,
  activeMenu,
  onMenuSelect,
  children
}) => {
  // 菜单项
  const menuItems = [
    {
      key: 'students',
      icon: <TeamOutlined />,
      label: '学生信息',
    },
    {
      key: 'agents',
      icon: <RobotOutlined />,
      label: '智能体管理',
    },
    {
      key: 'data',
      icon: <DatabaseOutlined />,
      label: '学生对话记录',
    },
  ];

  return (
    <Layout className="h-screen flex flex-row" suppressHydrationWarning data-no-translate>
      <Sider
        theme="light"
        width={250}
        className="border-r border-gray-200 bg-white flex-shrink-0 h-full"
        suppressHydrationWarning
      >
        <div className="h-full flex flex-col" data-no-translate>
          <div className="p-4 flex-shrink-0">
            <div className="flex items-center space-x-3 mb-6">
              <RobotOutlined className="text-2xl text-blue-600" />
              <div>
                <div className="font-bold text-lg" data-no-translate>AI智能体管理</div>
                <div className="text-xs text-gray-500" data-no-translate>管理员面板</div>
              </div>
            </div>
            
            <Menu
              mode="inline"
              selectedKeys={[activeMenu]}
              onSelect={({ key }) => onMenuSelect(key)}
              items={menuItems}
              className="border-0"
              suppressHydrationWarning
            />
          </div>
          
          <div className="mt-auto p-4 border-t border-gray-200 flex-shrink-0">
            <div className="text-center text-gray-500 text-sm" data-no-translate>
              <div>当前用户: {user?.username}</div>
              <div className="text-xs mt-1">管理员权限</div>
            </div>
          </div>
        </div>
      </Sider>
      
      <Layout className="flex-1 bg-gray-50 h-full" suppressHydrationWarning>
        <Content className="p-6 overflow-auto h-full" suppressHydrationWarning>
          <div className="bg-white h-full rounded-lg shadow-sm p-6 overflow-auto" suppressHydrationWarning>
            {children}
          </div>
        </Content>
      </Layout>
    </Layout>
  );
};

export default AdminLayout;
