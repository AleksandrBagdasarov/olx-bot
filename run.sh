docker build -t my-python-app .
docker run -v $HOME/my-python-app/data:/app -p 80:80 my-python-app