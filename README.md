# PowerProfiler

Basado en INA3221

* esphome/ -firmware y pruebas
* analytics/ - Notebooks con pruebas de cálculos
* app/ - aplicaciones: captura de salida serial, etc
* sample_data/ - en https://drive.google.com/drive/folders/1CM8SqmRR2LszMyvAy8zZjb8g4PDH1W1i

## Notas

* El INA3221 no sirve para medir <1mA, habrá que dividir los periodos de RUN y DEEP SLEEP y medir el DS con multímetro 
## Experimentos

* descarga_bateria
* ds-*: Pruebas de deep sleep en varios controladores:
    * nodemcu
    *  
## Tareas

* Mandar a archivo en vez de stdout

* ¿Por qué se resetea el NodeMCU de repente y al iniciar el serial? 


## Recursos
https://programarfacil.com/esp8266/esp8266-deep-sleep-nodemcu-wemos-d1-mini/

