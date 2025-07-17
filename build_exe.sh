#!/bin/bash

echo "Todo2 애플리케이션 EXE 파일 빌드를 시작합니다..."
echo

# 가상환경 활성화
if [ -f "venv/bin/activate" ]; then
    echo "가상환경을 활성화합니다..."
    source venv/bin/activate
else
    echo "가상환경을 찾을 수 없습니다. 전역 Python을 사용합니다."
fi

# PyInstaller 설치 확인
echo "PyInstaller를 확인/설치합니다..."
pip install pyinstaller

# 이전 빌드 결과 정리
if [ -d "dist" ]; then
    echo "이전 빌드 결과를 정리합니다..."
    rm -rf dist
fi
if [ -d "build" ]; then
    rm -rf build
fi

# EXE 파일 빌드
echo
echo "EXE 파일을 빌드합니다..."
pyinstaller todo2.spec

# 빌드 결과 확인
if [ -f "dist/Todo2" ]; then
    echo
    echo "================================"
    echo "   빌드가 성공적으로 완료되었습니다!"
    echo "================================"
    echo
    echo "생성된 파일: dist/Todo2"
    echo
    echo "실행 파일을 테스트하시겠습니까? (y/n)"
    read -p "> " choice
    if [[ $choice == [Yy]* ]]; then
        echo
        echo "Todo2를 실행합니다..."
        cd dist
        ./Todo2
    fi
else
    echo
    echo "================================"
    echo "      빌드에 실패했습니다!"
    echo "================================"
    echo
    echo "오류 로그를 확인하고 다시 시도해주세요."
fi

echo
read -p "아무 키나 눌러 종료하세요..."