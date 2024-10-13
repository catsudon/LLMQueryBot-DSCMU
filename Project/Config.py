import requests
import json


channel_access_token = '2BjMeO3RjnkMtDz47l+sqD5CKWZz0UxnWCD6QqHWo/CxscodtEws1B41nBfMRwyY6gYNFOi4G90RX8ZVlZprjRPny+V/6kKcwGTgqeQI6Ebrva+kKaKmDOD8CPLZsSYxEW4zsAjwJP3mn1z8MTNM8QdB04t89/1O/w1cDnyilFU='
yapper = '/UoTcFJqOYtXefsTg8x+UlB7VbSu7YSrGdz1Y7aRbWf+6AGeaGZZxe23KiKxclAtf8vkNty61Sri0lPYmr2scNNE1zU9Ji7bF25bqlSS30AStUoG0ABK0Cok/O7Be9LPnZk/PlB/BGtmb78Ewmt6/wdB04t89/1O/w1cDnyilFU='

channel_access_token = yapper

notify_url = 'https://notify-api.line.me/api/notify'
notify_token = 'dTHASUKdvjXK4PojkfsjVjEasZrvkvCMYtmvpgpJmuE'
notify_headers = {'content-type':'application/x-www-form-urlencoded','Authorization':'Bearer '+notify_token}


def log(code, title):
    requests.post(notify_url, headers=notify_headers, data = {'message': str(code) + " : " + title + "\n      https://nhentai.net/g/"+str(code)})