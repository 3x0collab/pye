from django.urls import path, include
from . import views
from django.contrib.auth.views import LoginView

urlpatterns = [
    path('customerclick', views.customerclick_view,name='customerclick'),
    #path('customersignup1', views.customer_signup_view,name='customersignup1'),
    #path('customer-dashboard1', views.customer_dashboard_view,name='customer-dashboard1'),
    path('dashboard', views.customer_dashboard_view,name='customer-dashboard'),
    path('gopro', views.customer_gopro_view,name='customer-gopro'),
    #path('customerlogin1', LoginView.as_view(template_name='backoffice/adminlogin.html'),name='customerlogin1'),
    path('login', LoginView.as_view(template_name='home/sign-in.html'),name='login'),
    path('process_payment/', views.process_payment, name='process_payment'),
    path('register', views.customer_signup_view,name='register'),
    path('paypal', include('paypal.standard.ipn.urls')),
    path('profile', views.profile_view,name='profile'),
    path('select-source/<int:pk>', views.select_source_view,name='select-source'),
    path('select-source-delete/<int:pk>', views.select_source_delete,name='select-source-delete'),
    path('source-credential', views.source_credential_view,name='source-credential'),
    path('virtual-reality', views.virtual_reality_view,name='virtual-reality'),
    path('rtl', views.rtl_view,name='rtl'),
    path('billing', views.billing_view,name='billing'),
    path('download-attendance', views.download_attendance,name='download-attendance'),
    path('download-payslip', views.download_payslip,name='download-payslip'),
    path('download-autorization/<int:pk>', views.download_autorization,name='download-autorization'), 
    path('tasks', views.apply_policy_view,name='apply-policy'),
    path('ai_models', views.ai_models,name='ai_models'),
    path('ai_models/<int:pk>', views.ai_models_bot,name='ai_models_bot'),
    path('chatbot/iframe/<str:api_id>', views.ai_models_bot_iframe,name='ai_models_bot_iframe'),
    path('process_message', views.process_message,name='process_message'),
    path('task-cri', views.new_task_view,name='new_task'),
    path('apply/<int:pk>', views.apply_view,name='apply'),
    path('toggle-email', views.toggle_email_view,name='toggle-email'),
    path('toggle-sms', views.toggle_sms_view,name='toggle-sms'),
    path('toggle-call', views.toggle_call_view,name='toggle-call'),
    path('toggle-whatsapp', views.toggle_whatsapp_view,name='toggle-whatsapp'),
    path('contracts', views.history_view,name='contracts'),
    path('webhook', views.stripe_webhook,name='webhook'),
    path('chatbot', views.chatbot_view,name='chatbot'),
    path('chatbot/delete', views.chatbot_delete,name='chatbot_delete'),
    path('ai_models/delete', views.ai_models_delete,name='ai_models_delete'),
    path('predict', views.predict_view,name='predict'),
    path('delete-contract/<int:pk>', views.delete_contract_view,name='delete-contract'),
    path('delete-card/<int:pk>', views.delete_card_view,name='delete-card'),
    path('delete-car/<int:pk>', views.delete_car_view,name='delete-car'),
    path('delete-question/<int:pk>', views.delete_question_view,name='delete-question'),
    path('checkout/<int:pk>', views.checkout_view,name='checkout'),
    path('coinbase-checkout/<int:pk>', views.coinbase_checkout_view,name='coinbase-checkout'),
    #path('ask-question', views.ask_question_view,name='ask-question'),
    path('transformer', views.question_history_view,name='question-history'),
    path('connector', views.connector_history_view,name='connector-history'),
    path('select_connector', views.select_connector,name='select_connector'),
    path('code_editor', views.code_editor,name='code_editor'),
    path('code_editor/<int:pk>', views.code_editor,name='edit_code_editor'),
    path('delete_code_editor/<int:pk>', views.delete_code_editor,name='delete_code_editor'),
    path('history', views.history_view, name='history'), 
path('subscribe/', views.subscribe, name='subscribe'),
path('get_chatbot_data/', views.get_chatbot_data, name='get_chatbot_data'),
    path(route='course', view=views.movie_recommendation_view, name='recommendations'),

]