# v12 출판 품질 PDF 템플릿 + 한글 폰트 옵션

## 1) 출판 품질 PDF 템플릿
- 커버 페이지(로고/캠페인/후원사/작성일)
- 목차(Heading1/Heading2 기반)
- 헤더/푸터(페이지 번호)
- 표 스타일 고정(헤더 배경/그리드/폰트)
- 마크다운 서브셋 렌더링:
  - # / ## / ###, bullet list, pipe table, code fence

구현:
- `app/server/pdf_renderer.py`
- `app/server/pdf_theme.py`

## 2) 한글 폰트(옵션)
컨테이너 기본 Helvetica는 한글 렌더링이 제한될 수 있습니다.
아래 방법 중 하나로 TTF 폰트를 제공하면 자동으로 등록해 사용합니다.

### 방법 A) 폰트 파일을 레포에 두고 마운트
- 폴더: `assets/fonts/`
- 예: `assets/fonts/NotoSansKR-Regular.ttf`, `assets/fonts/NotoSansKR-Bold.ttf`

### 방법 B) 절대 경로를 환경변수로 지정
`.env`:
```env
ARTBIZ_FONT_REGULAR=/app/assets/fonts/NotoSansKR-Regular.ttf
ARTBIZ_FONT_BOLD=/app/assets/fonts/NotoSansKR-Bold.ttf
PROPOSAL_TEMPLATE_VERSION=v12
```

## 3) 제안서 생성 시 PDF 저장 예시
```bash
curl -s http://localhost:8000/artbiz/proposal -H "Content-Type: application/json" -d '{
  "sponsor_name":"ACME",
  "campaign_title":"도시 커뮤니티 예술 캠페인",
  "budget_total_krw":30000000,
  "weeks":2,
  "org_type":"festival",
  "auto_approve":true,
  "save":true,
  "format":"both",
  "tags":["festival","ACME"],
  "template_version":"v12",
  "logo_path":"/app/assets/logo.png"
}' | jq .
```

## 4) 커스터마이즈 포인트
- 컬러/폰트/표 스타일: `app/server/pdf_theme.py`
- 커버 레이아웃: `app/server/pdf_renderer.py::_cover_page`
