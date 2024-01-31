# Usage(httpie is required)::
#   $ export token=xxx.xxx.xxx
#   $ httpa :8000/login-required-api
http $* "Authorization: Bearer $token"
