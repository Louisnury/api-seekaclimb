import secrets
import base64

# Générer une clé secrète de 32 bytes (256 bits)
secret_key = secrets.token_bytes(32)
# Convertir en string base64 pour faciliter le stockage
secret_key_str = base64.b64encode(secret_key).decode('utf-8')

print("Votre nouvelle clé secrète JWT :")
print(secret_key_str)
print("\nAjoutez cette clé dans votre fichier .env comme ceci :")
print("JWT_SECRET_KEY=" + secret_key_str)
