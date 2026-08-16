# productos/tests.py
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import User
from .models import Producto
import json

class ProductoAPITestCase(TestCase):
    def setUp(self):
        """Configuración inicial para todas las pruebas"""
        self.client = APIClient()
        
        # Crear productos de prueba
        self.producto1 = Producto.objects.create(
            codigo="P001",
            nombre="Laptop Dell",
            descripcion="Laptop 16GB RAM, 512GB SSD",
            precio=799.99,
            activo=True
        )
        
        self.producto2 = Producto.objects.create(
            codigo="P002",
            nombre="Mouse Logitech",
            descripcion="Mouse inalámbrico ergonómico",
            precio=29.99,
            activo=True
        )
        
        self.producto3 = Producto.objects.create(
            codigo="P003",
            nombre="Monitor Samsung",
            descripcion="Monitor 24 pulgadas Full HD",
            precio=199.99,
            activo=False
        )

        # URLs para las pruebas
        self.list_url = reverse('producto-list')
        self.detail_url = lambda pk: reverse('producto-detail', args=[pk])

    # ============ PRUEBA 1: Listar productos ============
    def test_listar_productos(self):
        """
        Prueba: Verificar que la lista de productos retorna correctamente
        """
        response = self.client.get(self.list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)  # Total de productos
        self.assertEqual(len(response.data['results']), 3)  # Productos en página actual
        
        # Verificar que los productos estén ordenados correctamente
        first_product = response.data['results'][0]
        self.assertEqual(first_product['codigo'], self.producto1.codigo)
        self.assertEqual(first_product['nombre'], self.producto1.nombre)

    # ============ PRUEBA 2: Crear producto ============
    def test_crear_producto(self):
        """
        Prueba: Crear un nuevo producto correctamente
        """
        data = {
            "codigo": "P004",
            "nombre": "Teclado Mecánico",
            "descripcion": "Teclado mecánico RGB",
            "precio": 89.99
        }
        
        response = self.client.post(
            self.list_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Producto.objects.count(), 4)
        
        # Verificar que el producto se creó correctamente
        producto_creado = Producto.objects.get(codigo="P004")
        self.assertEqual(producto_creado.nombre, "Teclado Mecánico")
        self.assertEqual(float(producto_creado.precio), 89.99)
        self.assertTrue(producto_creado.activo)  # Por defecto activo

    # ============ PRUEBA 3: Validación de código único ============
    def test_crear_producto_codigo_duplicado(self):
        """
        Prueba: Intentar crear un producto con código duplicado debe fallar
        """
        data = {
            "codigo": "P001",  # Código ya existente
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
        self.assertEqual(Producto.objects.count(), 3)  # No se creó nuevo producto
        self.assertIn('error', response.data)

    # ============ PRUEBA 4: Actualizar producto ============
    def test_actualizar_producto(self):
        """
        Prueba: Actualizar un producto existente
        """
        url = self.detail_url(self.producto1.id)
        data = {
            "codigo": "P001",
            "nombre": "Laptop Dell XPS",
            "descripcion": "Laptop 32GB RAM, 1TB SSD",
            "precio": 1299.99
        }
        
        response = self.client.put(
            url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar que se actualizó correctamente
        self.producto1.refresh_from_db()
        self.assertEqual(self.producto1.nombre, "Laptop Dell XPS")
        self.assertEqual(float(self.producto1.precio), 1299.99)
        self.assertEqual(self.producto1.descripcion, "Laptop 32GB RAM, 1TB SSD")

    # ============ PRUEBA 5: Toggle activo/desactivo ============
    def test_toggle_activo_producto(self):
        """
        Prueba: Activar y desactivar un producto
        """
        url = reverse('producto-toggle-activo', args=[self.producto1.id])
        
        # Desactivar producto (activo = True -> False)
        response = self.client.patch(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.producto1.refresh_from_db()
        self.assertFalse(self.producto1.activo)
        self.assertEqual(response.data['activo'], False)
        
        # Volver a activar producto (activo = False -> True)
        response = self.client.patch(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.producto1.refresh_from_db()
        self.assertTrue(self.producto1.activo)
        self.assertEqual(response.data['activo'], True)

    # ============ PRUEBA 6: Buscar productos ============
    def test_buscar_productos(self):
        """
        Prueba: Buscar productos por texto
        """
        # Buscar por código
        url = f"{self.list_url}buscar/?q=P001"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['codigo'], "P001")
        
        # Buscar por nombre
        url = f"{self.list_url}buscar/?q=Laptop"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['nombre'], "Laptop Dell")
        
        # Buscar por descripción
        url = f"{self.list_url}buscar/?q=inalámbrico"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['codigo'], "P002")
        
        # Búsqueda sin resultados
        url = f"{self.list_url}buscar/?q=inexistente"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    # ============ PRUEBA 7: Filtrar productos activos ============
    def test_filtrar_productos_activos(self):
        """
        Prueba: Obtener solo productos activos
        """
        url = f"{self.list_url}activos/"
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Solo P001 y P002 están activos
        
        # Verificar que todos sean activos
        for producto in response.data:
            self.assertTrue(producto['activo'])

    # ============ PRUEBA 8: Eliminar producto ============
    def test_eliminar_producto(self):
        """
        Prueba: Eliminar un producto
        """
        url = self.detail_url(self.producto1.id)
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Producto.objects.count(), 2)
        
        # Verificar que el producto ya no existe
        with self.assertRaises(Producto.DoesNotExist):
            Producto.objects.get(id=self.producto1.id)

    # ============ PRUEBA 9: Validación de precio negativo ============
    def test_crear_producto_precio_negativo(self):
        """
        Prueba: No permitir precios negativos
        """
        data = {
            "codigo": "P005",
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

    # ============ PRUEBA 10: Filtrar por precio mínimo ============
    def test_filtrar_por_precio_minimo(self):
        """
        Prueba: Filtrar productos con precio >= valor especificado
        """
        url = f"{self.list_url}?precio_min=100"
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Debería mostrar P001 (799.99) y P003 (199.99)
        self.assertEqual(response.data['count'], 2)
        
        # Verificar que todos los precios sean >= 100
        for producto in response.data['results']:
            self.assertTrue(float(producto['precio']) >= 100)

    # ============ PRUEBA 11: Ordenar productos ============
    def test_ordenar_productos(self):
        """
        Prueba: Ordenar productos por precio
        """
        # Orden ascendente
        url = f"{self.list_url}?ordering=precio"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        precios = [float(p['precio']) for p in response.data['results']]
        self.assertEqual(precios, sorted(precios))  # Verificar orden ascendente
        
        # Orden descendente
        url = f"{self.list_url}?ordering=-precio"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        precios = [float(p['precio']) for p in response.data['results']]
        self.assertEqual(precios, sorted(precios, reverse=True))  # Verificar orden descendente


class ProductoModelTestCase(TestCase):
    """
    Pruebas para el modelo Producto
    """
    def setUp(self):
        self.producto = Producto.objects.create(
            codigo="TEST001",
            nombre="Producto de Prueba",
            descripcion="Descripción de prueba",
            precio=99.99
        )

    def test_str_method(self):
        """
        Prueba: Verificar el método __str__ del modelo
        """
        expected_str = f"{self.producto.codigo} - {self.producto.nombre}"
        self.assertEqual(str(self.producto), expected_str)

    def test_codigo_mayusculas(self):
        """
        Prueba: Verificar que el código se guarda en mayúsculas
        """
        producto = Producto.objects.create(
            codigo="test002",
            nombre="Otro Producto",
            precio=50.00
        )
        self.assertEqual(producto.codigo, "TEST002")  # Debe estar en mayúsculas

    def test_nombre_formato_titulo(self):
        """
        Prueba: Verificar que el nombre se guarda con formato título
        """
        producto = Producto.objects.create(
            codigo="TEST003",
            nombre="producto de prueba",
            precio=50.00
        )
        self.assertEqual(producto.nombre, "Producto De Prueba")  # Formato título

    def test_activo_por_defecto(self):
        """
        Prueba: Verificar que el campo activo es True por defecto
        """
        producto = Producto.objects.create(
            codigo="TEST004",
            nombre="Nuevo Producto",
            precio=50.00
        )
        self.assertTrue(producto.activo)