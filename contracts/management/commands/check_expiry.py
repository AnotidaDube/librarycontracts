from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from contracts.models import Contract
from django.conf import settings

class Command(BaseCommand):
    help = 'Sends periodic email alerts (every 7 days) for contracts expiring in <= 90 days.'

    def handle(self, *args, **kwargs):
        today = timezone.now().date()
        limit_date = today + timedelta(days=90)
        
        # Set your "Nag Interval" here (e.g., send every 7 days)
        NAG_DAYS = 7 

        # 1. Fetch all active contracts expiring within the 90-day window
        expiring_contracts = Contract.objects.filter(
            end_date__lte=limit_date,
            end_date__gte=today,
            status='ACTIVE'
        )

        if not expiring_contracts:
            self.stdout.write(self.style.SUCCESS('No contracts require alerts today.'))
            return

        sent_count = 0

        for contract in expiring_contracts:
            # 2. Logic: Should we send an email today?
            # Send if: We've NEVER sent one OR it's been 7+ days since the last one
            days_since_last_email = None
            if contract.last_warning_sent_at:
                days_since_last_email = (today - contract.last_warning_sent_at).days

            if contract.last_warning_sent_at is None or days_since_last_email >= NAG_DAYS:
                
                subject = f"RECURRING ALERT: {contract.resource} Expiry Notice"
                message = f"""
Hello Team,

This is a periodic automated reminder from the MSU Library System.

The following resource is still approaching expiration:
- Resource: {contract.resource}
- Vendor: {contract.vendor}
- Expiry Date: {contract.end_date}
- Time Remaining: {contract.exact_time_remaining}

Please initiate the renewal process or update the contract status in the dashboard.
                """

                try:
                    send_mail(
                        subject,
                        message,
                        settings.DEFAULT_FROM_EMAIL,
                        settings.CONTRACT_ALERT_RECIPIENTS,
                        fail_silently=False,
                    )
                    
                    # 3. Update the timestamp to TODAY
                    contract.last_warning_sent_at = today
                    contract.save()
                    
                    sent_count += 1
                    self.stdout.write(self.style.SUCCESS(f'Alert sent for {contract.resource}'))
                
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error for {contract.resource}: {e}'))

        self.stdout.write(self.style.SUCCESS(f'Total alerts processed and sent: {sent_count}'))