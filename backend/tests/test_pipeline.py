import pytest
from services.email_personalization import generate_personalized_email

def test_generate_personalized_email_with_context():
    template = "Hi {{first_name}}, love your work at {{company_name}}!"
    context = {"first_name": "Alice", "company_name": "Acme Corp"}
    
    result = generate_personalized_email(template, context)
    assert result == "Hi Alice, love your work at Acme Corp!"

def test_generate_personalized_email_missing_context():
    template = "Hi {{first_name}}, love your work at {{company_name}}!"
    context = {"company_name": "Acme Corp"}
    
    result = generate_personalized_email(template, context)
    assert result == "Hi there, love your work at Acme Corp!"
