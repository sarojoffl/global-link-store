from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("shop", "0002_order_payment_gateway"),
    ]

    operations = [
        migrations.AlterField(
            model_name="order",
            name="payment_method",
            field=models.CharField(
                choices=[
                    ("cod", "Cash on Delivery"),
                    ("esewa", "eSewa"),
                    ("khalti", "Khalti"),
                ],
                default="cod",
                max_length=20,
            ),
        ),
    ]
