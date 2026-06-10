"""Email template personalization engine."""

import re

DEFAULT_HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; background-color: #f9fafb; margin: 0; padding: 40px 0;">
    <table align="center" border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 600px; background-color: #ffffff; border-radius: 12px; overflow: hidden; border: 1px solid #e5e7eb; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">
        <!-- Header Area -->
        <tr>
            <td style="background-color: #2563eb; background-image: linear-gradient(135deg, #2563eb 0%, #4f46e5 100%); padding: 40px 30px; text-align: center;">
                <h1 style="color: #ffffff; margin: 0; font-size: 28px; font-weight: bold; letter-spacing: -0.5px;">SubSpace</h1>
                <p style="color: #e0e7ff; margin: 10px 0 0 0; font-size: 16px;">Intelligent Infrastructure Scaling</p>
            </td>
        </tr>
        
        <!-- Content Area -->
        <tr>
            <td style="padding: 40px 30px; color: #374151; font-size: 16px; line-height: 1.6;">
                <p style="margin: 0 0 20px 0;">Hi {{ first_name }},</p>

                <p style="margin: 0 0 20px 0;">I came across <strong>{{ company_name }}</strong> while researching companies in the <strong>{{ industry }}</strong> space — impressive work you're doing there.</p>

                <p style="margin: 0 0 20px 0;">I'm reaching out because we help companies like yours streamline recurring costs and subscription management at scale. Our platform has helped similar organizations reclaim significant budget from underused software subscriptions — on average, companies find they're paying for tools their teams stopped using months ago.</p>

                <p style="margin: 0 0 24px 0;">I'd love to show you a 15-minute demo — no commitment, just a look at what we're seeing with companies in your space.</p>
                
                <!-- CTA Button -->
                <table border="0" cellpadding="0" cellspacing="0" style="margin: 0 0 24px 0;">
                    <tr>
                        <td align="center" bgcolor="#2563eb" style="border-radius: 6px;">
                            <!-- The href would normally be an actual booking link like Calendly -->
                            <a href="https://subspaceai.me/book" style="display: inline-block; padding: 12px 24px; color: #ffffff; font-weight: bold; font-size: 15px; text-decoration: none; border-radius: 6px;">Schedule a quick call</a>
                        </td>
                    </tr>
                </table>

                <p style="margin: 0 0 8px 0;">Best regards,</p>
                <p style="margin: 0; font-weight: bold; color: #111827;">The SubSpace Team</p>
            </td>
        </tr>
        
        <!-- Footer -->
        <tr>
            <td style="background-color: #f3f4f6; padding: 24px 30px; text-align: center;">
                <p style="margin: 0; color: #6b7280; font-size: 12px; line-height: 1.5;">
                    © 2026 SubSpace Technologies Inc.<br>
                    If this isn't relevant to you right now, simply <a href="mailto:outreach@subspaceai.me?subject=Unsubscribe" style="color: #6b7280; text-decoration: underline;">reply</a> to let me know, and I'll make sure we don't reach out again.
                </p>
            </td>
        </tr>
    </table>
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
