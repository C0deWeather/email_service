# --- Standard Python Libraries ---
# (Imports are the same)
import asyncio
import json
import logging
from contextlib import asynccontextmanager

# --- Third-Party Libraries ---
import aio_pika
from fastapi import FastAPI
from pydantic import ValidationError

# --- Local Application Imports ---
from .config import settings
from .logging_config import setup_logging
from .schemas import NotificationRequest, StatusUpdateRequest, NotificationStatus

# --- Global State ---
RABBITMQ_CONNECTION = None
log = logging.getLogger(__name__)

# --- Business Logic Function (Stubbed) ---
# (process_email_request stays the same for now)
async def process_email_request(request: NotificationRequest):
    # ... (all your existing logic) ...
    pass

# --- RabbitMQ Message Handler (UPDATED) ---
async def on_message(message: aio_pika.IncomingMessage):
    """
    This function is the entry point. It handles parsing
    and then delegates the work to 'process_email_request'.
    """
    request_id = "unknown"
    
    async with message.process():
        try:
            body = message.body.decode()
            data = json.loads(body)
            
            # 1. Parse and validate the message
            request = NotificationRequest(**data)
            request_id = request.request_id
            
            log.info(
                "Received new message", 
                extra={"request_id": request_id, "user_id": request.user_id}
            )
            
            # 2. Delegate to the business logic function
            await process_email_request(request)
            
            log.info(
                "Successfully processed message", 
                extra={"request_id": request_id}
            )

        except (ValidationError, json.JSONDecodeError) as e:
            # --- THIS IS THE UPDATED DLQ LOGIC ---
            log.warning(
                "Validation Error, moving to failed.queue", 
                extra={"error": str(e), "body": body}
            )
            
            # Get the channel from our app state
            channel = app.state.amqp_channel
            if channel:
                # Publish the original, raw message body to the failed queue
                await channel.default_exchange.publish(
                    aio_pika.Message(body=message.body),
                    routing_key="failed.queue" # Publish directly to the queue
                )
            
            # The 'message.process()' context will 'ack' the message
            # here, removing it from email.queue
            
        except Exception as e:
            # This is for failures in 'process_email_request'
            log.error(
                "Processing failed, message will be 'nacked'", 
                extra={"request_id": request_id, "error": str(e)}
            )
            # We re-raise the exception so 'message.process()' nacks it
            raise

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages the application's startup and shutdown logic.
    """
    global RABBITMQ_CONNECTION
    
    # --- Startup Logic ---
    setup_logging()
    log.info("FastAPI app is starting up...")
    
    try:
        # 1. Connect to RabbitMQ
        RABBITMQ_CONNECTION = await aio_pika.connect_robust(
            f"amqp://{settings.RABBITMQ_USER}:{settings.RABBITMQ_PASS}@{settings.RABBITMQ_HOST}/"
        )
        log.info("Successfully connected to RabbitMQ.")

        # 2. Create a channel
        channel = await RABBITMQ_CONNECTION.channel()
        
        # --- Store channel on app.state for other functions to use ---
        app.state.amqp_channel = channel
        
        # 3. Declare the Exchange
        exchange_name = "notifications.direct"
        await channel.declare_exchange(
            exchange_f"Successfully declared exchange '{exchange_name}'.")

        # 4. Declare the Email Queue
        queue_name = "email.queue"
        email_queue = await channel.declare_queue(
            queue_name, durable=True
        )
        log.info(f"Successfully declared queue '{queue_name}'.")
        
        # 5. Bind the Email Queue
        routing_key = "email"
        await email_queue.bind(exchange_name, routing_key=routing_key)
        log.info(f"Successfully bound queue '{queue_name}' to '{exchange_name}'.")

        # --- 6. Declare the Failed Queue (for DLQ) ---
        failed_queue_name = "failed.queue"
        await channel.declare_queue(
            failed_queue_name, durable=True
        )
        log.info(f"Successfully declared queue '{failed_queue_name}'.")

        # --- 7. Start the consumer ---
        await email_queue.consume(on_message)
        log.info(f"Started consuming from '{queue_name}'.")

    except aio_pika.exceptions.AMQPConnectionError as e:
        log.critical("Failed to connect to RabbitMQ", extra={"error": str(e)})
    
    log.info("Startup complete.")
    
    # --- Let the app run ---
    yield
    
    # --- Shutdown Logic ---
    log.info("FastAPI app is shutting down...")
    app.state.amqp_channel = None
    if RABBITMQ_CONNECTION:
        await RABBITMQ_CONNECTION.close()
        log.info("Closed RabbitMQ connection.")
    log.info("Shutdown complete.")

# --- Create the FastAPI App ---
app = FastAPI(title="Email Notification Service", lifespan=lifespan)

# --- Health Check Endpoint ---
@app.get("/health", status_code=200)
def health_check():
    return {"status": "ok", "service": "email-service"}