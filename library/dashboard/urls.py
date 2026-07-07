from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('admin/', views.AdminDashboardView.as_view(), name='admin_dashboard'),
    path('member/', views.MemberDashboardView.as_view(), name='member_dashboard'),
    path('reports/', views.PortalReportsView.as_view(), name='portal_reports'),
    path('reports/export/<str:report_type>/<str:format_type>/', views.ExportReportView.as_view(), name='export_report'),
]
