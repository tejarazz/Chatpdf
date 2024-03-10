# Docker Setup
- docker build -t  backend -f Dockerfile.backend .
- docker build -t  frontend -f Dockerfile.frontend .

- docker run -it --net=host -e GOOGLE_API_KEY='<KEY>' --name=test backend
- docker run -it --net=host --name=web frontend
- docker run -it --net=host -e MYSQL_USER='<dev user name>' -e MYSQL_PASSWORD='<pwd>' -e MYSQL_DATABASE='PDFCHAT' -e MYSQL_ROOT_PASSWORD='<pwd_root>' mysql

- sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /home/vinay/WORKSPACE/setup/chatpdf.key -out /home/vinay/WORKSPACE/setup/chatpdf.crt
- docker run --name nginx_server --net=host \
-v /home/vinay/WORKSPACE/setup/nginx.conf:/etc/nginx/nginx.conf:ro \
-v /home/vinay/WORKSPACE/setup/chatpdf.crt:/etc/ssl/private/chatpdf.crt:ro \
-v /home/vinay/WORKSPACE/setup/chatpdf.key:/etc/ssl/private/chatpdf.key:ro \
-d nginx
