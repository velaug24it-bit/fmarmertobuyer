from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import json
import random
import string
from datetime import datetime
from flask_cors import CORS
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = 'farmlink-secret-key-2025'  # Change this for production

# UPDATE CORS Configuration
CORS(app, 
     origins=["http://localhost:5000", "http://127.0.0.1:5000", "http://localhost:8000", "http://127.0.0.1:8000"],
     supports_credentials=True,
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     allow_headers=["Content-Type", "Authorization"])

# Email configuration from environment variables
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', EMAIL_ADDRESS)

# In-memory storage for orders (use database in production)
orders = []

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/send-message', methods=['POST', 'OPTIONS'])
def send_message():
    """Handle contact form submissions and send email"""
    if request.method == 'OPTIONS':
        return '', 200  # Handle preflight requests
    
    try:
        # Check if request is JSON
        if not request.is_json:
            return jsonify({'success': False, 'error': 'Content-Type must be application/json'}), 400
        
        data = request.get_json()
        print(f"Contact form data received: {data}")  # Debug log
        
        # Extract form data
        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        subject = data.get('subject', 'New Message from FarmLink').strip()
        message = data.get('message', '').strip()
        
        # Validation
        if not name or not email or not message:
            return jsonify({
                'success': False,
                'error': 'Please fill all required fields'
            }), 400
        
        # Validate email format
        if '@' not in email or '.' not in email:
            return jsonify({
                'success': False,
                'error': 'Please enter a valid email address'
            }), 400
        
        # For now, simulate email sending
        print(f"Email would be sent to admin: Name: {name}, Email: {email}, Subject: {subject}, Message: {message}")
        
        # In production, you would call send_contact_email() here
        # email_sent = send_contact_email(name, email, subject, message)
        
        # Simulate success
        email_sent = True
        
        if email_sent:
            return jsonify({
                'success': True,
                'message': 'Your message has been sent successfully! We will get back to you soon.'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to send email. Please try again later.'
            }), 500
            
    except Exception as e:
        print(f"Error sending message: {str(e)}")  # Debug log
        return jsonify({
            'success': False,
            'error': 'An internal server error occurred. Please try again.'
        }), 500

def send_contact_email(name, user_email, subject, message):
    """Send contact form submission to admin"""
    try:
        # Validate email inputs
        if not all([name, user_email, message]):
            print("Missing required fields")
            return False
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = ADMIN_EMAIL
        msg['Reply-To'] = user_email
        msg['Subject'] = f"FarmLink Contact: {subject}"
        
        # Create HTML email body
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #4CAF50; color: white; padding: 15px; text-align: center; }}
                .content {{ padding: 20px; background-color: #f9f9f9; }}
                .field {{ margin-bottom: 15px; }}
                .label {{ font-weight: bold; color: #4CAF50; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>New Contact Form Submission</h2>
                </div>
                <div class="content">
                    <div class="field">
                        <span class="label">Name:</span> {name}
                    </div>
                    <div class="field">
                        <span class="label">Email:</span> {user_email}
                    </div>
                    <div class="field">
                        <span class="label">Subject:</span> {subject}
                    </div>
                    <div class="field">
                        <span class="label">Message:</span><br>
                        <p>{message}</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Create plain text version
        text = f"""
        New Contact Form Submission
        
        Name: {name}
        Email: {user_email}
        Subject: {subject}
        
        Message:
        {message}
        
        Time received: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        # Attach both versions
        msg.attach(MIMEText(text, 'plain'))
        msg.attach(MIMEText(html, 'html'))
        
        # Send email with timeout
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=30) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
        
        print(f"✓ Contact email sent successfully to {ADMIN_EMAIL}")
        return True
        
    except smtplib.SMTPAuthenticationError:
        print("✗ SMTP Authentication Error: Check your email credentials")
        return False
    except smtplib.SMTPException as e:
        print(f"✗ SMTP Error: {str(e)}")
        return False
    except Exception as e:
        print(f"✗ Error sending contact email: {str(e)}")
        return False

def send_confirmation_email(name, user_email):
    """Send confirmation email to the user"""
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = user_email
        msg['Subject'] = "Thank you for contacting FarmLink!"
        
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ text-align: center; padding: 20px; background-color: #4CAF50; color: white; border-radius: 10px; }}
                .content {{ padding: 30px; background-color: #f9f9f9; border-radius: 0 0 10px 10px; }}
                .highlight {{ background-color: #e8f5e9; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #4CAF50; }}
                .contact-info {{ background-color: white; padding: 15px; border-radius: 5px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🌾 FarmLink</h1>
                    <h2>Direct Farmer to Buyer Marketplace</h2>
                </div>
                <div class="content">
                    <h3>Hi {name},</h3>
                    
                    <p>Thank you for contacting <strong>FarmLink</strong>! We have received your message and our team will get back to you within <strong>24 hours</strong>.</p>
                    
                    <div class="highlight">
                        <h4>📋 What happens next?</h4>
                        <p>1. Our support team reviews your message</p>
                        <p>2. We'll respond to your inquiry</p>
                        <p>3. If needed, we'll schedule a call to better understand your needs</p>
                    </div>
                    
                    <div class="contact-info">
                        <h4>📞 Need immediate assistance?</h4>
                        <p><strong>Phone:</strong> +91 9840994649</p>
                        <p><strong>Email:</strong> support@farmlink.com</p>
                        <p><strong>Location:</strong> Tirunelvelli, Agriculture City</p>
                    </div>
                    
                    <p>In the meantime, you can:</p>
                    <ul>
                        <li>📊 Browse our fresh produce listings</li>
                        <li>👥 Connect with farmers directly</li>
                        <li>🚚 Explore logistics options</li>
                    </ul>
                    
                    <p>Best regards,<br>
                    <strong>The FarmLink Team</strong></p>
                    
                    <hr>
                    <p style="color: #666; font-size: 0.9em;">
                        This is an automated message. Please do not reply to this email.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text = f"""
        Thank you for contacting FarmLink!
        
        Hi {name},
        
        Thank you for contacting FarmLink! We have received your message and our team will get back to you within 24 hours.
        
        What happens next?
        1. Our support team reviews your message
        2. We'll respond to your inquiry
        3. If needed, we'll schedule a call to better understand your needs
        
        Need immediate assistance?
        Phone: +91 9840994649
        Email: support@farmlink.com
        Location: Tirunelvelli, Agriculture City
        
        Best regards,
        The FarmLink Team
        
        This is an automated message. Please do not reply to this email.
        """
        
        msg.attach(MIMEText(text, 'plain'))
        msg.attach(MIMEText(html, 'html'))
        
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
        
        print(f"Confirmation email sent to {user_email}")
        return True
        
    except Exception as e:
        print(f"Error sending confirmation email: {str(e)}")
        return False

@app.route('/checkout', methods=['POST', 'OPTIONS'])
def checkout():
    """Handle checkout and payment initialization"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        if not request.is_json:
            return jsonify({'success': False, 'error': 'Content-Type must be application/json'}), 400
        
        data = request.get_json()
        print(f"Checkout data received: {data}")
        
        required_fields = ['name', 'phone', 'address', 'city', 'pincode', 'payment_method', 'cart', 'total']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'Missing field: {field}'}), 400
        
        transaction_id = 'TXN' + ''.join(random.choices(string.digits, k=8))
        
        order_data = {
            'id': f"FARM{int(datetime.now().timestamp())}",
            'transaction_id': transaction_id,
            'customer': {
                'name': data['name'],
                'phone': data['phone'],
                'address': data['address'],
                'city': data['city'],
                'pincode': data['pincode']
            },
            'payment_method': data['payment_method'],
            'cart': data['cart'],
            'total': data['total'],
            'status': 'pending',
            'timestamp': datetime.now().isoformat()
        }
        
        orders.append(order_data)
        print(f"Order created: {transaction_id}")
        
        return jsonify({
            'success': True,
            'transaction_id': transaction_id,
            'order_id': order_data['id'],
            'message': 'Checkout initialized successfully'
        })
        
    except Exception as e:
        print(f"Checkout error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/process_payment', methods=['POST', 'OPTIONS'])
def process_payment():
    """Process payment for an order"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        if not request.is_json:
            return jsonify({'success': False, 'error': 'Content-Type must be application/json'}), 400
        
        data = request.get_json()
        print(f"Payment data received: {data}")
        
        if 'transaction_id' not in data:
            return jsonify({'success': False, 'error': 'Transaction ID required'}), 400
        
        transaction_id = data['transaction_id']
        
        order = next((o for o in orders if o['transaction_id'] == transaction_id), None)
        if not order:
            return jsonify({'success': False, 'error': 'Order not found'}), 404
        
        payment_method = order['payment_method']
        print(f"Processing {payment_method} payment for {transaction_id}")
        
        if payment_method == 'upi':
            if 'upi_pin' not in data or len(str(data['upi_pin'])) != 6:
                return jsonify({'success': False, 'error': 'Invalid UPI PIN'}), 400
            
            payment_success = simulate_upi_payment(data['upi_pin'])
            
        elif payment_method == 'card':
            required_card_fields = ['card_number', 'card_holder', 'expiry', 'cvv', 'otp']
            for field in required_card_fields:
                if field not in data:
                    return jsonify({'success': False, 'error': f'Missing card field: {field}'}), 400
            
            payment_success = simulate_card_payment(data)
            
        elif payment_method == 'cod':
            payment_success = True
            
        elif payment_method == 'netbanking':
            payment_success = True
            
        else:
            return jsonify({'success': False, 'error': 'Invalid payment method'}), 400
        
        if payment_success:
            order['status'] = 'paid'
            order['payment_status'] = 'completed'
            order['payment_timestamp'] = datetime.now().isoformat()
            
            print(f"Payment successful for {transaction_id}")
            
            return jsonify({
                'success': True,
                'message': 'Payment successful',
                'order_id': order['id'],
                'transaction_id': transaction_id,
                'status': 'paid'
            })
        else:
            order['status'] = 'payment_failed'
            return jsonify({
                'success': False,
                'error': 'Payment failed. Please try again.'
            })
            
    except Exception as e:
        print(f"Payment processing error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/order_status/<transaction_id>', methods=['GET'])
def order_status(transaction_id):
    order = next((o for o in orders if o['transaction_id'] == transaction_id), None)
    if order:
        return jsonify({
            'success': True,
            'order': order
        })
    else:
        return jsonify({'success': False, 'error': 'Order not found'}), 404

@app.route('/api/orders', methods=['POST', 'OPTIONS'])
def create_order():
    if request.method == 'OPTIONS':
        return '', 200
        
    try:
        if not request.is_json:
            return jsonify({'success': False, 'error': 'Content-Type must be application/json'}), 400
            
        order_data = request.json
        
        # Generate order ID
        order_id = f"FARM{int(datetime.now().timestamp())}"
        
        order = {
            'id': order_id,
            'transaction_id': order_data.get('transaction_id', f"TXN{random.randint(10000000, 99999999)}"),
            'customer': order_data.get('customer', {}),
            'payment_method': order_data.get('payment_method', 'upi'),
            'cart': order_data.get('cart', []),
            'total': calculate_total(order_data.get('cart', [])),
            'date': datetime.now().isoformat(),
            'status': 'completed'
        }
        
        orders.append(order)
        
        return jsonify({
            'success': True,
            'message': 'Order created successfully',
            'order': order,
            'invoice_url': f'/api/invoice/{order["id"]}'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/invoice/<order_id>', methods=['GET'])
def get_invoice(order_id):
    try:
        # Find the order
        order = next((o for o in orders if o['id'] == order_id), None)
        
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        # Return order data for invoice generation
        return jsonify({
            'success': True,
            'order': order
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/invoice/pdf/<order_id>', methods=['GET'])
def get_invoice_pdf(order_id):
    try:
        # Find the order
        order = next((o for o in orders if o['id'] == order_id), None)
        
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        return jsonify({
            'success': True,
            'message': 'PDF generation would happen here',
            'order': order
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/test-email', methods=['GET'])
def test_email():
    """Test email functionality"""
    try:
        # Check if email credentials are set
        if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
            return jsonify({
                'success': False, 
                'error': 'Email credentials not configured. Please set EMAIL_ADDRESS and EMAIL_PASSWORD in .env file'
            })
        
        # Test sending a simple email
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = ADMIN_EMAIL
        msg['Subject'] = "Test Email from FarmLink"
        msg.attach(MIMEText('This is a test email from FarmLink server.', 'plain'))
        
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=30) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
        
        return jsonify({'success': True, 'message': 'Test email sent successfully!'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'FarmLink Backend',
        'email_configured': bool(EMAIL_ADDRESS and EMAIL_PASSWORD),
        'orders_count': len(orders),
        'timestamp': datetime.now().isoformat()
    })

def calculate_total(cart_items):
    total = 0
    for item in cart_items:
        price = item.get('price', 0)
        quantity = item.get('quantity', 0)
        total += price * quantity
    return total * 1.05  # Include 5% GST

def simulate_upi_payment(upi_pin):
    pin_str = str(upi_pin)
    return len(pin_str) == 6 and pin_str.isdigit()

def simulate_card_payment(card_data):
    otp_str = str(card_data.get('otp', ''))
    return len(otp_str) == 6 and otp_str.isdigit()

if __name__ == '__main__':
    # Check if email credentials are set
    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        print("⚠️ WARNING: Email credentials not set in .env file")
        print("Contact form emails will not be sent.")
        print("Please create a .env file with:")
        print("EMAIL_ADDRESS=your-email@gmail.com")
        print("EMAIL_PASSWORD=your-app-password")
        print("ADMIN_EMAIL=admin-email@example.com")
        print("\nFor now, contact form will work without sending actual emails.")
    
    print("✅ FarmLink Backend Server Starting...")
    print(f"📧 Email configured: {bool(EMAIL_ADDRESS and EMAIL_PASSWORD)}")
    print("🌐 Server running on http://localhost:5000")
    print("📊 Health check: http://localhost:5000/health")
    print("✉️ Test email: http://localhost:5000/test-email")
    
    app.run(debug=True, port=5000, host='0.0.0.0')
