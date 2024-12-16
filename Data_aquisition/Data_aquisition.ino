
/**
 * @section LICENSE
 *
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License as
 * published by the Free Software Foundation; either version 2 of
 * the License, or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
 * General Public License for more details at
 * http://www.gnu.org/copyleft/gpl.html
 * credits and special thanks to Hamed Seyed-Allaei
 * This program is based in his usefull repository 
 * https://github.com/hamed/snowWhiteNoise
 */



unsigned int rc = 42*5;       
unsigned int samplingRate=200000;
unsigned long nSamples=1<<22;  

#define BUFFER_SIZE 128
#define NUMBER_OF_BUFFERS 32

unsigned long dacIndex=0, dacUSBIndex=0, trngIndex=0, trngidx=0; 
unsigned long adcIndex=0, adcUSBIndex=0;
unsigned long dacBuffer[NUMBER_OF_BUFFERS][BUFFER_SIZE];
unsigned long adcBuffer[NUMBER_OF_BUFFERS][BUFFER_SIZE];
const unsigned long divider=NUMBER_OF_BUFFERS-1;

#include <Scheduler.h>

void setup() {

  Serial.begin(9600); 

  pmc_enable_periph_clk(ID_TC0);  
  pmc_enable_periph_clk(ID_TC1);  
  pmc_enable_periph_clk(ID_TRNG); 
  pmc_enable_periph_clk(ID_DACC); 

  trng_enable(TRNG);  
  trng_enable_interrupt(TRNG);

  int result = PIO_Configure( PIOB, PIO_PERIPH_B, PIO_PB25B_TIOA0, PIO_DEFAULT);

  Scheduler.startLoop(loopDAC);  
  Scheduler.startLoop(loopADC);
}

unsigned long nDACUSBSamples=0, nADCUSBSamples=0;  
signed long nDACSamples=-1, nADCSamples=-1;

void loopDAC() {
  if((nDACUSBSamples > 0) && (dacUSBIndex < trngIndex)) {
    SerialUSB.write((uint8_t *) dacBuffer[dacUSBIndex & divider], 4 * BUFFER_SIZE);  
    nDACUSBSamples -= 2 * BUFFER_SIZE;
    dacUSBIndex++;  
  }
    yield(); 
}

void loopADC() {
  if((nADCUSBSamples>0) && (adcUSBIndex < adcIndex)) {
    SerialUSB.write((uint8_t *) adcBuffer[adcUSBIndex & divider], 4 * BUFFER_SIZE);  
    nADCUSBSamples -= 2 * BUFFER_SIZE;
    adcUSBIndex++; 
  }
    yield();
}


void loop() {

  TC_Configure(TC0, 1, TC_CMR_WAVE|TC_CMR_WAVSEL_UP_RC|TC_CMR_ACPA_SET|TC_CMR_ACPC_CLEAR|TC_CMR_ASWTRG_CLEAR|TC_CMR_TCCLKS_TIMER_CLOCK1);
  TC_Configure(TC0, 0, TC_CMR_WAVE|TC_CMR_WAVSEL_UP_RC|TC_CMR_ACPA_CLEAR|TC_CMR_ACPC_SET|TC_CMR_ASWTRG_CLEAR|TC_CMR_TCCLKS_TIMER_CLOCK1);

  dacc_reset(DACC);                
  dacc_set_writeprotect(DACC, 0);
  dacc_set_transfer_mode(DACC, 1);  
  dacc_set_power_save(DACC, 0, 0);  
  dacc_set_timing(DACC, 0x08, 1, DACC_MR_STARTUP_0); 
  dacc_set_analog_control(DACC, DACC_ACR_IBCTLCH0(0x02)|DACC_ACR_IBCTLCH1(0x02)|DACC_ACR_IBCTLDACCORE(0x01)); 
  dacc_set_channel_selection(DACC, 1);  
  DACC->DACC_MR |= DACC_MR_TRGEN;       
  DACC->DACC_MR |= DACC_MR_TRGSEL(2);   
  DACC->DACC_IDR = ~(DACC_IDR_ENDTX);   
  DACC->DACC_IER = DACC_IER_ENDTX;     
  DACC->DACC_PTCR = DACC_PTCR_TXTEN | DACC_PTCR_RXTDIS;
  DACC->DACC_CHER = DACC_CHER_CH1;
  
  ADC->ADC_CR = ADC_CR_SWRST;         
  ADC->ADC_MR = 0;                    
  ADC->ADC_PTCR = (ADC_PTCR_RXTDIS|ADC_PTCR_TXTDIS);  

  ADC->ADC_MR |= ADC_MR_PRESCAL(3);  
  ADC->ADC_MR |= ADC_MR_STARTUP_SUT0; 
  ADC->ADC_MR |= ADC_MR_TRACKTIM(15);
  ADC->ADC_MR |= ADC_MR_TRANSFER(1);
  ADC->ADC_MR |= ADC_MR_TRGEN_EN; 
  ADC->ADC_MR |= ADC_MR_TRGSEL_ADC_TRIG1;
  ADC->ADC_CHER= ADC_CHER_CH5; % Uses chanel 2 of the arduino Due board 

  ADC->ADC_IDR   = ~ADC_IDR_ENDRX;
  ADC->ADC_IER   =  ADC_IER_ENDRX; 



  SerialUSB.begin(2000000); 
  while(!SerialUSB) { 
    delay(1000);
    Serial.print(".");
  };  

  while(SerialUSB.available() == 0);  
  nSamples = SerialUSB.parseInt();    
  Serial.println(nSamples);
   
  while(SerialUSB.available() == 0);    
  samplingRate = SerialUSB.parseInt();  

    
  while(SerialUSB.available() > 0) {SerialUSB.read();} 

  rc = 42000000/samplingRate;


  
  TC_SetRC(TC0, 1, rc);      
  TC_SetRA(TC0, 1, rc/2-25); 
                              
  TC_SetRC(TC0, 0, rc);     
  TC_SetRA(TC0, 0, rc/2);    
                              

  dacIndex=0; dacUSBIndex=0; adcIndex=0; adcUSBIndex=0; trngidx=0; trngIndex=0;

  nDACUSBSamples = nSamples;  
  nADCUSBSamples = nSamples;

  nDACSamples = nSamples;
  nADCSamples = nSamples;


  NVIC_EnableIRQ(TRNG_IRQn);
  while((trngIndex-dacIndex) <= divider) {delay(1); Serial.print('.');}

  while((dacUSBIndex < trngIndex) && nDACUSBSamples) {delay(1); Serial.print('.');}

  DACC->DACC_TPR  = (unsigned long) dacBuffer[dacIndex & divider];  
  DACC->DACC_TCR  = (unsigned int)  BUFFER_SIZE; 
  DACC->DACC_TNPR = (unsigned long) dacBuffer[(dacIndex + 1) & divider]; 
  DACC->DACC_TNCR = (unsigned int)  BUFFER_SIZE; 
  nDACSamples -= 2 * BUFFER_SIZE;


  ADC->ADC_RPR  = (unsigned long) adcBuffer[adcIndex & divider];  
  ADC->ADC_RCR  = (unsigned int)  2 * BUFFER_SIZE;  
  ADC->ADC_RNPR = (unsigned long) adcBuffer[(adcIndex + 1) & divider]; 
  ADC->ADC_RNCR = (unsigned int)  2 * BUFFER_SIZE;
  nADCSamples -= 2 * BUFFER_SIZE;


  NVIC_EnableIRQ(DACC_IRQn);
  NVIC_EnableIRQ(ADC_IRQn);
  ADC->ADC_PTCR  =  ADC_PTCR_RXTEN;  
  ADC->ADC_CR   |=  ADC_CR_START;    

  TC0->TC_CHANNEL[1].TC_SR;  
  TC0->TC_CHANNEL[0].TC_SR;
  TC0->TC_CHANNEL[1].TC_CCR = TC_CCR_CLKEN;  
  TC0->TC_CHANNEL[0].TC_CCR = TC_CCR_CLKEN;  

  TC0->TC_BCR = TC_BCR_SYNC;  
  while((nADCSamples > -1) || (nDACSamples > -1)) {yield();} 

  while((nADCUSBSamples > 0) || (nDACUSBSamples > 0)) {yield();} 

  yield();
}


void TRNG_Handler() {  
  int trngISR = TRNG->TRNG_ISR;
  if((trngIndex-dacIndex) <= divider) {  
    if(trngISR) {      
       dacBuffer[trngIndex & divider][trngidx] = (0x0FFF0FFF & TRNG->TRNG_ODATA) | 0x80008000; // TRNG, put 32 bits of random numbers into the buffer. 
      dacBuffer[trngIndex & divider][trngidx] =  0x8FFF8000; 
      trngidx++;  
      if(trngidx == BUFFER_SIZE) {
        trngidx=0;
        trngIndex++;
      }
    }
  }
}


void DACC_Handler() {
  unsigned long status =  DACC->DACC_ISR;
  if(status & DACC_ISR_ENDTX) {
    if(nDACSamples > 0) {
      dacIndex++;  
      DACC->DACC_TNPR = (unsigned long) dacBuffer[(dacIndex+1) & divider]; 
      DACC->DACC_TNCR = BUFFER_SIZE;  
      nDACSamples -= 2 * BUFFER_SIZE;
    }
    if((status & DACC_ISR_TXBUFE) && (nDACSamples == 0))  {

      nDACSamples=-1;
      dacIndex += 2;  
      NVIC_DisableIRQ(DACC_IRQn);  
      NVIC_DisableIRQ(TRNG_IRQn); 
      TC_Stop(TC0,1);
    }
  }
}


void ADC_Handler() {                
  unsigned long status = ADC->ADC_ISR;
  if(status & ADC_ISR_ENDRX)  {
    if(nADCSamples > 0) {
      adcIndex++;  
      ADC->ADC_RNPR  = (unsigned long) adcBuffer[(adcIndex+1) & divider];
      ADC->ADC_RNCR  = 2 * BUFFER_SIZE;
      nADCSamples   -= 2 * BUFFER_SIZE;
    }
    if((status & ADC_ISR_RXBUFF) && (nADCSamples == 0)) {
      nADCSamples=-1;   
      adcIndex +=2;    
      NVIC_DisableIRQ(ADC_IRQn);  
      TC_Stop(TC0,0);
      adc_stop(ADC);      
    }
  }
}
