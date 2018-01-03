import redis
r = redis.Redis(host='10.0.0.200',port=6379,password='123456')
r.set('hello','world')
print(r.get('hello'))
