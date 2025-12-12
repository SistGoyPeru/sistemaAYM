
from django.urls import path
from . import views

urlpatterns = [
    path('ordenes/<int:pk>/autorizar/', views.orden_compra_autorizar, name='orden_compra_autorizar'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('requisiciones/', views.solicitud_requisicion_list, name='solicitud_requisicion_list'),
    path('requisiciones/nueva/', views.solicitud_requisicion_create, name='solicitud_requisicion_create'),
    path('requisiciones/<int:pk>/', views.solicitud_requisicion_detail, name='solicitud_requisicion_detail'),
    path('requisiciones/<int:pk>/aprobar/', views.solicitud_requisicion_aprobar, name='solicitud_requisicion_aprobar'),
    path('requisiciones/<int:pk>/rechazar/', views.solicitud_requisicion_rechazar, name='solicitud_requisicion_rechazar'),
    path('ordenes/', views.orden_compra_list, name='orden_compra_list'),
    path('ordenes/nueva/', views.orden_compra_create, name='orden_compra_create'),
    path('ordenes/<int:pk>/', views.orden_compra_detail, name='orden_compra_detail'),
    path('ordenes/<int:pk>/estado/<str:nuevo_estado>/', views.orden_compra_cambiar_estado, name='orden_compra_cambiar_estado'),
    path('ordenes/<int:orden_id>/recepcion/', views.recepcion_mercancia_create, name='recepcion_mercancia_create'),
    # Facturas de proveedor
    path('ordenes/<int:orden_id>/facturas/', views.factura_proveedor_list, name='factura_proveedor_list'),
    path('ordenes/<int:orden_id>/facturas/nueva/', views.factura_proveedor_create, name='factura_proveedor_create'),
    path('facturas/<int:factura_id>/validar/', views.factura_proveedor_validar, name='factura_proveedor_validar'),
    # Reportes
    path('reportes/ordenes/', views.reporte_ordenes_compra, name='reporte_ordenes_compra'),
    path('ajax/sugerir_ultimo_costo/', views.sugerir_ultimo_costo, name='sugerir_ultimo_costo'),
    path('reportes/ordenes/exportar/', views.exportar_ordenes_compra_csv, name='exportar_ordenes_compra_csv'),
    path('reportes/recepciones/', views.reporte_recepciones, name='reporte_recepciones'),
    path('reportes/recepciones/exportar/', views.exportar_recepciones_csv, name='exportar_recepciones_csv'),
    path('reportes/historial_costos/', views.reporte_historial_costos, name='reporte_historial_costos'),
    path('reportes/historial_costos/exportar/', views.exportar_historial_costos_csv, name='exportar_historial_costos_csv'),
    path('reportes/pedidos_pendientes/', views.reporte_pedidos_pendientes, name='reporte_pedidos_pendientes'),
    path('reportes/pedidos_pendientes/exportar/', views.exportar_pedidos_pendientes_csv, name='exportar_pedidos_pendientes_csv'),
    path('ajax/proveedor_info/', views.proveedor_info, name='proveedor_info'),
]
