import pytz
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from api.models import Record
from datetime import datetime

# 新增運動紀錄
@api_view(['POST'])
def addrecord(request):
    data = request.data
    # 從請求中取得使用者 email
    user_email = data.get('user_email')  # 確保此名稱與請求中的一致

    # 從請求中取得其他資料
    count = data.get('count')
    datetime_str = data.get('datetime')
    left_errors = data.get('left_errors')
    right_errors = data.get('right_errors')
    sport_time = data.get('sport_time')

    # 驗證欄位是否為空
    if not all([user_email, count, datetime_str, sport_time]):
        return Response({"error": "缺少必要的欄位"}, status=status.HTTP_400_BAD_REQUEST)

    # 調整時間格式並改為台灣台北時區
    try:
        datetime_obj = datetime.strptime(datetime_str, "%Y-%m-%dT%H:%M:%S")  # 使用 ISO 格式
        taipei_tz = pytz.timezone('Asia/Taipei')
        datetime_obj = taipei_tz.localize(datetime_obj)
    except ValueError:
        return Response({"error": "日期時間格式不正確，應為 'YYYY-MM-DDTHH:MM:SS'"}, status=status.HTTP_400_BAD_REQUEST)

    # 建立運動紀錄
    try:
        record = Record(
            user_email=user_email,
            count=count,
            datetime=datetime_obj,
            left_errors=left_errors,
            right_errors=right_errors,
            sport_time=sport_time
        )
        record.save()
        return Response({"message": "運動紀錄新增成功"}, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# 抓取運動紀錄
@api_view(['GET'])
def get_user_records(request):
    # 從請求中取得用戶 email
    user_email = request.query_params.get('email')  # 假设您从查询参数中获取 email

    # 查找該用戶的運動紀錄
    try:
        records = Record.objects.filter(user_email=user_email)  # 根據用戶 email 過濾紀錄

        # 如果沒有找到紀錄
        if not records.exists():
            return Response({"message": "沒有找到運動紀錄"}, status=status.HTTP_404_NOT_FOUND)

        # 將紀錄序列化為字典格式
        records_data = [
            {
                "count": record.count,
                "datetime": record.datetime.strftime("%Y-%m-%d %H:%M:%S"),  # 格式化日期
                "left_errors": record.left_errors,
                "right_errors": record.right_errors,
                "sport_time": record.sport_time,
            }
            for record in records
        ]

        return Response({"records": records_data}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
