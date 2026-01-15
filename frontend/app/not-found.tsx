import Link from 'next/link';

export default function NotFound() {
    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50">
            <div className="text-center">
                <h1 className="text-6xl font-bold text-gray-800 mb-4">404</h1>
                <h2 className="text-2xl font-semibold text-gray-600 mb-6">抱歉，您访问的页面不存在。</h2>
                <p className="text-gray-500 mb-8">请检查您输入的网址是否正确，或点击下方按钮返回首页。</p>
                <Link href="/">
                    <button className="px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors">
                        返回首页
                    </button>
                </Link>
            </div>
        </div>
    );
}
