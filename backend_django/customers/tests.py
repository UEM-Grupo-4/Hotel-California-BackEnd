from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Cliente, Telefono


class ClienteApiTests(APITestCase):
    def test_cliente_crud(self):
        list_url = reverse('cliente-list')
        create_payload = {
            'nombre': 'Ana',
            'apellido_1': 'Lopez',
            'apellido_2': 'Diaz',
            'email': 'ana@example.com',
        }

        create_response = self.client.post(list_url, create_payload, format='json')
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        cliente_id = create_response.data['id']

        detail_url = reverse('cliente-detail', args=[cliente_id])

        list_response = self.client.get(list_url)
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(list_response.data), 1)

        patch_response = self.client.patch(detail_url, {'nombre': 'Ana Maria'}, format='json')
        self.assertEqual(patch_response.status_code, status.HTTP_200_OK)
        self.assertEqual(patch_response.data['nombre'], 'Ana Maria')

        delete_response = self.client.delete(detail_url)
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Cliente.objects.filter(id=cliente_id).exists())

    def test_cliente_retrieve_includes_telefonos(self):
        cliente = Cliente.objects.create(
            nombre='Luis',
            apellido_1='Perez',
            apellido_2='Rojas',
            email='luis@example.com',
        )
        Telefono.objects.create(cliente=cliente, telefono='+34600111222')

        detail_url = reverse('cliente-detail', args=[cliente.id])
        response = self.client.get(detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('telefonos', response.data)
        self.assertEqual(len(response.data['telefonos']), 1)
        self.assertEqual(response.data['telefonos'][0]['telefono'], '+34600111222')


class TelefonoApiTests(APITestCase):
    def setUp(self):
        self.cliente = Cliente.objects.create(
            nombre='Marta',
            apellido_1='Gomez',
            apellido_2='Soto',
            email='marta@example.com',
        )

    def test_telefono_crud_and_detail_serializer(self):
        list_url = reverse('telefono-list')
        create_payload = {
            'cliente': self.cliente.id,
            'telefono': '+34900111222',
        }

        create_response = self.client.post(list_url, create_payload, format='json')
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        telefono_id = create_response.data['id']

        detail_url = reverse('telefono-detail', args=[telefono_id])
        retrieve_response = self.client.get(detail_url)
        self.assertEqual(retrieve_response.status_code, status.HTTP_200_OK)
        self.assertIn('cliente', retrieve_response.data)
        self.assertEqual(retrieve_response.data['cliente']['id'], self.cliente.id)

        patch_response = self.client.patch(detail_url, {'telefono': '+34900111333'}, format='json')
        self.assertEqual(patch_response.status_code, status.HTTP_200_OK)
        self.assertEqual(patch_response.data['telefono'], '+34900111333')

        delete_response = self.client.delete(detail_url)
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Telefono.objects.filter(id=telefono_id).exists())
