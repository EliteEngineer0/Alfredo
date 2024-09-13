# Use the official Python image.
FROM python:3.9.20-alpine3.20

# Set the working directory inside the container.
WORKDIR /app

# Copy the requirements file to the working directory.
COPY requirements.txt .

# Install dependencies.
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your bot's code to the container.
COPY . .

# Command to run your bot (replace bot.py with your entry point).
CMD ["python", "bot.py"]
