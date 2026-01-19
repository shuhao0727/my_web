'use client';

import React from 'react';
import {
  RobotOutlined, DashboardOutlined, LogoutOutlined
} from '@ant-design/icons';
import { Button, Typography, Tooltip, Avatar } from 'antd';
import { User } from './types';

const { Title, Text } = Typography;

interface HeaderProps {
  user: User | null;
  onOpenAdminPanel: () => void;
  onLogout: () => void;
}

export default function Header({
  user,
  onOpenAdminPanel,
  onLogout,
}: HeaderProps) {
  return (
    <div className="border-b border-gray-100 bg-white shadow-sm">
      <div className="container mx-auto px-4 py-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-3">
              <RobotOutlined className="text-2xl text-blue-600" />
            </div>
            
            <div className="hidden md:block">
              {user && (
                <div className="flex items-center space-x-3">
                  <Avatar 
                    size="small" 
                    style={{ backgroundColor: user.isAdmin ? '#1890ff' : '#52c41a' }}
                  >
                    {user.username.charAt(0).toUpperCase()}
                  </Avatar>
                  <div>
                    <div className="text-sm font-medium">{user.username}</div>
                    {user.isAdmin && (
                      <div className="text-xs text-gray-500">管理员</div>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>

          <div className="flex items-center space-x-3">
            {user?.isAdmin && (
              <Tooltip title="管理智能体">
                <Button
                  type="primary"
                  icon={<DashboardOutlined />}
                  onClick={onOpenAdminPanel}
                >
                  管理
                </Button>
              </Tooltip>
            )}
            
            <Button
              icon={<LogoutOutlined />}
              onClick={onLogout}
            >
              退出
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
