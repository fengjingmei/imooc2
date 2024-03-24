import requests
import json

def send_single_sms(apikey, code, mobile):
    #发送单条短信
    url = "https://sms.yunpian.com/v2/sms/single_send.json"
    text = "【imooc】您的验证码是{}。如非本人操作，请忽略本短信".format(code)

    res = requests.post(url, data={
        "apikey": apikey,   #用户唯一标识，在管理控制台获取
        "mobile": mobile,   #接受的手机号
        "text": text
    })
    re_json = json.loads(res.text)
    return re_json


if __name__ == "__main__":
    res = send_single_sms("d6c4ddbf50ab36611d2f52041a0b949e","123456","17838536721")
    res_json = json.loads(res.text)
    code = res_json["code"]
    msg = res_json["msg"]    # msg text类型  发送成功或相应错误信息
    if code == 0:     #表示发送成功，code！=0 表示发送失败
        print("发送成功")
    else:
        print("发送失败: {}".format(msg))
    print(res.text)