# Generated by Django 4.2.13 on 2024-05-19 11:55

from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Usuario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('rol', models.PositiveSmallIntegerField(choices=[(1, 'administrador'), (2, 'profesor')], default=1)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Asignatura',
            fields=[
                ('asignatura_cod', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('descripcion', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Aula',
            fields=[
                ('aula_cod', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('descripcion', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Franja',
            fields=[
                ('franja_cod', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('descripcion', models.CharField(max_length=100)),
                ('horadesde', models.TimeField()),
                ('horahasta', models.TimeField()),
            ],
        ),
        migrations.CreateModel(
            name='Grupo',
            fields=[
                ('grupo_cod', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('descripcion', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Profesor',
            fields=[
                ('profesor_cod', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=50)),
                ('hash', models.CharField(max_length=8)),
                ('hash2', models.CharField(max_length=8)),
                ('usuario', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Horario',
            fields=[
                ('horario_cod', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('dia', models.CharField(max_length=1)),
                ('periodo_cod', models.IntegerField()),
                ('asignatura_cod', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='horarios.asignatura')),
                ('aula_cod', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='horarios.aula')),
                ('grupo_cod', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='horarios.grupo')),
                ('profesor_cod', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='horarios.profesor')),
            ],
        ),
        migrations.CreateModel(
            name='Ausencia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateTimeField(blank=True, default=django.utils.timezone.now)),
                ('motivo', models.TextField()),
                ('asignatura_cod', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='horarios.asignatura')),
                ('horario_cod', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='horarios.horario')),
                ('profesor_cod', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='horarios.profesor')),
            ],
        ),
    ]
