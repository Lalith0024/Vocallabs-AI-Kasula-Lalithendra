"""Email template personalization engine."""

import re

DEFAULT_HTML_TEMPLATE = """
<html>
<body style="font-family: Georgia, serif; color: #1a1a1a; line-height: 1.7; max-width: 600px; margin: 0 auto; padding: 24px;">
    <p>Hi {{ first_name }},</p>

    <p>I came across {{ company_name }} while researching companies in the {{ industry }} space — 
    impressive work you're doing there.</p>

    <p>I'm reaching out because we help companies like yours streamline recurring costs 
    and subscription management at scale. Our platform has helped similar organizations 
    reclaim significant budget from underused software subscriptions — on average, 
    companies find they're paying for tools their teams stopped using months ago.</p>

    <p>I'd love to show you a 15-minute demo — no commitment, just a look at 
    what we're seeing with companies in your space.</p>

    <p>Would any slot next week work for a quick call?</p>

    <p>Best,<br>
    The SubSpace Team</p>

    <p style="font-size: 11px; color: #9ca3af; border-top: 1px solid #e5e7eb; padding-top: 12px; margin-top: 24px;">
    If this isn't relevant, just reply and I'll remove you from outreach. No hard feelings.
    </p>
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
