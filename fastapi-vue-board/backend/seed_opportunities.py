import asyncio
from datetime import datetime

import app.models  # noqa: F401
from app.core.security import hash_password
from app.database import AsyncSessionLocal
from app.models.contest import Contest
from app.models.job import Job
from app.models.user import User
from sqlalchemy import select


JOBS = [
    {
        "company": "NAVER",
        "title": "NAVER Careers 채용 공고",
        "description": "Backend, Frontend, AI/ML, Data Engineering",
        "job_category": "개발/SW",
        "region": "분당/서울",
        "experience": "신입/경력",
        "education": "공고별 확인",
        "external_url": "https://recruit.navercorp.com/rcrt/list.do",
    },
    {
        "company": "Kakao",
        "title": "Kakao Careers 채용 공고",
        "description": "Server, Client, Platform, Infra, Data",
        "job_category": "개발/SW",
        "region": "판교",
        "experience": "신입/경력",
        "education": "공고별 확인",
        "external_url": "https://careers.kakao.com/jobs",
    },
    {
        "company": "Coupang",
        "title": "Coupang Engineering 채용 공고",
        "description": "Backend, Software Engineering, Machine Learning",
        "job_category": "개발/SW",
        "region": "서울/글로벌",
        "experience": "경력",
        "education": "공고별 확인",
        "external_url": "https://www.coupang.jobs/en/jobs/",
    },
    {
        "company": "Toss",
        "title": "Toss Careers 개발 직군 채용",
        "description": "Frontend, Server, Data, Product Engineering",
        "job_category": "개발/SW",
        "region": "서울",
        "experience": "경력",
        "education": "공고별 확인",
        "external_url": "https://toss.im/career/jobs",
    },
    {
        "company": "Hyundai Motor Group",
        "title": "현대자동차그룹 채용 공고",
        "description": "Software, Mobility, Autonomous Driving, Data",
        "job_category": "개발/SW",
        "region": "서울/경기",
        "experience": "신입/경력",
        "education": "공고별 확인",
        "external_url": "https://talent.hyundai.com/main/main.hc",
    },
]


CONTESTS = [
    {
        "title": "2026 관광데이터 활용 공모전",
        "organizer": "한국관광공사/카카오",
        "description": "웹/앱 개발, OpenAPI, 관광 데이터",
        "category": "개발/SW",
        "target": "대한민국 국민 누구나",
        "prize": "총 4,250만원",
        "start_date": datetime(2026, 3, 30),
        "deadline": datetime(2026, 5, 6, 16, 0),
        "external_url": "https://api.visitkorea.or.kr/#/cntSearchDetail?no=1",
    },
    {
        "title": "2026년 인천광역시 공공데이터·AI 활용 창업경진대회",
        "organizer": "인천광역시",
        "description": "공공데이터, AI, 창업, 서비스 개발",
        "category": "아이디어",
        "target": "대한민국 국민 누구나",
        "prize": "총 2,700만원",
        "start_date": datetime(2026, 4, 20),
        "deadline": datetime(2026, 6, 12, 18, 0),
        "external_url": "https://www.incheon.go.kr/IC010101/view?nttNo=2045782",
    },
    {
        "title": "2026 제2회 스마트양식 도전해(海) 공모전",
        "organizer": "FIPA",
        "description": "AI, 머신러닝, 수중환경 데이터, 스마트양식",
        "category": "개발/SW",
        "target": "누구나",
        "prize": "총 1억원",
        "start_date": datetime(2026, 4, 20),
        "deadline": datetime(2026, 5, 15),
        "external_url": "https://www.fipa-ai.kr/",
    },
    {
        "title": "Kaggle Competitions",
        "organizer": "Kaggle",
        "description": "AI/ML, Data Science, Competition",
        "category": "개발/SW",
        "target": "전 세계 참가자",
        "prize": "대회별 확인",
        "start_date": None,
        "deadline": None,
        "external_url": "https://www.kaggle.com/competitions",
    },
]


async def get_or_create_author(session):
    result = await session.execute(select(User).order_by(User.id).limit(1))
    user = result.scalar_one_or_none()
    if user:
        return user

    user = User(
        email="seed@example.com",
        username="seed_admin",
        password=hash_password("seed-password-change-me"),
        role="admin",
    )
    session.add(user)
    await session.flush()
    return user


async def insert_missing(session, model, items, author_id):
    created = 0
    for item in items:
        result = await session.execute(
            select(model).where(model.external_url == item["external_url"])
        )
        if result.scalar_one_or_none():
            continue

        session.add(model(**item, author_id=author_id))
        created += 1
    return created


async def main():
    async with AsyncSessionLocal() as session:
        author = await get_or_create_author(session)
        job_count = await insert_missing(session, Job, JOBS, author.id)
        contest_count = await insert_missing(session, Contest, CONTESTS, author.id)
        await session.commit()

    print(f"Seeded {job_count} jobs and {contest_count} contests.")


if __name__ == "__main__":
    asyncio.run(main())
