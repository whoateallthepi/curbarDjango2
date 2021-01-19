from django import template
from ..models import Post

register = template.Library()

@register.inclusion_tag('blog/post/latest_posts.html') 
def show_latest_posts(count=5):
    # always show the 'About 
    latest_posts = Post.published.order_by('-publish') [:count]
    about_post = Post.published.filter(slug='about-curbargapinfo').first()
    #breakpoint()
    return {'latest_posts':latest_posts,
            'about_post' : about_post}