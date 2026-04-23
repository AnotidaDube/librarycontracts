from django.db import models
from django.utils import timezone
from datetime import datetime, time

class Organization(models.Model):
    """Stores Vendor or Publisher contact details to avoid typing them repeatedly."""
    ORG_TYPES = [
        ('VENDOR', 'Vendor'),
        ('PUBLISHER', 'Publisher'),
    ]
    name = models.CharField(max_length=200, help_text="e.g. EBSCO Information Services")
    org_type = models.CharField(max_length=20, choices=ORG_TYPES)
    email = models.EmailField()
    phone_number = models.CharField(max_length=50)
    physical_address = models.TextField()

    def __str__(self):
        return self.name

class ElectronicResource(models.Model):
    """Stores the details of the journal, book, or software."""
    RESOURCE_TYPES = [
        ('JOURNAL', 'Electronic Journal'),
        ('BOOK', 'Electronic Book'),
        ('SOFTWARE', 'Software'),
    ]
    SUBSCRIPTION_TYPES = [
        ('SUBSCRIBED', 'Subscribed Content'),
        ('OPEN_ACCESS', 'Open Access'),
    ]
    title = models.CharField(max_length=200, help_text="e.g. EBSCO Host")
    resource_type = models.CharField(max_length=50, choices=RESOURCE_TYPES)
    subscription_type = models.CharField(max_length=50, choices=SUBSCRIPTION_TYPES)

    def __str__(self):
        return self.title


class Category(models.Model):
    """Dynamic categories managed via the Django Admin panel"""
    name = models.CharField(max_length=100, unique=True, help_text="e.g., E-Book, E-Journal, Software")
    
    class Meta:
        verbose_name_plural = "Categories" # Fixes spelling in the admin panel

    def __str__(self):
        return self.name

class Contract(models.Model):
    """Tracks financial details, dates, and automated status for library resources."""
    
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    
    CURRENCY_CHOICES = [
        ('USD', 'US Dollar ($)'),
        ('ZWG', 'Zimbabwe Gold (ZiG)'),
        ('GBP', 'British Pound (£)'),
    ]

    # Resource Identification
    resource = models.CharField(max_length=200, verbose_name="Resource Name")
    vendor = models.CharField(max_length=200, verbose_name="Vendor Name")
    vendor_email = models.EmailField(blank=True, null=True, help_text="Used for automated alert references.")
    
    # Dates & Financials
    start_date = models.DateField()
    end_date = models.DateField()
    cost = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='USD')
    
    # File Management
    pdf_contract = models.FileField(upload_to='contracts_pdfs/', blank=True, null=True)
    
    # Alert Tracking (Internal use for the recurring email script)
    last_warning_sent_at = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.resource} ({self.end_date})"

    # ==========================================
    # DYNAMIC PROPERTIES (Calculated on the fly)
    # ==========================================

    @property
    def dynamic_status(self):
        """
        Logic: If today is past end_date, it's Pending Renewal.
        Otherwise, it is automatically Active.
        """
        if self.end_date < timezone.now().date():
            return "PENDING RENEWAL"
        return "ACTIVE"

    @property
    def days_until_expiry(self):
        """Returns the raw number of days left."""
        today = timezone.now().date()
        delta = self.end_date - today
        return delta.days

    @property
    def exact_time_remaining(self):
        """Calculates exact breakdown for the dashboard display."""
        now = timezone.now()
        end_datetime = timezone.make_aware(datetime.combine(self.end_date, time(23, 59, 59)))
        
        if end_datetime < now:
            return "Expired"
            
        delta = end_datetime - now
        days = delta.days
        years = days // 365
        remaining_days = days % 365
        months = remaining_days // 30
        days_left = remaining_days % 30
        
        hours, remainder = divmod(delta.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        
        parts = []
        if years > 0: parts.append(f"{years}y")
        if months > 0: parts.append(f"{months}m")
        if days_left > 0: parts.append(f"{days_left}d")
        if hours > 0: parts.append(f"{hours}h")
        if minutes > 0: parts.append(f"{minutes}m")
        
        return " ".join(parts) if parts else "< 1m"

    # ==========================================
    # MODEL METHODS (Logic for saving/renewing)
    # ==========================================

    def save(self, *args, **kwargs):
        """
        Custom save logic to handle 'Renewal'.
        If the end_date is increased, we reset the alert tracker.
        """
        if self.pk: # If this is an update, not a new creation
            old_version = Contract.objects.get(pk=self.pk)
            # If the user extended the date
            if self.end_date > old_version.end_date:
                # Reset the alert system so they get fresh warnings next year
                self.last_warning_sent_at = None
        
        super().save(*args, **kwargs)