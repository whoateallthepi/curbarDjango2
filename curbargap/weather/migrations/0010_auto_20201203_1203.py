# Generated by Django 3.0.10 on 2020-12-03 12:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('weather', '0009_timestep_uv'),
    ]

    operations = [
        migrations.CreateModel(
            name='Symbol',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('symbol_key', models.IntegerField(unique=True, verbose_name='symbol key')),
                ('symbol_image', models.ImageField(blank=True, upload_to='symbols/')),
            ],
        ),
        migrations.AlterField(
            model_name='timestep',
            name='precipitation',
            field=models.IntegerField(verbose_name='%Rain'),
        ),
        migrations.AlterField(
            model_name='timestep',
            name='step_time',
            field=models.DateTimeField(verbose_name='Time'),
        ),
        migrations.AlterField(
            model_name='timestep',
            name='temperature',
            field=models.IntegerField(verbose_name='°C'),
        ),
        migrations.AlterField(
            model_name='timestep',
            name='weather',
            field=models.IntegerField(verbose_name='Symbol'),
        ),
        migrations.AlterField(
            model_name='timestep',
            name='wind_direction',
            field=models.CharField(max_length=3, verbose_name='Rose'),
        ),
        migrations.AlterField(
            model_name='timestep',
            name='wind_gust',
            field=models.IntegerField(verbose_name='Gust'),
        ),
    ]
