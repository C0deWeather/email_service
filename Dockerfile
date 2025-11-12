# 1. Start with a pre-made box
FROM python:3.13-slim

# 2. Set the main folder inside the box
WORKDIR /app

# 3. Copy just the "shopping list"
COPY requirements.txt .

# 4. Install everything on the list
RUN pip install -r requirements.txt

# 5. Copy the rest of your code
COPY . .

# 6. Set the default "start" command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]