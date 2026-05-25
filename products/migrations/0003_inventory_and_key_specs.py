from django.db import migrations, models


def migrate_stock_boolean_to_quantity(apps, schema_editor):
    Product = apps.get_model("products", "Product")
    for product in Product.objects.all():
        product.stock_quantity = 10 if product.stock else 0
        product.save(update_fields=["stock_quantity"])


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0002_productspecification_productvariantgroup_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="productspecification",
            name="is_key",
            field=models.BooleanField(
                default=False,
                help_text="Show this spec in the key specs section on the product page.",
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="stock_quantity",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="productvariantoption",
            name="stock_quantity",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.CreateModel(
            name="ProductVariantStock",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "variant_note",
                    models.CharField(
                        help_text='Example: "Color: Red, Storage: 128GB"',
                        max_length=255,
                    ),
                ),
                ("stock_quantity", models.PositiveIntegerField(default=0)),
                ("sku", models.CharField(blank=True, max_length=64)),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE,
                        related_name="variant_stocks",
                        to="products.product",
                    ),
                ),
            ],
            options={
                "ordering": ["variant_note"],
            },
        ),
        migrations.AddConstraint(
            model_name="productvariantstock",
            constraint=models.UniqueConstraint(
                fields=("product", "variant_note"),
                name="unique_product_variant_note_stock",
            ),
        ),
        migrations.RunPython(migrate_stock_boolean_to_quantity, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name="product",
            name="stock",
        ),
        migrations.AlterModelOptions(
            name="productspecification",
            options={"ordering": ["section", "name"]},
        ),
    ]
