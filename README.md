# Docker Setup
- docker build -t  backend -f Dockerfile.backend .
- docker build -t  frontend -f Dockerfile.frontend .

- docker run -it --net=host --env-file ~/WORKSPACE/setup/backend_config.dat --name=chatpdf_backend backend
- docker run -it --net=host --env-file ~/WORKSPACE/setup/frontend_config.dat --name=chatpdf_frontend frontend
- docker run -it --net=host --env-file ~/WORKSPACE/setup/db_config.dat --name=chatpdf_db mysql

- sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /home/vinay/WORKSPACE/setup/chatpdf.key -out /home/vinay/WORKSPACE/setup/chatpdf.crt
- docker run --name nginx_server --net=host \
-v /home/vinay/WORKSPACE/setup/nginx.conf:/etc/nginx/nginx.conf:ro \
-v /home/vinay/WORKSPACE/setup/chatpdf.crt:/etc/ssl/private/chatpdf.crt:ro \
-v /home/vinay/WORKSPACE/setup/chatpdf.key:/etc/ssl/private/chatpdf.key:ro \
-d nginx
