# README

## 安裝環境

打開終端機 輸入以下指令

```shell
# 安裝 Docker
brew cask install docker
docker run --name postgres -e POSTGRES_USER=sherry -e POSTGRES_PASSWORD=sherry -d -p 5432:5432 postgres

# 安裝 pyenv 以及 python 3.6.4
brew install pyenv
pyenv init
pyenv install 3.6.4
pyenv shell 3.6.4

# 從Github 下載程式碼
cd ~/Desktop
git clone https://github.com/sherry0306/payment-report


# 安裝 python google api 套件
pip install -r requirements.txt

# 執行程式
python download.py

```

