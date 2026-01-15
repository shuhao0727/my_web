'use client';

import { Card, Row, Col, Timeline, Avatar, Space, Typography } from 'antd';
import { UserOutlined, TrophyOutlined, BookOutlined, TeamOutlined, CalendarOutlined, MailOutlined } from '@ant-design/icons';

const { Title, Paragraph, Text } = Typography;

export default function AboutPage() {
    const achievements = [
        { year: '2025', title: '全国信息学竞赛优秀教练', description: '指导学生在NOI中获得3枚金牌' },
        { year: '2024', title: 'AI教育创新奖', description: '开发AI辅助教学系统获得省级创新奖' },
        { year: '2023', title: '优秀教师称号', description: '荣获市级优秀信息技术教师称号' },
        { year: '2022', title: '教学成果一等奖', description: '《人工智能基础》课程获得教学成果一等奖' },
        { year: '2021', title: '教育技术专利', description: '获得一项教育技术相关发明专利' },
    ];

    const teamMembers = [
        { name: '张老师', role: '首席教师/竞赛教练', bio: '15年信息技术教学经验，NOI金牌教练' },
        { name: '李老师', role: 'AI教育专家', bio: '人工智能博士，专注于AI在教育领域的应用' },
        { name: '王老师', role: '课程开发总监', bio: '10年课程开发经验，编写多本信息技术教材' },
        { name: '赵老师', role: '学习数据分析师', bio: '数据科学硕士，负责学习行为分析和个性化推荐' },
    ];

    return (
        <div className="min-h-screen bg-gray-50 py-12">
            <div className="container mx-auto px-4">
                {/* 页面标题 */}
                <div className="text-center mb-12">
                    <Title level={1} className="text-4xl md:text-5xl font-bold">关于我们</Title>
                    <Paragraph className="text-gray-600 text-lg max-w-3xl mx-auto">
                        我们是一支致力于将人工智能与教育深度融合的教师团队，
                        专注于高中信息技术教学和信息学竞赛培训。
                    </Paragraph>
                </div>

                {/* 教师介绍 */}
                <Card className="mb-12 border-0 shadow-lg">
                    <Row gutter={[32, 32]} align="middle">
                        <Col xs={24} md={8} className="text-center">
                            <Avatar size={200} icon={<UserOutlined />} className="bg-blue-100" />
                            <Title level={3} className="mt-6">首席教师</Title>
                            <Text strong className="text-lg">张老师</Text>
                            <Paragraph className="text-gray-600">
                                高中信息技术高级教师<br />
                                信息学竞赛金牌教练<br />
                                15年教学经验
                            </Paragraph>
                        </Col>
                        <Col xs={24} md={16}>
                            <Title level={2}>教育理念</Title>
                            <Paragraph className="text-lg text-gray-700">
                                我相信每个学生都有独特的潜能。通过结合人工智能技术和个性化教学，
                                我们可以为每个学生量身定制学习路径，让学习更加高效、有趣。
                            </Paragraph>
                            <Paragraph className="text-gray-600">
                                作为一名信息技术教师和竞赛教练，我见证了技术如何改变教育。
                                从传统的课堂教学到现在的AI辅助学习，我一直在探索如何利用技术
                                提升教学效果，激发学生的学习兴趣和创新思维。
                            </Paragraph>
                            <Space size="large" className="mt-6">
                                <div>
                                    <TrophyOutlined className="text-2xl text-blue-600 mr-2" />
                                    <Text strong>教学成果</Text>
                                    <Paragraph className="m-0">指导100+学生在竞赛中获奖</Paragraph>
                                </div>
                                <div>
                                    <BookOutlined className="text-2xl text-green-600 mr-2" />
                                    <Text strong>课程开发</Text>
                                    <Paragraph className="m-0">开发20+门信息技术课程</Paragraph>
                                </div>
                                <div>
                                    <TeamOutlined className="text-2xl text-purple-600 mr-2" />
                                    <Text strong>学生培养</Text>
                                    <Paragraph className="m-0">培养500+名优秀学生</Paragraph>
                                </div>
                            </Space>
                        </Col>
                    </Row>
                </Card>

                {/* 成就时间线 */}
                <div className="mb-12">
                    <Title level={2} className="text-center mb-8">主要成就</Title>
                    <Timeline
                        mode="alternate"
                        items={achievements.map((item, index) => ({
                            key: index,
                            color: index % 2 === 0 ? 'blue' : 'green',
                            content: (
                                <Card className="border-0 shadow-sm">
                                    <Text strong className="text-lg">{item.year}</Text>
                                    <Title level={4} className="mt-2">{item.title}</Title>
                                    <Paragraph className="text-gray-600">{item.description}</Paragraph>
                                </Card>
                            ),
                        }))}
                    />
                </div>

                {/* 团队介绍 */}
                <div className="mb-12">
                    <Title level={2} className="text-center mb-8">教师团队</Title>
                    <Row gutter={[32, 32]}>
                        {teamMembers.map((member, index) => (
                            <Col xs={24} md={12} lg={6} key={index}>
                                <Card className="border-0 shadow-lg hover:shadow-xl transition-shadow text-center">
                                    <Avatar size={100} icon={<UserOutlined />} className="mb-4 bg-gray-100" />
                                    <Title level={4}>{member.name}</Title>
                                    <Text type="secondary" className="block mb-3">{member.role}</Text>
                                    <Paragraph className="text-gray-600">{member.bio}</Paragraph>
                                </Card>
                            </Col>
                        ))}
                    </Row>
                </div>

                {/* 平台使命 */}
                <Card className="bg-gradient-to-r from-blue-50 to-blue-100 border-0">
                    <div className="text-center py-8">
                        <Title level={2}>我们的使命</Title>
                        <Paragraph className="text-lg text-gray-700 max-w-3xl mx-auto">
                            通过人工智能技术，打破传统教育的时空限制，为每位学生提供
                            个性化的学习体验。我们相信，技术的价值在于赋能教育，
                            让优质的教育资源更加公平、高效地服务于每一个学习者。
                        </Paragraph>
                        <div className="mt-8">
                            <CalendarOutlined className="text-3xl text-blue-600 mr-4" />
                            <MailOutlined className="text-3xl text-blue-600" />
                        </div>
                    </div>
                </Card>

                {/* 联系方式 */}
                <div className="mt-12 text-center">
                    <Title level={3}>联系我们</Title>
                    <Paragraph className="text-gray-600">
                        如果您对我们的平台有任何疑问或建议，欢迎通过以下方式联系我们：
                    </Paragraph>
                    <Space direction="vertical" size="middle" className="mt-6">
                        <Text>邮箱：teacher@ai-education.com</Text>
                        <Text>电话：(010) 1234-5678</Text>
                        <Text>地址：北京市海淀区中关村大街1号</Text>
                    </Space>
                </div>
            </div>
        </div>
    );
}
