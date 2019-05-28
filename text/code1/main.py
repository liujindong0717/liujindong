from app import create_app

if __name__ == '__main__':
    # 创建flask对象
    app = create_app()
    # 启动
    app.run()
