import tests.models
from django.db import migrations, models
import enumfields.fields


class Migration(migrations.Migration):

    initial = True

    operations = [
        migrations.CreateModel(
            name='enum_object',
            fields=[
                ('enum_field', enumfields.fields.EnumIntegerField(default=0, enum=tests.models.GenericEnum)),
            ]
        ),
    ]
