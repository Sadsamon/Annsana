from .base import *  # noqa: F401,F403
import environ

env = environ.Env()
environ.Env.read_env(str(BASE_DIR / ".env"))

SECRET_KEY = env("SECRET_KEY")
DEBUG = False
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])

DATABASES = {"default": env.db("DATABASE_URL")}

STORAGES = {
	"default": {
		"BACKEND": "django.core.files.storage.FileSystemStorage",
	},
	"staticfiles": {
		"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
	},
}

if env("AWS_STORAGE_BUCKET_NAME", default=""):
	STORAGES["default"] = {
		"BACKEND": "storages.backends.s3.S3Storage",
		"OPTIONS": {
			"access_key": env("AWS_ACCESS_KEY_ID"),
			"secret_key": env("AWS_SECRET_ACCESS_KEY"),
			"bucket_name": env("AWS_STORAGE_BUCKET_NAME"),
			"endpoint_url": env("AWS_S3_ENDPOINT_URL"),
			"region_name": env("AWS_S3_REGION_NAME", default="auto"),
			"default_acl": None,
			"file_overwrite": False,
			"signature_version": "s3v4",
		},
	}
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
X_FRAME_OPTIONS = "DENY"
SECURE_CROSS_ORIGIN_OPENER_POLICY = "same-origin"
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])
