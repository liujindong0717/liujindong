from flask import Blueprint

# 创建一个蓝图，用来管理多个函数视图 参数一是蓝图的名字 不要重复，参数2 和之前flask对象里一个作用
admin_blu = Blueprint("admin", __name__)

# 这里一定要添加导入 否则和views没有了关联，views里的视图路由也就不会生成
# 要写到蓝图对象生成后
from . import views
