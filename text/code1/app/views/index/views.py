# 从数据库查询数据 并且传给模板
import hashlib
import os
import traceback
import uuid

import flask
from flask import render_template, url_for, redirect, request, make_response, session, g, current_app
from flask_mail import Message
from sqlalchemy import and_, or_
from sqlalchemy.orm import sessionmaker

from app import db, mail
from app.models.models import User
from app.utils.commons.commons import login_user_data
from . import index_blu


# LOGIN_FLAG = False  # 标记是否登录  默认没有登录


@index_blu.route('/profile_v7')
@login_user_data  # profile7 = login_user_data(profile7)
def profile7():
    # 从g里面 获取到用户信息  在login_user_data装饰器里已经提前查询好了
    user = g.user
    if user:
        return render_template('index/profile.html', user_name=user.user_name, short_description=user.short_description
                               , head_img=user.head_img)
    else:
        return '去<a href="http://127.0.0.1:5000/index/login.html">登录</a>'





@index_blu.route('/login.html')
def login():
    """显示登录页面"""
    return render_template('index/login.html')


@index_blu.route('/login', methods=['POST', 'GET'])
def login_vf():
    """处理登录验证的逻辑"""
    # 1获取get请求传来的用户名和密码
    # 请求对象request  是一个上下文对象 只能用于视图里
    # request.args 获取get请求传来的参数  得到的是一个字典 可以使用字典的语法 获取里面 的内容
    print('request.args----', request.args)  # ImmutableMultiDict([('username', '123'), ('password', '321')])
    # request.form 获取post请求传来的参数 得到的是一个字典 可以使用字典的语法 获取里面 的内容
    print('request.form----', request.form)  # ImmutableMultiDict([('username', '123'), ('password', '321')])
    # 获取用户名和密码
    username = request.form.get('username')
    password = request.form.get('password')
    print('username==', username)
    print('password==', password)
    # 2 根据用户名和密码去数据库查询 如果能查到 登录成功 如果不能 就提示登录失败

    # DBSession = sessionmaker(bind=engine)
    # sqlsession = DBSession()  # 获取会话对象


    try:
        user = db.session.query(User).filter(and_(User.user_name == username, User.password == password)).one()
    except:
        # 出现异常 没有查询到用户 登录失败
        # make_response可以返回一个response对象 这样用response对象 就可以去设置cookie
        response = make_response('登录失败了 username = %s password = %s' % (username, password))
        # LOGIN_FLAG = False

        # response.set_cookie('login_flag', 'fail')
        session['login_flag'] = 'fail'
        # 自定义抛出异常
        # abort(500)
    else:
        # LOGIN_FLAG = True
        # 登录成功  redirect返回的是一个response对象 可以设置cookie
        response = redirect(url_for('index.profile7'))

        # response.set_cookie('login_flag', 'success')
        session['login_flag'] = 'success'
        # 把user_id也存进来2
        session['user_id'] = user.user_id

    finally:
        db.session.close()

    return response


@index_blu.route('/logout')
def logout():
    """退出登录"""
    # 获取response响应对象
    response = redirect(url_for("index.login"))
    # 把cookie登录相关的信息清除
    # response.delete_cookie('login_flag')
    # 清除session数据
    session.clear()

    return response


@index_blu.route("/register", methods=['GET', 'POST'])
def register():
    """显示注册页面 """
    # 判断请求方式
    if request.method == "POST":
        # print(request.form)
        # 提取 数据
        email = request.form.get("email")
        username = request.form.get("username")
        password = request.form.get("password")
        # 图片验证码
        captcha = request.form.get("captcha")

        # 只要有1个需要的数据，没有，那么就返回数据有误
        if not (email and username and password and captcha):
            # 返回对应的数据
            ret = {
                "status": 2,
                "msg": "输入数据有误，请重新输入"
            }
            return flask.jsonify(ret)

        # session里取出验证码
        session_captcha = session.get('captcha')
        # 判断验证码是否正确 转为小写判断 可以让用户忽略大小写输入
        if session_captcha.lower() != captcha.lower():
            # 返回对应的数据
            ret = {
                "status": 3,
                "msg": "验证码错误"
            }
            return flask.jsonify(ret)

        # 业务处理：注册用户
        # 判断是否注册过
        # 1. 业务处理
        # db_session = sessionmaker(bind=engine)()  # 生成会话对象
        # 去数据库查询 获取结果的第一条数据
        user_ret = db.session.query(User).filter(or_(User.email == email, User.user_name == username)).first()
        if user_ret:
            # 2. 如果邮箱或者用户名已经存在，则不允许使用
            # 3. 返回对应的数据
            ret = {
                "status": 1,
                "msg": "邮箱或用户名已存在，请修改"
            }

        else:
            # uuid 随机生成一个激活码  uuid1返回的是uuid对象 需要强转成字符串
            active_key = str(uuid.uuid1())  # fdskljj-fdjsk-fjdskl-fdsjkl
            # 去掉激活码里 的-
            active_key = active_key.replace('-', '')

            # host_url  127.0.0.1:5000/
            # 127.0.0.1:5000/index/active?id=xxx&activekey=xxxx
            active_addr = request.host_url + 'index/active?id={}&activekey={}'.format(username, active_key)

            msg = Message('激活邮件', sender='yanjianglong@126.com', recipients=[email])
            # 这里的sender是发信人，写上你发信人的名字，比如张三。
            # recipients是收信人，用一个列表去表示。
            msg.body = '激活邮件'
            msg.html = """<a href='{}'>点击激活</a>,如果有什么问题,请联系halon,电话:18512345678""".format(active_addr)
            # 发送邮件
            mail.send(msg)

            # 3. 未注册，那么则进行注册  注意别忘了激活码
            new_user = User(email=email, user_id=username, password=password, user_name=username, activekey=active_key)
            db.session.add(new_user)
            db.session.commit()

            # 3. 返回对应的数据
            ret = {
                "status": 0,
                "msg": "注册成功"
            }
        db.session.close()
        return flask.jsonify(ret)
    elif request.method == "GET":
        # 如果是get请求  就是请求页面
        return render_template("index/register.html")


from app.utils.captcha.captcha import captcha


@index_blu.route("/captcha")
def generate_captcha():
    # 1. 获取到当前的图片编号id
    captcah_id = request.args.get('id')

    print(type(captcah_id), captcah_id)

    # 2. 生成验证码
    # 返回保存的图片名字  验证码值  图片二进制内容
    name, text, image = captcha.generate_captcha()

    # print("注册时的验证码为：", name, text, image)  # 图片名字  验证码值  图片二进制内容

    # 3. 将生成的图片验证码值作为value，存储到session中
    session["captcha"] = text

    # 返回响应内容
    resp = make_response(image)
    # 设置内容类型
    resp.headers['Content-Type'] = 'image/jpg'
    return resp


# http://127.0.0.1:5000/index/active?id=halon555&activekey=ab71d3127bc811e9b57d000c29e0ef6c
@index_blu.route("/active")
def active():
    # 获取用户id和激活码
    user_id = request.args.get('id')
    activekey = request.args.get('activekey')

    try:
        # 去数据库查询 用户
        user = db.session.query(User).filter(and_(User.user_id == user_id, User.activekey == activekey)).one()
    except Exception as e:
        traceback.print_exc()
        # 如果查不到 提示从新注册
        response_str = '激活失败，请重新注册'
    else:
        # 如果查到，就修改status为1
        user.status = True
        # 提交
        db.session.commit()
        db.session.close()
        response_str = """激活成功，去<a href='{}'>登录</a>""".format(url_for('.login'))

    return response_str


@index_blu.route('/edit', methods=['POST', 'GET'])
@login_user_data
def edit():
    current_user = g.user
    # 如果没有登录  就去登录页面
    if not current_user:
        return redirect(url_for('.login'))

    if request.method == 'GET':
        return render_template('/index/edit.html', user=current_user)
    elif request.method == 'POST':
        # 处理修改数据的逻辑

        # 1.提取数据
        username = request.form.get("username")
        password = request.form.get("password")
        email = request.form.get("email")
        content = request.form.get("content")

        # 2获取头像
        f = request.files.get('image')
        if f:
            print('content---', content)
            print('headimg---', f)  # <FileStorage: 'head001.jpg' ('image/jpeg')>

            # 根据图片的二进制数据获取md5加密的一个字符串最为保存的名字
            name_hash = hashlib.md5()
            uuidstr = str(uuid.uuid1())  # uudi保证图片名字不一样 不会覆盖
            name_hash.update((f.filename + uuidstr).encode('utf-8'))
            # 获取的字符串就作为文件的名字
            image_file_name = name_hash.hexdigest()

            # 获取当前应用的绝对路径
            # print(current_app.root_path)  # /home/halon/桌面/code1/app

            # fdds.fsfs.jpeg
            # 获取图片的后缀
            image_type = f.filename[f.filename.rfind('.'):]
            # 包含了后缀的名字
            image_file_name = image_file_name + image_type

            image_path = os.path.join('/static/upload/images', image_file_name)
            upload_path = os.path.join(current_app.root_path, 'static/upload/images', image_file_name)
            print(upload_path)
            f.save(upload_path)
            # 图片路径存到数据库
            current_user.head_img = image_path

        # 把数据更新到数据库

        current_user.user_name = username
        current_user.short_description = content
        current_user.password = password
        current_user.email = email

        # 提交保存是怒局
        db.session.commit()
        db.session.close()

        # 保存完头像和其他信息后 就刷新页面
        return redirect(url_for('.edit'))
