# velog-sync

Velog 글을 **GraphQL(Graph Query Language) API** 로 가져와 **시리즈별 폴더/Markdown** 으로 저장합니다.
작성/수정 시각은 **KST** 로 변환해 파일에 함께 기록됩니다.

# GitHub Actions

```yml
name: velog-sync (daily KST 03:00)

on:
    schedule:
        - cron: "0 18 * * *" # 매일 03:00 KST
    workflow_dispatch: {}

permissions:
    contents: write

jobs:
    sync:
        runs-on: ubuntu-latest
        environment: velog_sync
        steps:
            - name: Checkout
              uses: actions/checkout@v4

            - name: Set up Python
              uses: actions/setup-python@v5
              with:
                  python-version: "3.11"

            - name: Install velog-sync
              run: |
                  python -m pip install --upgrade pip
                  pip install velog-sync

            - name: Run velog-sync
              env:
                  VELOG_USERNAME: ${{ vars.VELOG_USERNAME }}
              run: velog-sync

            - name: Configure Git
              run: |
                  git config user.name "github-actions[bot]"
                  git config user.email "41898282+github-actions[bot]@users.noreply.github.com"

            - name: Rebase with remote main
              run: |
                  git pull --rebase --autostash origin main

            - name: Commit if changed
              env:
                  TZ: Asia/Seoul
              run: |
                  if [ -n "$(git status --porcelain)" ]; then
                    DATE_KST="$(date +'%Y-%m-%d %H:%M:%S %Z')"
                    git add -A
                    git commit -m "chore: velog sync @ ${DATE_KST}"
                    git push
                  else
                    echo "No changes to commit."
                  fi
```

## 환경 설정

-   위의 Actions yml 파일을 Velog 백업용 repo 에 등록합니다.
-   Actions environment로 **velog_sync**를 지정합니다.
-   velog_sync 환경변수에 글로벌 변수로 `VELOG_USERNAME`에 자신의 velog 계정 이름을 설정합니다.
-   최초 등록 후 run-jobs를 통해 Actions를 실행합니다.
-   매일 03:00 마다 자동으로 업데이트 됩니다.

# 로컬 설치

## 요구 사항

-   Python 3.10+

> `pyproject.toml`은 단일 모듈(루트의 `velog_sync.py`)을 패키징하도록 설정되어 있습니다.

## 설치

```bash
pip install velog-sync
```

## 실행

환경변수 `VELOG_USERNAME`(본인 벨로그 사용자명, `@` 제외)을 반드시 지정한 뒤 **모듈 실행**:

### macOS/Linux

```bash
export VELOG_USERNAME=user-name
velog-sync
```

### Windows (PowerShell)

```powershell
$env:VELOG_USERNAME = "user-name"
velog-sync
```

### Windows (CMD)

```bat
set VELOG_USERNAME=user-name
velog-sync
```

## 출력 구조

출력 경로는 `./`입니다.
각 파일 상단에는:

-   Velog 원문 링크
-   `released at`, `updated at` (KST)
-   태그 테이블(클릭 시 velog 태그 페이지로 이동)

문의/개선 제안은 이슈로 남겨주세요.
