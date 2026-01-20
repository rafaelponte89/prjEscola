@echo off
setlocal

echo ===== Atualizando código do Git =====
git fetch origin
git reset --hard origin/main

echo ===== Rebuild da imagem Django =====
docker-compose build django

echo ===== Parando containers =====
docker-compose stop

echo ===== Subindo containers atualizados =====
docker-compose up -d


echo ===== Aplicando migrations no default =====
docker-compose exec django python manage.py migrate --database="default"

echo ===== Aplicando migrations no outro banco =====
docker-compose exec django python manage.py migrate --database="colaboradores"

echo ===== Coletando arquivos estáticos =====
docker-compose exec django python manage.py collectstatic --noinput

echo ===== Reiniciando Nginx =====
docker-compose restart nginx

echo ===== Atualização completa =====
pause
