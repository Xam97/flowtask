from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from django.db.models import Q
from .models import ContactRequest
from .serializers import UserSearchSerializer
from notifications.services import notify_contact_request_received, notify_contact_request_accepted

User = get_user_model()

class ContactViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    
    queryset = ContactRequest.objects.all()
    
    # 1. BUSCADOR DE USUARIOS INTEGRADO
    @action(detail=False, methods=['get'], url_path='search')
    def search_users(self, request):
        query = request.query_params.get('q', '').strip()
        if not query:
            return Response({"detail": "Falta el parámetro de búsqueda 'q'."}, status=status.HTTP_400_BAD_REQUEST)

        # Buscamos usuarios excluyendo al usuario actual
        users = User.objects.filter(
            (Q(username__icontains=query) | Q(email__icontains=query) | Q(first_name__icontains=query)) &
            ~Q(id=request.user.id)
        )

        serializer = UserSearchSerializer(users, many=True, context={'request': request})
        return Response(serializer.data)

    # 2. ENVIAR SOLICITUD DE CONTACTO
    @action(detail=False, methods=['post'], url_path='send-request')
    def send_request(self, request):
        receiver_id = request.data.get('user_id')
        if not receiver_id:
            return Response({"detail": "Se requiere 'user_id'."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            receiver_id = int(receiver_id)
        except (TypeError, ValueError):
            return Response({"detail": "'user_id' inválido."}, status=status.HTTP_400_BAD_REQUEST)

        if receiver_id == request.user.id:
            return Response({"detail": "No podés auto-enviarte una solicitud."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            receiver = User.objects.get(id=receiver_id)
        except User.DoesNotExist:
            return Response({"detail": "Usuario no encontrado."}, status=status.HTTP_404_NOT_FOUND)

        # Verificamos si ya existe algún tipo de registro
        relation = ContactRequest.objects.get_relation_status(request.user, receiver)

        if relation:
            if relation.status == 'accepted':
                return Response({"detail": "Ya son contactos."}, status=status.HTTP_400_BAD_REQUEST)
            if relation.status == 'pending':
                return Response({"detail": "Ya existe una solicitud pendiente entre ustedes."}, status=status.HTTP_400_BAD_REQUEST)
            # Si fue rechazada antes, permitimos "re-intentar" reseteándola a pendiente
            relation.status = 'pending'
            relation.sender = request.user
            relation.receiver = receiver
            relation.save()
        else:
            relation = ContactRequest.objects.create(sender=request.user, receiver=receiver)

        notify_contact_request_received(receiver=receiver, sender=request.user, contact_request=relation)

        return Response({"detail": "Solicitud enviada correctamente.", "status": "pending_sent"}, status=status.HTTP_201_CREATED)

    # 3. ACEPTAR O RECHAZAR SOLICITUD
    @action(detail=False, methods=['post'], url_path='respond-request')
    def respond_request(self, request):
        sender_id = request.data.get('user_id')
        action_type = request.data.get('action') # 'accept' o 'reject'

        if action_type not in ['accept', 'reject']:
            return Response({"detail": "Acción inválida. Debe ser 'accept' o 'reject'."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Buscamos la solicitud donde el usuario logueado sea el RECEPTOR
            contact_request = ContactRequest.objects.get(sender_id=sender_id, receiver=request.user, status='pending')
        except ContactRequest.DoesNotExist:
            return Response({"detail": "No tenés ninguna solicitud pendiente de este usuario."}, status=status.HTTP_404_NOT_FOUND)

        if action_type == 'accept':
            contact_request.status = 'accepted'
            contact_request.save()
            notify_contact_request_accepted(
                original_sender=contact_request.sender,
                accepted_by=request.user,
                contact_request=contact_request,
            )
            return Response({"detail": "Solicitud aceptada. Ahora son contactos.", "status": "accepted"})
        else:
            contact_request.status = 'rejected'
            contact_request.save()
            return Response({"detail": "Solicitud rechazada."})

    # 4. LISTA DE MIS CONTACTOS (BIDIRECCIONAL)
    @action(detail=False, methods=['get'], url_path='my-contacts')
    def my_contacts(self, request):
        # Filtramos todas las solicitudes aceptadas donde participe el usuario logueado
        accepted_relations = ContactRequest.objects.filter(
            Q(status='accepted') & (Q(sender=request.user) | Q(receiver=request.user))
        )

        # Extraemos los usuarios que no sean el usuario logueado
        contact_ids = []
        for rel in accepted_relations:
            if rel.sender_id == request.user.id:
                contact_ids.append(rel.receiver_id)
            else:
                contact_ids.append(rel.sender_id)

        contacts = User.objects.filter(id__in=contact_ids)
        serializer = UserSearchSerializer(contacts, many=True, context={'request': request})
        return Response(serializer.data)

    # 5. SOLICITUDES PENDIENTES RECIBIDAS (para el icono dedicado de la navbar)
    @action(detail=False, methods=['get'], url_path='pending-requests')
    def pending_requests(self, request):
        pending = ContactRequest.objects.filter(
            receiver=request.user, status='pending'
        ).select_related('sender').order_by('-created_at')

        data = [
            {
                'request_id': req.id,
                'id': req.sender.id,
                'username': req.sender.username,
                'first_name': req.sender.first_name,
                'last_name': req.sender.last_name,
                'created_at': req.created_at.strftime('%d/%m/%Y %H:%M'),
            }
            for req in pending
        ]
        return Response({'count': len(data), 'results': data})

    # 6. ELIMINAR UN CONTACTO YA ACEPTADO
    @action(detail=False, methods=['post'], url_path='remove-contact')
    def remove_contact(self, request):
        other_id = request.data.get('user_id')
        if not other_id:
            return Response({"detail": "Se requiere 'user_id'."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            other_id = int(other_id)
        except (TypeError, ValueError):
            return Response({"detail": "'user_id' inválido."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            other_user = User.objects.get(id=other_id)
        except User.DoesNotExist:
            return Response({"detail": "Usuario no encontrado."}, status=status.HTTP_404_NOT_FOUND)

        relation = ContactRequest.objects.filter(
            status='accepted'
        ).get_relation_status(request.user, other_user)

        if not relation:
            return Response({"detail": "No son contactos."}, status=status.HTTP_404_NOT_FOUND)

        relation.delete()
        return Response({"detail": "Contacto eliminado correctamente."})