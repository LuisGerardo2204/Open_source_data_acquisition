#
# @section LICENSE
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of
# the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details at
# http://www.gnu.org/copyleft/gpl.html
#  credits and special thanks to Hamed Seyed-Allaei
# This program is based in his usefull repository 
# https://github.com/hamed/snowWhiteNoise
#
#



from __future__ import division, absolute_import, print_function
import serial   
import array    
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.figure import Figure
import matplotlib.pylab as plb
import numpy as np
from optparse import OptionParser   
import time   
import math
plt.style.use('ggplot')
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk) 
import tkinter as tk
from tkinter import ttk
import tkinter.font as font
import serial.tools.list_ports
from PIL import ImageTk, Image
from scipy.signal import find_peaks
from scipy import signal
from scipy.fft import fftshift
from matplotlib import cm # colour map
from matplotlib import mlab

#----------------------------------------------------------
#                       --- functions ---
#----------------------------------------------------------
def serial_ports():    
    return serial.tools.list_ports.comports()

def on_select(event=None):

    # get selection from event    
    print("event.widget:", event.widget.get())
    global puerto
    puerto = cb.get()
    # or get selection directly from combobox
    print("comboboxes: ", cb.get())
    ser = serial.Serial(puerto[0:4],baudrate=2000000,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE,
                    bytesize=serial.EIGHTBITS)


def on_select2(event=None):

    # get selection from event    
    print("event.widget:", event.widget.get())
    samplingRate=int(entry2.get())
    T=1/samplingRate
    global muestras
    global n_muestras
    muestras=[T*2**12,T*2**14,T*2**16,T*2**18,T*2**20,T*2**22]
    cbt['values']=muestras
    row.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
    n_muestras = cbt.get()
    row.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
    # or get selection directly from combobox
    print("comboboxes: ", cb.get())
   
def on_select3(event=None):

    # get selection from event    
    print("event.widget:", event.widget.get())
 
    global nfft
    nfft=[2**12,2**14,2**16,2**18,2**20,2**22]
    cbf['values']=nfft
    row.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
    nfft= cbf.get()
    print(nfft)
    row.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
    # or get selection directly from combobox
    print("comboboxes: ", cbf.get())


def on_select4(event=None):

    # get selection from event    
    print("event.widget:", event.widget.get())
    global opcion
    global seleccion
    opcion=["Acceleration","Voltage","Mic"]
    cbo['values']=opcion
    row.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
    seleccion = cbo.get()
    print(seleccion)
    row.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
    # or get selection directly from combobox
    print("comboboxes: ", cbo.get())    

    if seleccion=="Acceleration":

       img2 = Image.open("acel.jpg")
       img2_resized=img2.resize((341,256)) # new width & height
       my_img2=ImageTk.PhotoImage(img2_resized)
       l1.place(rely=3.2*(0.1 + RH*0.54),relheight=0.48, relwidth=0.3)
       l1.configure(image=my_img2)
       l1.image = my_img2      
       
    elif seleccion=="Voltage":

       img2 = Image.open("volt.jpg")
       img2_resized=img2.resize((341,256)) # new width & height
       my_img2=ImageTk.PhotoImage(img2_resized)
       l1.place(rely=3.2*(0.1 + RH*0.54),relheight=0.48, relwidth=0.3)
       l1.configure(image=my_img2)
       l1.image = my_img2


    elif seleccion=="Mic":

       img2 = Image.open("mic.jpg")
       img2_resized=img2.resize((341,256)) # new width & height
       my_img2=ImageTk.PhotoImage(img2_resized)
       l1.place(rely=3.2*(0.1 + RH*0.54),relheight=0.48, relwidth=0.3)
       l1.configure(image=my_img2)
       l1.image = my_img2       
      
    else:

       img2 = Image.open("Arduino Due.jpg")
       img2_resized=img2.resize((331,256)) # new width & height
       my_img2=ImageTk.PhotoImage(img2_resized)
       l1.configure(image=my_img2)
       l1.image = my_img2  

          
def get_value():

    global T
    global nSamples
    global a
    global adc
    global t
    global ventana2
    global samplingRate
    T1.delete('1.0', tk.END)

    pb["value"] = 0
    samplingRate=int(entry2.get())
    
    T=1/samplingRate
    muestras=[T*2**12,T*2**14,T*2**16,T*2**18,T*2**20,T*2**22]
    cbt['values']=muestras
    cbt.pack(side=tk.LEFT,fill=tk.X)
    row.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
    p1.update()

    
   
    nSamples = int(float(n_muestras)/T)    

    
    NFFT = nfft               

    a = array.array('H') 


    parser = OptionParser()
    parser.add_option("-s", "--serial-port", dest="port", type="string",
                      help="Listen to PORT serial port. Like -s /dev/ttyACM0",
                      metavar="PORT")
    parser.add_option("-f", "--format", dest="format", type="string",
                      help="File format for the outputs: png, pdf, eps, ps, svg",
                      metavar="FORMAT")

    (options, args) = parser.parse_args()
   
    ser = serial.Serial(port=puerto[0:4],
                        baudrate=2000000,
                        parity=serial.PARITY_NONE,
                        stopbits=serial.STOPBITS_ONE,
                        bytesize=serial.EIGHTBITS)

    ser.write((str(nSamples) + '\n' + str(samplingRate) + '\n').encode(encoding='ascii',errors='strict'))


    print("Acquiring data")
    root.update()
    i=0
    if ser.isOpen():
        for i in range(nSamples//128):
            a.fromstring(ser.read(512))
            pb["value"] =((i+1)/(nSamples//128))*100
            p1.update()
    ser.close()
   
 
    print("Acquisition done. Post-processing starts")

    b = np.array(a)  # Make a numpy array.
    acel = np.array(a)
    

    adc = b[b < 2**13]
    v1=(adc-adc.mean());


    t=np.empty(adc.size)
    i=0
    acel=3.3*(adc-adc.mean())
    for i in range(adc.size):
        t[i]=i*(1/samplingRate)


    i=0
    if seleccion=="Acceleration":

       img2 = Image.open("acel.jpg")
       img2_resized=img2.resize((341,256)) # new width & height
       my_img2=ImageTk.PhotoImage(img2_resized)
       l1.configure(image=my_img2)
       l1.image = my_img2      

       f= open("Data_accel.txt","w+")
       for i in range(len(adc)):
           f.write(str(i*(1/samplingRate)))
           f.write(",")
           f.write(str(round((acel[i]/ 4096)/0.33,4)))
           f.write("\n")
           i=i+1
       f.close() 
       filename=str(int(time.time())) + "_" + str(nSamples) + "_" + str(samplingRate)
       
       
    elif seleccion=="Voltage":

       img2 = Image.open("volt.jpg")
       img2_resized=img2.resize((341,256)) # new width & height
       my_img2=ImageTk.PhotoImage(img2_resized)
       l1.configure(image=my_img2)
       l1.image = my_img2

       f= open("Data_voltage.txt","w+")
       for i in range(len(adc)):
           f.write(str(i*(1/samplingRate)))
           f.write(",")
           f.write(str(round((3.3*adc[i]/4095),4)))
           f.write("\n")
           i=i+1
       f.close() 
       filename=str(int(time.time())) + "_" + str(nSamples) + "_" + str(samplingRate)
       

    elif seleccion=="Mic":
       
       f= open("Data_mic.txt","w+")
       i=0
       for i in range(len(adc)):
            f.write(str(i*(1/samplingRate)))
            f.write(",")
            f.write(str(round(acel[i]/4096,4)))
            f.write("\n")
            i=i+1
       f.close()
       filename=str(int(time.time())) + "_" + str(nSamples) + "_" + str(samplingRate) 
       

    else:

        f= open("Data","w+")  
        i=0
        for i in range(len(adc)):
            f.write(str(i*(1/samplingRate)))
            f.write(",")
            f.write(str(round((3.3*(adc-adc.mean())/4096),4)))
            f.write("\n")
            i=i+1
        f.close() 
        filename=str(int(time.time())) + "_" + str(nSamples) + "_" + str(samplingRate) 
   

    
    if seleccion=="Acceleration":

        ax3.clear()
        tabla.clear()
        ax1.clear()
        ax2.clear()
        ax1.plot(t,(3.3*(adc-adc.mean())/ 4096)/0.33, color='C1')
        ax1.set_title('Acceleration')
        ax1.set_xlabel('time [s]')
        ax1.set_ylabel('Ac [g]')
        ax2.magnitude_spectrum(adc-adc.mean(),Fs=samplingRate, color='C1')
        ax2.set_xlabel('Frequency [Hz]')
        ax2.set_ylabel('Magnitude')

        ax3.magnitude_spectrum(v1,Fs=samplingRate, color='C1')
        ax3.set_xlabel('Frequency [Hz]')
        ax3.set_ylabel('Magnitude')

        ax1.set_facecolor("white")
        #ax1.grid(color='k', linestyle='-', linewidth=1)

        ax1.spines['bottom'].set_color('yellow')
        ax1.spines['top'].set_color('red')
        ax1.spines['right'].set_color('black')
        ax1.spines['left'].set_color('blue')
       
        ax1.spines['bottom'].set_color('black')
        ax1.spines['top'].set_color('black')
        ax1.spines['right'].set_color('black')
        ax1.spines['left'].set_color('black')

        ax2.set_facecolor("white")
        #ax2.grid(color='k', linestyle='-', linewidth=1)

        ax2.spines['bottom'].set_color('yellow')
        ax2.spines['top'].set_color('red')
        ax2.spines['right'].set_color('black')
        ax2.spines['left'].set_color('blue')
       
        ax2.spines['bottom'].set_color('black')
        ax2.spines['top'].set_color('black')
        ax2.spines['right'].set_color('black')
        ax2.spines['left'].set_color('black')
        
        linea1.draw()
        linea1.flush_events() 
        linea1.get_tk_widget().pack()

        linea2.draw()
        linea2.flush_events() 
        linea2.get_tk_widget().pack()

        line2.draw()
        line2.flush_events() 
        line2.get_tk_widget().pack()

 
        
    elif seleccion=="Voltage":

        ax3.clear()
        tabla.clear()
        ax1.clear()
        ax2.clear()
        ax1.plot(t,(3.3*adc/4096), color='C1')
        ax1.set_title('Voltage')
        ax1.set_xlabel('time [s]')
        ax1.set_ylabel('V [volts]')
        ax2.magnitude_spectrum(adc-adc.mean(),Fs=samplingRate, color='C1')
        ax2.set_xlabel('Frequency [Hz]')
        ax2.set_ylabel('Magnitude')

        ax3.magnitude_spectrum(v1,Fs=samplingRate, color='C1')
        ax3.set_xlabel('Frequency [Hz]')
        ax3.set_ylabel('Magnitude')

        ax1.set_facecolor("white")
        #ax1.grid(color='k', linestyle='-', linewidth=1)

        ax1.spines['bottom'].set_color('yellow')
        ax1.spines['top'].set_color('red')
        ax1.spines['right'].set_color('black')
        ax1.spines['left'].set_color('blue')
       
        ax1.spines['bottom'].set_color('black')
        ax1.spines['top'].set_color('black')
        ax1.spines['right'].set_color('black')
        ax1.spines['left'].set_color('black')

        ax2.set_facecolor("white")
        #ax2.grid(color='k', linestyle='-', linewidth=1)

        ax2.spines['bottom'].set_color('yellow')
        ax2.spines['top'].set_color('red')
        ax2.spines['right'].set_color('black')
        ax2.spines['left'].set_color('blue')
       
        ax2.spines['bottom'].set_color('black')
        ax2.spines['top'].set_color('black')
        ax2.spines['right'].set_color('black')
        ax2.spines['left'].set_color('black')
        
        linea1.draw()
        linea1.flush_events() 
        linea1.get_tk_widget().pack()

        linea2.draw()
        linea2.flush_events() 
        linea2.get_tk_widget().pack()

        line2.draw()
        line2.flush_events() 
        line2.get_tk_widget().pack()
        
    elif seleccion=="Mic":

         ax3.clear()
         tabla.clear()
         ax1.clear()
         ax2.clear()
         ax1.plot(t,(3.3*(adc-adc.mean())/4096), color='C1')
         ax1.set_title('Voltage')
         ax1.set_xlabel('time [s]')
         ax1.set_ylabel('V [volts]')
         ax2.magnitude_spectrum(adc-adc.mean(),Fs=samplingRate, color='C1')
         ax2.set_xlabel('Frequency [Hz]')
         ax2.set_ylabel('Magnitude')
         
         ax3.magnitude_spectrum(v1,Fs=samplingRate, color='C1')
         ax3.set_xlabel('Frequency [Hz]')
         ax3.set_ylabel('Magnitude')

         ax1.set_facecolor("white")
         ax2.set_facecolor("white")
        #ax1.grid(color='k', linestyle='-', linewidth=1)

         ax1.spines['bottom'].set_color('yellow')
         ax1.spines['top'].set_color('red')
         ax1.spines['right'].set_color('black')
         ax1.spines['left'].set_color('blue')
       
         ax1.spines['bottom'].set_color('black')
         ax1.spines['top'].set_color('black')
         ax1.spines['right'].set_color('black')
         ax1.spines['left'].set_color('black')

         ax2.spines['bottom'].set_color('yellow')
         ax2.spines['top'].set_color('red')
         ax2.spines['right'].set_color('black')
         ax2.spines['left'].set_color('blue')
       
         ax2.spines['bottom'].set_color('black')
         ax2.spines['top'].set_color('black')
         ax2.spines['right'].set_color('black')
         ax2.spines['left'].set_color('black')

         linea1.draw()
         linea1.flush_events() 
         linea1.get_tk_widget().pack()

         linea2.draw()
         linea2.flush_events() 
         linea2.get_tk_widget().pack()

         line2.draw()
         line2.flush_events() 
         line2.get_tk_widget().pack()

    else:
        
         ax3.clear()
         tabla.clear()
         ax1.clear()
         ax2.clear()
         ax1.plot(t,(3.3*(adc-adc.mean())/4096), color='C1')
         ax1.set_title('Voltage')
         ax1.set_xlabel('time [s]')
         ax1.set_ylabel('V [volts]')
         ax2.magnitude_spectrum(adc-adc.mean(),Fs=samplingRate, color='C1')
         ax3.set_xlabel('Frequency [Hz]')
         ax3.set_ylabel('Magnitud')
         ax2.set_xlabel('Frequency [Hz]')
         ax2.set_ylabel('Magnitud')

         ax1.set_facecolor("white")
         ax2.set_facecolor("white")
        #ax1.grid(color='k', linestyle='-', linewidth=1)

         ax1.spines['bottom'].set_color('yellow')
         ax1.spines['top'].set_color('red')
         ax1.spines['right'].set_color('black')
         ax1.spines['left'].set_color('blue')
       
         ax1.spines['bottom'].set_color('black')
         ax1.spines['top'].set_color('black')
         ax1.spines['right'].set_color('black')
         ax1.spines['left'].set_color('black')

         linea1.draw()
         linea1.flush_events() 
         linea1.get_tk_widget().pack()

         line2.draw()
         line2.flush_events() 
         line2.get_tk_widget().pack()

    nb.add(p2,text='Analysis')     
    ventana2="An"


def buscar ():
    
    global espectro
    global f
    global peaks
    global ventana3
    global selecciond
    T1.delete('1.0', tk.END)
    if(ventana2=="An"):
     
       ax3.clear()
       tabla.clear()
       v1=(adc-adc.mean());

       espectro,f,uno=ax3.magnitude_spectrum(v1,Fs=samplingRate, color='C1')
       ax3.set_xlabel('Frequency [Hz]')
       ax3.set_ylabel('Magnitude')
       altura=float(entry12.get())
       distancia=float(entry22.get())
       peaks, _ = find_peaks(espectro, height=altura,distance=distancia)
       np.diff(peaks)

       if len(peaks) == 0:
           T1.delete('1.0', tk.END)
           quote = "No peaks found"
           T1.tag_configure("center", justify='center')
           T1.tag_add("center", 1.0, "end")
           T1.insert(tk.END, quote)

       else:
           T1.delete('1.0', tk.END)
           quote = "Peaks found!!!"
           T1.tag_configure("center", justify='center')
           T1.tag_add("center", 1.0, "end")
           T1.insert(tk.END, quote)
           
           ax3.plot(f,espectro, color='C1')
           ax3.plot(f[peaks],espectro[peaks], "x")
           ax3.set_xlim(min(f[peaks])-0.25*min(f[peaks]),max(f[peaks])+0.25*max(f[peaks]))

           columns = ('Frequency [Hz]','Amplitude')
           rows=np.empty(peaks.size)
           i=0
           for i in range(peaks.size-1):
               rows[i] =i+1
    
           tabla.axis("off")
           datos=np.empty([peaks.size,2])
           #print(datos)
           a=(f[peaks])
           b=(espectro[peaks])
           i=0
           for i in range(peaks.size):
               datos[i][0] =a[i]
           i=0      
           for i in range(peaks.size):
              datos[i][1] =b[i]    

           i=0
           for i in range(peaks.size):
              rows[i]=str(i+1)    
              #print(datos)

           la_tabla = tabla.table(cellText=datos,rowLabels=rows, colLabels=columns,
                      loc='center')
           plt.subplots_adjust(bottom=0.05)
       
           ax3.set_facecolor("white")
          #ax1.grid(color='k', linestyle='-', linewidth=1)

           ax3.spines['bottom'].set_color('yellow')
           ax3.spines['top'].set_color('red')
           ax3.spines['right'].set_color('black')
           ax3.spines['left'].set_color('blue')
       
           ax3.spines['bottom'].set_color('black')
           ax3.spines['top'].set_color('black')
           ax3.spines['right'].set_color('black')
           ax3.spines['left'].set_color('black')
       
           line2.draw()
           line2.flush_events() 
           line2.get_tk_widget().pack()

           nb.add(p3,text='Spectrogram')     
           ventana3="Es"
           p1.update()
   
    else:
       ventana3="Es" 


def espectro ():
    global ventana3
    if(ventana3=="Es"):
    
        ax4.clear()
        ax5.clear()  
            
        v1=(adc-adc.mean());
        freq, time, spec = signal.spectrogram(v1,samplingRate)

        myfilter = (freq>min(f[peaks])-0.25*min(f[peaks])) & (freq<max(f[peaks])+0.25*max(f[peaks]))
        freq = freq[myfilter]
        spec = spec[myfilter, ...]
        
        ax5.plot_surface(freq[:, None],time[None, :], 10.0*np.log10(spec) , cmap=cm.coolwarm)
        
        ax4.specgram(v1,Fs=samplingRate,mode='magnitude')
        ax4.set_title('Spectrogram')
        ax4.set_xlabel('time [s]')
        ax4.set_ylabel('Frequency [Hz]')
       

        ax4.set_facecolor("white")
        ax4.grid(color='k', linestyle='-', linewidth=1)

        ax4.spines['bottom'].set_color('yellow')
        ax4.spines['top'].set_color('red')
        ax4.spines['right'].set_color('black')
        ax4.spines['left'].set_color('blue')
        
        ax4.spines['bottom'].set_color('black')
        ax4.spines['top'].set_color('black')
        ax4.spines['right'].set_color('black')
        ax4.spines['left'].set_color('black')

             
        line3.draw()
        line3.flush_events() 
        line3.get_tk_widget().pack()
      
        ax5.set_title('Spectrogram')
        ax5.set_ylabel('time [s]')
        ax5.set_xlabel('Frequency [Hz]')
        ax5.set_zlabel('Amplitude (dB)')

        ax5.set_facecolor("white")
        ax5.grid(color='w', linestyle='-', linewidth=1)

        ax5.spines['bottom'].set_color('yellow')
        ax5.spines['top'].set_color('red')
        ax5.spines['right'].set_color('black')
        ax5.spines['left'].set_color('blue')
        
        ax5.spines['bottom'].set_color('black')
        ax5.spines['top'].set_color('black')
        ax5.spines['right'].set_color('black')
        ax5.spines['left'].set_color('black')

        line4.draw()
        line4.flush_events() 
        line4.get_tk_widget().pack()
       

    else:
        ventana3=" " 
    p3.update()
#-----------------------------------------------------------------------------------
#                              ---Main loop---
#-----------------------------------------------------------------------------------

root = tk.Tk()
root.geometry('1300x690')
root.title("Signals analyzer")
nb=ttk.Notebook(root)
nb.pack(fill='both',expand='yes')
p1=ttk.Frame(nb)
p2=ttk.Frame(nb)
p3=ttk.Frame(nb)


ventana2="no"
ventana3="no"
nb.add(p1,text='Data acquisition')

row5 = tk.Frame(p1)
cbo = ttk.Combobox(row5, values=["Acceleration","Voltage","Mic"])
row5.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
lab5 = tk.Label(row5,font=('Century 12'), width=22,text="Sensor:")
lab5.pack(side=tk.LEFT)
cbo.pack(side=tk.LEFT,fill=tk.X)

row2 = tk.Frame(p1)
entry2 = ttk.Entry(row2,font=('Century 12'),width=6)
entry2.insert(0, "5000")
row2.pack(side=tk.TOP,fill=tk.BOTH,padx=5, pady=5)
lab2 = tk.Label(row2,font=('Century 12'), width=22,text="Sample Rate (max 100 KHz):")
lab2.pack(side=tk.LEFT)
entry2.pack(side=tk.LEFT,fill=tk.X)


samplingRate=int(entry2.get())
T=1/samplingRate
muestras=[T*2**12,T*2**14,T*2**16,T*2**18,T*2**20,T*2**22]
row = tk.Frame(p1)
cbt = ttk.Combobox(row, values=muestras)
row.pack(side=tk.TOP, fill=tk.BOTH, padx=5, pady=5)
lab = tk.Label(row,font=('Century 12'), width=22,text="Time (seconds):")
lab.pack(side=tk.LEFT)
cbt.pack(side=tk.LEFT,fill=tk.X)


row3 = tk.Frame(p1)
cb = ttk.Combobox(row3, values=serial_ports())
row3.pack(side=tk.TOP, fill=tk.BOTH, padx=5, pady=5)
lab3 = tk.Label(row3,font=('Century 12'), width=22,text="COM Port select:")
lab3.pack(side=tk.LEFT)
cb.pack(side=tk.LEFT,fill=tk.X)

row4 = tk.Frame(p1)
cbf = ttk.Combobox(row4, values=[2**12,2**14,2**16,2**18,2**20,2**22])
row4.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
lab4 = tk.Label(row4,font=('Century 12'), width=22,text="NFFT:")
lab4.pack(side=tk.LEFT)
cbf.pack(side=tk.LEFT,fill=tk.X)


RH = 0.1
s = ttk.Style()
s.configure('my.TButton', font=('Century', 16),padding=6, relief="flat",background="#000")
button= ttk.Button(p1, text="Acquire signal",style='my.TButton',command= get_value)
button.pack(side=tk.TOP,padx=250,pady=5)
button.place(rely= 2*(0.1 + RH*0.54),relx= 0.08,relheight=0.1, relwidth=0.13)


pb = ttk.Progressbar(p1, length=200,mode="determinate",orient=tk.HORIZONTAL)
pb.pack(side=tk.TOP,fill=tk.X,padx=25,pady=25)
pb.place(rely=2.8*(0.1 + RH*0.54),relheight=0.04, relwidth=0.3)
pb["value"] = 0


# Right frame

right_frame = tk.Frame(p1, bg='#C0C0C0', bd=1.5)
right_frame.place(relx=0.3, rely=0.0, relwidth=0.7, relheight=0.95)

nb1=ttk.Notebook(right_frame)
nb1.pack(fill='both',expand='yes')
pa1=ttk.Frame(nb1)
pa2=ttk.Frame(nb1)

fig1 = plt.figure()
ax1 = fig1.add_subplot(111)
linea1 = FigureCanvasTkAgg(fig1,pa1)
linea1.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH,expand=1)
toolbar = NavigationToolbar2Tk(linea1,pa1)


fig2 = plt.figure()
ax2 = fig2.add_subplot(111)
linea2 = FigureCanvasTkAgg(fig2,pa2)
linea2.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH,expand=1)
toolbar = NavigationToolbar2Tk(linea2,pa2)

nb1.add(pa1,text='Time domain')
nb1.add(pa2,text='Frequency domain')
#-------------------------------------------------------------------------------------------#
#                         Analysis tab                                                      #
#-------------------------------------------------------------------------------------------#
rotulo = tk.Frame(p2)
letrero= tk.Label(rotulo,font=('Century 12'), width=25,text="Peak pick parameters")
rotulo.pack(side=tk.TOP,fill=tk.BOTH,padx=15, pady=15)
letrero.pack(side=tk.LEFT)

row12 = tk.Frame(p2)
entry12 = ttk.Entry(row12,font=('Century 12'),width=5)
entry12.insert(0, "1")
row12.pack(side=tk.TOP,fill=tk.BOTH,padx=5, pady=5)
lab12 = tk.Label(row12,font=('Century 12'), width=15,text="Height(Abs):")
lab12.pack(side=tk.LEFT)
entry12.pack(side=tk.LEFT,fill=tk.X)

row22 = tk.Frame(p2)
entry22 = ttk.Entry(row22,font=('Century 12'),width=5)
entry22.insert(0, "1")
row22.pack(side=tk.TOP,fill=tk.BOTH,padx=5, pady=5)
lab22 = tk.Label(row22,font=('Century 12'), width=15,text="Separation(Hz):")
lab22.pack(side=tk.LEFT)
entry22.pack(side=tk.LEFT,fill=tk.X)

RH = 0.1
button2= ttk.Button(p2, text="Search peaks",style='my.TButton',command= buscar)
button2.pack(side=tk.TOP,padx=250,pady=5)
button2.place(rely= 1.5*(0.1 + RH*0.54),relx= 0.08,relheight=0.1, relwidth=0.13)

T1 = tk.Text(p2, height=10, width=30)
T1.pack()
quote = " "
T1.tag_configure("center", justify='center')
T1.tag_add("center", 1.0, "end")
T1.insert(tk.END, quote)
T1.place(rely= 2.3*(0.1 + RH*0.54),relx= 0.067,relheight=0.028, relwidth=0.15)

T2 = tk.Text(p2, height=10, width=30)
T2.pack()
quote = """In this tab, the search for peaks of the fast Fourier FFT transform is performed.
of the acquired data in the acquisition tab. The parameters or search criteria are distance in Hertz and the absolute value.
Once you have inspected the FFT graph and established the search criteria, in the corresponding text entries, click search.
If peaks were found with the established criteria, they will be plotted and displayed in a table on the graph to the right."""
T2.tag_configure("center", justify='center')
T2.tag_add("center", 1.0, "end")
T2.insert(tk.END, quote)
T2.place(rely= 2.9*(0.1 + RH*0.54),relx= 0.01,relheight=0.32, relwidth=0.28)


right_frame2= tk.Frame(p2, bg='#C0C0C0', bd=1.5)
right_frame2.place(relx=0.3, rely=0.0, relwidth=0.7, relheight=0.95)

fig2, (ax3,tabla) = plt.subplots(nrows=2)
line2 = FigureCanvasTkAgg(fig2, right_frame2)
line2.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH,expand=1)
toolbar2 = NavigationToolbar2Tk(line2,right_frame2)
#-------------------------------------------------------------------------------------------#
#                         Spectrogram Tab                                                   #
#-------------------------------------------------------------------------------------------#

RH = 0.1
button3= ttk.Button(p3, text="Plot Spectrogram",style='my.TButton',command= espectro)
button3.pack(side=tk.TOP,padx=250,pady=5)
button3.place(rely= 0.5*(0.1 + RH*0.54),relx= 0.02,relheight=0.1, relwidth=0.2)

# Right frame
right_frame3= tk.Frame(p3, bg='#C0C0C0', bd=1.5)
right_frame3.place(relx=0.3, rely=0.0, relwidth=0.7, relheight=0.95)
nb2=ttk.Notebook(right_frame3)
nb2.pack(fill='both',expand='yes')
p12=ttk.Frame(nb2)
p22=ttk.Frame(nb2)

fig3,ax4= plt.subplots(nrows=1)
line3 = FigureCanvasTkAgg(fig3,p12)
line3.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH,expand=1)
toolbar3 = NavigationToolbar2Tk(line3,p12)

fig4= plt.figure()
ax5 = fig4.add_subplot(111, projection='3d')
line4 = FigureCanvasTkAgg(fig4,p22)
line4.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH,expand=1)
toolbar4 = NavigationToolbar2Tk(line4,p22)

nb2.add(p12,text='Spectrogram')
nb2.add(p22,text='3D Spectrogram')

img = Image.open("Arduino Due.jpg")
img_resized=img.resize((341,224)) # new width & height
my_img=ImageTk.PhotoImage(img_resized)
l1=tk.Label(p1,image=my_img)
l1.pack(side=tk.LEFT)
l1.place(rely=3.1*(0.1 + RH*0.54),relheight=0.48, relwidth=0.3)

T3 = tk.Text(p3, height=10, width=30)
T3.pack()
quote = """In this tab the spectrogram of the signal acquired in the first tab of this interface is plotted.
The spectrogram is a graph that shows the evolution of the frequency content of a signal over time.
If the amount of information is adequate, the spectrogram will be displayed on the right, in the first tab of the graph and in the second tab the spectrogram will be displayed in a surface or 3D type graph.
In case of not visualizing the 3D graph, try with a longer total acquisition time in the main tab of this interface."""
T3.tag_configure("center", justify='center')
T3.tag_add("center", 1.0, "end")
T3.insert(tk.END, quote)
T3.place(rely= 2.9*(0.1 + RH*0.54),relx= 0.01,relheight=0.34, relwidth=0.28)


cb.bind('<<ComboboxSelected>>', on_select)
cbt.bind('<<ComboboxSelected>>',on_select2)
cbf.bind('<<ComboboxSelected>>',on_select3)
cbo.bind('<<ComboboxSelected>>',on_select4)



root.mainloop()

