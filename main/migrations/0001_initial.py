# Generated by Django 4.1 on 2023-02-14 14:05

from django.db import migrations, models
import django.db.models.deletion
import jsonfield.fields
import main.models
import main.storage


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Algorithms',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='AnnotationswrapJson',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('annotation', jsonfield.fields.JSONField(default={})),
                ('algorithm', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.algorithms')),
            ],
        ),
        migrations.CreateModel(
            name='Projects',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Registration_Images',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image1', models.ImageField(upload_to=main.models.image_fix_path)),
                ('image2', models.ImageField(upload_to=main.models.image_mov_path)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.projects')),
            ],
        ),
        migrations.CreateModel(
            name='Results',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('warping', models.ImageField(blank=True, max_length=255, storage=main.storage.OverwriteStorage(), upload_to=main.models.results_warp)),
                ('features_mov', models.ImageField(blank=True, max_length=255, storage=main.storage.OverwriteStorage(), upload_to=main.models.results_feature_mov)),
                ('features_fix', models.ImageField(blank=True, max_length=255, storage=main.storage.OverwriteStorage(), upload_to=main.models.results_feature_fix)),
                ('line_match', models.ImageField(blank=True, max_length=255, storage=main.storage.OverwriteStorage(), upload_to=main.models.results_line_match)),
                ('chessboard', models.ImageField(blank=True, max_length=255, storage=main.storage.OverwriteStorage(), upload_to=main.models.results_chess)),
                ('x_chessboard', models.PositiveSmallIntegerField(default=4)),
                ('y_chessboard', models.PositiveSmallIntegerField(default=4)),
                ('Registration_Images', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='main.registration_images')),
                ('algorithm', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.algorithms')),
                ('annotation_wrap', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='main.annotationswrapjson')),
            ],
        ),
        migrations.AddField(
            model_name='annotationswrapjson',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.projects'),
        ),
        migrations.CreateModel(
            name='AnnotationsJson',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('annotation', jsonfield.fields.JSONField(default={})),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.projects')),
            ],
        ),
    ]
