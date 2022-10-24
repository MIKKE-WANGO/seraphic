from django.urls import path,include
from .views import *


urlpatterns = [
  #path('pdf_view', pdf_view,),
  path('register', RegisterView.as_view()),
  path('user-details', RetrieveUserView.as_view()),
  path('request-reset-code', SendResetPasswordCode.as_view()),
  path('test-code', TesCode.as_view()),
  path('reset-password', ResetPassword.as_view()),
  path('event', ManageEvent.as_view()),
  path('quote-view', QuoteView.as_view()),
  path('get-quotations-list', QuotationList.as_view()),
  path('delete-event', DeleteEvent.as_view()),
  path('products', ProductsCategoryView.as_view()),
  path('tent/<str:pk>', TentView.as_view()),
  path('chair/<str:pk>', ChairView.as_view()),
  path('table/<str:pk>', TableView.as_view()),
  path('decor/<str:pk>', DecorView.as_view()),
  path('budget', BudgetLeft.as_view()),
  path('review', Review.as_view()),
  path('submit-quote', SubmitQuote.as_view()),
  path('addeventproduct', AddProductToEvent.as_view()),
  
  
]