import asyncio
from sqlalchemy.future import select
from app.database import AsyncSessionLocal, engine
from app.models.user import User
from app.models.post import Post
from app.models.comment import Comment
from app.models.interaction import PostLike, PostRecommend

async def test_relationship():
    print("🔍 데이터베이스 연결 및 관계 테스트를 시작합니다...")
    async with AsyncSessionLocal() as session:
        try:
            # 1. 테스트용 유저 생성
            test_user = User() # User 모델에 필드가 있다면 User(username="test") 식으로 수정
            session.add(test_user)
            await session.flush() # ID를 할당받기 위해 잠깐 밀어넣기
            print(f"✅ 유저 생성 성공 (ID: {test_user.id})")

            # 2. 해당 유저가 쓴 게시글 생성
            test_post = Post(
                title="연결 테스트 게시글",
                content="내용입니다.",
                author_id=test_user.id
            )
            session.add(test_post)
            await session.flush()
            print(f"✅ 게시글 생성 성공 (ID: {test_post.id}, 작성자: {test_post.author_id})")

            # 3. 게시글에 댓글 달기
            test_comment = Comment(
                post_id=test_post.id,
                user_id=test_user.id,
                content="연결 테스트 댓글입니다!"
            )
            session.add(test_comment)
            print("✅ 댓글 생성 성공")

            # 4. 좋아요 및 추천 누르기
            test_like = PostLike(user_id=test_user.id, post_id=test_post.id)
            test_rec = PostRecommend(user_id=test_user.id, post_id=test_post.id)
            session.add_all([test_like, test_rec])
            print("✅ 좋아요/추천 데이터 연결 성공")

            # 5. DB에 최종 저장
            await session.commit()
            print("\n🚀 모든 데이터가 성공적으로 커밋되었습니다!")

            # 6. 관계 조회 테스트 (JOIN 확인)
            print("\n--- 데이터 조회 결과 ---")
            result = await session.execute(select(Post).where(Post.id == test_post.id))
            fetched_post = result.scalar_one()
            print(f"조회된 게시글 제목: {fetched_post.title}")
            
            # 외래키 연결 확인
            if fetched_post.author_id == test_user.id:
                print("🔗 게시글 -> 유저 연결 확인됨")

        except Exception as e:
            await session.rollback()
            print(f"❌ 테스트 중 에러 발생: {e}")
        finally:
            # 테스트 데이터 삭제 (선택 사항: 깔끔하게 비우고 싶을 때)
            # await session.delete(test_user) 
            # await session.commit()
            await session.close()

if __name__ == "__main__":
    asyncio.run(test_relationship())