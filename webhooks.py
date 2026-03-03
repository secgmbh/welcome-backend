"""
Welcome Link Webhook System
Supports: Stripe, PayPal, and custom webhooks
"""

from fastapi import APIRouter, Request, HTTPException, Header
from pydantic import BaseModel
from typing import Optional, Dict, Any
import hashlib
import hmac
import json
from datetime import datetime

router = APIRouter(prefix="/webhooks", tags=["webhooks"])

# Webhook event types
class WebhookEvent(BaseModel):
    event_type: str
    timestamp: datetime
    data: Dict[str, Any]
    signature: Optional[str] = None


# Stripe Webhook Handler
@router.post("/stripe")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None, alias="Stripe-Signature")
):
    """
    Handle Stripe webhook events
    Events: checkout.session.completed, payment_intent.succeeded, etc.
    """
    payload = await request.body()
    
    # Verify signature (in production)
    # stripe.Webhook.construct_event(payload, stripe_signature, webhook_secret)
    
    try:
        event = json.loads(payload)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")
    
    event_type = event.get("type")
    event_data = event.get("data", {}).get("object", {})
    
    # Handle different event types
    if event_type == "checkout.session.completed":
        await handle_stripe_checkout_completed(event_data)
    elif event_type == "payment_intent.succeeded":
        await handle_stripe_payment_succeeded(event_data)
    elif event_type == "payment_intent.payment_failed":
        await handle_stripe_payment_failed(event_data)
    else:
        print(f"Unhandled Stripe event: {event_type}")
    
    return {"status": "received"}


async def handle_stripe_checkout_completed(session: dict):
    """Handle completed Stripe checkout session"""
    checkout_id = session.get("metadata", {}).get("checkout_id")
    payment_intent = session.get("payment_intent")
    
    # Update checkout status
    # await update_checkout_status(checkout_id, "paid", payment_intent)
    print(f"Stripe checkout completed: {checkout_id}")


async def handle_stripe_payment_succeeded(payment_intent: dict):
    """Handle successful payment"""
    print(f"Stripe payment succeeded: {payment_intent.get('id')}")


async def handle_stripe_payment_failed(payment_intent: dict):
    """Handle failed payment"""
    print(f"Stripe payment failed: {payment_intent.get('id')}")


# PayPal Webhook Handler
@router.post("/paypal")
async def paypal_webhook(request: Request):
    """
    Handle PayPal webhook events
    Events: CHECKOUT.ORDER.APPROVED, PAYMENT.CAPTURE.COMPLETED, etc.
    """
    try:
        event = await request.json()
    except:
        raise HTTPException(status_code=400, detail="Invalid JSON")
    
    event_type = event.get("event_type")
    resource = event.get("resource", {})
    
    # Handle different event types
    if event_type == "CHECKOUT.ORDER.APPROVED":
        await handle_paypal_order_approved(resource)
    elif event_type == "PAYMENT.CAPTURE.COMPLETED":
        await handle_paypal_capture_completed(resource)
    elif event_type == "PAYMENT.CAPTURE.DENIED":
        await handle_paypal_capture_denied(resource)
    else:
        print(f"Unhandled PayPal event: {event_type}")
    
    return {"status": "received"}


async def handle_paypal_order_approved(order: dict):
    """Handle approved PayPal order"""
    order_id = order.get("id")
    print(f"PayPal order approved: {order_id}")


async def handle_paypal_capture_completed(capture: dict):
    """Handle completed PayPal capture"""
    print(f"PayPal capture completed: {capture.get('id')}")


async def handle_paypal_capture_denied(capture: dict):
    """Handle denied PayPal capture"""
    print(f"PayPal capture denied: {capture.get('id')}")


# Custom Webhooks for Partners
@router.post("/partners/{partner_id}")
async def partner_webhook(
    partner_id: str,
    request: Request,
    signature: str = Header(None)
):
    """
    Handle partner webhooks
    Partners can register webhooks for events like:
    - booking.created
    - booking.cancelled
    - payment.received
    """
    payload = await request.body()
    
    # Verify signature
    # if not verify_partner_signature(partner_id, payload, signature):
    #     raise HTTPException(status_code=401, detail="Invalid signature")
    
    try:
        data = await request.json()
    except:
        raise HTTPException(status_code=400, detail="Invalid JSON")
    
    event_type = data.get("event_type")
    
    # Process webhook
    print(f"Partner {partner_id} webhook: {event_type}")
    
    return {"status": "received", "partner_id": partner_id}


# Webhook retry logic
async def send_webhook(url: str, event: dict, secret: str, max_retries: int = 3):
    """Send webhook with retry logic"""
    import httpx
    
    payload = json.dumps(event)
    signature = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    
    headers = {
        "Content-Type": "application/json",
        "X-Webhook-Signature": signature,
        "X-Webhook-Timestamp": datetime.utcnow().isoformat(),
    }
    
    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    content=payload,
                    headers=headers,
                    timeout=30.0
                )
                
                if response.status_code >= 200 and response.status_code < 300:
                    return True
                
                print(f"Webhook failed: {response.status_code}")
        except Exception as e:
            print(f"Webhook error (attempt {attempt + 1}): {e}")
        
        # Exponential backoff
        if attempt < max_retries - 1:
            await asyncio.sleep(2 ** attempt)
    
    return False


# Webhook logging
@router.get("/logs")
async def get_webhook_logs(limit: int = 50):
    """Get recent webhook logs (admin only)"""
    # In production, fetch from database
    return {
        "logs": [
            {
                "id": "1",
                "type": "stripe",
                "event": "checkout.session.completed",
                "status": "success",
                "timestamp": datetime.utcnow().isoformat(),
            }
        ]
    }