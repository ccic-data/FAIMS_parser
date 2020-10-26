from collections import Counter
import argparse
import ast
import os
import sys

def string_parser(string, index_num):
    temp_str = ''
    quote_count = 0
    
    for i in range(len(string)):
        if i == 25:
            temp_str = temp_str + str(index_num)
            break
        else:
            temp_str = temp_str + string[i]
            
    for i in range(len(string)):
        if string[i] == '"':
            quote_count = quote_count + 1
            
        if quote_count == 2:
            temp_str = temp_str + '" id="controllerType=0 controllerNumber=1 scan=' + str(index_num+1)
            break
        
    quote_count = 0
    
    for i in range(len(string)):
        if string[i] == '"':
            quote_count = quote_count + 1
        if quote_count >= 4:
            temp_str = temp_str + string[i]
    
    return temp_str

def string_parser2(string, index_num):
    temp_str = ''
    equal_count = 0
    
    for i in range(len(string)):
        
        temp_str = temp_str + string[i]
        
        if string[i] == '=':
            equal_count = equal_count+1
        
        if equal_count == 4:
            temp_str = temp_str + str(index_num)
            
            break

    quote_count = 0
    for i in range(len(string)):
        
        if string[i] == '"':
            quote_count = quote_count+1
        
        if quote_count == 2:
            temp_str = temp_str + string[i]
                                
        
    return temp_str

        
        
            

############################################################
############################################################
"""
Arguments and initial values
"""
############################################################
############################################################

ap = argparse.ArgumentParser()
ap.add_argument("-i", "--input", required=True, help="name of the file")
ap.add_argument("-cv", "--comp_voltage", required=True, help="the compensation voltages")
args = vars(ap.parse_args())

comp_vol = ast.literal_eval(args["comp_voltage"]) #the compensation voltages
file_name = args["input"]# the original FAIMS mzml file
namebase = os.path.splitext(file_name)[0] # the base name of the FAIMS mzml file

############################################################
############################################################
"""
Step -1 This part counts the number of scans for each
compensation voltage
"""
############################################################
############################################################

print('counting number of scans for each compensation voltage')
big_file = open(file_name, 'r')
index_value = 0 # used to count the number of total spectra
comp_vol_list = []
for line in big_file:
    if '<spectrum index=' in line:
        index_value += 1
    if 'name="FAIMS compensation voltage" ' in line:
        for i in range(len(comp_vol)):
            if str(comp_vol[i]) in line:
                comp_vol_list.append(str(comp_vol[i]))

totals = Counter(comp_vol_list)
for i in range(len(comp_vol)):
    print('there are ' + str(totals[str(comp_vol[i])]) + ' scans for compensation voltage ' + str(comp_vol[i]))

############################################################
############################################################
"""
Step -2 This is a for loop for making each file.  It starts
by writing the initial lines of the original FAIMS file,
then it proceeds to write the scans for the specific comp
voltage, then it finishes with the last lines of code
to build the mzml file
"""
############################################################
############################################################
for i in range(len(comp_vol)):
    scan_number = 0
    scan_number2 = 1
    big_file = open(file_name, 'r')
    file_str = namebase + '_' + str(comp_vol[i]) + '_temp.mzml'
    file_new = open(file_str, 'w')
    print('starting file ' + file_str)

    ############################################################
    ############################################################
    """
    Step 2A - Writes first lines of mzML file to all three files
    """
    ############################################################
    ############################################################
    print('writing initial lines of code for ' + file_str)
    for line in big_file:
       if '<spectrumList count' not in line:
           file_new.write(line)
       else:
           break


    ############################################################
    ############################################################
    """
    Step -2B Write in the correct next line for each file
    """
    ############################################################
    ############################################################
    print('writing in spectrum list count for ' + file_str)
    file_new.write('      <spectrumList count="' + str(totals[str(comp_vol[i])]) +
                      '" defaultDataProcessingRef="pwiz_Reader_Thermo_conversion">\n')


    ############################################################
    ############################################################
    """
    Step -2C Write in the scans section
    """
    ############################################################
    ############################################################
    print('writing in temporary data for ' + file_str)

    big_file.close()
    big_file = open(file_name, 'r')

    for line in big_file:
        if '<spectrumList count=' in line:
            break

    for j in range(index_value):
        if comp_vol_list[j] == str(comp_vol[i]):
            for line in big_file:
                
                if '</spectrum>' in line:
                    file_new.write(line)
                    break
                
                elif '<spectrum index=' in line:
                    file_new.write(string_parser(line, scan_number))
                    scan_number = scan_number + 1
                
                else:
                    file_new.write(line)
        else:
            for line in big_file:
                if '</spectrum>' in line:
                    break
    ############################################################
    ############################################################
    """
    Step -2d Write in the next lines of code
    """
    ############################################################
    ############################################################
    file_new.write('      </spectrumList>\n    </run>\n  </mzML>\n  <indexList count="2">\n    <index name="spectrum">\n')

    for line in big_file:
        if '<index name="spectrum">' in line:
            break

    for j in range(index_value):
        if comp_vol_list[j] == str(comp_vol[i]):
            for line in big_file:
                file_new.write(string_parser2(line,scan_number2))
                scan_number2 = scan_number2 + 1
                break
        else:
            for line in big_file:
                break
    ############################################################
    ############################################################
    """
    Step -2e Write in the final lines of code
    """
    ############################################################
    ############################################################
    for line in big_file:
        if '<offset idRef=' in line:
            continue
        else:
            file_new.write(line)

    big_file.close()

    file_new.close()

    ############################################################
    ############################################################
    """
    Step -2f goes through and eliminates comp voltage line
    from each scan
    """
    ############################################################
    ############################################################

    print('deleting comp voltage line from file ' + file_str)
    file_new_temp = open(file_str, 'r')

    file_fin = open(namebase + '_' + str(comp_vol[i]) + '.mzml', 'w')

    for line in file_new_temp:
        if line.strip("\n") != '          <cvParam cvRef="MS" accession="MS:1001581" name="FAIMS compensation ' \
                               'voltage" value="-' + str(comp_vol[i]) + '.0"/>':
            file_fin.write(line)
    file_new_temp.close()
    file_fin.close()
    os.remove(file_str)

print('Finished!')