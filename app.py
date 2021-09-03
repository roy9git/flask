from flask import Flask , render_template
from azure.keyvault import KeyVaultClient
from azure.storage.blob import BlockBlobService
from msrestazure.azure_active_directory import MSIAuthentication
app = Flask(__name__)

@app.route('/')
def hello_world():
    return render_template('index.html')
    #return "<p>Hello-World!</p>"

@app.route('/products')
def products():
    return 'this is products page'

if __name__ == "__main__":
    app.run(debug=True)
