from django.core.paginator import Paginator
from django.utils.timezone import make_aware
from datetime import datetime, timedelta


class YourModelAdmin(admin.ModelAdmin):
    # Existing code...

    def changelist_view(self, request, extra_context=None):
        queryset = self.get_queryset(request)
        today = datetime.today()

        # Filter today's orders for sales calculations
        total_order_revenue = queryset.filter(
            is_ordered=True, deleted=False, date__date=today
        )

        # Calculate total revenue
        total_revenue = sum(
            order.get_total_with_delivery() for order in total_order_revenue
        )

        # Prepare extra context data
        extra_context = extra_context or {}
        extra_context["total_orders"] = queryset.filter(is_ordered=True).count()
        extra_context["pending_orders"] = queryset.filter(is_ordered=False).count()
        extra_context["user_cancelled"] = queryset.filter(user_cancelled=True).count()
        extra_context["delivered_orders"] = queryset.filter(
            is_delivered=True, is_ordered=True, is_received=True
        ).count()
        extra_context["undelivered_orders"] = queryset.filter(
            is_delivered=False, is_ordered=True, is_received=False
        ).count()
        extra_context["total_revenue"] = total_revenue

        # Calculate sales data by date
        start_date = make_aware(
            datetime.combine(today - timedelta(days=7), datetime.min.time())
        )  # Past 7 days
        end_date = make_aware(datetime.combine(today, datetime.max.time()))
        sales_data = (
            queryset.filter(date__range=[start_date, end_date], is_ordered=True)
            .values("date__date")  # Group by date
            .annotate(total_quantity=Sum("quantity"))  # Sum the quantities
            .order_by("date__date")
        )

        # Pagination setup
        paginator = Paginator(sales_data, 10)  # Show 10 sales per page
        page_number = request.GET.get("page", 1)
        page_obj = paginator.get_page(page_number)

        # Prepare data for chart
        sales_dates = [
            item["date__date"].strftime("%Y-%m-%d") for item in page_obj
        ]  # Format dates for chart
        sales_quantities = [
            item["total_quantity"] for item in page_obj
        ]  # Get quantities

        # Pass sales data to template
        extra_context["sales_dates"] = sales_dates
        extra_context["sales_quantities"] = sales_quantities
        extra_context["page_obj"] = page_obj  # Pass pagination object to template

        # Call the parent changelist_view
        return super().changelist_view(request, extra_context=extra_context)
