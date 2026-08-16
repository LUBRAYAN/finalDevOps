from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from django.db import models
from django.db import connection
from django.db.utils import OperationalError
from django.conf import settings
from datetime import datetime
import time
import platform
import sys
from .models import Producto
from .serializers import ProductoSerializer  # Solo usar este serializer


class ProductoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar productos.
    Proporciona CRUD completo con búsqueda y filtros.
    """
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer  # Usar siempre ProductoSerializer
    parser_classes = [JSONParser]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['codigo', 'nombre', 'descripcion']
    ordering_fields = ['codigo', 'nombre', 'precio', 'fecha_creacion']
    ordering = ['-fecha_creacion']

    # ELIMINA este método para que siempre use el mismo serializer
    # def get_serializer_class(self):
    #     if self.action == 'list':
    #         return ProductoListSerializer
    #     return ProductoSerializer

    def get_queryset(self):
        """
        Filtros personalizados sin django-filter
        """
        queryset = Producto.objects.all()
        
        # Filtrar por código
        codigo = self.request.query_params.get('codigo', None)
        if codigo:
            queryset = queryset.filter(codigo__icontains=codigo)
        
        # Filtrar por nombre
        nombre = self.request.query_params.get('nombre', None)
        if nombre:
            queryset = queryset.filter(nombre__icontains=nombre)
        
        # Filtrar por activo (true/false)
        activo = self.request.query_params.get('activo', None)
        if activo is not None:
            if activo.lower() == 'true':
                queryset = queryset.filter(activo=True)
            elif activo.lower() == 'false':
                queryset = queryset.filter(activo=False)
        
        # Filtrar por precio mínimo
        precio_min = self.request.query_params.get('precio_min', None)
        if precio_min:
            try:
                queryset = queryset.filter(precio__gte=float(precio_min))
            except ValueError:
                pass
        
        # Filtrar por precio máximo
        precio_max = self.request.query_params.get('precio_max', None)
        if precio_max:
            try:
                queryset = queryset.filter(precio__lte=float(precio_max))
            except ValueError:
                pass
        
        return queryset

    # =============================================
    # ENDPOINTS DE SALUD
    # =============================================

    @action(detail=False, methods=['get'], url_path='health')
    def health_check(self, request):
        """
        Endpoint de salud para verificar el estado completo de la API
        """
        start_time = time.time()
        
        # Obtener el nombre de la base de datos como string
        db_name = settings.DATABASES['default']['NAME']
        if hasattr(db_name, '__str__'):
            db_name = str(db_name)
        
        health_info = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'service': {
                'name': 'productos-api',
                'version': '1.0.0',
                'environment': getattr(settings, 'ENVIRONMENT', 'development')
            },
            'database': {
                'status': 'checking',
                'type': settings.DATABASES['default']['ENGINE'].split('.')[-1],
                'name': db_name
            },
            'system': {
                'platform': platform.platform(),
                'python_version': sys.version.split()[0],
                'timezone': settings.TIME_ZONE
            }
        }
        
        # Verificar conexión a la base de datos
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                health_info['database']['status'] = 'connected'
                health_info['database']['response_time'] = round(
                    (time.time() - start_time) * 1000, 2
                )
        except OperationalError as e:
            health_info['status'] = 'unhealthy'
            health_info['database']['status'] = 'disconnected'
            health_info['database']['error'] = str(e)
            return Response(health_info, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except Exception as e:
            health_info['status'] = 'degraded'
            health_info['database']['status'] = 'error'
            health_info['database']['error'] = str(e)
            return Response(health_info, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Verificar dependencias críticas
        health_info['dependencies'] = {
            'rest_framework': 'active',
            'cors_headers': 'active' if 'corsheaders' in settings.INSTALLED_APPS else 'inactive'
        }
        
        health_info['response_time_ms'] = round(
            (time.time() - start_time) * 1000, 2
        )
        
        return Response(health_info, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='ping')
    def ping(self, request):
        """
        Endpoint simple para verificar que la API está activa
        """
        return Response({
            'status': 'ok',
            'timestamp': datetime.now().isoformat(),
            'message': 'pong'
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='readiness')
    def readiness(self, request):
        """
        Endpoint de readiness (listo para recibir tráfico)
        """
        health_info = {
            'status': 'ready',
            'timestamp': datetime.now().isoformat(),
            'checks': {
                'database': {
                    'status': 'checking'
                }
            }
        }
        
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            health_info['checks']['database']['status'] = 'pass'
        except:
            health_info['checks']['database']['status'] = 'fail'
            return Response(health_info, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        return Response(health_info, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='liveness')
    def liveness(self, request):
        """
        Endpoint de liveness (la aplicación está viva)
        """
        return Response({
            'status': 'alive',
            'timestamp': datetime.now().isoformat()
        }, status=status.HTTP_200_OK)

    # =============================================
    # ENDPOINTS DE PRODUCTOS
    # =============================================

    @action(detail=False, methods=['get'])
    def activos(self, request):
        """
        Endpoint para obtener solo productos activos
        """
        productos = Producto.objects.filter(activo=True)
        serializer = self.get_serializer(productos, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def buscar(self, request):
        """
        Endpoint personalizado para búsqueda avanzada
        """
        query = request.query_params.get('q', '')
        if query:
            productos = Producto.objects.filter(
                models.Q(codigo__icontains=query) |
                models.Q(nombre__icontains=query) |
                models.Q(descripcion__icontains=query)
            )
            serializer = self.get_serializer(productos, many=True)
            return Response(serializer.data)
        return Response(
            {'error': 'Parámetro de búsqueda "q" requerido'}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    # =============================================
    # CRUD CON VALIDACIONES
    # =============================================

    def create(self, request, *args, **kwargs):
        """
        Crear producto con validaciones adicionales
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            codigo = serializer.validated_data.get('codigo')
            if Producto.objects.filter(codigo=codigo).exists():
                return Response(
                    {'error': f'Ya existe un producto con el código {codigo}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        """
        Actualizar producto con validación de código único
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        if serializer.is_valid():
            codigo = serializer.validated_data.get('codigo')
            if codigo and Producto.objects.filter(codigo=codigo).exclude(id=instance.id).exists():
                return Response(
                    {'error': f'Ya existe otro producto con el código {codigo}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            self.perform_update(serializer)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        """
        Eliminar producto (override para manejar errores)
        """
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response(
                {'mensaje': 'Producto eliminado correctamente'},
                status=status.HTTP_204_NO_CONTENT
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['patch'])
    def toggle_activo(self, request, pk=None):
        """
        Activar/desactivar producto
        """
        try:
            producto = self.get_object()
            producto.activo = not producto.activo
            producto.save()
            return Response({
                'id': producto.id,
                'codigo': producto.codigo,
                'nombre': producto.nombre,
                'activo': producto.activo,
                'mensaje': f'Producto {"activado" if producto.activo else "desactivado"} correctamente'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )