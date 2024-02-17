docker build -t my-python-app .
docker run -v $HOME/my-python-app/data:/app/db -p 80:80 my-python-app