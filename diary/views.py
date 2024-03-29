from django.db import transaction
from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView

from config.basemodel import ApiResponse
from diary.serializers import *
from diary.text_rank_modules.textrank import TextRank, make_quiz
from users.models import User
from .graph import GraphDB


class WriteView(APIView):
    @transaction.atomic
    @swagger_auto_schema(operation_description="일기 작성", request_body=WriteRequest, responses={"201": '작성 성공'})
    def post(self, request):
        requestSerial = WriteRequest(data=request.data)

        isValid, response_status = requestSerial.is_valid()
        # 유효성 검사 통과하지 못한 경우
        if not isValid:
            return ApiResponse.on_fail(requestSerial.errors, response_status=response_status)

        request = requestSerial.validated_data

        # user 가져오기
        user_id = request.get('userId')
        findUser = User.objects.get(id=user_id)

        content = request.get('content')

        # Diary 객체 생성
        newDiary = Diary.objects.create(user=findUser, title=request.get('title'), createDate=request.get('date'),
                                        content=content)

        # 키워드 추출
        memory = TextRank(content=content)

        conn = GraphDB()
        conn.create_and_link_nodes(
            user_id=user_id, diary_id=newDiary.id,
            words_graph=memory.words_graph,
            words_dict=memory.words_dict,
            weights_dict=memory.weights_dict
        )

        # 키워드 추출 후 가중치가 높은 키워드 5개로 퀴즈 생성
        question, keyword = make_quiz(memory, keyword_size=5)

        # 각 키워드별로 Question 생성
        for q, k in zip(question, keyword):
            newKeyword = Keywords.objects.create(keyword=k, diary=newDiary)
            Questions.objects.create(question=q, keyword=newKeyword)

        return ApiResponse.on_success(
            result=DiaryResultResponse(newDiary).data,
            response_status=status.HTTP_201_CREATED
        )


class UpdateView(APIView):
    @transaction.atomic
    @swagger_auto_schema(operation_description="일기 수정", request_body=UpdateRequest, responses={"201": '작성 성공'})
    def patch(self, request):
        requestSerial = UpdateRequest(data=request.data)

        isValid, response_status = requestSerial.is_valid()

        # 유효성 검사 통과하지 못한 경우
        if not isValid:
            return ApiResponse.on_fail(requestSerial.errors, response_status=response_status)

        # 유효성 검사 통과한 경우
        request = requestSerial.validated_data

        # Diary 가져오기
        diary_id = request.get('diaryId')
        findDiary = Diary.objects.get(id=diary_id)

        # Diary 삭제
        findDiary.delete()

        # GraphDB에서도 삭제
        conn = GraphDB()
        conn.delete_diary(user_id=request.get('userId'), diary_id=diary_id)

        # user 가져오기
        user_id = request.get('userId')
        findUser = User.objects.get(id=user_id)

        content = request.get('content')

        # Diary 객체 생성
        updateDiary = Diary.objects.create(user=findUser, title=request.get('title'), createDate=request.get('date'),
                                           content=content)

        # 키워드 추출
        memory = TextRank(content=content)

        # GraphDB에 추가
        conn.create_and_link_nodes(
            user_id=user_id, diary_id=updateDiary.id,
            words_graph=memory.words_graph,
            words_dict=memory.words_dict,
            weights_dict=memory.weights_dict
        )

        # 키워드 추출 후 가중치가 높은 키워드 5개로 퀴즈 생성
        question, keyword = make_quiz(memory, keyword_size=5)

        # 각 키워드별로 Question 생성
        for q, k in zip(question, keyword):
            newKeyword = Keywords.objects.create(keyword=k, diary=updateDiary)
            Questions.objects.create(question=q, keyword=newKeyword)

        return ApiResponse.on_success(
            result=DiaryResultResponse(updateDiary).data,
            response_status=status.HTTP_201_CREATED
        )


class GetDiaryByUserView(APIView):
    @transaction.atomic
    @swagger_auto_schema(operation_description="유저의 일기 조회", query_serializer=GetUserRequest,
                         response={"200": DiaryResultResponse})
    def get(self, request):
        requestSerial = GetUserRequest(data=request.query_params)

        isValid, response_status = requestSerial.is_valid()

        # 유효성 검사 통과하지 못한 경우
        if not isValid:
            return ApiResponse.on_fail(requestSerial.errors, response_status=response_status)

        # 유효성 검사 통과한 경우
        request = requestSerial.validated_data

        # User 가져오기
        user_id = request.get('userId')
        findUser = User.objects.get(id=user_id)

        # User와 연관된 모든 Diary 가져오기
        findDiaries = Diary.objects.filter(user=findUser)

        return ApiResponse.on_success(
            result=DiaryResultResponse(findDiaries, many=True).data,
            response_status=status.HTTP_200_OK
        )


class GetQuizView(APIView):
    @transaction.atomic
    @swagger_auto_schema(operation_description="일기회상 퀴즈", query_serializer=GetDiaryRequest,
                         responses={"200": "퀴즈"})
    def get(self, request):
        requestSerial = GetDiaryRequest(data=request.query_params)

        isValid, response_status = requestSerial.is_valid()
        if not isValid:
            return ApiResponse.on_fail(requestSerial.errors, response_status=response_status)

        # 유효성 검사 통과한 경우
        request = requestSerial.validated_data

        # Diary 가져오기
        diary_id = request.get('diaryId')
        findDiary = Diary.objects.get(id=diary_id)

        keywords = findDiary.keywords.all()

        # 모든 Sentence 와 연관된 Question 가져오기
        question_keyword = []

        for keyword in keywords:
            question_keyword.append({
                "Q": keyword.questions.first().question,
                "A": keyword.keyword
            })

        return ApiResponse.on_success(
            result=question_keyword,
            response_status=status.HTTP_200_OK
        )


class GetDiaryByDateView(APIView):
    @transaction.atomic
    @swagger_auto_schema(operation_description="날짜로 일기 검색", query_serializer=GetDiaryByDateRequest,
                         responses={"200": "일기"})
    def get(self, request):
        requestSerial = GetDiaryByDateRequest(data=request.query_params)

        isValid, response_status = requestSerial.is_valid()
        if not isValid:
            return ApiResponse.on_fail(requestSerial.errors, response_status=response_status)

        # 유효성 검사 통과한 경우
        request = requestSerial.validated_data

        # User 불러오기
        user_id = request.get('userId')
        findUser = User.objects.get(id=user_id)
        findDiary = Diary.objects.get(user=findUser, createDate=request.get('date'))

        return ApiResponse.on_success(
            result=DiaryResultResponse(findDiary).data,
            response_status=status.HTTP_200_OK
        )
    

class DeleteDiaryView(APIView):
    @transaction.atomic
    @swagger_auto_schema(operation_description="일기 삭제", request_body=DeleteDiaryRequest, 
                         responses={200: '삭제 완료'})
    def delete(self, request):
        requestSerial = DeleteDiaryRequest(data=request.data)

        isValid, response_status = requestSerial.is_valid()
        # 유효성 검사 통과하지 못한 경우
        if not isValid:
            return ApiResponse.on_fail(requestSerial.errors, response_status=response_status)

        request = requestSerial.validated_data

        # 다이어리 아이디 가져오기
        diary_id = request.get('diaryId')
        findDiary = Diary.objects.get(id=diary_id)

        Diary.delete(findDiary)

        return ApiResponse.on_success(
            result=DiaryResultResponse(findDiary).data,
            response_status=status.HTTP_200_OK
        )