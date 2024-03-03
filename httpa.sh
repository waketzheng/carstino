# Usage(httpie is required)::
#   $ export token=xxx.xxx.xxx
#   $ httpa :8000/login-required-api
AUTH_HEAD="${AUTH_HEAD:-Authorization: Bearer}"
http $* "$AUTH_HEAD $token"
