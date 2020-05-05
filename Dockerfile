FROM gorialis/discord.py:3.8.1-slim-buster-master-minimal

WORKDIR /app

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "temp.py"]
