import requests
import sys
import uuid

BASE_URL = "http://127.0.0.1:8000/api/v1"
PASSWORD = "pass"

def log(msg):
    print(f"[TEST] {msg}")

def login(email, password):
    response = requests.post(f"{BASE_URL}/auth/login/access-token", data={
        "username": email,
        "password": password
    })
    if response.status_code != 200:
        log(f"Login failed for {email}: {response.text}")
        return None
    return response.json()["access_token"]

def test_full_flow():
    # 1. Login as Admin
    log("Logging in as Admin...")
    # Use username 'admin', not email
    admin_token = login("admin", PASSWORD)
    if not admin_token: return
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    log("Admin login successful.")

    # 2. Login as Gestionnaire to test permissions
    log("Logging in as Gestionnaire...")
    gestionnaire_token = login("gestionnaire1", PASSWORD)
    if not gestionnaire_token: return
    gest_headers = {"Authorization": f"Bearer {gestionnaire_token}"}
    log("Gestionnaire login successful.")

    # 3. Create a Livreur (Delivery Person) as Gestionnaire
    # Note: Create user endpoint is POST /api/v1/users/
    unique_livreur = f"livreur_{uuid.uuid4().hex[:6]}"
    livreur_email = f"{unique_livreur}@test.com"
    log(f"Creating Livreur {unique_livreur} as Gestionnaire...")
    
    livreur_data = {
        "username": unique_livreur,
        "email": livreur_email,
        "password": "pass",
        "role": "livreur",
        "is_active": True
    }
    
    resp = requests.post(f"{BASE_URL}/users/", json=livreur_data, headers=gest_headers)
    if resp.status_code != 200:
        log(f"Failed to create livreur: {resp.text}")
        return
    livreur = resp.json()
    livreur_id = livreur["id"]
    log(f"Livreur created with ID {livreur_id}")

    # 4. Create an Order as Client
    log("Logging in as Client...")
    client_token = login("client1", PASSWORD)
    if not client_token: return
    client_headers = {"Authorization": f"Bearer {client_token}"}
    
    # We need a product ID first
    products = requests.get(f"{BASE_URL}/products/", headers=client_headers).json()
    if not products:
        log("No products found, skipping order creation.")
        return
    product_id = products[0]["id"]
    product_price = products[0]["price"]

    log("Creating Order as Client...")
    order_data = {
        "client_name": "Test Client",
        "phone": "1234567890",
        "delivery_address": "123 Test St",
        "order_number": f"CMD-{uuid.uuid4().hex[:8]}",
        "total_price": product_price * 2,
        "items": [
            {"product_id": product_id, "quantity": 2, "unit_price": product_price}
        ]
    }
    
    resp = requests.post(f"{BASE_URL}/orders/", json=order_data, headers=client_headers)
    if resp.status_code != 200:
        log(f"Failed to create order: {resp.text}")
        return
    order = resp.json()
    order_id = order["id"]
    log(f"Order created with ID {order_id}. Status: {order['status']}")

    # 5. Assign Order as Gestionnaire
    log("Assigning Order to Livreur as Gestionnaire...")
    assign_url = f"{BASE_URL}/orders/{order_id}/assign?livreur_id={livreur_id}"
    resp = requests.patch(assign_url, headers=gest_headers)
    
    if resp.status_code != 200:
        log(f"Failed to assign order: {resp.text}")
        return
    
    updated_order = resp.json()
    if updated_order["livreur_id"] == livreur_id:
        log(f"Order successfully assigned to livreur ID {livreur_id}")
    else:
        log("Order assignment failed verification.")

    # 6. Verify Livreur can see the order
    log(f"Logging in as new Livreur {unique_livreur}...")
    # New created livreur uses username
    livreur_token = login(unique_livreur, "pass")
    livreur_headers = {"Authorization": f"Bearer {livreur_token}"}
    
    log("Fetching assigned orders as Livreur...")
    orders_resp = requests.get(f"{BASE_URL}/orders/", headers=livreur_headers)
    my_orders = orders_resp.json()
    
    found = False
    for o in my_orders:
        if o["id"] == order_id:
            found = True
            break
    
    if found:
        log("SUCCESS: Livreur sees the assigned order.")
    else:
        log("FAILURE: Livreur does not see the order.")

    # 7. Test Image Upload permissions as Producteur
    log("Logging in as Producteur...")
    # Use username 'producteur1'
    prod_token = login("producteur1", PASSWORD)
    if prod_token:
        log("Producteur login successful.")
        # create valid dummy image
        with open("test_image.jpg", "wb") as f:
            f.write(b'\xFF\xD8\xFF\xE0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xFF\xDB\x00C\x00\xFF\xC0\x00\x11\x08\x00\n\x00\n\x03\x01\x22\x00\x02\x11\x01\x03\x11\x01\xFF\xC4\x00\x1F\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0A\x0B\xFF\xDA\x00\x0C\x03\x01\x00\x02\x11\x03\x11\x00\x3F\x00\xBF\x00\x00')
        
        files = {"file": ("test_image.jpg", open("test_image.jpg", "rb"), "image/jpeg")}
        prod_headers = {"Authorization": f"Bearer {prod_token}"}
        
        # Upload to first product
        log(f"Attempting image upload as Producteur for product {product_id}...")
        img_resp = requests.post(f"{BASE_URL}/products/{product_id}/image", files=files, headers=prod_headers)
        if img_resp.status_code == 200:
            log("SUCCESS: Producteur uploaded image.")
        else:
            log(f"FAILURE: Image upload failed: {img_resp.text}")

    # Cleanup
    if gestionnaire_token and livreur_id:
        log("Cleaning up test livreur...")
        requests.delete(f"{BASE_URL}/users/{livreur_id}", headers=gest_headers)

    print("--- Tests Complete ---")

if __name__ == "__main__":
    test_full_flow()
