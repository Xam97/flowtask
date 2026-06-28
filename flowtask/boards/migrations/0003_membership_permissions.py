from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('boards', '0002_cardlabel_label_cardlabel_label_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='membership',
            name='can_manage_labels',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='membership',
            name='can_delete_cards',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='membership',
            name='can_edit_lists',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='membership',
            name='can_invite',
            field=models.BooleanField(default=False),
        ),
    ]
