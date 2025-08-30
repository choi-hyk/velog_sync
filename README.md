# velog-sync

Velog 글을 **GraphQL(Graph Query Language) API(Application Programming Interface)** 로 가져와 **시리즈별 폴더/Markdown(.md)** 로 저장합니다.
작성/수정 시각은 **KST(Korea Standard Time)** 로 변환해 파일에 함께 기록됩니다.

## 요구 사항

-   Python 3.10+
-   의존성: `requests`, `tzdata` (Windows의 `zoneinfo`용)

> `pyproject.toml`은 단일 모듈(루트의 `velog_sync.py`)을 패키징하도록 설정되어 있습니다.

## 실행

환경변수 `VELOG_USERNAME`(본인 벨로그 사용자명, `@` 제외)을 반드시 지정한 뒤 **모듈 실행**:

### macOS/Linux

```bash
export VELOG_USERNAME=user-name
python -m velog_sync
```

### Windows (PowerShell)

```powershell
$env:VELOG_USERNAME = "user-name"
python -m velog_sync
```

### Windows (CMD)

```bat
set VELOG_USERNAME=user-name
python -m velog_sync
```

## 출력 구조

출력 경로는 `velog_posts/`입니다.
각 파일 상단에는:

-   Velog 원문 링크
-   `released at`, `updated at` (KST)
-   태그 테이블(클릭 시 velog 태그 페이지로 이동)

문의/개선 제안은 이슈로 남겨주세요.
