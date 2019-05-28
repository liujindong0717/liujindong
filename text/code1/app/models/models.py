# from sqlalchemy import create_engine, Column, Integer, String
# from sqlalchemy.ext.declarative import declarative_base

# 获取引擎  连接数据库
# engine = create_engine('mysql+pymysql://root:mysql@localhost:3306/flask_test1')
# 获取Base 模型类基类
# Base = declarative_base()


# 模型类 model
# class User(Base):
#     __tablename__ = 'user'
#     id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
#     user_id = Column(String(50), nullable=False)
#     user_name = Column(String(50), nullable=False)
#     head_img = Column(String(200), nullable=True)
#     short_description = Column(String(300), nullable=True)
#     password = Column(String(100), nullable=False)
#     email = Column(String(100), nullable=True)

from app import db


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = db.Column(db.String(50), nullable=False)
    user_name = db.Column(db.String(50), nullable=False)
    head_img = db.Column(db.String(200), nullable=True)
    short_description = db.Column(db.String(300), nullable=True)
    password = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=True)
    status = db.Column(db.Boolean, default=False)  # 是否激活
    activekey = db.Column(db.String(50))  # 激活码
