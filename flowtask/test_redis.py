# test_redis.py
from decouple import config
import redis

print(" Probando conexión a Redis...")

try:
    redis_url = config('REDIS_URL')
    print(f" URL: {redis_url[:60]}...")
    
    # Conexión normal SIN SSL (para Redis local)
    r = redis.from_url(redis_url)
    
    # Probar conexión
    r.ping()
    print(" ¡Conexión exitosa a Redis!")
    
    # Probar escritura/lectura
    r.set('test', 'FlowTask funciona!')
    valor = r.get('test')
    print(f" Prueba de escritura/lectura: {valor}")
    
except Exception as e:
    print(f" Error: {e}")