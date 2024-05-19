from flask import Blueprint, jsonify, request
from db.models import RecipientList, Recipient, EmailTemplate, Campaign
from db import db
from datetime import datetime

api_bp = Blueprint('api', __name__)


@api_bp.route('/api/recipient_lists', methods=['GET'])
def get_recipient_lists():
    recipient_lists = RecipientList.query.all()
    return jsonify([resp_list.serialize() for resp_list in recipient_lists])


@api_bp.route('/api/recipients', methods=['GET'])
def get_recipients():
    recipients = Recipient.query.all()
    return jsonify([recipient.serialize() for recipient in recipients])


@api_bp.route('/api/email_templates', methods=['GET'])
def get_email_templates():
    email_templates = EmailTemplate.query.all()
    return jsonify([template.serialize() for template in email_templates])


@api_bp.route('/api/campaigns', methods=['GET'])
def get_campaigns():
    campaigns = Campaign.query.all()
    return jsonify([campaign.serialize() for campaign in campaigns])


@api_bp.route('/api/recipients', methods=['POST'])
def create_recipient():
    data = request.json

    # Check if email is provided
    if 'email' not in data or not data['email']:
        return jsonify({
            'error': 'Invalid input',
            'message': 'email is required and cannot be null.'
        }), 400

    # Check if recipient_category is provided
    if 'recipient_category' not in data or not data['recipient_category']:
        return jsonify({
            'error': 'Invalid input',
            'message': 'recipient_category is required and cannot be null.'
        }), 400

    # Check if email is unique
    existing_recipient = Recipient.query.filter_by(email=data['email']).first()
    if existing_recipient:
        return jsonify({
            'error': 'Duplicate entry',
            'message': 'A recipient with this email already exists.'
        }), 409

    # Check if name exceeds maximum length
    if 'name' in data and len(data['name']) > 32:
        return jsonify({
            'error': 'Invalid input',
            'message': 'name cannot be more than 32 characters.'
        }), 400

    # If no issues, create the new recipient
    new_recipient = Recipient(email=data['email'], name=data.get('name'),
                              recipient_category=data.get('recipient_category'))
    db.session.add(new_recipient)
    db.session.commit()
    return jsonify(new_recipient.serialize()), 201


@api_bp.route('/api/recipient_lists', methods=['POST'])
def create_recipient_list():
    data = request.json
    if not data or 'recipient_category' not in data or not data['recipient_category']:
        return jsonify({'error': 'Invalid input', 'message': 'recipient_category is required and cannot be null.'}), 400
    recipient_category = data['recipient_category']

    # Check for duplicates
    existing_list = RecipientList.query.filter_by(recipient_category=recipient_category).first()
    if existing_list:
        return jsonify(
            {'error': 'Duplicate entry', 'message': 'A recipient list with this category already exists.'}), 409

    # If no duplicate is found, create the new recipient list
    new_list = RecipientList(recipient_category=recipient_category, description=data.get('description'))
    db.session.add(new_list)
    db.session.commit()
    return jsonify(new_list.serialize()), 201


@api_bp.route('/api/email_templates', methods=['POST'])
def create_email_template():
    data = request.json

    # Check if template name is provided and not null
    if 'name' not in data or not data['name']:
        return jsonify({
            'error': 'Invalid input',
            'message': 'Template name is required and cannot be null.'
        }), 400

    # Check if template name length exceeds 20 characters
    if len(data['name']) > 20:
        return jsonify({
            'error': 'Invalid input',
            'message': 'Template name cannot be more than 20 characters.'
        }), 400

    # Check if template name is unique
    existing_template = EmailTemplate.query.filter_by(name=data['name']).first()
    if existing_template:
        return jsonify({
            'error': 'Duplicate entry',
            'message': 'A template with this name already exists.'
        }), 409

    # If no issues, create the new email template
    new_template = EmailTemplate(name=data['name'], content=data['content'])
    db.session.add(new_template)
    db.session.commit()
    return jsonify(new_template.serialize()), 201


@api_bp.route('/api/campaigns', methods=['POST'])
def create_campaign():
    data = request.json

    # Check if campaign name is provided and not null
    if 'name' not in data or not data['name']:
        return jsonify({'error': 'Campaign name is required'}), 400

    # Check if campaign name exceeds max length of 20 characters
    if len(data['name']) > 60:
        return jsonify({'error': 'Campaign name exceeds maximum length of 20 characters'}), 400

    # Check if send_time is provided and not null
    if 'send_time' not in data or not data['send_time']:
        return jsonify({'error': 'Send time is required'}), 400

    # Convert send_time to datetime object
    try:
        send_time = datetime.fromisoformat(data['send_time'])
    except ValueError:
        return jsonify({'error': 'Invalid send time format. ISO 8601 format expected'}), 400

    # Check if send_time is in the past
    if send_time < datetime.utcnow():
        return jsonify({'error': 'Send time must be in the future'}), 400

    # Check if campaign name is unique
    existing_campaign = Campaign.query.filter_by(name=data['name']).first()
    if existing_campaign:
        return jsonify({'error': 'Campaign name already exists'}), 409

    recipient_category = data.get('recipient_category')
    if recipient_category:
        recipient_list = RecipientList.query.filter_by(recipient_category=recipient_category).first()
        if not recipient_list:
            return jsonify({'error': 'Recipient category not found'}), 404

    # Check if the template_name exists in email_templates
    template_name = data.get('template_name')
    if template_name:
        email_template = EmailTemplate.query.filter_by(name=template_name).first()
        if not email_template:
            return jsonify({'error': 'Email template not found'}), 404

    # Create the new campaign
    new_campaign = Campaign(name=data['name'], send_time=send_time, recipient_category=recipient_category,
                            campaign_template=data['campaign_template'], template_name=template_name)
    db.session.add(new_campaign)
    db.session.commit()

    return jsonify(new_campaign.serialize()), 201


@api_bp.route('/api/campaigns/delete', methods=['DELETE'])
def delete_campaign_by_name():
    name = request.args.get('name')
    print(name)
    if not name:
        return jsonify({'error': 'Name parameter is required for deletion'}), 400

    campaign = Campaign.query.filter_by(name=name).first()
    print(campaign)
    if not campaign:
        return jsonify({'error': 'Campaign not found'}), 404

    # Update the status to "Cancelled"
    campaign.status = "Cancelled"
    db.session.commit()

    return jsonify({'message': f'Campaign "{name}" has been cancelled'}), 200


@api_bp.route('/api/recipients/<recipient_category>', methods=['GET'])
def get_recipients_by_category(recipient_category):
    recipients = Recipient.query.filter_by(recipient_category=recipient_category).all()
    if not recipients:
        return jsonify({'error': 'No recipients found for the given category'}), 404
    return jsonify([recipient.serialize() for recipient in recipients])


@api_bp.route('/api/campaigns/<name>', methods=['PUT'])
def update_campaign_by_name(name):
    data = request.json

    # Check if the campaign exists
    campaign = Campaign.query.filter_by(name=name).first()
    if not campaign:
        return jsonify({'error': 'Campaign not found'}), 404

    # Check if the campaign name is provided and not null
    if 'name' in data:
        if not data['name']:
            return jsonify({'error': 'Campaign name is required'}), 400
        # Check if campaign name exceeds max length of 60 characters
        if len(data['name']) > 60:
            return jsonify({'error': 'Campaign name exceeds maximum length of 60 characters'}), 400
        # Check if campaign name is unique
        existing_campaign = Campaign.query.filter_by(name=data['name']).first()
        if existing_campaign and existing_campaign.id != campaign.id:
            return jsonify({'error': 'Campaign name already exists'}), 409
        campaign.name = data['name']

    # Check if send_time is provided and not null
    if 'send_time' in data:
        if not data['send_time']:
            return jsonify({'error': 'Send time is required'}), 400
        # Convert send_time to datetime object
        try:
            send_time = datetime.fromisoformat(data['send_time'])
        except ValueError:
            return jsonify({'error': 'Invalid send time format. ISO 8601 format expected'}), 400
        # Check if send_time is in the future
        if send_time <= datetime.utcnow():
            return jsonify({'error': 'Send time must be greater than the current time'}), 400
        campaign.send_time = send_time

    # Check if the recipient_category exists in recipient_lists
    if 'recipient_category' in data:
        recipient_category = data['recipient_category']
        recipient_list = RecipientList.query.filter_by(recipient_category=recipient_category).first()
        if not recipient_list:
            return jsonify({'error': 'Recipient category not found'}), 404
        campaign.recipient_category = recipient_category

    # Check if the template_name exists in email_templates
    if 'template_name' in data:
        template_name = data['template_name']
        email_template = EmailTemplate.query.filter_by(name=template_name).first()
        if not email_template:
            return jsonify({'error': 'Email template not found'}), 404
        campaign.template_name = template_name

    # Update other fields if provided
    if 'campaign_template' in data:
        if not data['campaign_template']:
            return jsonify({'error': 'Campaign Template cannot be Null'}), 400
        campaign.campaign_template = data['campaign_template']

    db.session.commit()
    return jsonify(campaign.serialize()), 200


@api_bp.route('/api/campaigns/<name>', methods=['PATCH'])
def partial_update_campaign_by_name(name):
    data = request.json

    # Check if the campaign exists
    campaign = Campaign.query.filter_by(name=name).first()
    if not campaign:
        return jsonify({'error': 'Campaign not found'}), 404

    # Update fields if provided
    if 'name' in data:
        campaign.name = data['name']

    if 'send_time' in data:
        try:
            send_time = datetime.fromisoformat(data['send_time'])
        except ValueError:
            return jsonify({'error': 'Invalid send time format. ISO 8601 format expected'}), 400

        if send_time <= datetime.utcnow():
            return jsonify({'error': 'Send time must be greater than the current time'}), 400

        campaign.send_time = send_time

    if 'recipient_category' in data:
        recipient_category = data['recipient_category']
        recipient_list = RecipientList.query.filter_by(recipient_category=recipient_category).first()
        if not recipient_list:
            return jsonify({'error': 'Recipient category not found'}), 404
        campaign.recipient_category = recipient_category

    if 'template_name' in data:
        template_name = data['template_name']
        email_template = EmailTemplate.query.filter_by(name=template_name).first()
        if not email_template:
            return jsonify({'error': 'Email template not found'}), 404
        campaign.template_name = template_name

    if 'campaign_template' in data:
        if data['campaign_template'] == "":
            return jsonify({'error': 'Campaign Template cannot be Null'}), 404
        campaign.campaign_template = data['campaign_template']

    db.session.commit()
    return jsonify(campaign.serialize()), 200


@api_bp.route('/api/campaigns/<status>', methods=['GET'])
def get_campaigns_by_status(status):
    # Assuming Campaign model exists with a 'status' field

    # Retrieve campaigns based on status
    campaigns = Campaign.query.filter_by(status=status).all()

    # Serialize the campaigns
    serialized_campaigns = [campaign.serialize() for campaign in campaigns]

    return jsonify(serialized_campaigns), 200
