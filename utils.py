#! coding: utf-8
import pyqrcode


def order_dic(dic):
    ordered_dic={}
    key_ls=sorted(dic.keys())
    for key in key_ls:
        ordered_dic[key]=dic[key]
    return ordered_dic

def generate_qrcode(address):
    filename = '/tmp/' + address + '.png'
    qr = pyqrcode.create(address)
    qr.png(filename, scale=5)

    return open(filename, 'rb')
