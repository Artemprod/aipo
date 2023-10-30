FROM python:3.11

COPY . .


RUN apt-get update -y
RUN apt-get upgrade -y
RUN pip install --upgrade pip
RUN pip install --upgrade setuptools
RUN pip install -r requirements.txt
RUN apt-get install -y ffmpeg
ENV PYTHONPATH $PYTHONPATH:.


#Вот здесь создание скрипта для запуска нескольких файлов 1 раз при создании к
#RUN echo '#!/bin/bash' > run_multiple_scripts.sh && \
#    echo 'python3 /chat_bot/bot.py' >> run_multiple_scripts.sh && \
#    echo 'python3 /reporter/__main__.py' >> run_multiple_scripts.sh && \
#    chmod +x run_multiple_scripts.sh  # Делаем скрипт исполняемым
#
##вот сюда запуск срипта
#CMD ["./run_multiple_scripts.sh"]

CMD ["python3", "/chat_bot/bot.py"]