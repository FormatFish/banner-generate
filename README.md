# Banner generate
This project coded by python django and pil. It can generate a banner when you give the material , background, title , detail and so on. And this work is based on the paper "Learning layouts for single-pagegraphic designs" 

Banner generate have two parts , the first is generating the banner which based on the template and the second is optiming , which based on the paper' method -- feature calculating and Simulated annealing algorithm. Also I implement the algorithm NIO(Non-linear Inverse Optimization), however , this algorithm have no obviously effect , so I just implement it in `alibanner/alibanner/views.py` and never use it.

[demo](http://123.56.90.153:8002)
![demo](https://ww1.sinaimg.cn/large/006y8lVajw1fcmkooub6gg31a10sqb2a.gif)

# Install
1. `pip install -r requirements.txt`
2. If you don't care the security or you just run it for your curiosity , you can run `python manage.py runserver 0.0.0.0:8000` . Or you should deploy it as the [offical document](https://docs.djangoproject.com/en/1.10/howto/deployment/)

