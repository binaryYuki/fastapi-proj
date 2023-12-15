# # import json
# #
# # content = str({
# #     "server_status": "ok",
# #     "history": "ok",
# #     "server_timezone": "Asia/Shanghai",
# # })
# # print(json.dumps(content))
# #
# # import redis
# #
# # r = redis.from_url("redis://default:5kuU79ZtVhVlgTw96UJ8Cu2stnoY4SVy@redis-10721.c251.east-us-mz.azure.cloud.redislabs.com:10721", encoding="utf-8", decode_responses=True)
# #
# # r.set('foo', 'bar')
# # print(r.get('foo'))
# #
# #
# import uuid
#
# # print(uuid.UUID("6e9ceb42-72f5-41ec-8cca-1f97e76a9ff2").version == 4)
# # def check_user_id(v):
# #     try:
# #         return uuid.UUID(str(v)).version == 4
# #     except ValueError:
# #         raise ValueError("Invalid UUID")
# #
# # print(check_user_id("6e9ceb42-72f5-41ec-8cca-1f97e76a9ff2"))
# import json
# from datetime import datetime
#
# from tzlocal import get_localzone_name
#
#
# def serialize_json(json_obj):
#     if isinstance(json_obj, dict):
#         serialized_obj = {}
#         for key, value in json_obj.items():
#             serialized_obj[key] = serialize_json(value)
#         return serialized_obj
#     elif isinstance(json_obj, list):
#         serialized_obj = []
#         for item in json_obj:
#             serialized_obj.append(serialize_json(item))
#         return serialized_obj
#     elif isinstance(json_obj, str):
#         return json_obj
#     else:
#         return str(json_obj)
#
#
# # 示例多层嵌套的JSON对象
# json_data = {
#     "request_id": "be46372734574326",
#     "code": 200,
#     "status": "ok",
#     "data": {
#         "server_status": "ok",
#         "server_timezone": get_localzone_name(),
#         "server_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#         "version": "0.0.1"
#     }
# }
#
# # 序列化JSON对象
# serialized_data = serialize_json(json_data)
#
# # 打印序列化后的JSON字符串
# print(json.dumps(serialized_data, indent=4))
