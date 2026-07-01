#!/usr/bin/env bash
set -e
# 테이블 생성은 app.main 에서 create_all 로 처리됨. 콘텐츠 시드 실행(실패해도 계속).
python -m app.seed || echo "seed skipped"
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
