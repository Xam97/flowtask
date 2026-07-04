# Generated manually on 2026-06-30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0004_notification_contact_request_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='type',
            field=models.CharField(choices=[('card_assigned', 'Tarea asignada'), ('new_comment', 'Nuevo comentario'), ('card_moved', 'Tarjeta movida'), ('member_added', 'Miembro agregado'), ('card_deleted', 'Tarjeta eliminada'), ('contact_request', 'Solicitud de contacto'), ('contact_accepted', 'Solicitud de contacto aceptada')], max_length=20),
        ),
    ]
