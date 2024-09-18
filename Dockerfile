#Python runtime as a parent image
FROM python:3.9.6

#Setting working directory
WORKDIR /app

#Copy contents of the current directory to the container's app directory
COPY . /app

#Upgrade pip
RUN pip install --no-cache-dir --upgrade pip

#Install sip first
RUN pip install --no-cache-dir sip

#Installing dependencies
RUN pip install --no-cache-dir -r requirements.txt

#Make the port available outside the container
EXPOSE 3000

#Specify the command to run on container start
CMD ["python", "main.py"]


