export FLASK_APP=../aumai
export FLASK_ENV=development
export FLASK_PORT=5001
flask run --host=0.0.0.0


curl 0.0.0.0:5000/api/v2/initDB/aumai
curl 0.0.0.0:5000/api/v2/load/societa
curl 0.0.0.0:5000/api/v2/load/negozi
curl 0.0.0.0:5000/api/v2/load/fornitori