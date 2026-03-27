from sqlalchemy import Column, Integer
from app.database import Base

class User(Base):
    # 실제 DB에 있는 유저 테이블 이름과 똑같이 맞춰야 합니다! (보통 "users"를 많이 씁니다)
    __tablename__ = "users"

    # 댓글 테이블이 연결될 기준점(id)
    id = Column(Integer, primary_key=True, index=True)