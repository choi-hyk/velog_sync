import os
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo  
import requests
import re

ENDPOINT = "https://v2.velog.io/graphql"
USER_NAME = os.getenv("VELOG_USERNAME") 
if not USER_NAME:
    raise ValueError("VELOG_USERNAME 환경 변수를 설정해야 합니다.")
LIMIT = 20
UNSERIZED = "unserized"
OUTPUT_DIR = "."
_INVALID = r'[<>:"/\\|?*\uFF5C]'

def sanitize(name: str, max_len: int = 120) -> str:
    """
    주어진 문자열을 폴더 형식에 맞게 안전하게 변환하는 함수
    - 연속된 하이픈을 하나의 하이픈으로 변환
    - 금지된 문자를 하이픈으로 변환
    - 앞뒤 하이픈, 공백, 마침표, 언더바 제거
    - 최대 길이에 맞게 잘라내기

    Args:
        name (str): 변환할 문자열
        max_len (int, optional): 최대 길이. Defaults to 120.

    Returns:
        str: 변환된 문자열
    """
    s = re.sub(r"-{2,}", "-", name)             
    s = re.sub(_INVALID, "-", s)       
    s = s.strip(" .-_")

    return s[:max_len]

def format_kst(iso_str: str | None) -> str:
    """
    Format ISO 8601 를 KST 형식으로 바꾸는 함수

    Args:
        iso_str (str | None): ISO 8601 형식의 날짜/시간 문자열

    Returns:
        str: KST로 변환된 날짜/시간
    """
    if not iso_str:
        return ""
    dt_utc = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
    dt_kst = dt_utc.astimezone(ZoneInfo("Asia/Seoul"))
    return dt_kst.strftime("%Y-%m-%d %H:%M:%S %Z")
    
def gql(query: str, variables: dict | None = None) -> dict:
    """
    GraphQL 쿼리를 실행하는 함수

    Args:
        query (str): GraphQL 쿼리 문자열
        variables (dict | None, optional): 쿼리 변수

    Returns:
        data["data"] (dict): GraphQL 응답 데이터
    """
    payload = {"query": query, "variables": variables or {}}
    res = requests.post(ENDPOINT, json=payload, timeout=15)
    res.raise_for_status()
    data = res.json()
    if "errors" in data:
        msgs = "; ".join(e.get("message", "") for e in data["errors"])
        raise RuntimeError(f"GraphQL 오류: {msgs}")
    return data["data"]

LIST_QUERY = """
query Posts($username: String!, $limit: Int!, $cursor: ID) {
    posts(username: $username, limit: $limit, cursor: $cursor) {
        id
        url_slug
    }
}
""" 

DETAIL_QUERY = """
query ReadPost($username: String!, $slug: String!) {
    post(username: $username, url_slug: $slug) {
        id
        url_slug
        title
        tags
        series { name }
        released_at
        updated_at
        is_markdown
        body
    }
}
"""

def get_slug() -> list[dict]:
    """
    사용자의 Velog slug 목록을 가져오는 함수

    Returns:
        slugs (list[dict]): 포스트 슬러그를 포함하는 딕셔너리 목록
    """
    cursor = None
    slugs = []
    while True:
        data = gql(LIST_QUERY, {"username": USER_NAME, "limit": LIMIT, "cursor": cursor})
        slugs.extend(data["posts"])
        if len(data["posts"]) < LIMIT:
            break
        cursor = slugs[-1]["id"]
    return slugs

def get_posts() -> dict[str, list[dict]]:
    """
    사용자의 Velog 포스트를 가져오는 함수

    Returns:
        post_dict (dict[str, list[dict]]): 사용자의 Velog 포스트를 포함하는 딕셔너리
    """
    slugs = get_slug()
    posts_dict = {}
    for slug in slugs:
        data = gql(DETAIL_QUERY, {"username": USER_NAME, "slug": slug["url_slug"]})
        post = data["post"]
        if post["series"]:
            series_name = post["series"]["name"]
            posts_dict.setdefault(series_name, []).append(post)
        else:
            posts_dict.setdefault(UNSERIZED, []).append(post)
    return posts_dict

def make_tags_table(tags: list) -> str:
    """_summary_
    tag를 마크다운 형식의 테이블로 만드는 함수

    Args:
        tags (list): 포스트의 태그 목록

    Returns:
        tag_table (str): 마크다운 형식의 태그 테이블
    """
    if not tags:
        return ""
    tag_underline = "|" + len(tags) * "----|"
    tag_box = "|"
    for tag in tags:
        origin_tag = tag
        for_url_tag = tag.strip()
        for_url_tag = re.sub(r"\s+", "-", for_url_tag)
        tag_box += f"[{origin_tag}](https://velog.io/tags/{for_url_tag})|"
    return tag_box + "\n" + tag_underline + "\n\n"

def save_posts(posts_dict: dict) -> None:
    """
    사용자의 Velog 포스트를 저장하는 함수

    Args:
        posts_dict (dict): 사용자의 Velog 포스트를 포함하는 딕셔너리
    """
    base = Path(OUTPUT_DIR)
    base.mkdir(parents=True, exist_ok=True)
    for series_name, posts in posts_dict.items():
        series_dir = base / sanitize(series_name)
        series_dir.mkdir(parents=True, exist_ok=True)
        for post in posts:
            content = ""
            post_file = series_dir / f"{sanitize(post['title'])}.md"
            tag_table = make_tags_table(post["tags"])
            content += f"[Velog로 가기](https://velog.io/@{USER_NAME}/{post['url_slug']})\n\n"
            content += f"released at {format_kst(post['released_at'])}\n\n"
            content += f"updated at {format_kst(post['updated_at'])}\n\n"
            content += f"{tag_table}"
            content += post["body"]
            post_file.write_text(content, encoding="utf-8")

def main():
    velog_posts = get_posts()
    save_posts(velog_posts)

if __name__ == "__main__":
    main()