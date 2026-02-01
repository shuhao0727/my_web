#!/bin/bash
echo "下载Typst x86_64版本..."
mkdir -p .typst-cache
curl -fsSL https://github.com/typst/typst/releases/download/v0.14.2/typst-x86_64-unknown-linux-musl.tar.xz -o typst.tar.xz
if [ $? -eq 0 ]; then
    tar -xf typst.tar.xz
    mv typst .typst-cache/typst
    chmod +x .typst-cache/typst
    rm -f typst.tar.xz
    echo "Typst x86_64版本已下载到 .typst-cache/"
    echo "文件架构:"
    file .typst-cache/typst
else
    echo "下载失败，请检查网络连接"
    exit 1
fi
