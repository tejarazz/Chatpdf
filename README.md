# Docker Setup
- docker build -t  backend -f Dockerfile.backend .
- docker build -t  frontend -f Dockerfile.frontend .

- docker run -it --net=host -e GOOGLE_API_KEY='<KEY>' --name=test backend
- docker run -it --net=host --name=web frontend
- docker run -it --net=host -e MYSQL_USER='<dev user name>' -e MYSQL_PASSWORD='<pwd>' -e MYSQL_DATABASE='PDFCHAT' -e MYSQL_ROOT_PASSWORD='<pwd_root>' mysql
