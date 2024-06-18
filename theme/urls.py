"""zanex URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path("", views.login, name='index'),

    path("about", views.about, name='about'),

    path("accordion", views.accordion, name='accordion'),

    path("alerts", views.alerts, name='alerts'),

    path("avatarradius", views.avatarradius, name='avatarradius'),

    path("avatarround", views.avatarround, name='avatarround'),

    path("avatarsquare", views.avatarsquare, name='avatarsquare'),

    path("badge", views.badge, name='badge'),

    path("blog", views.blog, name='blog'),

    path("breadcrumbs", views.breadcrumbs, name='breadcrumbs'),

    path("buttons", views.buttons, name='buttons'),

    path("calendar", views.calendar, name='calendar'),

    path("calendar2", views.calendar2, name='calendar2'),

    path("cards", views.cards, name='cards'),

    path("carousel", views.carousel, name='carousel'),

    path("cart", views.cart, name='cart'),

    path("chart", views.chart, name='chart'),

    path("chartchartist", views.chartchartist, name='chartchartist'),

    path("chartdonut", views.chartdonut, name='chartdonut'),

    path("chartechart", views.chartechart, name='chartechart'),

    path("chartflot", views.chartflot, name='chartflot'),

    path("chartline", views.chartline, name='chartline'),

    path("chartmorris", views.chartmorris, name='chartmorris'),

    path("chartnvd3", views.chartnvd3, name='chartnvd3'),

    path("chartpie", views.chartpie, name='chartpie'),

    path("charts", views.charts, name='charts'),

    path("chat", views.chat, name='chat'),

    path("checkout", views.checkout, name='checkout'),

    path("colors", views.colors, name='colors'),

    path("construction", views.construction, name='construction'),

    path("counters", views.counters, name='counters'),

    path("cryptocurrencies", views.cryptocurrencies, name='cryptocurrencies'),

    path("datatable", views.datatable, name='datatable'),

    path("dropdown", views.dropdown, name='dropdown'),

    path("editprofile", views.editprofile, name='editprofile'),

    path("email", views.email, name='email'),

    path("emailservices", views.emailservices, name='emailservices'),

    path("empty", views.empty, name='empty'),

    path("error400", views.error400, name='error400'),

    path("error401", views.error401, name='error401'),

    path("error403", views.error403, name='error403'),

    path("error404", views.error404, name='error404'),

    path("error500", views.error500, name='error500'),

    path("error503", views.error503, name='error503'),

    path("faq", views.faq, name='faq'),

    path("footers", views.footers, name='footers'),

    path("forgotpassword", views.forgotpassword, name='forgotpassword'),

    path("formadvanced", views.formadvanced, name='formadvanced'),

    path("formelements", views.formelements, name='formelements'),

    path("formvalidation", views.formvalidation, name='formvalidation'),

    path("formwizard", views.formwizard, name='formwizard'),

    path("gallery", views.gallery, name='gallery'),

    path("headers", views.headers, name='headers'),

    path("icons", views.icons, name='icons'),

    path("icons2", views.icons2, name='icons2'),

    path("icons3", views.icons3, name='icons3'),

    path("icons4", views.icons4, name='icons4'),

    path("icons5", views.icons5, name='icons5'),

    path("icons6", views.icons6, name='icons6'),

    path("icons7", views.icons7, name='icons7'),

    path("icons8", views.icons8, name='icons8'),

    path("icons9", views.icons9, name='icons9'),

    path("icons10", views.icons10, name='icons10'),

    path("index", views.index, name='index'),

    path("invoice", views.invoice, name='invoice'),

    path("list", views.list, name='list'),

    path("loaders", views.loaders, name='loaders'),

    path("lockscreen", views.lockscreen, name='lockscreen'),

    path("login", views.login, name='login'),

    path("maps", views.maps, name='maps'),

    path("maps1", views.maps1, name='maps1'),

    path("maps2", views.maps2, name='maps2'),

    path("mediaobject", views.mediaobject, name='mediaobject'),

    path("modal", views.modal, name='modal'),

    path("navigation", views.navigation, name='navigation'),

    path("notify", views.notify, name='notify'),

    path("pagination", views.pagination, name='pagination'),

    path("panels", views.panels, name='panels'),

    path("pricing", views.pricing, name='pricing'),

    path("profile", views.profile, name='profile'),

    path("progress", views.progress, name='progress'),

    path("rangeslider", views.rangeslider, name='rangeslider'),

    path("rating", views.rating, name='rating'),

    path("register", views.register, name='register'),

    path("scroll", views.scroll, name='scroll'),

    path("search", views.search, name='search'),

    path("services", views.services, name='services'),

    path("shop", views.shop, name='shop'),

    path("shopdescription", views.shopdescription, name='shopdescription'),

    path("sweetalert", views.sweetalert, name='sweetalert'),

    path("tables", views.tables, name='tables'),

    path("tabs", views.tabs, name='tabs'),

    path("tags", views.tags, name='tags'),

    path("terms", views.terms, name='terms'),

    path("thumbnails", views.thumbnails, name='thumbnails'),

    path("timeline", views.timeline, name='timeline'),

    path("tooltipandpopover", views.tooltipandpopover, name='tooltipandpopover'),

    path("treeview", views.treeview, name='treeview'),

    path("typography", views.typography, name='typography'),

    path("userslist", views.userslist, name='userslist'),

    path("widgets", views.widgets, name='widgets'),

    path("wishlist", views.wishlist, name='wishlist'),

    path("wysiwyag", views.wysiwyag, name='wysiwyag'),

    #employer list
    path("employer-list", views.employer_list, name='employer-list'),
]
