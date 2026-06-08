"""Email template personalization engine."""

import re

DEFAULT_HTML_TEMPLATE = """
<html>
<body style="font-family: sans-serif; color: #333; line-height: 1.6;">
    <p>Hi {{ first_name }},</p>
    
    <p>I noticed {{ company_name }} is doing some interesting work in the {{ industry }} space. 
    At our company, we've solved similar challenges for organizations like yours.</p>
    
    <p>I'd love to explore a potential partnership. Are you open to a brief call next week?</p>
    
    <p>Best regards,<br>
    The Outreach Team</p>
</body>
</html>
"""

def generate_personalized_email(template: str, context: dict) -> str:
    """
    Replace mustache-style variables in template with context values.
    Example: {{ first_name }} -> context.get('first_name')
    """
    if not template:
        template = DEFAULT_HTML_TEMPLATE
        
    def replace_var(match):
        var_name = match.group(1).strip()
        value = context.get(var_name)
        # Fallback for missing values
        if not value:
            if var_name == "first_name":
                return "there"
            return f"[{var_name}]"
        return str(value)
        
    pattern = r"\{\{(.*?)\}\}"
    return re.sub(pattern, replace_var, template)
