
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activity',
            name='action',
            field=models.CharField(choices=[('create_board', 'Creó tablero'), ('create_card', 'Creó tarea'), ('delete_card', 'Eliminó tarea'), ('move_card', 'Movió tarea'), ('edit_card', 'Editó tarea'), ('add_comment', 'Comentó'), ('create_list', 'Creó lista'), ('delete_list', 'Eliminó lista'), ('add_member', 'Agregó miembro'), ('remove_member', 'Eliminó miembro')], max_length=20),
        ),
    ]
