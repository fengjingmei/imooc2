from django.conf.urls import url

from apps.operations.views import AddFavView, CommentView

urlpatterns = [
    url(r'^fav/$', AddFavView.as_view(), name="fav"),  #用户收藏
    url(r'^comment/$', CommentView.as_view(), name="comment"), #用户评论
]
