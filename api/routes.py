from flask import Blueprint, jsonify, request
from db.models import RecipientList, Recipient, EmailTemplate, Campaign
from db import db
import datetime

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
    new_recipient = Recipient(email=data['email'], name=data.get('name'),
                              recipient_category=data.get('recipient_category'))
    db.session.add(new_recipient)
    db.session.commit()
    return jsonify(new_recipient.serialize()), 201


@api_bp.route('/api/recipient_lists', methods=['POST'])
def create_recipient_list():
    data = request.json
    new_list = RecipientList(recipient_category=data['recipient_category'], description=data.get('description'))
    db.session.add(new_list)
    db.session.commit()
    return jsonify(new_list.serialize()), 201


@api_bp.route('/api/email_templates', methods=['POST'])
def create_email_template():
    data = request.json
    new_template = EmailTemplate(name=data['name'], content=data['content'])
    db.session.add(new_template)
    db.session.commit()
    return jsonify(new_template.serialize()), 201


@api_bp.route('/api/campaigns', methods=['POST'])
def create_campaign():
    data = request.json

    # Check if the send_time is greater than the current time
    send_time = datetime.strptime(data['send_time'], '%Y-%m-%dT%H:%M:%S')
    if send_time <= datetime.utcnow():
        return jsonify({'error': 'Send time must be greater than the current time'}), 400

    # Check if the recipient_category exists in recipient_lists
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
    new_campaign = Campaign(name=data['name'], send_time=data['send_time'], recipient_category=recipient_category,
                            campaign_template=data['campaign_template'], template_name=template_name)
    db.session.add(new_campaign)
    db.session.commit()

    return jsonify(new_campaign.serialize()), 201


@api_bp.route('/api/campaigns/delete', methods=['DELETE'])
def delete_campaign_by_name():
    name = request.args.get('name')
    if not name:
        return jsonify({'error': 'Name parameter is required for deletion'}), 400

    campaign = Campaign.query.filter_by(name=name).first()
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

    # Check if the send_time is greater than the current time
    if 'send_time' in data:
        send_time = datetime.strptime(data['send_time'], '%Y-%m-%dT%H:%M:%S')
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
    if 'name' in data:
        campaign.name = data['name']

    if 'campaign_template' in data:
        if data['campaign_template'] == "":
            return jsonify({'error': 'Campaign Template cannot be Null'}), 404
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
        send_time = datetime.strptime(data['send_time'], '%Y-%m-%dT%H:%M:%S')
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
