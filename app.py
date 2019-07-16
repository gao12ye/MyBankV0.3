from flask import Flask, request
from flask_restful import Resource, Api
from flask_restful import reqparse
import flask_restful
from functools import wraps


app = Flask(__name__)
api = Api(app)

account = {}
remainBal = 0


parser = reqparse.RequestParser(bundle_errors=True)
parser.add_argument('authorization', type=str, location='headers')
parser.add_argument('acNum', help='You have to provide a string.', required=True)  
#parser.add_argument('startBal', help='The value needs to be integer.', type=int)
#parser.add_argument('acNum', help='Validation Error')
#parser.add_argument('deltaAmount', help='The value needs to be integer.', type=int)


def check_negative(input_amount):
    if input_amount < 0:
        return True
        
def check_acNum(acNum, account):
    if acNum in list(account.keys()):
        return True

def authenticate(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not getattr(func, 'authorization', True):
            return func(*args, **kwargs)
        args1 = parser.parse_args()
        authToken = args1['authorization']
        acct = check_authentication(authToken)
        if acct:
            return func(*args, **kwargs)
        flask_restful.abort(401)
    return wrapper

def check_authentication(authtoken):
    if authtoken == 'abcdefg':
        return True

class Resource(flask_restful.Resource): #add authenticate method to the Resource class - authenticate will fail the request 
    method_decorators = [authenticate]

class CreateAccount(Resource):
        
    def put(self): #Set up account initially.
        parserCreateAc = parser.copy()
        parserCreateAc.add_argument('startBal', help='The value needs to be integer.', type=int, required=True)
        args = parserCreateAc.parse_args()
        key_acNum = args['acNum']
        value_acNum = args['startBal']
        if check_acNum(key_acNum, account):
            return "Account already exisits, please use a different account", 400  
        if check_negative(value_acNum):
            return "Your input cannot be less than 0.", 400        
        account[key_acNum] = value_acNum
        parser.remove_argument('startBal')
        return account, 201

class CheckAccount(Resource):
    def post(self):
        args = parser.parse_args()
        key_acNum = args['acNum']
        if not check_acNum(key_acNum, account):
            return "Account does not exist", 400 
        return account[key_acNum], 200

class Deposite(Resource):        
    def post(self):
        parserDeposite = parser.copy()
        parserDeposite.add_argument('deltaAmount', help='The value needs to be integer.', type=int, required=True)
        error = []
        args = parserDeposite.parse_args()
        key_acNum = args['acNum']
        deltaAmount = args['deltaAmount']
        if not check_acNum(key_acNum, account):
            error.append("Account does not exist.")
            if check_negative(deltaAmount):
                    error.append("Your input cannot be less than 0.")
        else:
            if check_negative(deltaAmount):
                error.append("Your input cannot be less than 0.")
        if not error:
            account[key_acNum] += deltaAmount
            return account[key_acNum], 200
        else:
            return error, 400
class Withdraw(Resource):    
    def post(self):
        parserWithdraw = parser.copy()
        parserWithdraw.add_argument('deltaAmount', help='The value needs to be integer.', type=int, required=True)
        error = []
        args = parserWithdraw.parse_args()
        key_acNum = args['acNum']
        deltaAmount = args['deltaAmount']
        if not check_acNum(key_acNum, account):
            error.append("Account does not exist.")
            if check_negative(deltaAmount):
                error.append("Your input cannot be less than 0.")
        else:
            if check_negative(deltaAmount):
                error.append("Your input cannot be less than 0.")
            if (account[key_acNum]-deltaAmount)<0:
                error.append("Forbidden, your withdraw will result a negative balance.")
        if not error:
            account[key_acNum] -= deltaAmount
            return account[key_acNum], 200
        else:
            return error, 400     	
	
api.add_resource(CreateAccount,'/mybank/create')
api.add_resource(CheckAccount,'/mybank/account')
api.add_resource(Deposite,'/mybank/deposite')
api.add_resource(Withdraw,'/mybank/withdraw')


if __name__ == '__main__':
    app.run(host = '0.0.0.0',port = 1111, debug=True)