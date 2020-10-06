import pdfkit
import pyqrcode
import csv,json
import codecs
from flask import Flask, request
from flask_restful import Api, Resource
from pdfrw import PdfReader, PdfWriter
from PyPDF4 import PdfFileMerger, PdfFileReader, PdfFileWriter
from PyPDF4.utils import PdfReadError

app = Flask(__name__)
api = Api(app)

# Function that validates a PDF file
def validatePDF(path):
	try:
		with open(path,'rb') as fh:
			PdfFileReader(fh)
		return path
	except PdfReadError:
		# Read the file with pdfrw and save
		pdf = PdfReader(path)
		write_pdf = PdfWriter()
		for page in range(pdf.numPages):
			write_pdf.addpage(pdf.pages[page])
		write_pdf.write(path)
		print('PDF corregido, mejor chequear que se envia bien')
		return path
	except Exception as e:
		raise e

# Verify pdf file
class Verify(Resource):
	def get(self):
		return {'error':'Method not supported'}
	def post(self):
		try:
			json = request.get_json()
			valid = validatePDF(json['path'])
			return {'message' : 'OK','path' : valid},200 
		except Exception as error:
			return {'error':str(error)}

# Merge various pdfs into one PDF
class Merge(Resource):
	def get(self):
		return {'error':'Method not supported'}
	def post(self):
		try:
			json = request.get_json()
			files = json['input']
			output_path = json['output']
			merge = PdfFileMerger()
			for filename in files:
				# Validate that each file is pdf file
				input_path = validatePDF(filename)
				with open(input_path,'rb') as fh:
					merge.append(PdfFileReader(fh))
			merge.write(output_path)
			return {'message' : 'OK'},200 
		except Exception as error:
			return {'error': str(error)}

# Generate pdf from html
class htmlPDF(Resource):
	def get(self):
		return {'error':'Method not supported'}
	def post(self):
		try:
			path_wkthmltopdf = 'C:/wkhtmltopdf/bin/wkhtmltopdf.exe'
			config = pdfkit.configuration(wkhtmltopdf=path_wkthmltopdf)
			json = request.get_json()
			operation = json['type']
			input_file = json['input']
			output_file = json['output']
			if operation == "url":
				pdfkit.from_url(input_file, output_file, configuration=config)
			elif operation == "file":
				pdfkit.from_file(input_file, output_file, configuration=config)
			elif operation == "string":
				pdfkit.from_string(input_file, output_file, configuration=config)
			print('CHECK PDF: ' + output_file)
			return {'message' : 'OK'}
		except Exception as error:
			return {'error': str(error)}
# Generate QRCode and save it in PNG
class generateQR(Resource):
	def post(self):
		try:
			json = request.get_json()
			data = json['data']
			output = json['output']
			url = pyqrcode.create(data)
			with open(output, 'wb') as fstream:
				url.png(fstream, scale=5)
			return {'message' : 'OK'}
		except Exception as error:
			return {'error': str(error)}

# From JSON to CSV
class json2csv(Resource):
	def post(self):
		json_data = request.get_json()
		fileInput = json_data['input']
		fileOutput = json_data['output']
		outputFile = open(fileOutput, 'w', newline='',encoding='utf-8') #load csv file
		with codecs.open(fileInput, 'r', 'utf-8') as data_file:
			data = json.load(data_file) #load json content
		output = csv.writer(outputFile) #create a csv.write
		output.writerow(data[0].keys())  # header row
		for row in data:
			output.writerow(row.values()) #values row
		return {'message' : 'OK'}

# Endpoints
api.add_resource(Merge,'/merge')
api.add_resource(Verify,'/verify')
api.add_resource(htmlPDF,'/html2pdf')
api.add_resource(generateQR,'/qrcode')
api.add_resource(json2csv,'/json2csv')

if __name__ == '__main__':
	app.run(debug=True)
	#app.run()
