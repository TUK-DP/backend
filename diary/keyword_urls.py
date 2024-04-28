from django.urls import path

from .keyword_views import *

urlpatterns = [
    path('/diray/<int:diaryId>', GetKeywordView.as_view()),
    path('/<int:keywordId>/image', KeywordImgSaveView.as_view()),
]
