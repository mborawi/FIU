import csv
from collections import defaultdict
import os
import sys #dealing with multiple versions of Python and some minor differences between them
if sys.version_info[0] < 3:
	from Tkinter import *
	import tkFileDialog

else:
	from tkinter import *
	from tkinter import filedialog

def clean_ctr(path, headers, outpath = None):
	data = defaultdict(list)
	with open(path) as f:
	    reader = csv.DictReader(f) # read rows into a dictionary format
	    for row in reader: # read a row as {column1: value1, column2: value2,...}
	    	for (k,v) in row.items(): # go over each column name and value
	    		data[k.strip()].append(v.strip()) # append the value into the appropriate list
	                                 # based on column name k

	data["CTRID"] = list(map(lambda x: '"' + x + '"', data["CTRID"]))
	data['cashAmount'] = list(map(lambda x: str(x.replace(",","")), data['cashAmount']))
	data['cashAmount'] = list(map(lambda x: str(x.replace("$","")), data['cashAmount']))
	data["fullNameOfFinancialInstitution"] = list(map(lambda x: '"' + x + '"', data["fullNameOfFinancialInstitution"]))
	dirs = path.split("/")
	name = dirs[-1]
	name = "UPDATED_" + name
	if outpath is None:
		outpath = "/".join(dirs[:len(dirs)-1]) + "/" + name
	else:
		outpath += "/" + name
	with open(outpath, 'w') as fout:
		fout.write(",".join(headers) + "\n")
		for i in range(len(data['CTRID'])):
			line = ''
			if data['CTRID'][i] not in taipan_ctr_data:
				taipan_ctr_data[data['CTRID'][i]] = {}
			for val in headers:
				line += data[val][i]
				colName = get_taipan_friendly_header(val, "CTRs")
				taipan_ctr_data[ data['CTRID'][i] ][ colName ] = data[val][i]
				line += ","
			line += "\n"
			fout.write(line)
	fout.close()


def clean_pit(path, headers, outpath = None):
	data = defaultdict(list)
	with open(path) as f:
	    reader = csv.DictReader(f) # read rows into a dictionary format
	    for row in reader: # read a row as {column1: value1, column2: value2,...}
	    	for (k,v) in row.items(): # go over each column name and value
	    		data[k.strip()].append(v.strip()) # append the value into the appropriate list
	                                 # based on column name k

	data['accountNumbers'] = list(map(lambda x: " " if x == '' else " / ".join(str(x).split(",")), data['accountNumbers']))
	data['CTRID'] = list(map(lambda x: '"' + str(x) + "0"*(9-len(str(x))) + '"', data['CTRID']))
	data['lastNameOrNameOfEntity'] = list(map(lambda x : 'GIBBONS' if x.strip().upper() == 'GIBSONS' else x.strip().upper(), data['lastNameOrNameOfEntity']))
	for i in range(len(data['lastNameOrNameOfEntity'])):
		if data['lastNameOrNameOfEntity'][i].upper() == "WHIPPS":
			if data['firstName'][i].upper() == "SURANGEL":
				if data['dateOfBirth'][i] == '2/21/1939':
					data['lastNameOrNameOfEntity'][i] = "WHIPPS SR"
		if data['lastNameOrNameOfEntity'][i].upper() in ['BILLY TAKAMINE', 'HARRY BESEBES']:
			names = data['lastNameOrNameOfEntity'][i].upper().split()
			data['lastNameOrNameOfEntity'][i] = names[1].upper()
			data['firstName'][i] = names[0].upper()
	data['contactPhoneNumber'] = list(map((lambda x: str(x).strip()), data['contactPhoneNumber']))
	data['contactPhoneNumber'] = list(map(lambda x: "" if len(str(x)) == 0 else ('"' + str(x)[:3] + "-" + str(x)[3:6] + "-" + str(x)[6:] + '"') if len(str(x)) == 10 else ('"' + "680-" + str(x)[:3] + "-" + str(x)[3:6] + '"' if len(str(x)) == 7 else '"' + str(x) + '"'), data['contactPhoneNumber']))
	data['cashAmount'] = list(map(lambda x: str(x.replace(",","")), data['cashAmount']))
	data['cashAmount'] = list(map(lambda x: str(x.replace("$","")), data['cashAmount']))
	authority_map = dict()
	authority_map['PW'] = 'Palau'
	authority_map['HI'] = 'Hawaii'
	authority_map['DE'] = 'Delaware'
	authority_map['GU'] = 'Guam'
	data['idIssuingAuthority'] = list(map(lambda x: "" if len(str(x).strip()) == 0 else (str(x).strip().upper() if str(x).strip().upper() not in authority_map else authority_map[str(x).strip().upper()]), data['idIssuingAuthority']))
	dirs = path.split("/")
	name = dirs[-1]
	name = "UPDATED_" + name
	if outpath is None:
		outpath = "/".join(dirs[:len(dirs)-1]) + "/" + name
	else:
		outpath += "/" + name
	with open(outpath, 'w') as fout:
		fout.write(",".join(headers) + "\n")
		for i in range(len(data['CTRID'])):
			line = ''
			record = {}
			if data['CTRID'][i] not in taipan_pit_data:
				taipan_pit_data[data['CTRID'][i]] = []
			for val in headers:
				line += data[val][i]
				colName = get_taipan_friendly_header(val, "PersonInTransaction")
				record[colName] = data[val][i]
				line += ","
			taipan_pit_data[data['CTRID'][i]].append(record)
			line += "\n"
			fout.write(line)
	fout.close()

def gen_taipan_entries(path, taipan_headers, outpath = None):
	# join CTR and PIT entries
	# for each PIT find corresponding CTR and merge using taipan header col order for csv output
	dirs = path.split("/")
	name = dirs[-1]
	name = "TAIPAN_" + name
	if outpath is None:
		outpath = "/".join(dirs[:len(dirs)-1]) + "/" + name
	else:
		outpath += "/" + name
	with open(outpath, 'w') as fout:
		fout.write(",".join(taipan_headers) + "\n")
		for k, taipan_pit_vals in taipan_pit_data.items():
			for pit in taipan_pit_vals:
				line = ''
				if k not in taipan_ctr_data:
					print("Could not find CTRID: {} in CTR file".format(k))
					exit(1)
				taipan_ctr_vals = taipan_ctr_data[k]
				for header in taipan_headers:
					if header in pit:
						field = pit[header]
					elif header in taipan_ctr_vals:
						field = taipan_ctr_vals[header]
					else:
						print("Could not find header: {} for {} in nither file!".format(header, k))
						print(taipan_ctr_vals)
						exit(1)

					line += field
					line += ","
				line += "\n"
				fout.write(line)
	fout.close()

def get_taipan_friendly_header(colname, tabName):
	match colname:
		case "CTRID":
			return "CTRs_CTRID"
		case "cashDirection":
			return "{}_{}".format(tabName,colname)
		case "cashAmount":
			return "{}_{}".format(tabName,colname)
		case _:
			return colname

def run():
	ctr_headers = ["CTRID","dateOfTransaction","cashDirection","cashAmount",\
		"typeOfFinancialInstitution","fullNameOfFinancialInstitution","nameOfBranchOfficeAgency"]

	pit_headers = ["CTRID","relationshipToTransaction",\
		"lastNameOrNameOfEntity","firstName","middleName",\
		"gender","occupationOrTypeOfBusiness","address",\
		"addressCity","addressState","zipCode","addressCountry", \
		"dateOfBirth","contactPhoneNumber","emailAddress","idType",\
		"idNumber","idCountry","idIssuingAuthority","accountNumbers", "cashDirection","cashAmount"]

	taipan_headers = ["CTRs_CTRID", "dateOfTransaction", "CTRs_cashDirection", "CTRs_cashAmount", \
    	"typeOfFinancialInstitution", "fullNameOfFinancialInstitution", "nameOfBranchOfficeAgency", \
    	"relationshipToTransaction", "lastNameOrNameOfEntity", "firstName", "middleName",\
    	"gender", "occupationOrTypeOfBusiness", "address", "addressCity", "addressState", "zipCode", \
    	"addressCountry", "dateOfBirth", "contactPhoneNumber", "emailAddress", "idType", "idNumber", \
    	"idCountry", "idIssuingAuthority", "accountNumbers", "PersonInTransaction_cashDirection", \
    	"PersonInTransaction_cashAmount"]

	Tk().withdraw() #dont need a console open
	zippaths = filedialog.askopenfiles(mode ='r', filetypes =[('CTR and TIP CSVs', '.csv .CSV')])
	if len(zippaths)!=2:
		# print error message using GUI
		print("need two files",len(zippaths), zippaths)
		sys.exit(1)
	pit_path = zippaths[0].name
	ctr_path = zippaths[1].name
	if "pit" in ctr_path.lower():
		tmp = pit_path
		pit_path = ctr_path
		ctr_path = tmp

	if "pit" not in pit_path.lower():
		# print error message using GUI
		print("one file need to have tip in name", ctr_path, pit_path)
		sys.exit(1)

	clean_ctr(ctr_path, ctr_headers)
	clean_pit(pit_path, pit_headers)
	gen_taipan_entries(pit_path, taipan_headers)


taipan_ctr_data = {}
taipan_pit_data = {}
run()

