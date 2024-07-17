import requests
import time
import base64
import hmac
from hashlib import sha1
import pymysql
from requests_toolbelt.multipart.encoder import MultipartEncoder

config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',  # 修改为你的数据库密码
    'database': 'douban',
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_unicode_ci',
    'cursorclass': pymysql.cursors.DictCursor
}

def hash_hmac(code):
    key = "bf7dddc7c9cfe6f7"
    hmac_code = hmac.new(key.encode(), code.encode(), sha1).digest()
    return base64.b64encode(hmac_code).decode()

def join(cookie):
    t = time.time()
    token = cookie
    udid = "811829c2cb430ef800c8153d4ac248bb3f5a196d"
    req_url = f"POST&%2Fapi%2Fv2%2Fgroup%2F743282%2Fjoin&{token}&{format(int(t))}"
    print(req_url)
    sign = hash_hmac(req_url)
    print(sign)
    headers = {
        'Authorization': f'Bearer {token}',
        'User-Agent': f'api-client/1 com.douban.frodo/7.18.0(230) Android/28 product/M973Q vendor/Meizu model/M973Q brand/Meizu  rom/flyme4  network/wifi  udid/{udid}  platform/AndroidPad',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Host': 'frodo.douban.com',
        'Connection': 'Keep-Alive',
    }
    data = {
        'type': 'join',
        'apikey': '0dad551ec0f84ed02907ff5c42e8ec70',
        'channel': 'Yingyongbao_Market',
        'udid': udid,
        'os_rom': 'flyme4',
        '_sig': sign,
        '_ts': int(t),
    }
    response = requests.post('https://frodo.douban.com/api/v2/group/743282/join?timezone=Asia%2FShanghai', headers=headers, data=data)
    data = response.json()
    print(data)
    if 'code' in data:
        if data['code'] == 4011:
            print("无法加入该小组，(可能是已经加入过了)错误消息：", data.get('localized_message', '无详细错误信息'))
            return False
        else:
            print("遇到未知错误，错误代码：", data['code'])
            return False
    else:
        print("成功加入小组：", data.get('name', '未知小组名'))
        return True

def send_comment(cookie, text):
    t = time.time()
    token = cookie
    udid = "811829c2cb430ef800c8153d4ac248bb3f5a196d"
    req_url = f"POST&%2Fapi%2Fv2%2Fgroup%2Ftopic%2F307140986%2Fcreate_comment&{token}&{format(int(t))}"
    print(req_url)
    sign = hash_hmac(req_url)
    print(sign)
    url = "https://frodo.douban.com/api/v2/group/topic/307140986/create_comment?timezone=Asia%2FShanghai"
    user_agent = f"api-client/1 com.douban.frodo/7.18.0(230) Android/28 product/M973Q vendor/Meizu model/M973Q brand/Meizu  rom/flyme4 network/wifi udid/{udid} platform/AndroidPad"
    multipart_data = MultipartEncoder(
        fields={
            'nested': ('nofilename', '1', 'application/x-www-form-urlencoded'),
            'text': text,
            'apikey': '0dad551ec0f84ed02907ff5c42e8ec70',
            'channel': 'Yingyongbao_Market',
            'udid': udid,
            'os_rom': 'flyme4',
            '_sig': sign,
            '_ts': str(int(t))
        },
        boundary='eada003a-631c-4930-816d-573df69e386a'
    )
    headers = {
        "Authorization": f"Bearer {token}",
        "User-Agent": user_agent,
        "Content-Type": multipart_data.content_type
    }
    response = requests.post(url, headers=headers, data=multipart_data)
    try:
        data = response.json()
        print(data)
        if data.get("is_deleted") == False and data.get("is_disabled") == False:
            print("发送成功！")
        else:
            print("发送失败或数据有误。")
    except ValueError:
        print("响应内容不是有效的 JSON 格式。")
    except Exception as e:
        print(f"发生错误：{e}")

def main():
    # 创建连接
    connection = pymysql.connect(**config)
    
    users = []
    try:
        with connection.cursor() as cursor:
            # 执行SQL查询
            sql = "SELECT douban_user_name, ck FROM user"
            cursor.execute(sql)
            
            # 获取所有记录
            results = cursor.fetchall()
            
            for index, row in enumerate(results):
                print(f"{index + 1}. Username: {row['douban_user_name']}")
                users.append(row)
    finally:
        # 关闭连接
        connection.close()

    print("请选择以下选项之一：")
    print("1. 全部加入讨论")
    print("2. 全部单独讨论")
    print("3. 加入讨论")
    print("4. 单独讨论")
    
    choice = input("请输入选项数字 (1-4): ")
    
    if choice == '1':
        for user in users:
            join(user["ck"])
    elif choice == '2':
        text = input("请输入要发送的评论: ")
        for user in users:
            send_comment(user["ck"], text)
    elif choice in ['3', '4']:
        user_choice = int(input("请选择一个用户 (输入序号): ")) - 1
        
        if user_choice < 0 or user_choice >= len(users):
            print("无效选择")
            return
        
        selected_user = users[user_choice]
        selected_cookie = selected_user["ck"]
        
        if choice == '3':
            join(selected_cookie)
        elif choice == '4':
            text = input("请输入要发送的评论: ")
            send_comment(selected_cookie, text)
    else:
        print("输入错误，请输入 1-4 的数字。")

if __name__ == "__main__":
    main()
