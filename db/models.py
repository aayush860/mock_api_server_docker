from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from datetime import datetime
from . import db


class RecipientList(db.Model):
    __tablename__ = 'recipient_lists'
    id = Column(Integer, primary_key=True, autoincrement=True)
    recipient_category = Column(String, nullable=False, unique=True)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def serialize(self):
        return {
            'id': self.id,
            'recipient_category': self.recipient_category,
            'description': self.description,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class Recipient(db.Model):
    __tablename__ = 'recipients'
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, unique=True, nullable=False)
    name = Column(String)
    recipient_category = Column(String)

    def serialize(self):
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'recipient_category': self.recipient_category
        }

class EmailTemplate(db.Model):
    __tablename__ = 'email_templates'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'content': self.content,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
    }

class Campaign(db.Model):
    __tablename__ = 'campaigns'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    send_time = Column(DateTime, nullable=False)
    campaign_template = Column(String, nullable=False)
    recipient_category = Column(String, ForeignKey('recipient_lists.recipient_category'))
    template_name = Column(String, ForeignKey('email_templates.name'))
    status = Column(String, default='Scheduled')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'send_time': self.send_time.isoformat(),
            'campaign_template': self.campaign_template,
            'recipient_category': self.recipient_category,
            'template_name': self.template_name,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
