from django.contrib import admin
from django.utils.html import format_html
from .models import Contract, Category  # Added Category here

# 1. Register the new Category model
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

# 2. Update ContractAdmin to include categories
@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    # ADDED: 'category' to the display columns
    list_display = ('resource', 'category', 'vendor', 'start_date', 'end_date', 'expiry_status', 'cost', 'currency')
    
    # ADDED: 'category' to the sidebar filters
    list_filter = ('category', 'currency', 'end_date')
    
    # ADDED: 'category__name' so you can type "Software" in the search bar and find all software contracts
    search_fields = ('resource', 'vendor', 'category__name')
    
    ordering = ['end_date']
    
    def expiry_status(self, obj):
        days_left = obj.days_until_expiry
        
        if days_left < 0:
            color = 'black'
            msg = 'EXPIRED'
        elif days_left <= 30:
            color = 'red'
            msg = f'CRITICAL ({days_left} days)'
        elif days_left <= 90:
            color = 'orange'
            msg = f'Warning ({days_left} days)'
        else:
            color = 'green'
            msg = 'Healthy'

        return format_html(
            '<span style="color: white; background-color: {}; padding: 5px 10px; border-radius: 5px; font-weight: bold;">{}</span>',
            color,
            msg
        )
    
    expiry_status.short_description = 'Status'

# Note: The @admin.register() decorators above replace the need for admin.site.register() at the bottom.