from django import template

register = template.Library()

@register.simple_tag
def parse_commenttree(commentlist, comment):
    """获得当前评论子评论的列表
        用法: {% parse_commenttree article_comments comment as childcomments %}
    """
    datas = []

    def parse(c):
        childs = commentlist.filter(parent_comment=c, is_enable=True)
        for child in childs:
            datas.append(child)
            parse(child)

    parse(comment)
    return datas

@register.inclusion_tag('comments/tags/comment_item.html')
def show_comment_item(comment, ischild):
    """
    2018-7-23：暂时没用到
    评论
    """
    depth = 2 if ischild else 1
    return {
        'comment_item': comment,
        'depth': depth
    }
