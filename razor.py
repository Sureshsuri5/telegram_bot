import razorpay

client=razorpay.Client(
    auth=('rzp_test_T78O2fyU8wa2Tq','PPBgFDXHqrWRGszmsJp5NacA')
)

order=client.order.create({
    'amount':50000,
    'currency':'INR',
    'payment_capture':1
})

order_id=order['id']

data=client.order.fetch(
    'order_T78RosxakkSOqW'
)
print(data)