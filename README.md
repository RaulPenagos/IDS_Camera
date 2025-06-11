# IDS Camera

Este repositorio incluye scipts que permiten utilizar una cámara IDS, tomar y analizar imágenes.

Librerías necesarias: ids_peak, numpy, matplotlib, cv2, ...


## Resumen Scripts:

- CircleCompleter: incluye una función Likelihood para ajustar una serie de puntos al borde de un circulo y extraer su centro. 

- IDS_Camera: Define la clase Camera con todas la funciones necesarias para abrir, operar y tomar fotos con una cámaras IDS

- Image: define la clase Image, para guardar, anlizar y extraer información de imagenes tomadas con la cámara.

- test: Incluye ejemplos de uso de las principales funcionalidades.



## Uso de la cámara IDS y procesamiento de imágenes 

Para la utilización de la cámara, que inicialmente se empleará para medir la posición de puntos y marcas fiduciales, fue necesaria la implementación de un *software* orientado a objetos. En primer lugar, se desea fotografías y manipular todos los parámetros de la cámara desde códigos de Python, para lo que se creó la clase *IDS_Camera*. En segundo lugar, las fotografías deben permitir obtener el punto central de marcas fiduciales, y de los puntos de calibración (en la práctica orificios escariados de 1 mm ), para lo que fueron necesarios algoritmos básicos de edición de imagen, para facilitar este trabajo se generó la clase *Image*.

### Clase *IDS_Camera*

Para ejecutar la cámara correctamente, es necesarias la instalación de ciertas librerías gratuitas. En primer lugar se recomienda instalar la *suite software* desde la página de IDS utilizando el buscador para el modelo específico de la cámara[Camera uEye. Interface: USB3.0, Family: CP Rev2.2, Model: U3-3270CP-M-GL Rev 2.2.]. Se seleccionará entre las opciones el instalador de software *IDS-peak standard setup* y se extraerá en el equipo. Así, se habrá instalado también el *IDS cockpit*, para manipular la cámara con GUI. A continuación es necesario crear una variable de entorno apuntando al *path* del archivo *.cti* correspondiente (U3 y 64 bits) en la carpeta del software instalado. La variable se llamará:

```python
GENICAM_GENTL64_PATH
```

Por último, para su utilización en *python* bastará instalar la librería de la marca con *pip*. Esta por sí sola no permitiría la conexión a la cámara, razón por la que se han indicado los pasos anteriores.

```python
pip install ids_peak
```

Para usar la cámara se debe inicializar la librería de *ids_peak* y crear una instancia del controlador de dispositivos. Al actualizarlo, se puede detectar la cámara (si no está siendo utilizada por otra aplicación). A continuación, se abre la cámara y se establece el tipo de disparo (*software trigger*). Seguidamente, se puede iniciar la adquisición, período durante el cual se pueden tomar fotografías. Es necesario para esto definir el *buffer* y activar la adquisición a la espera de *triggers*. Se puede establecer el tiempo de exposición y a continuación tomar una imagen, ejecutando el trigger, extrayéndola del *buffer* y transformándola a formato color rgb. Finalmente, se puede guardar o procesar.

Al acabar, es necesario asegurar que los dispositivos estén cerrados. Para lo cual se cierra la librería *ids_peak*.

```python
ids_peak.Library.Close()
```

Los anteriores pasos se englobaron en una clase *IDS_Camera*, en la cual se simplifica el uso de la cámara a:
1. Conectar la cámara al ordenador con USB
2. Crear una instancia de la clase *IDS_Camera*
3. Ejecutar la función *start_camera()*, que inicializa la cámara desde cero hasta la adquisición.
4. Tomar fotografías con las funciones desarrolladas *get_image()* o *auto_exposure_get_image()*. La segunda de las cuales realiza varias fotografías para calibrar su exposición a las condiciones externas automáticamente.
5. Finalmente, ejecutar *close_device()*.

### Clase *Image*

Con el fin de editar las imágenes tomadas con la cámara, estas se crean como instancias de la clase *Image*. En esta, se almacena una copia original de la matriz de la imagen y se ofrecen múltiples métodos para procesarla. *Image* utiliza la librería *python* *cv2*, que se puede instalar así:

```python
pip install opencv-python
```

- **save()** Guarda la imagen en el *path* indicado. Las fotografía se identifican acorde a la fecha y hora de creación.
- **display()** Muestra la imagen en su último estado de edición por pantalla.
- **binarize()** Binariza la imagen, originalmente en escala de grises [0,255]. Utiliza como *treshold* la mitad (o el especificado) del máximo valor encontrado en la imagen y devuelve una fotografía en blanco (255) y negro (0).
- **soften()** Dado que la calidad de la binarización depende de lo bien que se haya ajustado la exposición de la cámara, esta función permite corregir las imperfecciones en la silueta de los objetos fotografiados (un fiducial por ejemplo). Realiza un promedio en la fotografía tomando un *kernel* del tamaño especificado por el usuario.
- **serch_cm()** Busca el "centro de masa" de un fiducial, u otra silueta, en una imagen binarizada que se encuentre en el campo de visión. Obteniendo de esta forma el centro de su posición de una forma precisa. Realiza un promedio al número de píxeles blancos en ambos ejes.
- **search_border()** Una vez binarizada la imagen, se puede realizar una búsqueda de bordes. Con este fin se buscan los píxeles frontera que estén rodeados por otros de distinto color. Estos se retornan como dos listas $(x,y)$ y se muestra una imagen en pantalla de los bordes y la imagen.
- **circle_treatment()** Fundamental para poder calibrar el robot en la situación real con orificios de Ø=1 mm. Dados los bordes de una imagen binarizada con un círculo (agujero negro) sobre fondo blanco (el metal refleja la luz), se utiliza esta función para obtener el centro del círculo aún cuando este no se vea al completo. Se hace uso de la clase auxiliar *CircleFit*. Esta crea un modelo estadístico a partir de los puntos $(x, y)$ del borde y obtiene mediante una minimización la posición del centro $(x_c, y_c)$ y el radio $r$ del círculo que mejor se ajusta a los datos.

### Ejemplos de uso

Así pues, utilizar la cámara para hacer una fotografía puede ser tan sencillo como ejecutar:

```python
my_camera = IDS_Camera()
my_camera.start_camera()
my_camera.auto_exposure_get_image()
fig = my_camera.image
# Edit and save the image
my_camera.close_device()
```

Además, con el postprocesado utilizando la clase *Image*, se puede obtener resultados como los que se presentan a continuación. Se incluyen las líneas de código ejecutadas y el resultado obtenido en las diferentes etapas.

```python
fig.soften(16).display(True)
fig.binarize().display(True)
fig.find_cm()
fig.display(True)
```


```python
fig = Image(cv2.imread('./path_to_image.png'))

fig.soften(8).binarize(2).display(True)
fig.soften(16).binarize(2.5).display(True)
fig.search_border(show=True, save=True)
fig.circle_treatment(show=True, save=True)
```
 
