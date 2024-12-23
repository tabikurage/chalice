from chalice import Chalice, Cron
from urllib import request
from dateutil.relativedelta import relativedelta
import urllib
import json
import os
import datetime
import jpholiday

app = Chalice(app_name='shinkansen')

@app.schedule(Cron(55, 0, '*', '*', '?', '*'))
def lambda_handler(event):
    # デバッグ用
    # print("event:")
    # print(vars(event))

    # チェック対象の日付を格納するListを作成
    checkdaylist = []

    # 引数から渡された日付＝本日の日付を取得
    s_format = '%Y-%m-%dT%H:%M:%SZ'
    today = datetime.datetime.strptime(event.time, s_format) 

    if today.day == 1:
        yesterday = today - relativedelta(days=1)
        nextmonth = today + relativedelta(months=1)
        if yesterday.day == 28:
            checkdaylist.append()
    s_format = '%Y-%m-%dT%H:%M:%SZ'
    dt_after1m = datetime.datetime.strptime(event.time, s_format) + relativedelta(months=1)
    print(dt_after1m)


    checkdaylist = [dt_after1m]

    for checkday in checkdaylist :
        # 連休数を格納
        renkyu = 0
        # 1ヶ月後の日付が金曜日 and 祝日でないか判定　or 今日が木曜日 and 明日が祝日 →　通知対象
        if (checkday.weekday() == 4) and (not jpholiday.is_holiday(checkday)) :
            # 月曜日が祝日か判定
            if jpholiday.is_holiday(checkday + relativedelta(days=3)):
                renkyu = 3
            else :
                renkyu = 2
        # 1ヶ月後の日付が木曜日 and 翌日が祝日
        elif (checkday.weekday() == 3) and (jpholiday.is_holiday(checkday + relativedelta(days=1))) :
            renkyu = 3
        else :
            renkyu = 0
        
        # 休前日であればメール通知
        if renkyu >= 2 :
            request_url = 'https://api.line.me/v2/bot/message/narrowcast'
            headers = {'Authorization': 'Bearer ' + os.environ['API_KEY'], 'content-type': 'application/json'}

            data = {
                "messages": [
                    {
                        "type": "text",
                        "text": checkday.strftime('%Y年%m月%d日') + "の新幹線の予約開始日です。"
                    }
                ]
            }

            if renkyu == 3 :
                data = {
                    "messages": [
                        {
                            "type": "text",
                            "text": checkday.strftime('%Y年%m月%d日') + "の新幹線の予約開始日です。3連休のため混雑が予想されます。"
                        }
                    ]
                }
            
            try:
                request_post = request.Request(url=request_url, method="POST",headers=headers,data=json.dumps(data).encode())
                with request.urlopen(request_post) as res:
                    body = res.read().decode()
                return json.loads(body)

            except (urllib.error.HTTPError) as error:
                status_code = error.code
                print("エラーログなし %s\n URL: %s" %(status_code,request_url))
                return {
                    'statusCode': status_code
                }
            except (urllib.error.URLError) as error:
                status_code = "HTTP通信の不可"
                print(status_code)
                return {
                    'statusCode': status_code
                }

    return {
        'statusCode': 200,
        'body': json.dumps("hello")
    }
