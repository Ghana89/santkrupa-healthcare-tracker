# Generated migration for StandardPrescriptionTemplate models

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('hospital', '0023_doctornotes_checkin_purpose_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='StandardPrescriptionTemplate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text="Template name (e.g., 'Cold & Cough')", max_length=255)),
                ('description', models.TextField(blank=True, help_text='What is this template for?')),
                ('keyword', models.CharField(blank=True, help_text="Search keyword for quick access (e.g., 'fever', 'pneumonia')", max_length=100)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('clinic', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='prescription_templates', to='hospital.clinic')),
                ('doctor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='prescription_templates', to='hospital.doctor')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='StandardTemplateTest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('test_name', models.CharField(max_length=200)),
                ('test_type', models.CharField(choices=[('blood', 'Blood Test'), ('urine', 'Urine Test'), ('xray', 'X-Ray'), ('ultrasound', 'Ultrasound'), ('ecg', 'ECG'), ('ct_scan', 'CT Scan'), ('mri', 'MRI'), ('other', 'Other')], max_length=50)),
                ('description', models.TextField(blank=True)),
                ('template', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tests', to='hospital.standardprescriptiontemplate')),
            ],
            options={
                'ordering': ['test_name'],
            },
        ),
        migrations.CreateModel(
            name='StandardTemplateMedicine',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('medicine_name', models.CharField(max_length=200)),
                ('dosage', models.CharField(max_length=100)),
                ('frequency_per_day', models.PositiveIntegerField(default=1)),
                ('duration', models.CharField(max_length=100)),
                ('medicine_type', models.CharField(choices=[('tablet', 'Tablet'), ('capsule', 'Capsule'), ('syrup', 'Syrup'), ('injection', 'Injection'), ('ointment', 'Ointment'), ('drops', 'Drops')], default='tablet', max_length=20)),
                ('qty', models.PositiveIntegerField(default=1)),
                ('schedule', models.CharField(blank=True, choices=[('morning', 'Morning'), ('afternoon', 'Afternoon'), ('evening', 'Evening'), ('night', 'Night'), ('morning_evening', 'Morning & Evening'), ('morning_afternoon_evening', 'Morning, Afternoon & Evening')], max_length=50)),
                ('food_instruction', models.CharField(blank=True, choices=[('before_food', 'Before Food'), ('with_food', 'With Food'), ('after_food', 'After Food')], max_length=20)),
                ('instructions', models.TextField(blank=True)),
                ('template', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='medicines', to='hospital.standardprescriptiontemplate')),
            ],
            options={
                'ordering': ['medicine_name'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='standardprescriptiontemplate',
            unique_together={('clinic', 'doctor', 'name')},
        ),
    ]
