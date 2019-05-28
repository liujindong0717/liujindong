import functools
import traceback

from flask import session, g
from sqlalchemy.orm import sessionmaker

from app import db
from app.models.models import User


def login_user_data(view_func):

    # 添加这个装饰起 让路由重新指向正确的视图函数
    @functools.wraps(view_func)
    def wrapper(*args, **kwargs):
        # 尝试从session中获取user_id
        user_id = session.get('user_id')  # 获取不到，返回None

        user = None
        if user_id:
            # 用户已登录
            try:
                # DBSession = sessionmaker(bind=engine)
                # sqlsession = DBSession()  # 获取会话对象
                # 根据uesr_id查询用户数据
                user = db.session.query(User).filter(User.user_id == user_id).first()
            except Exception as e:
                print("登录查询用户信息，产生异常...")
                traceback.print_exc()

        # 使用g变量临时保存user信息
        # g变量中保存的数据可以在请求开始到请求结束过程中的使用
        g.user = user

        return view_func(*args, **kwargs)

    return wrapper
