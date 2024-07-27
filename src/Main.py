# -*- coding: utf-8 -*-
"""
Created on Fri Apr 30 18:00 2021
@author: George Madeley gm768
"""

import numpy as np
import math
import csv
import sys
import os

class CircuitBlock:

    # A = [0,0]
    # B = [0,1]
    # C = [1,0]
    # D = [1,1]

    previousBlock = None

    def __init__(self, name, resistance=0, capacitance=0, inductance=0, series=True):
        self.resistance = resistance
        self.capacitance = capacitance
        self.inductance = inductance
        self.name = name
        self.series = series

    def __str__(self):
        return ("Block Name: "+ str(self.name))

    def InputVoltage(self, termsDict, freqeuncy):
        """ Calculates the input voltage

        This calculates the input voltage at the given frequency

        :param termsDict: (Dictionary) contains all the given terms
        :param frequency: (float) the source frequency

        :return: (complex) list of the input voltage for that block
        """
        # checks to ensure the passed arguments are of the correct data type
        if type(termsDict) != dict:
            print("ERROR:\ntermsDict must be type Dict and not type ", type(termsDict))
            CreateEmptyCSV()
        try:
            # tries to convert variable to type float if possible
            if type(termsDict["rl"]) != float:
                termsDict["rl"] = float(termsDict["rl"])
        # prints error message if it could not be converted
        except KeyError:
            print("ERROR:\nThe value for rl could not be found")
            CreateEmptyCSV()
        except OverflowError:
            print("ERROR:\nThe data type for rl must be float, not: ", type(termsDict["rl"]))
            CreateEmptyCSV()
        try:
            # tries to convert variable to type float if possible
            if type(termsDict["rs"]) != float:
                termsDict["rs"] = float(termsDict["rs"])
        # prints error message if it could not be converted
        except KeyError:
            print("ERROR:\nThe value for rs could not be found")
            CreateEmptyCSV()
        except OverflowError:
            print("ERROR:\nThe data type for rs must be float, not: ", type(termsDict["rs"]))
            CreateEmptyCSV()

        # checks if there is a voltage source
        if termsDict["vt"] != None:
            try:
                # returns the calculated input voltage
                return (termsDict["vt"] * self.InputImpedance(termsDict["rl"], freqeuncy))/(termsDict["rs"]+self.InputImpedance(termsDict["rl"], freqeuncy))
            except ZeroDivisionError:
                # prints error message if division by zero exception occurs
                print("ERROR:\nThe value of rs and Zin was zero: ",(termsDict["rs"]+self.InputImpedance(termsDict["rl"], freqeuncy)))
                CreateEmptyCSV()
        # else it is a current source
        elif termsDict["in"] != None:
            try:
                # returns the calculated input voltage
                totalResistance = 1/((1/self.InputImpedance(termsDict["rl"], freqeuncy))+(1/termsDict["rs"]))
                return totalResistance * termsDict["in"]
            except ZeroDivisionError:
                # prints error message if division by zero exception occurs
                print("ERROR:\nThe value of rs: %f or Zin: %f cannot be zero."%(termsDict["rs"], self.InputImpedance(termsDict["rl"], freqeuncy)))
                CreateEmptyCSV()
        else:
            # prints error message if vt or in was not given in the input file
            print("ERROR:\nThe value of in and vt are not given")
            CreateEmptyCSV()

    def InputCurrent(self, termsDict, freqeuncy):
        """ Calculates the input current

        This calculates the input current from the given data in termsDict and matrixABCD.

        :param termsDict: (Dictionary) contains all the given terms
        :param frequency: (float) the source frequency

        :return: (complex) list of the input currents for that block
        """
        # checks to ensure the passed arguments are of the correct data type
        if type(termsDict) != dict:
            print("ERROR:\ntermsDict must be type Dict and not type ", type(termsDict))
            CreateEmptyCSV()
        try:
            # tries to convert variable to type float if possible
            if type(termsDict["rl"]) != float:
                termsDict["rl"] = float(termsDict["rl"])
        # prints error message if it could not be converted
        except KeyError:
            print("ERROR:\nThe value for rl could not be found")
            CreateEmptyCSV()
        except OverflowError:
            print("ERROR:\nThe data type for rl must be float, not: ", type(termsDict["rl"]))
            CreateEmptyCSV()
        try:
            # tries to convert variable to type float if possible
            if type(termsDict["rs"]) != float:
                termsDict["rs"] = float(termsDict["rs"])
        # prints error message if it could not be converted
        except KeyError:
            print("ERROR:\nThe value for rs could not be found")
            CreateEmptyCSV()
        except OverflowError:
            print("ERROR:\nThe data type for rs must be float, not: ", type(termsDict["rs"]))
            CreateEmptyCSV()
        
        # checks if there is a voltage source
        if termsDict["vt"] != None:
            try:
                # returns the calculated input current
                return termsDict["vt"]/(termsDict["rs"]+self.InputImpedance(termsDict["rl"], freqeuncy))
            except ZeroDivisionError:
                # prints error message if division by zero exception occurs
                print("ERROR:\nThe value of rs and Zin was zero: ",(termsDict["rs"]+self.InputImpedance(termsDict["rl"], freqeuncy)))
                CreateEmptyCSV()
        # else it is a current source
        elif termsDict["in"] != None:
            try:
                # returns the calculated input current
                totalResistance = 1/((1/self.InputImpedance(termsDict["rl"], freqeuncy))+(1/termsDict["rs"]))
                voltage = totalResistance * termsDict["in"]
                return termsDict["in"] - (voltage / termsDict["rs"])
            except ZeroDivisionError:
                # prints error message if division by zero exception occurs
                print("ERROR:\nThe value of rs: %f or Zin: %f cannot be zero."%(termsDict["rs"], self.InputImpedance(termsDict["rl"], freqeuncy)))
                CreateEmptyCSV()
        else:
            # prints error message if vt or in was not given in the input file
            print("ERROR:\nThe value of in and vt are not given")
            CreateEmptyCSV()

    def OutputVoltage(self, termsDict, freqeuncy):
        """ Calculates the output voltage

        This calculates the output voltage from the given data in inputVoltage, inputCurrent, and matrixABCD.

        :param termsDict: (Dictionary) contains all the given terms
        :param frequency: (float) the source frequency

        :return: (complex) list of the output voltage for that block
        """
        # checks to ensure the passed arguments are of the correct data type
        if type(termsDict) != dict:
            print("ERROR:\ntermsDict must be type Dict and not type ", type(termsDict))
            CreateEmptyCSV()
        # gets the total matrix of the circuit
        matrixT = self.TotalMatrix(freqeuncy)
        if np.linalg.det(matrixT) == 0:
            print("ERROR:\nThe determinate of the total matrix was 0. The matrix is:\n ")
            print("Frequency: ", freqeuncy)
            print("A: ", matrixT[0,0])
            print("B: ", matrixT[0,1])
            print("C: ", matrixT[1,0])
            print("D: ", matrixT[1,1])
            print("AD: ", matrixT[0,0]*matrixT[1,1])
            print("BC: ", matrixT[0,1]*matrixT[1,0])
            print("AD-BC: ", matrixT[0,0]*matrixT[1,1] - matrixT[0,1]*matrixT[1,0])
            return 0
        # calculates the inverse of the total matrix
        inverseABCD = np.linalg.inv(matrixT)
        # converts the input current and voltage into a column matrix
        inputVoltageCurrent = [self.InputVoltage(termsDict, freqeuncy), self.InputCurrent(termsDict, freqeuncy)]
        inputVoltageCurrent = np.matrix(inputVoltageCurrent)
        inputVoltageCurrent = np.transpose(inputVoltageCurrent)
        try:
            if (matrixT[0,0]*matrixT[1,1] - matrixT[0,1]*matrixT[1,0]) == 0:
                raise ZeroDivisionError
            # calculates the output current and voltage
            outputVoltageCurrent = (1/(matrixT[0,0]*matrixT[1,1] - matrixT[0,1]*matrixT[1,0]))*np.matmul(inverseABCD, inputVoltageCurrent)
            # returns the output voltage
            return complex(outputVoltageCurrent[0])
        except ZeroDivisionError:
            # prints error message if a divide by zero error occurs
            print("ERROR:\nDivide by zero error in Output voltage")
            return 0
        except Exception:
            # prints error message if an unknown error occurs
            print("ERROR:\nAn unknown error occured in Output Voltage: ", sys.exc_info())
            CreateEmptyCSV()

    def OutputCurrent(self, termsDict, freqeuncy):
        """ Calculates the output current

        This calculates the output voltage from the given data in inputVoltage, inputCurrent, and matrixABCD.

        :param termsDict: (Dictionary) contains all the given terms
        :param frequency: (float) the source frequency

        :return: (complex) list of the output current for that block.
        """
        # checks to ensure the passed arguments are of the correct data type
        if type(termsDict) != dict:
            print("ERROR:\ntermsDict must be type Dict and not type ", type(termsDict))
            CreateEmptyCSV()
        # gets the total matrix of the circuit
        matrixT = self.TotalMatrix(freqeuncy)
        if np.linalg.det(matrixT) == 0:
            print("ERROR:\nThe determinate of the total matrix was 0. The matrix is:\n ")
            print("Frequency: ", freqeuncy)
            print("A: ", matrixT[0,0])
            print("B: ", matrixT[0,1])
            print("C: ", matrixT[1,0])
            print("D: ", matrixT[1,1])
            print("AD: ", matrixT[0,0]*matrixT[1,1])
            print("BC: ", matrixT[0,1]*matrixT[1,0])
            print("AD-BC: ", matrixT[0,0]*matrixT[1,1] - matrixT[0,1]*matrixT[1,0])
            return 0
        # calculates the inverse of the total matrix
        inverseABCD = np.linalg.inv(matrixT)
        # converts the input current and voltage into a column matrix
        inputVoltageCurrent = [self.InputVoltage(termsDict, freqeuncy), self.InputCurrent(termsDict, freqeuncy)]
        inputVoltageCurrent = np.matrix(inputVoltageCurrent)
        inputVoltageCurrent = np.transpose(inputVoltageCurrent)
        try:
            if (float(matrixT[0,0])*float(matrixT[1,1]) - float(matrixT[0,1])*float(matrixT[1,0])) == 0:
                raise ZeroDivisionError
            # calculates the output current and voltage
            outputVoltageCurrent = (1/(matrixT[0,0]*matrixT[1,1] - matrixT[0,1]*matrixT[1,0]))*np.matmul(inverseABCD, inputVoltageCurrent)
            # returns the output current
            return complex(outputVoltageCurrent[1])
        except ZeroDivisionError:
            # prints error message if a divide by zero error occurs
            print("ERROR:\nDivide by zero error in Output current")
            return 0
        except Exception:
            # prints error message if an unknown error occurs
            print("ERROR:\nAn unknown error occured in Output Current: ", sys.exc_info())
            CreateEmptyCSV()

    def InputPower(self, termsDict, freqeuncy):
        """ Calculates the input power

        This calculates the input power from the returns of InputVoltage and InputCurrent.

        :param termsDict: (Dictionary) contains all the given terms
        :param frequency: (float) the source frequency

        :return: (complex) list of the input power of that block.
        """
        # checks to ensure the passed arguments are of the correct data type
        if type(termsDict) != dict:
            print("ERROR:\ntermsDict must be type Dict and not type ", type(termsDict))
            CreateEmptyCSV()
        # calculates the complex conjugate of the input current and multiplies it to the input voltage to get power in
        inputPower = np.conj(self.InputCurrent(termsDict, freqeuncy)) * self.InputVoltage(termsDict, freqeuncy)
        # returns power in
        return inputPower

    def OutputPower(self, termsDict, freqeuncy):
        """ Calculates the output power

        This calculates the output power from the returns of OutputVoltage and OutputCurrent.

        :param termsDict: (Dictionary) contains all the given terms
        :param frequency: (float) the source frequency

        :return: (complex) list of the output power of that block.
        """
        # checks to ensure the passed arguments are of the correct data type
        if type(termsDict) != dict:
            print("ERROR:\ntermsDict must be type Dict and not type ", type(termsDict))
            CreateEmptyCSV()
        # calculates the complex conjugate of the output current and multiplies it to the output voltage to get power out
        outputPower = np.conj(self.OutputCurrent(termsDict, freqeuncy)) * self.OutputVoltage(termsDict, freqeuncy)
        # returns power out
        return complex(outputPower)

    def InputImpedance(self, impedanceLoad, freqeuncy):
        """ Calculates the input impedance.

        This calculates the input impedance from the given impedanceLoad and matrixABCD.

        :param impedanceLoad: (float) the value of the load impedance of the block.
        :param frequency: (float) the source frequency

        :return: (complex) list of the input impedance of that block.
        """
        # checks to see if the arguments are of the ocrrect data type
        if type(impedanceLoad) != float:
            try:
                # tries to convert variable to type float if possible
                impedanceLoad = float(impedanceLoad)
            except Exception:
                # prints error message if it could not be converted
                print("ERROR:\nimpedanceLoad must be a type float, not tpye ", type(impedanceLoad))
                CreateEmptyCSV()
        # gets the ABCD matrix of t he whole circuit
        matrixT = self.TotalMatrix(freqeuncy)
        try:
            # calculates input impedance and returns it
            #print("A: ", matrixT[0,0])
            #print("B: ", matrixT[0,1])
            #print("C: ", matrixT[1,0])
            #print("D: ", matrixT[1,1])
            #print("Load: ", impedanceLoad)
            inputImpedance = (matrixT[0,0]*impedanceLoad + matrixT[0,1])/(matrixT[1,0]*impedanceLoad + matrixT[1,1])
            #print("Calculated: ", inputImpedance)
            #print("="*50)
            return inputImpedance
        except ZeroDivisionError:
            # prints error message if a divide by zero error occurs
            print("ERROR:\nCannot divide by zero. ImpedanceLoad value: %f, element A: %s, element B: %s, element C: %s, element D: %s"%(impedanceLoad, str(matrixT[0,0]), str(matrixT[0,1]), str(matrixT[1,0]), str(matrixT[1,1])))
            CreateEmptyCSV()
        except Exception:
            # prints error message if an unknown error occurs
            print("ERROR:\nAn unknown error has occured in InputImpedance(): ", sys.exc_info)
            CreateEmptyCSV()

    def OutputImpedance(self, impedanceSource, freqeuncy):
        """ Calculates the output impedance.

        This calculates the output impedance from the data in ##.

        :param impedanceSource: (float) the value of the source impedance of the block.
        :param frequency: (float) the source frequency

        :return: (complex) list of the output impedance of that block.
        """
        # checks to see if the arguments are of the ocrrect data type
        if type(impedanceSource) != float:
            try:
                # tries to convert variable to type float if possible
                impedanceSource = float(impedanceSource)
            except Exception:
                # prints error message if it could not be converted
                print("ERROR:\nimpedanceLoad must be a type float, not tpye ", type(impedanceSource))
                CreateEmptyCSV()
        # gets the ABCD matrix of t he whole circuit
        matrixT = self.TotalMatrix(freqeuncy)
        try:
            # calculates output impedance and returns it
            outputImpedance = (matrixT[1,1]*impedanceSource + matrixT[0,1])/(matrixT[1,0]*impedanceSource + matrixT[0,0])
            return outputImpedance
        except ZeroDivisionError:
            # prints error message if a divide by zero error occurs
            print("ERROR:\nCannot divide by zero. ImpedanceSource value: %f, element A: %s, element B: %s, element C: %s, element D: %s"%(impedanceSource, str(matrixT[0,0]), str(matrixT[0,1]), str(matrixT[1,0]), str(matrixT[1,1])))
            CreateEmptyCSV()
        except Exception:
            # prints error message if an unknown error occurs
            print("\nAn unknown error has occured in InputImpedance(): ", sys.exc_info)
            CreateEmptyCSV()

    def CurrentGain(self, impedanceLoad, freqeuncy):
        """ Calculatres the current gain

        This calculates the current gain of the block from the returns of TotalMatrix and load impedance of the circuit.

        :param impedanceSource: (float) Source impedance of the circuit.
        :param frequency: (float) the source frequency

        :return: (complex) the value of the current gain of the block.
        """
        # checks to see if the arguments are of the ocrrect data type
        if type(impedanceLoad) != float:
            try:
                # tries to convert variable to type float if possible
                impedanceLoad = float(impedanceLoad)
            except Exception:
                # prints error message if it could not be converted
                print("ERROR:nimpedanceLoad must be a type float, not tpye ", type(impedanceLoad))
                CreateEmptyCSV()
        # gets the ABCD matrix of the whole circuit
        matrixT = self.TotalMatrix(freqeuncy)
        try:
            # calculates current gain and returns it
            currentGain = 1/(matrixT[1,0]*impedanceLoad + matrixT[1,1])
            return currentGain
        except ZeroDivisionError:
            # prints error message if a divide by zero error occurs
            print("ERROR:\nCannot divide by zero. ImpedanceLoad value: %f, element C: %s, element D: %s"%(impedanceLoad, str(matrixT[1,0]), str(matrixT[1,1])))
            CreateEmptyCSV()
        except Exception:
            # prints error message if an unknown error occurs
            print("ERROR:\nAn unknown error has occured in CurrentGain() \n", sys.exc_info())
            CreateEmptyCSV()

    def VoltageGain(self, impedanceLoad, freqeuncy):
        """ Calculatres the voltage gain

        This calculates the voltage gain of the block from the returns of TotalMatrix and load impedance of the circuit.

        :param impedanceLoad: (float) Source impedance of the circuit.
        :param frequency: (float) the source frequency

        :return: (complex) the value of the voltage gain of the block.
        """
        # checks to see if the arguments are of the ocrrect data type
        if type(impedanceLoad) != float:
            try:
                # tries to convert variable to type float if possible
                impedanceLoad = float(impedanceLoad)
            except Exception:
                # prints error message if it could not be converted
                print("ERROR:\nimpedanceLoad must be a type float, not tpye ", type(impedanceLoad))
                CreateEmptyCSV()
        # gets the ABCD matrix of the whole circuit
        matrixT = self.TotalMatrix(freqeuncy)
        try:
            # calculates voltage gain and returns it
            voltageGain = impedanceLoad/(matrixT[0,0]*impedanceLoad + matrixT[0,1])
            return voltageGain
        except ZeroDivisionError:
            # prints error message if a divide by zero error occurs
            print("ERROR:\nCannot divide by zero. ImpedanceLoad value: %f, element A: %f, element B: %f"%(impedanceLoad, float(matrixT[0,0]), float(matrixT[0,1])))
            CreateEmptyCSV()
        except Exception:
            # prints error message if an unknown error occurs
            print("ERROR:\nAn unknown error has occured in VoltagetGain() \n", sys.exc_info())
            CreateEmptyCSV()     

    def CalculateMatrix(self, frequency):
        """ this calculates the ABCD Matrix of the current block counter in the frequency

        This checks the B and C elements of the matrix and divides or multiplies them by the given frequency depending if
        the imaginery component is positive or negative
        
        :param frequency: (float) the source frequency
        """
        # checks to see if the arguments are of the correct data type
        if type(self.capacitance) != float:
            try:
                # tries to convert variable to type float if possible
                self.capacitance = float(self.capacitance)
            except Exception:
                # prints error message if it could not be converted
                print("ERROR:\nself.capacitance must be a type float, not tpye ", type(self.capacitance))
                CreateEmptyCSV()
        if type(self.inductance) != float:
            try:
                # tries to convert variable to type float if possible
                self.inductance = float(self.inductance)
            except Exception:
                # prints error message if it could not be converted
                print("ERROR:\nself.inductance must be a type float, not tpye ", type(self.inductance))
                CreateEmptyCSV()
        if type(self.resistance) != float:
            try:
                # tries to convert variable to type float if possible
                self.resistance = float(self.resistance)
            except Exception:
                # prints error message if it could not be converted
                print("ERROR:\nself.resistance must be a type float, not tpye ", type(self.resistance))
                CreateEmptyCSV()
        if type(frequency) != float:
            try:
                # tries to convert variable to type float if possible
                frequency = float(frequency)
            except Exception:
                # prints error message if it could not be converted
                print("ERROR:\nfrequency must be a type float, not tpye ", type(frequency))
                CreateEmptyCSV()
        # prints an error message if frequeny is less than or equal to zero
        if frequency <= 0:
            print("ERROR:\nFrfequency must not be less than or equal to 0")
            CreateEmptyCSV()
        # create a matrix of type complex
        self.matrixABCD = np.identity(2, dtype=complex)
        # if the name has a 0, the component is in parallel


        if self.series == False:
            # if inductance is not 0
            if self.inductance != 0:
                # calculates impedance for an inductor
                impedance = 2*math.pi*frequency*self.inductance
                self.matrixABCD[1,0] = 1/complex(real=0, imag=impedance)
            # if capacitance is not 0
            elif self.capacitance != 0:
                # calculates impedance for a capacitor
                impedance = -1/(2*math.pi*frequency*self.capacitance)
                self.matrixABCD[1,0] = 1/complex(real=0, imag=impedance)
            # if resistance is not 0
            elif self.resistance != 0:
                # calculates impedance of a resistor
                self.matrixABCD[1,0] = 1/complex(real=self.resistance, imag=0)
            else:
                # sets the values to zero if neither impedance, capacitance, or resistance are given
                self.matrixABCD[1,0] = complex(real=0, imag=0)
        # else, the component is in series
        else:
            # if inductance is not 0
            if self.inductance != 0:
                # calculates impedance for an inductor
                impedance = 2*math.pi*frequency*self.inductance
                self.matrixABCD[0,1] = complex(real=0, imag=impedance)
            # if capacitance is not 0
            elif self.capacitance != 0:
                # calculates impedance for a capacitor
                impedance = -1/(2*math.pi*frequency*self.capacitance)
                self.matrixABCD[0,1] = complex(real=0, imag=impedance)
            # if resistance is not 0
            elif self.resistance != 0:
                # calculates impedance of a resistor
                self.matrixABCD[0,1] = complex(real=self.resistance, imag=0)
            else:
                # sets the values to zero if neither impedance, capacitance, or resistance are given
                self.matrixABCD[1,0] = complex(real=0, imag=0)

    def TotalMatrix(self, frequency):
        """ Calculates the total ABCD Matrix up to this block.

        This calcualtes the total ABCD Matrix using the previous blocks' total matrix method. This acts
        as recusion as it asks the previous matrix to multiple its matrix by the return of the circuit
        block before that one

        :param frequency: (float) the source frequency

        :return: (complex) the total ABCD matrix up to the current block
        """
        # calculates the matrix for the current circuit block
        self.CalculateMatrix(frequency)
        # If there is not circuit block before this one, the function returns its own matrix
        if self.previousBlock == None:
            return self.matrixABCD
        # if there is a circuit block before this one, it multiplies its own matrix by the returned matrix of the previous circuit block
        else:
            return np.matmul(self.previousBlock.TotalMatrix(frequency), self.matrixABCD)
































def ReadInputFile(filename):
    """ Read the input files to identify the required outputs and the given inputs.

    Loop over each line of the input within the <CIRCUIT> section of the input and call the ReadFileLine() function
    and store the block in a list. Find the <TERMS> section and identify the values by calling ReadFileLine()function
    then store the values in the termsDict and frequencyDict. Find the <OUTPUT> section and identify the required
    outputs by calling the IdentifyUnits() function. Store the required outputs, units and power in a dictionary.

    :param filename: (string) name of the file to be read

    :return: (dictionary) the required outputs, their units and their powers
    :return: (list) the list of blocks created.
    :return: (dictionary) frequency information
    :return: (dictionary) terms information
    """
    # tries to open the file
    try:
        file=open(filename,'rt')
    except FileNotFoundError:
        # prints error if the file could not be found
        print('File <%s> not found'%(filename))
        currentLocation=os.getcwd() 
        print("executing program in directory: "+currentLocation) 
        CreateEmptyCSV()
    # gets all the lines in a list
    fileLines=file.readlines()
    listOfBlocks = []
    # creates the required dictionaries
    termsDict = {"vt":None, "rs":None, "in":None, "rl":None}
    frequencyDict = {"fstart":None, "fend":None, "nfreqs":None, "lfstart":None, "lfend":None}
    outputDict = {}
    state = 0
    for index,line in enumerate(fileLines):
        # remove \n from the line
        line = line.strip("\n")
        # if the line is nothing, go to the next line
        if (line == ""):
            continue
        if (line[0] == "<"):
            greaterThanIdx = line.find(">")
            line = line[1:greaterThanIdx]
            line = line.lower()
            # if the line is "<circuit>", change state to 1
            if (line == "circuit"):
                state = 1
                continue
            # if the line is "<terms>", change state to 2
            elif (line == "terms"):
                state = 2
                continue
            # if the line is "<output>", change state to 3
            elif (line == "output"):
                state = 3
                continue
            # els,e change it to state 0
            elif (line == "/circuit" or line == "/terms" or line == "/output"):
                state = 0
                continue
            else:
            # error message if the line states with "<" but is not circuit, terms, or output
                print("ERROR:\nUnrecognised section header or footer: ", line)
                continue
        # if the line is a comment or the state is 0, continue to the next line
        if (line[0] == "#" or state == 0):
            continue
        # if the sate is 1, the program is reading lines from the CIRCUIT section
        if (state == 1):
            # creates a circuit block instance and stores it in a list
            tempBlock = ReadFileLine(line)
            listOfBlocks.append(tempBlock)
        # if the sate is 2, the program is reading lines from the TERMS section
        elif (state == 2):
            # reads the course and loads and stores them in two dictionaries
            termsDict, frequencyDict = ReadFileLine(line, False, termsDict, frequencyDict)
        # if the sate is 3, the program is reading lines from the OUTPUT section
        elif (state == 3):
            # store the returns in the dictionary
            unit, exponent, name = IdentifyOutputVariable(line)
            outputDict[name.lower()] = []
            outputDict[name.lower()].append(unit)
            outputDict[name.lower()].append(-exponent)
        else: continue
    return outputDict, listOfBlocks, frequencyDict, termsDict

def ReadFileLine(readLine, createBlock=True, termsDict=None, frequencyDict=None):
    """Read a given line from the input file. Split up the given input and passes to the IdentifyVariables() function.
    
    If createBlock is true, creates instance of the custom class circuit block and assigns the its attributes to the
    values or resistance, conductance, capacitance, or inductance. If createBlock is flase, store the found values
    in the provided dictionaries and returns them.

    :param readLine: (String) A list of strings for the given line in the file
    :param block: (bool) creates an instance of a block if true
    :param termsDict: (Dictionary) Used to store the values from </TERMS> section
    :param frequencyDict: (Dictionary) Used to store the frequency values from </TERMS> section
    
    :return: (circuit Block) returns the created block.
    :returns: (Dictionary) the dictionary of given terms
    :returns: (Dictionary) the dictionary of given frequency terms
    """
    # Checks if the arguments are of the right type and prints an error message if not
    if type(readLine) != str:
        print("ERROR:\nreadLine must be type str and not type ", type(readLine))
        CreateEmptyCSV()
    if type(createBlock) != bool:
        print("ERROR:\ncreateBlock must be type bool and not type ", type(createBlock))
        CreateEmptyCSV()
    if type(termsDict) != dict and termsDict != None:
        print("ERROR:\nHere!!!termsDict must be type dict and not type ", type(termsDict))
        CreateEmptyCSV()
    if type(frequencyDict) != dict and frequencyDict != None:
        print("ERROR:\nfrequencyDict must be type dict and not type ", type(frequencyDict))
        CreateEmptyCSV()
    node1 = 0
    node2 = 0
    resistance = 0
    inductance = 0
    capacitance = 0
    previousSpaceIdx = 0 
    spaceIdx = 0
    # loops over the whole line
    while (spaceIdx != len(readLine)):
        # finds the next whitespace index in the given string
        nextVariables = readLine[previousSpaceIdx:]
        spaceIdx = nextVariables.find(" ")
        # if there is not whitespace, set the index to the last element
        if (spaceIdx == -1):
            spaceIdx = len(readLine)
        # returns everything between the two whitespaces
        readVariable = readLine[previousSpaceIdx:previousSpaceIdx+spaceIdx]
        # gets the name and value of the given variable
        value, name = IdentifyInputVariable(readVariable)
        # if there was not name or value, an error message is printed
        if value == None or name == None:
            print("ERROR:\nIdentifyInputVariable returnded value: "+str(value)+", name: "+str(name)+", from the passed variable readVariable: "+str(readVariable))
            CreateEmptyCSV()
        # Check the name of the variable and processes the value
        name = name.lower()
        if (name == "n1"):
            node1 = value
        elif (name == "n2"):
            node2 = value
        elif (name == "r"):
            resistance = value
        elif (name == "g"):
            # error message to check if g is 0
            if value == 0:
                print("ERROR:\nCannot divide by zero. g: %f"%(value))
            else:
                resistance = 1/value
        elif (name == "l"):
            inductance = value
        elif (name == "c"):
            capacitance = value
        elif (name == "vt"
            or name == "rs"
            or name == "in"
            or name == "gs"
            or name == "rl"):
            if name == "gs":
                # error message to check if g is 0
                if value == 0:
                    print("ERROR:\nCannot divide by zero. gs: %f"%(value))
                    return None
            # storing the values of the terms section within the terms dictionary
                termsDict["rs"] = 1/value
            else:
                termsDict[name] = value
        elif (name == "fstart"
            or name == "fend"
            or name == "nfreqs"
            or name == "lfstart"
            or name == "lfend"):
            # storing the values of the frequencies within the frequency dictionary
            frequencyDict[name] = value
        else:
            # prints an error message if the name is unrecognised
            print("ERROR:\nAnother variable has been identified %s"%(name))
        # set the previous space index to the current one to find the next variable in trhe given string line
        previousSpaceIdx += spaceIdx + 1
    if createBlock:
        # concaternating the node values to make the block name
        node1 = int(node1)
        node2 = int(node2)
        # if node2 is 0, the component is in parallel
        if node2 == 0:
            digitDifference = abs(len(str(node1)) - len(str(node2)))
            blockName = int(str(node1) + (str(node2)*(digitDifference + 1)))
            # create an instance of the Circuit Block object to be used to calculate the ABCD matrix
            tempBlock = CircuitBlock(name=blockName, resistance=resistance, capacitance=capacitance, inductance=inductance, series=False)
        # else, the component is in series
        else:
            blockName = int(str(node1) + str(node2))
            # create an instance of the Circuit Block object to be used to calculate the ABCD matrix
            tempBlock = CircuitBlock(name=blockName, resistance=resistance, capacitance=capacitance, inductance=inductance, series=True)
        return tempBlock
    else:
        # returns the terms and frequency dictionaries
        return termsDict, frequencyDict

def IdentifyInputVariable(stringVariable):
    """ Read the line and identify the given variables name and value.
    
    :param stringVariable: (String) contains the variable name and value
    
    :return: (float) returns the value of the variable
    :return: (string) name of the variable
    """
    # Checks to see if the given argument is of type string
    if type(stringVariable) != str:
        # prints error message if not type string
        print("ERROR:\nstringVariable must be type str and not type ", type(stringVariable))
        CreateEmptyCSV()
    # Removes the whitespaces in the string
    stringVariable.replace(" ","")
    # Finds the equals sign
    equalsIdx = stringVariable.find("=")
    if (equalsIdx > -1):
        # Everything before the equals is the variable name
        name  = stringVariable[0:equalsIdx]
        # everthing after is the variable value
        value = stringVariable[equalsIdx+1:]
        # assume exponent is 0
        exponent = 0
        # checks to see if there is a prefix
        if (value[len(value)-1].isalpha() and value.find("e") == -1):
            # Get shte corresponding exponent of the prefix
            exponent = IdentifyExponent(value[len(value)-1])
            # remove the prefix from the variable value
            value = value.rstrip(value[len(value)-1])
        try:
            # convert the value to a float
            value = float(value)
        except:
            # prints error message if it could not be turned into a float
            print('ERROR:\nTried to find float <%s> in string <%s>'%(value,stringVariable))
            CreateEmptyCSV()
        # using the exponent, converts the value into the correct form
        value *= (10**exponent)
        return value, name
    else:
        # if equals was not found, print an error message
        print("ERROR:\nEquals could not be found in <%s>"%(stringVariable))
        CreateEmptyCSV()

def IdentifyOutputVariable(stringVariable):
    """ Read the line and identify the given variables in that line.
    
    :param stringVariable: (String) contains the variable name and unit
    
    :return: (string) unit
    :return: (float) exponenet
    :return: (string) name
    """
    # Checks if thw arguments are the correct type. Prints error message if not
    if type(stringVariable) != str:
        print("ERROR:\nstringVariable must be type str and not type ", type(stringVariable))
        CreateEmptyCSV()
    # remove whitespace from either side of the string BUT not within the string
    stringVariable = stringVariable.rstrip()
    # finds the space within the string
    spaceIdx = stringVariable.find(" ")
    if (spaceIdx > -1):
        # everything before the whitespace is the variable name
        name = stringVariable[0:spaceIdx]
        # everything after the whitespace if the variable unit
        unit = stringVariable[spaceIdx+1:]
        # send over the first letter in the unit to check if it is a prefix
        exponent = IdentifyExponent(unit[0])
        if exponent != 0:
            if len(unit) == 1:
                # if there is a prefix but not unit, add concaternate "L" to the prefix
                unit = str(unit)+"L"
        # returns the variable unit, exponent, and name
        return unit, exponent, name
    else:
        # assume that the variable is voltage or current gain
        if stringVariable.lower().find("a") > -1:
            name = stringVariable
            # return the unit "L", exponent of 0 and the variable name
            return "L", 0, name
        else:
            # else, if there is no letter a, its not gain and therefore, there is an error in the input file
            print("ERROR:\nstringVariable must have spaces inbetween its name and unit")
            CreateEmptyCSV()

def IdentifyExponent(prefix):
    """ Converts the prefix into its corresponding exponent
    
    :param prefix: (string) unit prefix i.e. (k, u, G)
    
    :return: (float) the exponent i.e. (3, -6, 9)
    """
    # checks if the argument prefix is a string
    if type(prefix) != str:
        # prints error message if it is not a string
        print("ERROR:\nprefix must be type str and not type ", type(prefix))
        CreateEmptyCSV()
    # a dictionary of the prefixes and thier corresponding values
    unitDict = {"p":-12, "n":-9, "u":-6, "m":-3, "k":3, "K":3, "M":6, "G":9, "T":12}
    try:
        # returns the corressponding exponent
        exponent = unitDict[prefix]
        return exponent
    except Exception:
        # returns 0 if the prefix was not found
        return 0

def CalculateOutputs(blockList, termsDict, freqDict, outputDict):
    """ It will calculate the required outputs from the given output dictionary.

    Runs through each block in the list IN ORDER and calculates the requested values for each frequency
    
    :param blockList: (Block) the created blocks of the circuit to be used to calculate the required outputs
    :param termsDict: (Dictionary) the given terms
    :param freqDict: (Dictionary) the given frequency terms
    :param outputDict: (Dictionary) the required outputs
    
    :return: (2D-array) an array of all the values calculated.
    """
    resultsArray = []
    # gets the last circuit block in the list
    lastBlock = blockList[-1]

    # calculates a list of all the required frequencies
    if freqDict["fstart"] == None and freqDict["fend"] == None:
        # calculates logarithmic frequencies
        freqRange = list(np.logspace(math.log10(freqDict["lfstart"]), math.log10(freqDict["lfend"]), num = int(freqDict["nfreqs"])))
    elif freqDict["lfstart"] == None and freqDict["lfend"] == None:
        # calculates linear frequencies
        freqSteps = float((freqDict["fend"]-freqDict["fstart"])/(freqDict["nfreqs"]-1))
        freqRange = [int(freqDict["fstart"]) + freqSteps * i for i in range(int(freqDict["nfreqs"]))]
    else:
        print("ERROR:\nThere exists values for both linear and logarithmic frequencies")
        CreateEmptyCSV()

    # for each frequency within the frequency range, calculate the required outputs
    for frequency in freqRange:
        results = [frequency]
        for key, value in outputDict.items():
            if value != []:    
                if key == "vin":
                    # if the key is vin, calculates input voltage
                    result = lastBlock.InputVoltage(termsDict, frequency)*(10**value[1])
                elif key == "vout":
                    # if the key is vout, calculates output voltage
                    result = lastBlock.OutputVoltage(termsDict, frequency)*(10**value[1])
                elif key == "iin":
                    # if the key is iin, calculates input current
                    result = lastBlock.InputCurrent(termsDict, frequency)*(10**value[1])
                elif key == "iout":
                    # if the key is iout, calculates output current
                    result = lastBlock.OutputCurrent(termsDict, frequency)*(10**value[1])
                elif key == "pin":
                    # if the key is pin, calculates power in
                    result = lastBlock.InputPower(termsDict, frequency)*(10**value[1])
                elif key == "pout":
                    # if the key is pout, calculates power out
                    result = lastBlock.OutputPower(termsDict, frequency)*(10**value[1])
                elif key == "zin":
                    # if the key is zin, calculates input impedance
                    result = lastBlock.InputImpedance(termsDict["rl"], frequency)*(10**value[1])
                elif key == "zout":
                    # if the key is zout, calculates output impedance
                    result = lastBlock.OutputImpedance(termsDict["rs"], frequency)*(10**value[1])
                elif key == "av":
                    # if the key is av, calculates voltage gain
                    result = lastBlock.VoltageGain(termsDict["rl"], frequency)*(10**value[1])
                elif key == "ai":
                    # if the key is ai, calculates current gain
                    result = lastBlock.CurrentGain(termsDict["rl"], frequency)*(10**value[1])
                else:
                    # if there is an unknown key, prints an error message
                    print("ERROR:\nUnkown key: %s"%(key))
                # checks if the result must be in decibels
                if str(value[0]).find("dB") > -1:
                    # turns the values into decibels
                    result = CartessianToPolar(real=result.real, imag=result.imag)
                    result = complex(result[0], result[1])
                # append the result to the results list
                results.append(result)
        # append out results list to an array
        resultsArray.append(results)
    # return thje array of results
    return resultsArray

def CartessianToPolar(real, imag):
    """ Converts the given inputs from Cartesian form to polar form

    :param real: (float) the real value
    :param imag: (float) the imaginary value

    :return: (float) the value for magnitude
    :return: (float) the value for phase
    """
    # calculates the phase of the two given numbers
    phase = math.atan2(imag, real)
    # calculates the magnitude of the two given numbers
    magnitude = 20 * math.log10(math.sqrt((real**2)+(imag**2)))
    return magnitude, phase

def TimeResponse(outputDict):
    """ Calculates the time response of each output

    :param outputDict: (Dictionary) the calculated output values
    :param M: (int) denotes the multiplication of the length of the IFFT calculation

    :return: (Dictionary) same dictionary however the calculated values are in the time domain
    """
    for key, value in outputDict.items():
        np.fft.ifft([value[2]])

def CreateEmptyCSV():
    """ Create an empty CSV file for when an error occurs
    Creates an empty CSV file with the provided name if an error occurs within the program
    """
    print("\n\tError Creating Empty CSV file")
    # open a new CSV file with variable named f
    with open(outputFile, "w", newline="") as f:
        # create a CSV writer ot write to the file
        writerCSV = csv.writer(f)
    quit()

def FormatOutputTable(outputDict, results, filename="test"):
    """ Format the information into the correct format as desired by the lab script
    
    :param outputDict: (Dictionary) the requested output values and their units
    :param results: (float) 2D-array of the calculated values
    :param filename: (string) name of the output file
    """
    # adjusts the sapces of each element in the CSV file
    fieldNames = ["Freq".rjust(10)]
    fieldUnits = ["Hz".rjust(10)]
    for key, value in outputDict.items():
        if value != []:
            # if the output variable is in decibels
            if str(value[0]).find("dB") > -1:
                # format the field names to be in decibels
                fieldNames.append(("|%s|"%(str(key)).capitalize()).rjust(11))
                fieldNames.append(("/_%s"%(str(key)).capitalize()).rjust(11))
                # format the units to include rads
                fieldUnits.append(str(value[0]).rjust(11))
                fieldUnits.append("rads".rjust(11))
            # else, if the unit is not decibels
            else:
                # format the field names to be in real and imaginery
                fieldNames.append(("Re(%s)"%(str(key)).capitalize()).rjust(11))
                fieldNames.append(("Im(%s)"%(str(key)).capitalize()).rjust(11))
                # prints the units twice
                fieldUnits.append(str(value[0]).rjust(11))
                fieldUnits.append(str(value[0]).rjust(11))

    # open a new CSV file with variable named f
    with open(filename, "w", newline="") as f:
        # create a CSV writer ot write to the file
        writerCSV = csv.writer(f)
        
        # write the fields names and field units to the file
        writerCSV.writerow(fieldNames)
        writerCSV.writerow(fieldUnits)

        # loops through each results row in results
        for resultsRow in results:
            # formats each number to have 4 significant figures and be in scientific notation
            stringFreq = "{:.3e}".format(resultsRow[0])
            fieldValues = [stringFreq.rjust(10)]
            for idx in range(len(resultsRow)):
                if idx != 0:
                    stringReal = "{:.3e}".format(resultsRow[idx].real)
                    stringImag = "{:.3e}".format(resultsRow[idx].imag)
                    fieldValues.append(stringReal.rjust(11))
                    fieldValues.append(stringImag.rjust(11))
            # writes that row of results to the CSV file
            writerCSV.writerow(fieldValues)
    

print("\n\t")
print(sys.argv)
if (len(sys.argv)<3):
    print("\n\tError, program needs three arguments to run\n" )
    sys.exit(1)

# stores the input arguments in two variables
inputFile = sys.argv[1]
outputFile = sys.argv[2]

# read the file
outputDict, blockList, freqDict, termsDict = ReadInputFile(inputFile)

# sorts the circuit blocks in the list
blockList = sorted(blockList, key=lambda Block: Block.name)
for index,block in enumerate(blockList):
    if index != 0:
        block.previousBlock = blockList[index - 1]

# calcualte the requested outputs
results = CalculateOutputs(blockList,termsDict,freqDict,outputDict)

# save the results to a file
try:
    FormatOutputTable(outputDict, results, filename=outputFile)
except Exception:
    FormatOutputTable(outputDict, results)
