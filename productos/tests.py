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
    """

    def setUp(self):
        """Configuración inicial - Crear datos de prueba"""
        self.client = APIClient()
        
        self.list_url = reverse('producto-list')
        self.detail_url = lambda pk: reverse('producto-detail', args=[pk])
        
        # Crear productos de prueba
        self.producto1 = Producto.objects.create(
            codigo="P001",
            nombre="Laptop",
            descripcion="Laptop 16GB RAM",
            precio=799.99,
            activo=True
        )
        
        self.producto2 = Producto.objects.create(
            codigo="P002",
            nombre="Mouse Logitech",
            descripcion="Mouse inalámbrico",
            precio=29.99,
            activo=True
        )
        
        self.producto3 = Producto.objects.create(
            codigo="P003",
            nombre="Monitor Samsung",
            descripcion="Monitor 24 pulgadas",
            precio=199.99,
            activo=True
        )
        
        self.producto4 = Producto.objects.create(
            codigo="P004",
            nombre="Teclado Mecánico",
            descripcion="Teclado RGB",
            precio=89.99,
            activo=True
        )
        
        self.producto5 = Producto.objects.create(
            codigo="P005",
            nombre="Disco Ssd",
            descripcion="SSD 1TB",
            precio=129.99,
            activo=True
        )
        
        self.producto6 = Producto.objects.create(
            codigo="P010",
            nombre="Mouse Rgb",
            descripcion=None,
            precio=20.00,
            activo=True
        )

    def test_listar_productos(self):
        """Prueba: Verificar que la lista de productos retorna correctamente"""
        response = self.client.get(self.list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 6)

    def test_verificar_producto_laptop(self):
        """Prueba: Verificar que el producto Laptop existe con los datos correctos"""
        response = self.client.get(self.detail_url(self.producto1.id))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['codigo'], 'P001')
        self.assertEqual(response.data['nombre'], 'Laptop')
        self.assertEqual(response.data['descripcion'], 'Laptop 16GB RAM')
        self.assertEqual(response.data['precio'], '799.99')
        self.assertTrue(response.data['activo'])

    def test_verificar_producto_mouse_logitech(self):
        """Prueba: Verificar que el producto Mouse Logitech existe"""
        response = self.client.get(self.detail_url(self.producto2.id))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['codigo'], 'P002')
        self.assertEqual(response.data['nombre'], 'Mouse Logitech')
        self.assertEqual(response.data['descripcion'], 'Mouse inalámbrico')
        self.assertEqual(response.data['precio'], '29.99')

    def test_verificar_producto_mouse_rgb(self):
        """Prueba: Verificar que el producto Mouse Rgb tiene descripción nula"""
        response = self.client.get(self.detail_url(self.producto6.id))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['codigo'], 'P010')
        self.assertEqual(response.data['nombre'], 'Mouse Rgb')
        self.assertIsNone(response.data['descripcion'])
        self.assertEqual(response.data['precio'], '20.00')

    def test_crear_producto(self):
        """Prueba: Crear un nuevo producto"""
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
        self.assertEqual(Producto.objects.count(), count_before + 1)

    def test_crear_producto_codigo_duplicado(self):
        """Prueba: Intentar crear producto con código existente (debe fallar)"""
        data = {
            "codigo": "P001",
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
        self.assertIn('codigo', response.data)

    def test_actualizar_producto(self):
        """Prueba: Actualizar un producto existente"""
        url = self.detail_url(self.producto3.id)
        
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
        self.producto3.refresh_from_db()
        self.assertEqual(self.producto3.nombre, 'Monitor Samsung 4K')

    def test_actualizar_parcialmente(self):
        """
        Prueba: Actualizar solo el precio de un producto
        """
        url = self.detail_url(self.producto4.id)
        
        data = {
            "codigo": "P004",
            "nombre": "Teclado Mecánico",
            "descripcion": "Teclado RGB",
            "precio": 69.99, #Cambió el precio
            "activo": True
        }
        
        response = self.client.patch(
            url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.producto4.refresh_from_db()
        self.assertEqual(float(self.producto4.precio), 69.99)

    def test_buscar_por_codigo(self):
        """Prueba: Buscar productos por código"""
        url = f"{self.list_url}buscar/?q=P001"
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_buscar_por_nombre(self):
        """Prueba: Buscar productos por nombre"""
        url = f"{self.list_url}buscar/?q=Mouse"
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_buscar_por_descripcion(self):
        """Prueba: Buscar productos por descripción"""
        url = f"{self.list_url}buscar/?q=SSD"
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_buscar_sin_resultados(self):
        """Prueba: Búsqueda sin resultados"""
        url = f"{self.list_url}buscar/?q=inexistente"
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_filtrar_por_precio_minimo(self):
        """Prueba: Filtrar productos con precio >= 100"""
        url = f"{self.list_url}?precio_min=100"
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)

    def test_filtrar_por_precio_maximo(self):
        """Prueba: Filtrar productos con precio <= 50"""
        url = f"{self.list_url}?precio_max=50"
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)

    def test_filtrar_por_rango_precio(self):
        """Prueba: Filtrar productos en rango de precio"""
        url = f"{self.list_url}?precio_min=80&precio_max=150"
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)

    def test_ordenar_por_precio_ascendente(self):
        """Prueba: Ordenar productos por precio ascendente"""
        url = f"{self.list_url}?ordering=precio"
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        precios = [float(item['precio']) for item in response.data['results']]
        self.assertEqual(precios, sorted(precios))
        self.assertEqual(response.data['results'][0]['nombre'], 'Mouse Rgb')

    def test_ordenar_por_precio_descendente(self):
        """Prueba: Ordenar productos por precio descendente"""
        url = f"{self.list_url}?ordering=-precio"
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        precios = [float(item['precio']) for item in response.data['results']]
        self.assertEqual(precios, sorted(precios, reverse=True))
        self.assertEqual(response.data['results'][0]['nombre'], 'Laptop')

    def test_ordenar_por_nombre(self):
        """Prueba: Ordenar productos por nombre alfabéticamente"""
        url = f"{self.list_url}?ordering=nombre"
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        nombres = [item['nombre'] for item in response.data['results']]
        self.assertEqual(nombres, sorted(nombres))

    def test_toggle_activo_desactivar(self):
        """Prueba: Desactivar un producto"""
        self.assertTrue(self.producto2.activo)
        
        url = reverse('producto-toggle-activo', args=[self.producto2.id])
        response = self.client.patch(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.producto2.refresh_from_db()
        self.assertFalse(self.producto2.activo)

    def test_toggle_activo_reactivar(self):
        """Prueba: Reactivar un producto previamente desactivado"""
        url = reverse('producto-toggle-activo', args=[self.producto3.id])
        
        response = self.client.patch(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.producto3.refresh_from_db()
        self.assertFalse(self.producto3.activo)
        
        response = self.client.patch(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.producto3.refresh_from_db()
        self.assertTrue(self.producto3.activo)

    def test_validar_precio_negativo(self):
        """Prueba: No permitir precios negativos"""
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
        """Prueba: No permitir código vacío"""
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

    def test_eliminar_producto(self):
        """Prueba: Eliminar un producto"""
        count_before = Producto.objects.count()
        url = self.detail_url(self.producto6.id)
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Producto.objects.count(), count_before - 1)

    def test_health_check(self):
        """Prueba: Verificar el endpoint de salud"""
        response = self.client.get('/api/productos/health/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'healthy')

    def test_ping(self):
        """Prueba: Verificar el endpoint ping"""
        response = self.client.get('/api/productos/ping/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'ok')

    def test_cantidad_total_productos(self):
        """Prueba: Verificar que hay exactamente 6 productos"""
        count = Producto.objects.count()
        self.assertEqual(count, 6)

    def test_todos_los_productos_estan_activos(self):
        """Prueba: Verificar que todos los productos están activos"""
        productos = Producto.objects.all()
        for producto in productos:
            self.assertTrue(producto.activo)

    def test_codigos_formateados(self):
        """Prueba: Verificar que los códigos están en mayúsculas"""
        productos = Producto.objects.all()
        for producto in productos:
            self.assertEqual(producto.codigo, producto.codigo.upper())

    def test_nombres_formateados(self):
        """Prueba: Verificar que los nombres tienen formato título"""
        laptop = Producto.objects.get(codigo='P001')
        self.assertEqual(laptop.nombre, 'Laptop')
        
        mouse = Producto.objects.get(codigo='P002')
        self.assertEqual(mouse.nombre, 'Mouse Logitech')


class ModelProductoTestCase(TestCase):
    """
    Pruebas para el modelo Producto
    """

    def setUp(self):
        self.producto = Producto.objects.create(
            codigo="TEST001",
            nombre="Producto de Prueba",
            descripcion="Descripción de prueba",
            precio=99.99,
            activo=True
        )

    def test_str_method(self):
        """Prueba: Verificar el método __str__ del modelo"""
        expected_str = "TEST001 - Producto De Prueba"
        self.assertEqual(str(self.producto), expected_str)

    def test_auto_fechas(self):
        """Prueba: Verificar que las fechas se generan automáticamente"""
        self.assertIsNotNone(self.producto.fecha_creacion)
        self.assertIsNotNone(self.producto.fecha_actualizacion)

    def test_descripcion_nula(self):
        """Prueba: Verificar que la descripción puede ser nula"""
        producto = Producto.objects.create(
            codigo="TEST002",
            nombre="Producto sin descripción",
            precio=50.00,
            descripcion=None
        )
        self.assertIsNone(producto.descripcion)

    def test_codigo_mayusculas(self):
        """Prueba: Verificar que el código se guarda en mayúsculas"""
        producto = Producto.objects.create(
            codigo="test003",
            nombre="Otro Producto",
            precio=50.00
        )
        self.assertEqual(producto.codigo, "TEST003")

    def test_activo_por_defecto(self):
        """Prueba: Verificar que el campo activo es True por defecto"""
        producto = Producto.objects.create(
            codigo="TEST004",
            nombre="Nuevo Producto",
            precio=50.00
        )
        self.assertTrue(producto.activo)