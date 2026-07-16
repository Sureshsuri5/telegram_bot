import qrcode

amount=int(input('enter amount:'))
upi = 'suresh.ottmaker@fam'
name = 'Suresh Amarakonda'
url = f'upi://pay?pa={upi}&pn={name}&am={amount}'
file_path = 'qr_code.png'

qr = qrcode.QRCode()
qr.add_data(url)
img = qr.make_image()
img.save(file_path)