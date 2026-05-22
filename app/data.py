import json

BUSINESS_DATA = {
    "company": {
        "name": "SwiftMove Logistics",
        "region": "Ireland & EU",
        "support_hours": "Monday to Friday, 9:00 AM – 5:30 PM IST",
        "support_email": "support@swiftmove.ie",
        "support_phone": "+353 1 800 9000",
        "website": "www.swiftmove.ie",
        "social": {
            "twitter": "@SwiftMoveIE",
            "facebook": "facebook.com/swiftmoveie",
        },
    },
    "orders": [
        {
            "order_id": "ORD-20489",
            "customer_name": "Liam O'Brien",
            "email": "liam.obrien@email.ie",
            "phone": "+353 87 123 4567",
            "status": "In Transit",
            "placed_on": "2026-05-15",
            "estimated_delivery": "2026-05-21",
            "last_location": "Dublin Distribution Centre, Ireland",
            "carrier": "SwiftMove Express",
            "tracking_events": [
                {"timestamp": "2026-05-15 10:22", "event": "Order placed and confirmed"},
                {"timestamp": "2026-05-15 14:05", "event": "Payment verified"},
                {"timestamp": "2026-05-16 08:30", "event": "Order picked and packed at Dublin Warehouse"},
                {"timestamp": "2026-05-17 11:00", "event": "Dispatched from Dublin Warehouse"},
                {"timestamp": "2026-05-18 09:45", "event": "Arrived at Dublin Distribution Centre"},
            ],
            "items": [
                {"name": "Wireless Headphones", "qty": 1, "sku": "SKU-WH-001", "unit_price_eur": 79.99},
                {"name": "Phone Case", "qty": 2, "sku": "SKU-PC-042", "unit_price_eur": 12.99},
            ],
            "order_total_eur": 105.97,
            "payment_method": "Credit Card",
            "payment_status": "Paid",
            "address_change_eligible": True,
            "delivery_address": {
                "line1": "14 Maple Avenue",
                "city": "Dublin",
                "county": "Dublin",
                "eircode": "D04 XY12",
                "country": "Ireland",
            },
            "notes": "Parcel is at distribution centre, final dispatch pending",
        },
        {
            "order_id": "ORD-19834",
            "customer_name": "Aoife Murphy",
            "email": "aoife.murphy@email.ie",
            "phone": "+353 85 987 6543",
            "status": "Delivered",
            "placed_on": "2026-05-10",
            "delivered_on": "2026-05-16",
            "last_location": "Cork, Ireland",
            "carrier": "SwiftMove Standard",
            "tracking_events": [
                {"timestamp": "2026-05-10 09:10", "event": "Order placed and confirmed"},
                {"timestamp": "2026-05-10 11:30", "event": "Payment verified"},
                {"timestamp": "2026-05-11 08:00", "event": "Order picked and packed at Cork Warehouse"},
                {"timestamp": "2026-05-12 10:15", "event": "Dispatched from Cork Warehouse"},
                {"timestamp": "2026-05-14 14:00", "event": "Arrived at Cork Distribution Centre"},
                {"timestamp": "2026-05-16 11:20", "event": "Out for delivery"},
                {"timestamp": "2026-05-16 14:35", "event": "Delivered and signed for by A. Murphy"},
            ],
            "items": [{"name": "Yoga Mat", "qty": 1, "sku": "SKU-YM-007", "unit_price_eur": 34.99}],
            "order_total_eur": 34.99,
            "payment_method": "PayPal",
            "payment_status": "Paid",
            "address_change_eligible": False,
            "delivery_address": {
                "line1": "7 River Walk",
                "city": "Cork",
                "county": "Cork",
                "eircode": "T12 AB34",
                "country": "Ireland",
            },
            "notes": "Delivered and signed for",
        },
        {
            "order_id": "ORD-21100",
            "customer_name": "Sean Gallagher",
            "email": "sean.gallagher@email.ie",
            "phone": "+353 86 555 7890",
            "status": "Processing",
            "placed_on": "2026-05-18",
            "estimated_delivery": "2026-05-24",
            "last_location": "Warehouse — Dublin",
            "carrier": "SwiftMove Express",
            "tracking_events": [
                {"timestamp": "2026-05-18 08:45", "event": "Order placed and confirmed"},
                {"timestamp": "2026-05-18 09:00", "event": "Payment verified"},
                {"timestamp": "2026-05-19 07:30", "event": "Order being picked and packed at Dublin Warehouse"},
            ],
            "items": [
                {"name": "Standing Desk", "qty": 1, "sku": "SKU-SD-019", "unit_price_eur": 299.0},
                {"name": "Monitor Arm", "qty": 1, "sku": "SKU-MA-003", "unit_price_eur": 49.99},
            ],
            "order_total_eur": 348.99,
            "payment_method": "Debit Card",
            "payment_status": "Paid",
            "address_change_eligible": True,
            "delivery_address": {
                "line1": "22 Oak Street",
                "city": "Galway",
                "county": "Galway",
                "eircode": "H91 CD56",
                "country": "Ireland",
            },
            "notes": "Order is being picked and packed, large item — requires signature on delivery",
        },
        {
            "order_id": "ORD-21345",
            "customer_name": "Niamh Kelly",
            "email": "niamh.kelly@email.ie",
            "phone": "+353 83 444 2211",
            "status": "Out for Delivery",
            "placed_on": "2026-05-14",
            "estimated_delivery": "2026-05-19",
            "last_location": "Limerick Delivery Hub, Ireland",
            "carrier": "SwiftMove Express",
            "tracking_events": [
                {"timestamp": "2026-05-14 13:00", "event": "Order placed and confirmed"},
                {"timestamp": "2026-05-14 13:45", "event": "Payment verified"},
                {"timestamp": "2026-05-15 09:00", "event": "Order picked and packed at Limerick Warehouse"},
                {"timestamp": "2026-05-16 08:30", "event": "Dispatched from Limerick Warehouse"},
                {"timestamp": "2026-05-18 10:00", "event": "Arrived at Limerick Delivery Hub"},
                {"timestamp": "2026-05-19 07:50", "event": "Out for delivery with courier"},
            ],
            "items": [
                {"name": "Air Fryer", "qty": 1, "sku": "SKU-AF-033", "unit_price_eur": 89.99},
                {"name": "Kitchen Scale", "qty": 1, "sku": "SKU-KS-011", "unit_price_eur": 19.99},
            ],
            "order_total_eur": 109.98,
            "payment_method": "Credit Card",
            "payment_status": "Paid",
            "address_change_eligible": False,
            "delivery_address": {
                "line1": "5 Elm Court",
                "city": "Limerick",
                "county": "Limerick",
                "eircode": "V94 EF78",
                "country": "Ireland",
            },
            "notes": "Out for delivery today, customer should be available to receive",
        },
        {
            "order_id": "ORD-20901",
            "customer_name": "Ciarán Doyle",
            "email": "ciaran.doyle@email.ie",
            "phone": "+353 89 321 6540",
            "status": "Delayed",
            "placed_on": "2026-05-12",
            "original_estimated_delivery": "2026-05-17",
            "revised_estimated_delivery": "2026-05-22",
            "last_location": "Customs Clearance — Dublin Port, Ireland",
            "carrier": "SwiftMove International",
            "tracking_events": [
                {"timestamp": "2026-05-12 10:00", "event": "Order placed and confirmed"},
                {"timestamp": "2026-05-12 10:30", "event": "Payment verified"},
                {"timestamp": "2026-05-13 09:00", "event": "Order picked and packed at International Warehouse"},
                {"timestamp": "2026-05-14 12:00", "event": "Dispatched via international carrier"},
                {"timestamp": "2026-05-16 08:00", "event": "Arrived at Dublin Port"},
                {"timestamp": "2026-05-16 09:30", "event": "Held at customs for inspection"},
                {"timestamp": "2026-05-18 11:00", "event": "Customs clearance in progress — additional documentation requested"},
            ],
            "items": [{"name": "Electric Scooter", "qty": 1, "sku": "SKU-ES-005", "unit_price_eur": 499.0}],
            "order_total_eur": 499.0,
            "payment_method": "Bank Transfer",
            "payment_status": "Paid",
            "address_change_eligible": False,
            "delivery_address": {
                "line1": "88 Pine Road",
                "city": "Waterford",
                "county": "Waterford",
                "eircode": "X91 GH90",
                "country": "Ireland",
            },
            "notes": "Delayed due to customs documentation requirements at Dublin Port. Customer has been notified via email.",
        },
        {
            "order_id": "ORD-20755",
            "customer_name": "Fiona Brennan",
            "email": "fiona.brennan@email.ie",
            "phone": "+353 87 654 3210",
            "status": "Cancelled",
            "placed_on": "2026-05-13",
            "cancelled_on": "2026-05-14",
            "cancellation_reason": "Customer requested cancellation before dispatch",
            "carrier": "N/A",
            "tracking_events": [
                {"timestamp": "2026-05-13 15:00", "event": "Order placed and confirmed"},
                {"timestamp": "2026-05-13 15:20", "event": "Payment verified"},
                {"timestamp": "2026-05-14 09:10", "event": "Cancellation requested by customer"},
                {"timestamp": "2026-05-14 09:45", "event": "Order cancelled — refund initiated"},
            ],
            "items": [{"name": "Bluetooth Speaker", "qty": 1, "sku": "SKU-BS-022", "unit_price_eur": 59.99}],
            "order_total_eur": 59.99,
            "payment_method": "Credit Card",
            "payment_status": "Refunded",
            "refund_status": {
                "initiated_on": "2026-05-14",
                "expected_credit_by": "2026-05-21",
                "refund_amount_eur": 59.99,
                "refund_method: ": "Original payment method (Credit Card)",
            },
            "address_change_eligible": False,
            "delivery_address": {
                "line1": "3 Birch Lane",
                "city": "Kilkenny",
                "county": "Kilkenny",
                "eircode": "R95 JK21",
                "country": "Ireland",
            },
            "notes": "Order cancelled before dispatch, full refund processed",
        },
        {
            "order_id": "ORD-21500",
            "customer_name": "Patrick Walsh",
            "email": "patrick.walsh@email.ie",
            "phone": "+353 85 111 2233",
            "status": "Return In Progress",
            "placed_on": "2026-05-05",
            "delivered_on": "2026-05-10",
            "return_requested_on": "2026-05-13",
            "return_reason": "Item received was defective — screen cracked on arrival",
            "return_status": "Return shipment picked up, under inspection at warehouse",
            "last_location": "Dublin Returns Warehouse",
            "carrier": "SwiftMove Returns",
            "tracking_events": [
                {"timestamp": "2026-05-05 11:00", "event": "Order placed and confirmed"},
                {"timestamp": "2026-05-06 08:00", "event": "Order picked and packed at Dublin Warehouse"},
                {"timestamp": "2026-05-07 09:30", "event": "Dispatched from Dublin Warehouse"},
                {"timestamp": "2026-05-10 13:00", "event": "Delivered and signed for"},
                {"timestamp": "2026-05-13 10:00", "event": "Return requested — defective item reported"},
                {"timestamp": "2026-05-14 14:00", "event": "Return shipment collected from customer"},
                {"timestamp": "2026-05-16 09:00", "event": "Return received at Dublin Returns Warehouse"},
                {"timestamp": "2026-05-18 11:30", "event": "Item under inspection"},
            ],
            "items": [{"name": "Tablet 10-inch", "qty": 1, "sku": "SKU-TB-008", "unit_price_eur": 249.99}],
            "order_total_eur": 249.99,
            "payment_method": "Debit Card",
            "payment_status": "Paid",
            "refund_status": {
                "initiated_on": None,
                "expected_credit_by": "2026-05-26",
                "refund_amount_eur": 249.99,
                "refund_method": "Original payment method (Debit Card)",
                "notes": "Refund will be initiated upon successful inspection completion",
            },
            "address_change_eligible": False,
            "delivery_address": {
                "line1": "19 Willow Drive",
                "city": "Dublin",
                "county": "Dublin",
                "eircode": "D08 LM44",
                "country": "Ireland",
            },
            "notes": "Return under warehouse inspection, refund expected by 26 May 2026",
        },
        {
            "order_id": "ORD-21678",
            "customer_name": "Sinead Connor",
            "email": "sinead.connor@email.ie",
            "phone": "+353 86 778 9900",
            "status": "Failed Delivery",
            "placed_on": "2026-05-16",
            "estimated_delivery": "2026-05-19",
            "last_location": "Drogheda Delivery Hub, Ireland",
            "carrier": "SwiftMove Express",
            "tracking_events": [
                {"timestamp": "2026-05-16 10:00", "event": "Order placed and confirmed"},
                {"timestamp": "2026-05-16 10:30", "event": "Payment verified"},
                {"timestamp": "2026-05-17 08:00", "event": "Order picked and packed at Dublin Warehouse"},
                {"timestamp": "2026-05-18 09:00", "event": "Dispatched from Dublin Warehouse"},
                {"timestamp": "2026-05-19 08:30", "event": "Out for delivery"},
                {"timestamp": "2026-05-19 13:15", "event": "Delivery attempted — no one available at address"},
                {"timestamp": "2026-05-19 13:20", "event": "Delivery card left at address, parcel held at Drogheda Delivery Hub"},
            ],
            "items": [
                {"name": "Running Shoes", "qty": 1, "sku": "SKU-RS-044", "unit_price_eur": 119.99},
                {"name": "Sports Socks (3-pack)", "qty": 2, "sku": "SKU-SS-012", "unit_price_eur": 9.99},
            ],
            "order_total_eur": 139.97,
            "payment_method": "Credit Card",
            "payment_status": "Paid",
            "address_change_eligible": False,
            "redelivery_options": {
                "redelivery_available": True,
                "collection_available": True,
                "collection_address": "Drogheda Delivery Hub, Unit 4, Industrial Estate, Drogheda, Co. Louth",
                "parcel_held_until": "2026-05-26",
            },
            "delivery_address": {
                "line1": "10 Cedar Close",
                "city": "Drogheda",
                "county": "Louth",
                "eircode": "A92 NP67",
                "country": "Ireland",
            },
            "notes": "Delivery attempted, parcel held at hub. Customer can schedule redelivery or collect in person before 26 May 2026.",
        },
    ],
    "faqs": [
        {
            "question": "How do I track my order?",
            "answer": "You can track your order by providing your order ID to our Support Assistant. You will get a full status update including current location and estimated delivery date.",
        },
        {
            "question": "How long does delivery take?",
            "answer": "Standard delivery within Ireland takes 2–4 business days. EU deliveries take 5–8 business days depending on the destination country. Express delivery is available at checkout for 1–2 business days within Ireland.",
        },
        {
            "question": "Can I change my delivery address?",
            "answer": "Address changes are possible only if the order has not yet been dispatched for final delivery. Contact our support team immediately if you need to make a change. Once the order is out for delivery, address changes are no longer possible.",
        },
        {
            "question": "How do I return an item?",
            "answer": "Returns can be initiated within 14 days of delivery. The item must be unused and in its original packaging, unless it is defective. Contact support@swiftmove.ie to raise a return request and our team will arrange a collection.",
        },
        {
            "question": "How long does a refund take?",
            "answer": "Refunds are typically processed within 5–7 business days after the return has been inspected and approved. The refund will be credited to your original payment method.",
        },
        {
            "question": "What do I do if my order arrives damaged or defective?",
            "answer": "If your order arrives damaged or defective, please take clear photographs of the item and packaging, then contact support@swiftmove.ie within 48 hours of delivery. We will arrange a return collection and process a replacement or full refund.",
        },
        {
            "question": "What happens if I miss my delivery?",
            "answer": "If a delivery attempt is made and no one is available, our courier will leave a delivery card at your address. Your parcel will be held at the nearest delivery hub for up to 7 days. You can schedule a redelivery or collect the parcel in person. Contact our support team with your order ID to arrange this.",
        },
        {
            "question": "Can I cancel my order?",
            "answer": "Orders can be cancelled free of charge before they are dispatched. Once dispatched, cancellation is no longer possible and you would need to initiate a return after delivery. Contact support@swiftmove.ie as soon as possible to cancel.",
        },
        {
            "question": "Why is my order delayed?",
            "answer": "Delays can occur due to high volume periods, adverse weather, or customs clearance for international shipments. You will be notified by email if your order is delayed, and a revised delivery date will be provided.",
        },
        {
            "question": "Do you deliver outside Ireland?",
            "answer": "Yes, SwiftMove delivers to all EU member states. International delivery times are 5–8 business days. Additional customs duties or taxes may apply depending on the destination country, which are the responsibility of the recipient.",
        },
        {
            "question": "What payment methods are accepted?",
            "answer": "We accept Credit Card, Debit Card, PayPal, and Bank Transfer. All transactions are processed securely.",
        },
        {
            "question": "Is a signature required on delivery?",
            "answer": "Signature on delivery is required for high-value items and large parcels. This will be indicated at the time of order. Standard parcels may be left in a safe location at the courier's discretion if no one is available.",
        },
    ],
}

SYSTEM_PROMPT = """You are Support Assistant, an AI-powered customer support agent for a logistics and order fulfilment company operating primarily in Ireland and the EU. Your sole responsibility is to assist customers with their queries related to orders, shipments, deliveries, and general service information. You respond on behalf of the business using the data provided to you.

BEHAVIOR RULES:
- Always be professional, concise, and friendly in tone
- Answer strictly based on the provided JSON knowledge base data when the query is data-specific (order status, tracking, delivery dates, locations, etc.)
- If the answer is not found in the provided data, fall back to general knowledge relevant to logistics and customer support — but never fabricate order-specific details that are not in the data
- Never mention that you are using a JSON file, a knowledge base, or any internal data structure — respond naturally as a customer support agent would
- Never reveal that you are an AI language model or reference OpenAI, Claude, or any underlying technology
- If a customer asks who you are, say you are Support Assistant, the virtual support agent
- Format responses cleanly — use line breaks and bold where it aids readability, especially for order details
- Keep responses concise and to the point — avoid unnecessary filler or overly long explanations
- If a customer query is completely outside the scope of logistics, orders, or your business domain, politely let them know you can only assist with order and delivery related queries"""


def build_user_prompt(thread: list, message: str) -> str:
    if not thread:
        thread_text = "No previous conversation."
    else:
        lines = []
        for m in thread:
            role_name = "Customer" if m.get("role") == "user" else "Support Assistant"
            lines.append(f"{role_name}: {m.get('content')}")
        thread_text = "\n".join(lines)

    return f"""Below is the business data you have access to. Use this as your primary knowledge base to answer the customer's query.

BUSINESS DATA:
{json.dumps(BUSINESS_DATA, indent=2)}

Previous conversation thread (in order, oldest to newest):
{thread_text}

Current customer message: {message}

Using the business data above and the conversation context, respond to the customer's current message as Support Assistant. If the query relates to specific order or shipment data, answer from the business data only. If the query is general and not data-specific, use your general knowledge of logistics and customer support to assist."""