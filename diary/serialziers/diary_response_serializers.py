from django.db.models import QuerySet

from config.paging_handler import PagingSerializer, get_paging_data
from diary.serialziers.keyword_serializers import KeywordResponse
from diary.validator import *
from users.serializers.user_get_post_put_delete_serializers import *


class DiarySerializer(serializers.ModelSerializer):
    user = UserSafeSerializer(read_only=True)

    class Meta:
        model = Diary
        fields = '__all__'


class DiaryResultResponse(serializers.ModelSerializer):
    diaryId = serializers.IntegerField(source="id")

    class Meta:
        model = Diary
        fields = ['diaryId', 'title', 'createDate', 'content', 'imgUrl']


class GetDiaryPreviewResponse(serializers.Serializer):
    diaryId = serializers.IntegerField(source='id')
    title = serializers.CharField()
    createDate = serializers.DateField()
    content = serializers.CharField()

    @staticmethod
    def to_json(diary: Diary):
        return {
            'diaryId': diary.id,
            'title': diary.title,
            'createDate': diary.createDate,
            'content': diary.content
        }


class GetDiaryDetailResponse(GetDiaryPreviewResponse):
    keywords = KeywordResponse(many=True)
    imgUrl = serializers.CharField()

    @staticmethod
    def to_json(diary: Diary):
        r = GetDiaryPreviewResponse.to_json(diary)
        r['keywords'] = [KeywordResponse.to_json(keyword) for keyword in diary.keywords.all()]
        r['imgUrl'] = diary.imgUrl
        return r


class GetDiariesByUserAndDateResponse(serializers.Serializer):
    user = UserSafeSerializer()
    diaries = GetDiaryDetailResponse(many=True)

    @staticmethod
    def to_json(user: User, diaries: QuerySet):
        return {
            'user': UserSafeSerializer(user).data,
            'diaries': [GetDiaryPreviewResponse.to_json(diary) for diary in diaries]
        }


class DiaryPagingResponse(PagingSerializer):
    diaryList = serializers.ListField(child=DiaryResultResponse())

    def __init__(self, *args, page=1, pageSize=1, object_list=None, **kwargs):
        if object_list is None:
            object_list = []

        data = get_paging_data(page, pageSize, object_list, data_name="diaryList")

        super().__init__(data, *args, **kwargs)