import redis

# Connexion à Redis
r = redis.Redis()

# Ajout des URLs dans un set
r.sadd('urls', 'http://example1.com')
r.sadd('urls', 'http://example2.com')
r.sadd('urls', 'http://example1.com')  # Ceci ne sera pas ajouté, car il est déjà présent.
