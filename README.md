Приложение запускает веб сервер который преобразует RTSP поток с камеры подключенной к роботу в  MJPEG поток и позволяет вывести его на веб страницу. Так же на странице отображается карта и элементы позволяющие управлять роботом.

# Установка

```
git clone https://github.com/guinmoon/Roborock-Project-Vacumba  
cd Roborock-Project-Vacumba  
pip install -r requirements.txt
```

# Запуск

```python3 vacumba_web_light.py```

# Подключение камеры
У роботов 1 поколения есть диагностический USB порт на который подается напряжение достаточное для питания камеры, на других поколениях не проверял  
![Roborock with IP Camera](/templates/dist/imgs/robot1.jpg)
![Roborock IP Camera conncet](/templates/dist/imgs/robot2.jpg)

