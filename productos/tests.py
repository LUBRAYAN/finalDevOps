# productos/tests.py
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from datetime import datetime
import json
from .models import Producto


class ProductoAPITestCase(TestCase):
    """
    Pruebas automatizadas para la API de Productos
    Basadas en los datos existentes
    """

    def setUp(self):
        """Configuración inicial - No crea datos, usa los existentes"""
        self.client = APIClient()
        
        # URLs para las pruebas
        self.list_url = reverse('producto-list')
        self.detail_url = lambda pk: reverse('producto-detail', args=[pk])
        
        # Datos de prueba basados en los productos existentes, ingresados previamente vía POST
        self.productos_existentes = [
            {
                'id': 1,
                'codigo': 'P001',
                'nombre': 'Laptop',
                'descripcion': 'Laptop 16GB RAM',
                'precio': '799.99',
                'activo': True
            },
            {
                'id': 2,
                'codigo': 'P002',
                'nombre': 'Mouse Logitech',
                'descripcion': 'Mouse inalámbrico',
                'precio': '29.99',
                'activo': True
            },
            {
                'id': 3,
                'codigo': 'P003',
                'nombre': 'Monitor Samsung',
                'descripcion': 'Monitor 24 pulgadas',
                'precio': '199.99',
                'activo': True
            },
            {
                'id': 4,
                'codigo': 'P004',
                'nombre': 'Teclado Mecánico',
                'descripcion': 'Teclado RGB',
                'precio': '89.99',
                'activo': True
            },
            {
                'id': 5,
                'codigo': 'P005',
                'nombre': 'Disco Ssd',
                'descripcion': 'SSD 1TB',
                'precio': '129.99',
                'activo': True
            },
            {
                'id': 6,
                'codigo': 'P010',
                'nombre': 'Mouse Rgb',
                'descripcion': None,
                'precio': '20.00',
                'activo': True
            }
        ]

    # =============================================
    # PRUEBA 1: Listar todos los productos
    # =============================================
    def test_listar_productos(self):
        """
        Prueba: Verificar que la lista de productos retorna correctamente
        """
        response = self.client.get(self.list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 6)  # Deberían ser 6 productos
        
        # Verificar que los IDs coinciden
        ids = [item['id'] for item in response.data['results']]
        self.assertIn(1, ids)  # Laptop
        self.assertIn(2, ids)  # Mouse Logitech
        self.assertIn(3, ids)  # Monitor Samsung
        self.assertIn(4, ids)  # Teclado Mecánico
        self.assertIn(5, ids)  # Disco Ssd
        self.assertIn(6, ids)  # Mouse Rgb

    # =============================================
    # PRUEBA 2: Verificar productos específicos
    # =============================================
    def test_verificar_producto_laptop(self):
        """
        Prueba: Verificar que el producto Laptop existe con los datos correctos
        """
        response = self.client.get(self.detail_url(1))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['codigo'], 'P001')
        self.assertEqual(response.data['nombre'], 'Laptop')
        self.assertEqual(response.data['descripcion'], 'Laptop 16GB RAM')
        self.assertEqual(response.data['precio'], '799.99')
        self.assertTrue(response.data['activo'])

    def test_verificar_producto_mouse_logitech(self):
        """
        Prueba: Verificar que el producto Mouse Logitech existe
        """
        response = self.client.get(self.detail_url(2))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['codigo'], 'P002')
        self.assertEqual(response.data['nombre'], 'Mouse Logitech')
        self.assertEqual(response.data['descripcion'], 'Mouse inalámbrico')
        self.assertEqual(response.data['precio'], '29.99')

    def test_verificar_producto_mouse_rgb(self):
        """
        Prueba: Verificar que el producto Mouse Rgb tiene descripción nula
        """
        response = self.client.get(self.detail_url(6))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['codigo'], 'P010')
        self.assertEqual(response.data['nombre'], 'Mouse Rgb')
        self.assertIsNone(response.data['descripcion'])
        self.assertEqual(response.data['precio'], '20.00')

    # =============================================
    # PRUEBA 3: Crear nuevo producto
    # =============================================
    def test_crear_producto(self):
        """
        Prueba: Crear un nuevo producto (debe incrementar el conteo)
        """
        # Contar productos antes
        count_before = Producto.objects.count()
        
        data = {
            "codigo": "P011",
            "nombre": "Audífonos Sony",
            "descripcion": "Audífonos con cancelación de ruido",
            "precio": 149.99
        }
        
        response = self.client.post(
            self.list_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verificar que el conteo aumentó
        count_after = Producto.objects.count()
        self.assertEqual(count_after, count_before + 1)
        
        # Verificar que el producto se creó correctamente
        nuevo_producto = Producto.objects.get(codigo='P011')
        self.assertEqual(nuevo_producto.nombre, 'Audífonos Sony')
        self.assertEqual(nuevo_producto.descripcion, 'Audífonos con cancelación de ruido')
        self.assertEqual(float(nuevo_producto.precio), 149.99)

    # =============================================
    # PRUEBA 4: No permitir códigos duplicados
    # =============================================
    def test_crear_producto_codigo_duplicado(self):
        """
        Prueba: Intentar crear producto con código existente (debe fallar)
        """
        data = {
            "codigo": "P001",  # Código ya existente (Laptop)
            "nombre": "Producto Duplicado",
            "descripcion": "Este producto tiene código duplicado",
            "precio": 100.00
        }
        
        response = self.client.post(
            self.list_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Ya existe un producto con el código P001')

    # =============================================
    # PRUEBA 5: Actualizar producto existente
    # =============================================
    def test_actualizar_producto(self):
        """
        Prueba: Actualizar un producto existente
        """
        # Obtener el producto Monitor Samsung
        producto = Producto.objects.get(codigo='P003')
        url = self.detail_url(producto.id)
        
        data = {
            "codigo": "P003",
            "nombre": "Monitor Samsung 4K",
            "descripcion": "Monitor 27 pulgadas 4K",
            "precio": 399.99
        }
        
        response = self.client.put(
            url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar que se actualizó correctamente
        producto.refresh_from_db()
        self.assertEqual(producto.nombre, 'Monitor Samsung 4K')
        self.assertEqual(producto.descripcion, 'Monitor 27 pulgadas 4K')
        self.assertEqual(float(producto.precio), 399.99)

    # =============================================
    # PRUEBA 6: Actualizar parcialmente
    # =============================================
    def test_actualizar_parcialmente(self):
        """
        Prueba: Actualizar solo el precio de un producto
        """
        producto = Producto.objects.get(codigo='P004')  # Teclado Mecánico
        url = self.detail_url(producto.id)
        
        data = {
            "precio": 69.99  # Solo actualizar precio
        }
        
        response = self.client.patch(
            url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        producto.refresh_from_db()
        self.assertEqual(float(producto.precio), 69.99)
        self.assertEqual(producto.nombre, 'Teclado Mecánico')  # Sin cambios

    # =============================================
    # PRUEBA 7: Buscar productos
    # =============================================
    def test_buscar_por_codigo(self):
        """
        Prueba: Buscar productos por código
        """
        url = f"{self.list_url}buscar/?q=P001"
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['codigo'], 'P001')
        self.assertEqual(response.data[0]['nombre'], 'Laptop')

    def test_buscar_por_nombre(self):
        """
        Prueba: Buscar productos por nombre
        """
        url = f"{self.list_url}buscar/?q=Mouse"
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Mouse Logitech y Mouse Rgb
        
        nombres = [item['nombre'] for item in response.data]
        self.assertIn('Mouse Logitech', nombres)
        self.assertIn('Mouse Rgb', nombres)

    def test_buscar_por_descripcion(self):
        """
        Prueba: Buscar productos por descripción
        """
        url = f"{self.list_url}buscar/?q=SSD"
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['codigo'], 'P005')
        self.assertEqual(response.data[0]['nombre'], 'Disco Ssd')

    def test_buscar_sin_resultados(self):
        """
        Prueba: Búsqueda sin resultados
        """
        url = f"{self.list_url}buscar/?q=inexistente"
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    # =============================================
    # PRUEBA 8: Filtrar productos
    # =============================================
    def test_filtrar_por_precio_minimo(self):
        """
        Prueba: Filtrar productos con precio >= 100
        """
        url = f"{self.list_url}?precio_min=100"
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Deberían ser: Laptop (799.99), Monitor (199.99), Disco SSD (129.99)
        self.assertEqual(response.data['count'], 3)
        
        precios = [float(item['precio']) for item in response.data['results']]
        for precio in precios:
            self.assertTrue(precio >= 100)

    def test_filtrar_por_precio_maximo(self):
        """
        Prueba: Filtrar productos con precio <= 50
        """
        url = f"{self.list_url}?precio_max=50"
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Deberían ser: Mouse Logitech (29.99) y Mouse Rgb (20.00)
        self.assertEqual(response.data['count'], 2)
        
        precios = [float(item['precio']) for item in response.data['results']]
        for precio in precios:
            self.assertTrue(precio <= 50)

    def test_filtrar_por_rango_precio(self):
        """
        Prueba: Filtrar productos en rango de precio
        """
        url = f"{self.list_url}?precio_min=80&precio_max=150"
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Deberían ser: Teclado Mecánico (89.99) y Disco SSD (129.99)
        self.assertEqual(response.data['count'], 2)
        
        nombres = [item['nombre'] for item in response.data['results']]
        self.assertIn('Teclado Mecánico', nombres)
        self.assertIn('Disco Ssd', nombres)

    # =============================================
    # PRUEBA 9: Ordenar productos
    # =============================================
    def test_ordenar_por_precio_ascendente(self):
        """
        Prueba: Ordenar productos por precio ascendente
        """
        url = f"{self.list_url}?ordering=precio"
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        precios = [float(item['precio']) for item in response.data['results']]
        self.assertEqual(precios, sorted(precios))
        
        # El primer producto debería ser Mouse Rgb (20.00)
        self.assertEqual(response.data['results'][0]['nombre'], 'Mouse Rgb')
        self.assertEqual(float(response.data['results'][0]['precio']), 20.00)

    def test_ordenar_por_precio_descendente(self):
        """
        Prueba: Ordenar productos por precio descendente
        """
        url = f"{self.list_url}?ordering=-precio"
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        precios = [float(item['precio']) for item in response.data['results']]
        self.assertEqual(precios, sorted(precios, reverse=True))
        
        # El primer producto debería ser Laptop (799.99)
        self.assertEqual(response.data['results'][0]['nombre'], 'Laptop')
        self.assertEqual(float(response.data['results'][0]['precio']), 799.99)

    def test_ordenar_por_nombre(self):
        """
        Prueba: Ordenar productos por nombre alfabéticamente
        """
        url = f"{self.list_url}?ordering=nombre"
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        nombres = [item['nombre'] for item in response.data['results']]
        self.assertEqual(nombres, sorted(nombres))
        
        # El primer producto alfabéticamente debería ser Disco Ssd
        self.assertEqual(response.data['results'][0]['nombre'], 'Disco Ssd')

    # =============================================
    # PRUEBA 10: Toggle activo/desactivo
    # =============================================
    def test_toggle_activo_desactivar(self):
        """
        Prueba: Desactivar un producto
        """
        # Tomar el producto Mouse Logitech
        producto = Producto.objects.get(codigo='P002')
        self.assertTrue(producto.activo)
        
        url = reverse('producto-toggle-activo', args=[producto.id])
        response = self.client.patch(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        producto.refresh_from_db()
        self.assertFalse(producto.activo)
        self.assertEqual(response.data['activo'], False)
        self.assertEqual(response.data['mensaje'], 'Producto desactivado correctamente')

    def test_toggle_activo_reactivar(self):
        """
        Prueba: Reactivar un producto previamente desactivado
        """
        # Primero desactivar
        producto = Producto.objects.get(codigo='P003')
        url = reverse('producto-toggle-activo', args=[producto.id])
        
        response = self.client.patch(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        producto.refresh_from_db()
        self.assertFalse(producto.activo)
        
        # Luego reactivar
        response = self.client.patch(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        producto.refresh_from_db()
        self.assertTrue(producto.activo)
        self.assertEqual(response.data['mensaje'], 'Producto activado correctamente')

    # =============================================
    # PRUEBA 11: Validaciones
    # =============================================
    def test_validar_precio_negativo(self):
        """
        Prueba: No permitir precios negativos
        """
        data = {
            "codigo": "P999",
            "nombre": "Producto Inválido",
            "descripcion": "Precio negativo",
            "precio": -100.00
        }
        
        response = self.client.post(
            self.list_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('precio', response.data)

    def test_validar_codigo_vacio(self):
        """
        Prueba: No permitir código vacío
        """
        data = {
            "codigo": "",
            "nombre": "Producto sin código",
            "descripcion": "Código vacío",
            "precio": 100.00
        }
        
        response = self.client.post(
            self.list_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_validar_nombre_vacio(self):
        """
        Prueba: No permitir nombre vacío
        """
        data = {
            "codigo": "P999",
            "nombre": "",
            "descripcion": "Nombre vacío",
            "precio": 100.00
        }
        
        response = self.client.post(
            self.list_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # =============================================
    # PRUEBA 12: Eliminar producto
    # =============================================
    def test_eliminar_producto(self):
        """
        Prueba: Eliminar un producto
        """
        # Crear un producto temporal para eliminar
        producto_temp = Producto.objects.create(
            codigo='P999',
            nombre='Producto Temporal',
            precio=10.00
        )
        
        count_before = Producto.objects.count()
        url = self.detail_url(producto_temp.id)
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Producto.objects.count(), count_before - 1)

    # =============================================
    # PRUEBA 13: Endpoints de salud
    # =============================================
    def test_health_check(self):
        """
        Prueba: Verificar el endpoint de salud
        """
        response = self.client.get('/api/productos/health/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'healthy')
        self.assertIn('timestamp', response.data)

    def test_ping(self):
        """
        Prueba: Verificar el endpoint ping
        """
        response = self.client.get('/api/productos/ping/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'ok')
        self.assertEqual(response.data['message'], 'pong')

    def test_version(self):
        """
        Prueba: Verificar el endpoint de versión
        """
        response = self.client.get('/api/productos/version/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('version', response.data)
        self.assertIn('environment', response.data)
        self.assertIn('git', response.data)
        self.assertIn('commit', response.data['git'])
        self.assertIn('branch', response.data['git'])

    # =============================================
    # PRUEBA 14: Datos específicos de tus productos
    # =============================================
    def test_cantidad_total_productos(self):
        """
        Prueba: Verificar que hay exactamente 6 productos
        """
        count = Producto.objects.count()
        self.assertEqual(count, 6)

    def test_todos_los_productos_estan_activos(self):
        """
        Prueba: Verificar que todos los productos están activos
        """
        productos = Producto.objects.all()
        for producto in productos:
            self.assertTrue(producto.activo)

    def test_precios_unicos(self):
        """
        Prueba: Verificar que todos los precios son únicos
        """
        precios = Producto.objects.values_list('precio', flat=True)
        self.assertEqual(len(precios), len(set(precios)))

    def test_codigos_formateados(self):
        """
        Prueba: Verificar que los códigos están en mayúsculas
        """
        productos = Producto.objects.all()
        for producto in productos:
            self.assertEqual(producto.codigo, producto.codigo.upper())

    def test_nombres_formateados(self):
        """
        Prueba: Verificar que los nombres tienen formato título
        """
        # Verificar algunos productos específicos
        laptop = Producto.objects.get(codigo='P001')
        self.assertEqual(laptop.nombre, 'Laptop')
        
        mouse = Producto.objects.get(codigo='P002')
        self.assertEqual(mouse.nombre, 'Mouse Logitech')


class ModelProductoTestCase(TestCase):
    """
    Pruebas para el modelo Producto con datos existentes
    """

    def test_str_method(self):
        """
        Prueba: Verificar el método __str__ del modelo
        """
        producto = Producto.objects.get(codigo='P001')
        expected_str = "P001 - Laptop"
        self.assertEqual(str(producto), expected_str)

    def test_auto_fechas(self):
        """
        Prueba: Verificar que las fechas se generan automáticamente
        """
        producto = Producto.objects.get(codigo='P002')
        self.assertIsNotNone(producto.fecha_creacion)
        self.assertIsNotNone(producto.fecha_actualizacion)

    def test_descripcion_nula(self):
        """
        Prueba: Verificar que la descripción puede ser nula
        """
        producto = Producto.objects.get(codigo='P010')
        self.assertIsNone(producto.descripcion)