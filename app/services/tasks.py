import enum
from sqlalchemy import Column, Integer, String, Enum, Text, JSON, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


# 定义任务状态的枚举类型 | Define an enum for task status
class TaskStatus(enum.Enum):
    QUEUED = 'queued'
    PROCESSING = 'processing'
    COMPLETED = 'completed'
    FAILED = 'failed'


Base = declarative_base()


class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True)
    status = Column(Enum(TaskStatus), default=TaskStatus.QUEUED)
    file_path = Column(String, nullable=False)
    result = Column(Text)
    error = Column(Text)
    decode_options = Column(JSON)


# 创建数据库引擎和会话 | Create database engine and session
engine = create_engine('sqlite:///tasks.db', connect_args={"check_same_thread": False})
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)
