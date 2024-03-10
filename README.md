# Docker Setup
1. ```docker build -t  backend -f Dockerfile.backend .```
1. ```docker build -t  frontend -f Dockerfile.frontend .```

1. ```docker run -it --net=host --env-file ~/WORKSPACE/setup/db_config.dat --name=chatpdf_db mysql```
1. ```docker run -it --net=host --env-file ~/WORKSPACE/setup/backend_config.dat --name=chatpdf_backend backend```
1. ```docker run -it --net=host --env-file ~/WORKSPACE/setup/frontend_config.dat --name=chatpdf_frontend frontend```


1. ```sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /home/vinay/WORKSPACE/setup/chatpdf.key -out /home/vinay/WORKSPACE/setup/chatpdf.crt```
1. ```docker run --name nginx_server --net=host -v /home/vinay/WORKSPACE/setup/nginx.conf:/etc/nginx/nginx.conf:ro -v /home/vinay/WORKSPACE/setup/chatpdf.crt:/etc/ssl/private/chatpdf.crt:ro -v /home/vinay/WORKSPACE/setup/chatpdf.key:/etc/ssl/private/chatpdf.key:ro -d nginx```
