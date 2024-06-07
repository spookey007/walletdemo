from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .models import User, Transaction
from web3 import Web3
from eth_account import Account
ganache_url = 'http://172.16.16.14:8545'
web3 = Web3(Web3.HTTPProvider(ganache_url))

def register(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        if not User.objects.filter(email=email).exists():
            account = web3.eth.account.create()
            wallet_address = account.address
            private_key = account._private_key.hex()

            initial_balance = web3.to_wei(100, 'ether')

            sender_address = '0xd5cE4DB109f199169FbA76047467619C1D0083E4'
            sender_private_key = '0x47638c4e937be5d4ab1982908407ce4cedf7e3c5d7ec485e5cdb20a7a5e1dfc3'
            nonce = web3.eth.get_transaction_count(sender_address)
            tx = {
                'nonce': nonce,
                'to': wallet_address,
                'value': initial_balance,
                'gas': 2000000,
                'gasPrice': web3.to_wei('1', 'gwei')
            }
            signed_tx = web3.eth.account.sign_transaction(tx, sender_private_key)
            tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
            tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

            user = User.objects.create_user(username=email, email=email, password=password, wallet_address=wallet_address, private_key=private_key)
            return redirect('login')
        else:
            return HttpResponse("Email already exists")
    return render(request, 'register.html')

def user_login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return HttpResponse("Invalid login credentials")
    return render(request, 'login.html')

@login_required
def home(request):
    user = request.user
    balance = web3.eth.get_balance(user.wallet_address)
    balance_eth = web3.from_wei(balance, 'ether')
    transactions = Transaction.objects.filter(user=user)
    if request.method == 'POST':
        to_address = request.POST['to_address']
        amount = request.POST['amount']
        private_key = user.private_key
        nonce = web3.eth.get_transaction_count(user.wallet_address)
        tx = {
            'nonce': nonce,
            'to': to_address,
            'value': web3.to_wei(amount, 'ether'),
            'gas': 2000000,
            'gasPrice': web3.to_wei('1', 'gwei')
        }
        signed_tx = web3.eth.account.sign_transaction(tx, private_key)
        tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
        Transaction.objects.create(user=user, to_address=to_address, tx_hash=tx_hash.hex(), amount=amount)
        return redirect('home')
    return render(request, 'home.html', {'wallet_address': user.wallet_address, 'balance': balance_eth, 'transactions': transactions})

def user_logout(request):
    logout(request)
    return redirect('login')
