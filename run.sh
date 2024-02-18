docker build -t my-python-app .
docker run -v $HOME/my-python-app/data:/app/db my-python-app