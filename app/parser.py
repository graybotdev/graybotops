import re

def clean_status(raw_line):
    line = raw_line.lower()
    if "delivered" in line:
        return "Delivered"
    if "waiting" in line or "stuck" in line:
        return "Stuck at shipper"
    if "canceled" in line:
        return "Canceled"
    return "Update"

def infer_status(text):
    text = text.lower()
    if "delivered" in text:
        return "Delivered"
    if "still waiting on dock" in text:
        return "Stuck at shipper"
    if "canceled by customer" in text:
        return "Canceled"
    if "rolling" in text:
        return "Rolling"
    return None

def parse_email(subject, body):
    messages = []

    # 🟡 Step 1: Handle multiple loads in one body
    multi_loads = re.findall(r"Load (\d+): (.+)", body, re.IGNORECASE)
    if multi_loads:
        for load_id, line in multi_loads:
            messages.append({
                "load_id": load_id,
                "status": clean_status(line),
                "eta": None,
                "old_eta": None,
                "new_eta": None,
                "pickup_date": None,
                "pickup_time": None,
                "delivery_date": None,
                "delivery_time": None,
                "route": None,
                "location": None,
                "doc_type_requested": None,
                "driver_name": None,
                "truck_number": None,
            })
        return messages

    # 🟢 Step 2: Single-message fallback
    parsed_email = {
        "load_id": None,
        "status": None,
        "eta": None,
        "old_eta": None,
        "new_eta": None,
        "pickup_date": None,
        "pickup_time": None,
        "delivery_date": None,
        "delivery_time": None,
        "route": None,
        "location": None,
        "doc_type_requested": None,
        "driver_name": None,
        "truck_number": None,
    }

    full_text = subject + " " + body

    # Load ID
    load_id_match = re.search(r"Load\s+#?(\d+)", full_text, re.IGNORECASE)
    if load_id_match:
        parsed_email["load_id"] = load_id_match.group(1)

    # Rate Con detection
    if "rate con" in full_text.lower() or "rate confirmation" in full_text.lower():
        parsed_email["status"] = "Rate Confirmation Received"

    # POD/BOL/Invoice detection
    doc_match = re.search(r"(need|missing|waiting for|send).{0,20}\b(POD|BOL|invoice)\b", full_text, re.IGNORECASE)
    if doc_match:
        parsed_email["doc_type_requested"] = doc_match.group(2).upper()
        parsed_email["status"] = f"Awaiting {parsed_email['doc_type_requested']}"

    # ETA
    eta_match = re.search(r"ETA (to Consignee:)?\s*([0-9]{1,2}(:[0-9]{2})?\s*[APMapm]{2})", full_text)
    if eta_match:
        parsed_email["eta"] = eta_match.group(2).upper()

    old_eta_match = re.search(r"instead of\s+([0-9]{1,2}(:[0-9]{2})?\s*[APMapm]{2})", full_text)
    if old_eta_match:
        parsed_email["old_eta"] = old_eta_match.group(1).upper()

    new_eta_match = re.search(r"ETA (is now|is)\s+([0-9]{1,2}(:[0-9]{2})?\s*[APMapm]{2})", full_text)
    if new_eta_match:
        parsed_email["new_eta"] = new_eta_match.group(2).upper()
        parsed_email["status"] = parsed_email["status"] or "Delayed"

    # Pickup / Delivery
    pu_match = re.search(r"PU[:\s]+([0-9/]+)\s*@\s*([0-9APMapm:]+)", full_text)
    if pu_match:
        parsed_email["pickup_date"] = pu_match.group(1)
        parsed_email["pickup_time"] = pu_match.group(2).upper()

    del_match = re.search(r"DEL[:\s]+([0-9/]+)(.*?)((before|by)?\s*[0-9APMapm:]+|noon)?", full_text)
    if del_match:
        parsed_email["delivery_date"] = del_match.group(1)
        if del_match.group(3):
            parsed_email["delivery_time"] = del_match.group(3).strip()

    # Route
    route_match = re.search(r"going from ([\w\s]+) to ([\w\s]+)", full_text, re.IGNORECASE)
    if route_match:
        parsed_email["route"] = f"{route_match.group(1).strip()} to {route_match.group(2).strip()}"

    # Location
    location_match = re.search(r"Location[:\s]+(.+)", full_text, re.IGNORECASE)
    if location_match:
        parsed_email["location"] = location_match.group(1).strip()
    else:
        alt_location = re.search(r"traffic (outside|near)\s+([A-Za-z\s]+)", full_text, re.IGNORECASE)
        if alt_location:
            parsed_email["location"] = f"{alt_location.group(1).capitalize()} {alt_location.group(2).strip()}"

    # Driver + Truck
    driver_match = re.search(r"Driver Name[:\s]+(.+)", full_text, re.IGNORECASE)
    truck_match = re.search(r"Truck #[:\s]+(.+)", full_text, re.IGNORECASE)
    if driver_match:
        parsed_email["driver_name"] = driver_match.group(1).strip()
    if truck_match:
        parsed_email["truck_number"] = truck_match.group(1).strip()

    if not parsed_email["status"]:
        parsed_email["status"] = infer_status(full_text)

    return [parsed_email]
