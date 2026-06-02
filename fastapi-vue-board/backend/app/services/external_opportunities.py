from __future__ import annotations

import asyncio
import json
import re
import time
from datetime import datetime, timezone
from html import unescape
from typing import Any
from urllib.parse import unquote, urlencode, urljoin
from urllib.error import URLError
from urllib.request import Request, urlopen
from xml.etree import ElementTree

from app.core.config import settings


CACHE_TTL_SECONDS = 15 * 60
HTTP_TIMEOUT_SECONDS = 4

KONTESTS_URL = "https://kontests.net/api/v1/all"
CODEFORCES_URL = "https://codeforces.com/api/contest.list?gym=false"
CONTESTKOREA_BASE_URL = "https://www.contestkorea.com"
CONTESTKOREA_IT_LIST_URL = (
    "https://www.contestkorea.com/sub/list.php"
    "?displayrow=12&int_gbn=1&Txt_sGn=1&Txt_key=all&Txt_word="
    "&Txt_bcode=030310001&Txt_sortkey=a.int_sort&Txt_sortword=desc&page={page}"
)
KIPRIS_IDEA_DETAIL_URL = (
    "https://plus.kipris.or.kr/portal/data/util/DBII_000000000000228/"
    "view.do?menuNo=210007&subTab=SC002"
)
WORKNET_KEYWORDS = ["개발자", "프로그래머", "소프트웨어", "데이터", "정보보안"]
KIPRIS_IT_KEYWORDS = ["소프트웨어", "정보통신", "데이터", "모바일", "플랫폼", "보안", "인공지능", "앱"]
IT_CONTEST_TERMS = [
    "it",
    "sw",
    "ai",
    "ict",
    "iot",
    "정보통신",
    "소프트웨어",
    "기술",
    "공학",
    "통계",
    "스타트업",
    "창업",
    "반도체",
    "로봇",
    "콘텐츠",
    "메타버스",
    "해커톤",
    "프로그램",
    "프로그래밍",
    "개발",
    "데이터",
    "빅데이터",
    "인공지능",
    "모바일",
    "앱",
    "어플",
    "웹",
    "플랫폼",
    "디지털",
    "보안",
    "알고리즘",
    "컴퓨터",
    "인터넷",
    "시스템",
]
SARAMIN_IT_CATEGORY_URL = (
    "https://www.saramin.co.kr/zf_user/jobs/list/job-category"
    "?cat_kewd=84&search_optional_item=n&search_done=y&panel_count=y&preview=y&page_count=50&sort=RD"
)

_cache: dict[str, tuple[float, list[dict[str, Any]]]] = {}


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _strip_html(value: str | None) -> str:
    if not value:
        return ""
    text = re.sub(r"<[^>]*>", " ", value)
    return re.sub(r"\s+", " ", unescape(text)).strip()


def _parse_datetime(value: Any) -> datetime | None:
    if value in (None, ""):
        return None
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value, tz=timezone.utc)
    if isinstance(value, str):
        normalized = value.replace("Z", "+00:00")
        try:
            parsed = datetime.fromisoformat(normalized)
            return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
        except ValueError:
            return None
    return None


def _get_json(url: str) -> Any:
    request = Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "DevCareer/1.0 (+local development)",
        },
    )
    with urlopen(request, timeout=HTTP_TIMEOUT_SECONDS) as response:
        return json.loads(response.read().decode("utf-8"))


def _get_text(url: str) -> str:
    request = Request(
        url,
        headers={
            "Accept": "application/xml,text/xml,*/*",
            "User-Agent": "DevCareer/1.0 (+local development)",
        },
    )
    with urlopen(request, timeout=HTTP_TIMEOUT_SECONDS) as response:
        return response.read().decode("utf-8", errors="replace")


async def _get_cached(cache_key: str, url: str, mapper, limit: int) -> list[dict[str, Any]]:
    cached = _cache.get(cache_key)
    if cached and time.time() - cached[0] < CACHE_TTL_SECONDS:
        return cached[1][:limit]

    try:
        payload = await asyncio.to_thread(_get_json, url)
        rows = mapper(payload)
    except (TimeoutError, URLError, OSError, ValueError, json.JSONDecodeError):
        rows = []

    _cache[cache_key] = (time.time(), rows)
    return rows[:limit]


def _text(parent: ElementTree.Element, name: str) -> str:
    node = parent.find(name)
    return (node.text or "").strip() if node is not None else ""


def _parse_worknet_date(value: str) -> datetime | None:
    value = (value or "").strip()
    if not value or "채용시" in value or "상시" in value:
        return None
    for fmt in ("%Y-%m-%d", "%y-%m-%d", "%Y%m%d", "%y%m%d"):
        try:
            return datetime.strptime(value, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return None


def _parse_compact_date(value: str) -> datetime | None:
    value = (value or "").strip()
    if not value:
        return None
    match = re.search(r"(\d{4})[-./]?(\d{2})[-./]?(\d{2})", value)
    if not match:
        return None
    try:
        return datetime(
            int(match.group(1)),
            int(match.group(2)),
            int(match.group(3)),
            tzinfo=timezone.utc,
        )
    except ValueError:
        return None


def _parse_contestkorea_period(value: str) -> tuple[datetime | None, datetime | None]:
    match = re.search(r"(\d{1,2})\.(\d{1,2})\s*~\s*(\d{1,2})\.(\d{1,2})", value or "")
    if not match:
        return None, None

    now = _now()
    start_month, start_day, end_month, end_day = (int(part) for part in match.groups())
    start_year = now.year
    end_year = start_year + 1 if end_month < start_month else start_year

    try:
        start_at = datetime(start_year, start_month, start_day, tzinfo=timezone.utc)
        end_at = datetime(end_year, end_month, end_day, 23, 59, tzinfo=timezone.utc)
    except ValueError:
        return None, None

    if end_at < now and now.month >= 10 and end_month <= 3:
        start_at = start_at.replace(year=start_at.year + 1)
        end_at = end_at.replace(year=end_at.year + 1)

    return start_at, end_at


def _xml_name(node: ElementTree.Element) -> str:
    return node.tag.rsplit("}", 1)[-1].lower()


def _child_texts(node: ElementTree.Element) -> dict[str, str]:
    values: dict[str, str] = {}
    for child in list(node):
        if list(child):
            continue
        text = (child.text or "").strip()
        if text:
            values[_xml_name(child)] = text
    return values


def _pick(values: dict[str, str], *names: str) -> str:
    normalized = {re.sub(r"[^a-z0-9]", "", key.lower()): value for key, value in values.items()}
    for name in names:
        value = normalized.get(re.sub(r"[^a-z0-9]", "", name.lower()))
        if value:
            return value
    return ""


def _has_it_signal(*values: str) -> bool:
    text = " ".join(value for value in values if value).lower()
    return any(term.lower() in text for term in IT_CONTEST_TERMS)


def _map_worknet_jobs(xml_text: str, id_offset: int = 0) -> list[dict[str, Any]]:
    root = ElementTree.fromstring(xml_text)
    error_message = _text(root, "error") or _text(root, "message")
    if error_message:
        raise ValueError(f"Worknet API error: {error_message}")

    mapped: list[dict[str, Any]] = []

    for index, item in enumerate(root.findall(".//wanted"), start=1):
        title = _text(item, "title")
        company = _text(item, "company")
        url = _text(item, "wantedInfoUrl") or _text(item, "wantedMobileInfoUrl")
        auth_no = _text(item, "wantedAuthNo")
        if not title or not company or not url:
            continue

        close_dt = _parse_worknet_date(_text(item, "closeDt"))
        created_at = _parse_worknet_date(_text(item, "regDt")) or _now()
        sal = " ".join(part for part in [_text(item, "salTpNm"), _text(item, "sal")] if part).strip()
        education = " ~ ".join(
            part for part in [_text(item, "minEdubg"), _text(item, "maxEdubg")] if part
        ).strip()
        description_parts = [
            _text(item, "jobsCd"),
            _text(item, "infoSvc"),
            _text(item, "holidayTpNm"),
            _text(item, "empTpCd"),
        ]

        mapped.append(
            {
                "id": -400000 - id_offset - index,
                "title": title,
                "company": company,
                "description": ", ".join(part for part in description_parts if part) or "워크넷 채용정보",
                "job_category": "개발/SW",
                "region": _text(item, "region") or _text(item, "basicAddr") or "국내",
                "experience": _text(item, "career") or "경력 무관",
                "education": sal or education or "공고별 확인",
                "deadline": close_dt,
                "external_url": url,
                "author_id": 0,
                "is_active": True,
                "created_at": created_at,
                "updated_at": None,
                "scrap_count": 0,
                "is_external": True,
                "source": "워크넷",
                "external_key": auth_no,
            }
        )

    return mapped


def _first_match(pattern: str, text: str, flags: int = re.S) -> str:
    match = re.search(pattern, text, flags)
    return unescape(_strip_html(match.group(1))) if match else ""


def _parse_saramin_deadline(value: str) -> datetime | None:
    value = (value or "").strip()
    match = re.search(r"~\s*(\d{1,2})\.(\d{1,2})", value)
    if not match:
        return None

    year = _now().year
    month = int(match.group(1))
    day = int(match.group(2))
    try:
        deadline = datetime(year, month, day, 23, 59, tzinfo=timezone.utc)
        if deadline < _now():
            deadline = datetime(year + 1, month, day, 23, 59, tzinfo=timezone.utc)
        return deadline
    except ValueError:
        return None


def _map_saramin_jobs(html_text: str) -> list[dict[str, Any]]:
    blocks = re.findall(
        r'<div id="rec-(\d+)" class="list_item[^"]*">(.*?)(?=<div id="rec-\d+" class="list_item|</section>)',
        html_text,
        flags=re.S,
    )
    mapped: list[dict[str, Any]] = []

    for index, (rec_id, block) in enumerate(blocks[:80], start=1):
        company = _first_match(r'<div class="col company_nm">.*?<a[^>]*class="str_tit"[^>]*>(.*?)</a>', block)
        title = _first_match(r'<div class="job_tit">.*?<a[^>]*title="([^"]+)"', block)
        href_match = re.search(r'<div class="job_tit">.*?<a[^>]*href="([^"]+)"', block, flags=re.S)
        href = unescape(href_match.group(1)) if href_match else ""

        if not company or not title or not href:
            continue

        sectors = re.findall(r'<span class="job_sector">\s*(.*?)\s*</span>', block, flags=re.S)
        sector_text = _strip_html(sectors[0]) if sectors else "IT 채용"
        work_place = _first_match(r'<p class="work_place">(.*?)</p>', block)
        career = _first_match(r'<p class="career">(.*?)</p>', block)
        education = _first_match(r'<p class="education">(.*?)</p>', block)
        deadline_text = _first_match(r'<span class="date">(.*?)</span>', block)
        updated_text = _first_match(r'<span class="deadlines">(.*?)</span>', block)

        mapped.append(
            {
                "id": -500000 - int(rec_id),
                "title": title,
                "company": company,
                "description": sector_text,
                "job_category": "개발/SW",
                "region": work_place or "국내",
                "experience": career or "경력 무관",
                "education": education or "공고별 확인",
                "deadline": _parse_saramin_deadline(deadline_text),
                "external_url": urljoin("https://www.saramin.co.kr", href),
                "author_id": 0,
                "is_active": True,
                "created_at": _now(),
                "updated_at": None,
                "scrap_count": 0,
                "is_external": True,
                "source": f"사람인 {updated_text}".strip(),
                "external_key": rec_id,
            }
        )

    return mapped


async def _fetch_saramin_jobs(limit: int) -> list[dict[str, Any]]:
    try:
        html_text = await asyncio.to_thread(_get_text, SARAMIN_IT_CATEGORY_URL)
        return _map_saramin_jobs(html_text)[:limit]
    except (TimeoutError, URLError, OSError, ValueError, re.error):
        return []


async def _fetch_worknet_keyword(keyword: str, display: int, page: int, id_offset: int) -> list[dict[str, Any]]:
    params = {
        "authKey": unquote(settings.WORKNET_API_KEY),
        "callTp": "L",
        "returnType": "XML",
        "startPage": page,
        "display": display,
        "keyword": keyword,
        "sortOrderBy": "DESC",
    }
    url = f"{settings.WORKNET_API_URL}?{urlencode(params)}"

    try:
        xml_text = await asyncio.to_thread(_get_text, url)
        return _map_worknet_jobs(xml_text, id_offset=id_offset)
    except (ElementTree.ParseError, TimeoutError, URLError, OSError, ValueError):
        return []


def _map_kontests(payload: Any) -> list[dict[str, Any]]:
    items = payload if isinstance(payload, list) else []
    mapped: list[dict[str, Any]] = []

    for index, item in enumerate(items[:80], start=1):
        if not isinstance(item, dict):
            continue

        title = item.get("name")
        url = item.get("url")
        if not title or not url:
            continue

        site = item.get("site") or "Kontests"
        start_at = _parse_datetime(item.get("start_time"))
        end_at = _parse_datetime(item.get("end_time"))
        status = item.get("status") or "coding contest"

        mapped.append(
            {
                "id": -200000 - index,
                "title": title,
                "organizer": site,
                "description": f"{site}, {status}, coding contest",
                "category": "개발/SW",
                "target": "개발자/학생/일반 참가자",
                "prize": "대회별 확인",
                "start_date": start_at,
                "deadline": end_at,
                "external_url": url,
                "author_id": 0,
                "is_active": True,
                "created_at": start_at or _now(),
                "updated_at": None,
                "scrap_count": 0,
                "is_external": True,
                "source": "Kontests",
            }
        )

    return mapped


def _map_codeforces(payload: Any) -> list[dict[str, Any]]:
    items = payload.get("result", []) if isinstance(payload, dict) and payload.get("status") == "OK" else []
    mapped: list[dict[str, Any]] = []

    for item in items:
        if not isinstance(item, dict):
            continue
        if item.get("phase") not in {"BEFORE", "CODING"}:
            continue

        contest_id = item.get("id")
        title = item.get("name")
        if not contest_id or not title:
            continue

        start_at = _parse_datetime(item.get("startTimeSeconds"))
        duration_seconds = item.get("durationSeconds") or 0
        end_at = (
            datetime.fromtimestamp(item["startTimeSeconds"] + duration_seconds, tz=timezone.utc)
            if item.get("startTimeSeconds")
            else None
        )

        mapped.append(
            {
                "id": -300000 - int(contest_id),
                "title": title,
                "organizer": "Codeforces",
                "description": "Codeforces, algorithm, programming contest",
                "category": "개발/SW",
                "target": "개발자/학생/일반 참가자",
                "prize": "대회별 확인",
                "start_date": start_at,
                "deadline": end_at,
                "external_url": f"https://codeforces.com/contest/{contest_id}",
                "author_id": 0,
                "is_active": True,
                "created_at": start_at or _now(),
                "updated_at": None,
                "scrap_count": 0,
                "is_external": True,
                "source": "Codeforces",
            }
        )

    return mapped


def _map_kipris_ideas(xml_text: str, id_offset: int = 0) -> list[dict[str, Any]]:
    root = ElementTree.fromstring(xml_text)
    error_message = (
        root.findtext(".//error")
        or root.findtext(".//message")
        or root.findtext(".//faultstring")
        or root.findtext(".//resultMsg")
    )
    result_code = (root.findtext(".//resultCode") or "").strip()
    if error_message and result_code not in {"", "00", "0"}:
        raise ValueError(f"KIPRIS API error: {error_message}")

    mapped: list[dict[str, Any]] = []
    seen: set[str] = set()

    for node in root.iter():
        values = _child_texts(node)
        if not values:
            continue

        title = _pick(values, "ideaName", "ideaNm", "IDEA_NM", "title", "name")
        description = _strip_html(
            _pick(values, "ideaContent", "ideaCont", "IDEA_CONT", "content", "description")
        )
        contest_name = _pick(values, "contestName", "cntstNm", "CNTST_NM", "competitionName")
        if not title or (not description and not contest_name):
            continue
        if not _has_it_signal(title, description, contest_name):
            continue

        idea_id = _pick(values, "contestId", "cntstId", "CNTST_ID")
        idea_seq = _pick(values, "ideaSeq", "IDEA_SEQ")
        external_key = ":".join(part for part in [idea_id, idea_seq, title] if part) or title
        if external_key in seen:
            continue
        seen.add(external_key)

        award = _pick(values, "awardName", "awardNm", "AWARD_NM") or "수상/공개작"
        organizer = (
            _pick(
                values,
                "organizer",
                "hostInstitution",
                "cntstInstnNm",
                "CNTST_INSTN_NM",
                "supervisingInstitution",
            )
            or contest_name
            or "KIPRISPlus"
        )
        opening_date = _parse_compact_date(
            _pick(values, "openingDate", "cntstOpnDt", "CNTST_OPN_DT", "openDate")
        )
        tech_class = _pick(
            values,
            "technologyClass",
            "techClass",
            "techClss",
            "TECH_CLSS_NM",
            "ipc",
            "IPC",
        )
        summary_parts = [contest_name, award, tech_class, description]
        summary = ", ".join(part for part in summary_parts if part)

        mapped.append(
            {
                "id": -600000 - id_offset - len(mapped) - 1,
                "title": title,
                "organizer": organizer,
                "description": summary[:700] or "KIPRISPlus 공모전 아이디어 공개 데이터",
                "category": "개발/SW",
                "target": "공모전별 확인",
                "prize": award,
                "start_date": opening_date,
                "deadline": None,
                "external_url": KIPRIS_IDEA_DETAIL_URL,
                "author_id": 0,
                "is_active": True,
                "created_at": opening_date or _now(),
                "updated_at": None,
                "scrap_count": 0,
                "is_external": True,
                "source": "KIPRISPlus 공모전 아이디어",
                "external_key": external_key,
            }
        )

    return mapped


def _extract_contestkorea_field(block: str, icon_class: str) -> str:
    match = re.search(
        rf'<li class="{re.escape(icon_class)}">\s*<strong>[^<]+</strong>\s*\.\s*(.*?)</li>',
        block,
        flags=re.S,
    )
    return _strip_html(match.group(1)) if match else ""


def _map_contestkorea_contests(html_text: str, id_offset: int = 0) -> list[dict[str, Any]]:
    section_match = re.search(r'<div class="list_style_2">\s*<ul>(.*?)</ul>\s*</div>', html_text, flags=re.S)
    section = section_match.group(1) if section_match else html_text
    blocks = re.findall(r'(<div class="title">.*?)(?=<div class="title">|\s*</ul>)', section, flags=re.S)
    mapped: list[dict[str, Any]] = []

    for block in blocks:
        hrefs = re.findall(r'<a\s+href="([^"]*view\.php[^"]*)"', block, flags=re.S)
        title_match = re.search(r'<span class="txt">(.*?)</span>', block, flags=re.S)
        if not hrefs or not title_match:
            continue

        title = _strip_html(title_match.group(1))
        href = unescape(hrefs[-1])
        if not title:
            continue

        organizer = _extract_contestkorea_field(block, "icon_1") or "콘테스트코리아"
        if not _has_it_signal(title, organizer):
            continue

        target = _extract_contestkorea_field(block, "icon_2") or "공모전별 확인"
        category_matches = re.findall(r'<span class="category">(.*?)</span>', block, flags=re.S)
        categories = [_strip_html(category) for category in category_matches if _strip_html(category)]
        period_match = re.search(r'<span class="step-1">\s*<em>접수</em>\s*(.*?)</span>', block, flags=re.S)
        period_text = _strip_html(period_match.group(1)) if period_match else ""
        start_at, deadline = _parse_contestkorea_period(period_text)
        d_day = _first_match(r'<span class="day"[^>]*>(.*?)</span>', block)
        status = _first_match(r'<span class="condition"[^>]*>(.*?)</span>', block)
        like_count = _first_match(r'<span class="icon_like"[^>]*>(.*?)</span>', block)
        external_url = urljoin(f"{CONTESTKOREA_BASE_URL}/sub/", href)
        key_match = re.search(r"str_no=([0-9]+)", external_url)
        external_key = key_match.group(1) if key_match else external_url

        description_parts = [
            ", ".join(categories) or "학문•과학•IT",
            f"접수기간 {period_text}" if period_text else "",
            status,
            d_day,
        ]

        mapped.append(
            {
                "id": -700000 - id_offset - len(mapped) - 1,
                "title": title,
                "organizer": organizer,
                "description": ", ".join(part for part in description_parts if part),
                "category": "개발/SW",
                "target": target,
                "prize": "상세 페이지 확인",
                "start_date": start_at,
                "deadline": deadline,
                "external_url": external_url,
                "author_id": 0,
                "is_active": True,
                "created_at": start_at or _now(),
                "updated_at": None,
                "scrap_count": int(like_count) if like_count.isdigit() else 0,
                "is_external": True,
                "source": "콘테스트코리아",
                "external_key": external_key,
            }
        )

    return mapped


async def _fetch_contestkorea_page(page: int, id_offset: int) -> list[dict[str, Any]]:
    try:
        html_text = await asyncio.to_thread(_get_text, CONTESTKOREA_IT_LIST_URL.format(page=page))
        return _map_contestkorea_contests(html_text, id_offset=id_offset)
    except (TimeoutError, URLError, OSError, ValueError, re.error):
        return []


async def _fetch_contestkorea_contests(limit: int) -> list[dict[str, Any]]:
    cache_key = f"contestkorea_it_contests:{limit}"
    cached = _cache.get(cache_key)
    if cached and time.time() - cached[0] < CACHE_TTL_SECONDS:
        return cached[1][:limit]

    page_count = max(1, min(4, (limit // 8) + 1))
    results = await asyncio.gather(
        *(_fetch_contestkorea_page(page, id_offset=(page - 1) * 1000) for page in range(1, page_count + 1)),
        return_exceptions=True,
    )

    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    for result in results:
        if isinstance(result, Exception):
            continue
        for row in result:
            key = row.get("external_key") or row.get("external_url")
            if key in seen:
                continue
            seen.add(key)
            rows.append(row)

    _cache[cache_key] = (time.time(), rows)
    return rows[:limit]


async def _fetch_kipris_keyword(keyword: str, limit: int, id_offset: int) -> list[dict[str, Any]]:
    if not settings.KIPRIS_API_KEY or not settings.KIPRIS_IDEA_API_URL:
        return []

    params = {
        "ideaName": keyword,
        "openingDate": "",
    }
    query = urlencode(params)
    access_key = urlencode({"accessKey": unquote(settings.KIPRIS_API_KEY)})
    separator = "&" if "?" in settings.KIPRIS_IDEA_API_URL else "?"
    url = f"{settings.KIPRIS_IDEA_API_URL}{separator}{query}&{access_key}"

    try:
        xml_text = await asyncio.to_thread(_get_text, url)
        return _map_kipris_ideas(xml_text, id_offset=id_offset)[:limit]
    except (ElementTree.ParseError, TimeoutError, URLError, OSError, ValueError):
        return []


async def _fetch_kipris_contests(limit: int) -> list[dict[str, Any]]:
    cache_key = f"kipris_idea_contests:{limit}"
    cached = _cache.get(cache_key)
    if cached and time.time() - cached[0] < CACHE_TTL_SECONDS:
        return cached[1][:limit]

    per_keyword = max(2, min(8, (limit // min(len(KIPRIS_IT_KEYWORDS), 4)) + 1))
    tasks = [
        _fetch_kipris_keyword(keyword, per_keyword, id_offset=index * 1000)
        for index, keyword in enumerate(KIPRIS_IT_KEYWORDS[:6])
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    for result in results:
        if isinstance(result, Exception):
            continue
        for row in result:
            key = row.get("external_key") or row.get("title")
            if key in seen:
                continue
            seen.add(key)
            rows.append(row)

    _cache[cache_key] = (time.time(), rows)
    return rows[:limit]


async def fetch_external_jobs(limit: int = 30) -> list[dict[str, Any]]:
    cache_key = f"worknet_jobs:{limit}"
    cached = _cache.get(cache_key)
    if cached and time.time() - cached[0] < CACHE_TTL_SECONDS:
        return cached[1][:limit]

    tasks = [_fetch_saramin_jobs(limit)]
    if settings.WORKNET_API_KEY:
        per_keyword = max(3, min(10, (limit // len(WORKNET_KEYWORDS)) + 1))
        tasks.extend(
            _fetch_worknet_keyword(keyword, per_keyword, page=1, id_offset=index * 1000)
            for index, keyword in enumerate(WORKNET_KEYWORDS)
        )

    results = await asyncio.gather(*tasks, return_exceptions=True)

    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    for result in results:
        if isinstance(result, Exception):
            continue
        for row in result:
            key = row.get("external_key") or row.get("external_url")
            if key in seen:
                continue
            seen.add(key)
            rows.append(row)

    _cache[cache_key] = (time.time(), rows)
    return rows[:limit]


async def fetch_external_contests(limit: int = 30) -> list[dict[str, Any]]:
    rows = await _fetch_contestkorea_contests(limit)

    fallback_limit = max(limit - len(rows), 0)
    if fallback_limit:
        rows.extend(await _fetch_kipris_contests(fallback_limit))
        fallback_limit = max(limit - len(rows), 0)
    if fallback_limit:
        rows.extend(await _get_cached("kontests_contests", KONTESTS_URL, _map_kontests, fallback_limit))
    if len(rows) < limit:
        codeforces_rows = await _get_cached(
            "codeforces_contests",
            CODEFORCES_URL,
            _map_codeforces,
            limit,
        )
        seen_urls = {row["external_url"] for row in rows}
        rows.extend(row for row in codeforces_rows if row["external_url"] not in seen_urls)
    return rows[:limit]
