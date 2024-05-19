from datetime import datetime, timedelta
from db import db
from .models import RecipientList, Recipient, EmailTemplate, Campaign


# Function to create dummy data for RecipientList
def create_recipient_lists():
    recipient_lists_data = [
        {"recipient_category": "admin", "description": "Send Email Campaign to Admin Level Users"},
        {"recipient_category": "vendors", "description": "Send Email Campaign to Vendor Level Users"},
        {"recipient_category": "customer", "description": "Send Email Campaign to Customer Level Users"},
        # Add more entries as needed
    ]
    for data in recipient_lists_data:
        recipient_list = RecipientList(
            recipient_category=data["recipient_category"],
            description=data["description"],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.session.add(recipient_list)
    db.session.commit()


# Function to create dummy data for Recipient
def create_recipients():
    recipients_data = [
        {"email": "admin_1@example.com", "name": "Recipient 1", "recipient_category": "admin"},
        {"email": "vendor_1@example.com", "name": "Recipient 2", "recipient_category": "vendors"},
        {"email": "customer_1@example.com", "name": "Recipient 3", "recipient_category": "customer"},
        {"email": "admin_2@example.com", "name": "Recipient 4", "recipient_category": "admin"},
        {"email": "vendor_2@example.com", "name": "Recipient 5", "recipient_category": "vendors"},
        {"email": "customer_2@example.com", "name": "Recipient 6", "recipient_category": "customer"},
        {"email": "vendor_3@example.com", "name": "Recipient 7", "recipient_category": "vendors"},
        # Add more entries as needed
    ]
    for data in recipients_data:
        recipient = Recipient(
            email=data["email"],
            name=data["name"],
            recipient_category=data["recipient_category"]
        )
        db.session.add(recipient)
    db.session.commit()


# Function to create dummy data for EmailTemplate
def create_email_templates():
    email_templates_data = [
        {"name": "Admin_Template", "content": "Email intended for Admins"},
        {"name": "Vendor_Template", "content": "Email intended for Vendors"},
        {"name": "Customer_Template", "content": "Email intended for Consumers"},
        # Add more entries as needed
    ]
    for data in email_templates_data:
        email_template = EmailTemplate(
            name=data["name"],
            content=data["content"],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.session.add(email_template)
    db.session.commit()


# Function to create dummy data for Campaign
def create_campaigns():
    # Retrieve the IDs of the previously inserted recipient lists and email templates
    recipient_list_ids = [rl.recipient_category for rl in RecipientList.query.all()]
    template_ids = [et.name for et in EmailTemplate.query.all()]
    campaigns = [
        Campaign(name='Admin_camp', send_time=datetime.utcnow() + timedelta(hours=5), recipient_category=recipient_list_ids[0],
                 template_name=template_ids[0], campaign_template="Hello Admins How are You", status='Scheduled'),
        Campaign(name='Vendor_camp', send_time=datetime.utcnow() + timedelta(hours=10), recipient_category=recipient_list_ids[1],
                 template_name=template_ids[1], campaign_template="Hello Vendors How are You", status='Scheduled'),
        Campaign(name='Consumer_camp', send_time=datetime.utcnow() + timedelta(hours=24), recipient_category=recipient_list_ids[2],
                 template_name=template_ids[2], campaign_template="Hello Customer How are You", status='Scheduled'),
        Campaign(name='Regular_camp', send_time=datetime.utcnow() + timedelta(hours=14), recipient_category=recipient_list_ids[0],
                 template_name=template_ids[0], campaign_template="Hello Regulars How are You", status='Cancelled')
    ]
    db.session.bulk_save_objects(campaigns)
    db.session.commit()


def create_dummy_data():
    # Create dummy data for each table
    create_recipient_lists()
    print("#"*30)
    create_recipients()
    create_email_templates()
    create_campaigns()
