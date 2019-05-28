# 添加一个过滤器
import jinja2


def do_listreverse(li):
    """实现li的翻转"""
    # 通过原列表创建一个新列表
    temp_li = list(li)
    # 将新列表进行返转
    temp_li.reverse()
    return temp_li


# 添加一个过滤器  FILTERS是一个字典 存了所有过滤器 key是过滤器的名字 值是对应的函数
jinja2.filters.FILTERS['lireverse'] = do_listreverse
