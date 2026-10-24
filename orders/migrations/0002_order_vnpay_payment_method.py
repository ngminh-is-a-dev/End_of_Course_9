from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='payment_method',
            field=models.CharField(
                choices=[
                    ('cod', 'Thanh toán khi nhận hàng'),
                    ('sepay', 'Chuyển khoản SePay (đơn cũ)'),
                    ('vnpay', 'Thanh toán trực tuyến qua VNPay'),
                ],
                max_length=10,
            ),
        ),
    ]
